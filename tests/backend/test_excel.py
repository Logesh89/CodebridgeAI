"""Excel validation service tests."""

import uuid

import pandas as pd
import pytest

from app.services.excel_service import ExcelService, REQUIRED_COLUMNS


def test_required_columns_defined():
    assert "Pipeline Name" in REQUIRED_COLUMNS
    assert "Pipeline Path" in REQUIRED_COLUMNS


@pytest.mark.asyncio
async def test_validate_missing_columns(db_session):
    service = ExcelService(db_session)
    df = pd.DataFrame({"Name": ["test"]})
    content = df.to_csv(index=False).encode()

    with pytest.raises(Exception):
        await service.process_upload(content, "test.csv", uuid.uuid4())
