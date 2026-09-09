"""Excel upload and validation service."""

import uuid
from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ValidationError
from app.models import Pipeline, PipelineStatus
from app.repositories.pipeline_repository import PipelineRepository
from app.schemas import ExcelUploadResponse, ExcelValidationError

settings = get_settings()

REQUIRED_COLUMNS = ["Pipeline Name", "Pipeline Path", "Project", "Description"]


class ExcelService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pipeline_repo = PipelineRepository(db)

    def _read_file(self, content: bytes, filename: str) -> pd.DataFrame:
        ext = Path(filename).suffix.lower()
        buffer = BytesIO(content)

        if ext == ".csv":
            return pd.read_csv(buffer)
        if ext in (".xlsx", ".xls"):
            return pd.read_excel(buffer)
        raise ValidationError(f"Unsupported file format: {ext}")

    def _validate_dataframe(self, df: pd.DataFrame) -> tuple[list[dict[str, Any]], list[ExcelValidationError]]:
        errors: list[ExcelValidationError] = []
        valid_rows: list[dict[str, Any]] = []

        # Normalize column names for flexible matching
        col_map = {str(c).strip().lower(): c for c in df.columns}
        for req in REQUIRED_COLUMNS:
            req_lower = req.lower()
            if req_lower in col_map:
                df.rename(columns={col_map[req_lower]: req}, inplace=True)

        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            raise ValidationError(
                f"Missing required columns: {', '.join(missing_cols)}. File headers found: {list(df.columns)}",
                details={"missing_columns": missing_cols},
            )

        df = df.dropna(how="all")
        duplicates = df.duplicated(subset=["Pipeline Path"], keep=False)

        for idx, row in df.iterrows():
            row_num = int(idx) + 2
            row_errors: list[str] = []

            if duplicates[idx]:
                row_errors.append("Duplicate pipeline path")

            name = str(row.get("Pipeline Name", "")).strip()
            if not name or pd.isna(row.get("Pipeline Name")):
                row_errors.append("Pipeline Name is required")

            path = str(row.get("Pipeline Path", "")).strip()
            if not path or pd.isna(row.get("Pipeline Path")):
                row_errors.append("Pipeline Path is required")
            else:
                if not path.startswith("/"):
                    path = f"/{path}"

            if row_errors:
                for err in row_errors:
                    errors.append(ExcelValidationError(row=row_num, error=err))
            else:
                valid_rows.append({
                    "name": name,
                    "path": path,
                    "project": str(row.get("Project", "")).strip() if pd.notna(row.get("Project")) else None,
                    "description": str(row.get("Description", "")).strip() if pd.notna(row.get("Description")) else None,
                })

        return valid_rows, errors

    async def process_upload(
        self,
        content: bytes,
        filename: str,
        user_id: uuid.UUID,
    ) -> ExcelUploadResponse:
        df = self._read_file(content, filename)
        valid_rows, errors = self._validate_dataframe(df)

        batch_id = str(uuid.uuid4())
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / f"{batch_id}_{filename}"
        file_path.write_bytes(content)

        pipelines_created = 0
        for row in valid_rows:
            existing = await self.pipeline_repo.get_by_path(row["path"])
            if existing:
                continue

            pipeline = Pipeline(
                name=row["name"],
                path=row["path"],
                project=row["project"],
                description=row["description"],
                status=PipelineStatus.QUEUED,
                upload_batch_id=batch_id,
                created_by=user_id,
            )
            await self.pipeline_repo.create(pipeline)
            pipelines_created += 1

        return ExcelUploadResponse(
            batch_id=batch_id,
            total_rows=len(df),
            valid_rows=len(valid_rows),
            invalid_rows=len(errors),
            errors=errors,
            pipelines_created=pipelines_created,
        )
