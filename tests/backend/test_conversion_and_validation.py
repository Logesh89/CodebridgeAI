"""Unit tests for AI Conversion and Validation engines."""

import uuid
import pytest
from pathlib import Path
import pandas as pd

from app.models import Pipeline, PipelineStatus, ValidationStatus
from app.services.ai_conversion_service import AIConversionService
from app.services.validation_service import ValidationService


@pytest.mark.asyncio
async def test_ai_conversion_fallback_template(db_session):
    pipeline = Pipeline(
        name="Test Pipeline",
        path="/projects/test/pipe1",
        project="Test Project",
        status=PipelineStatus.QUEUED,
    )
    db_session.add(pipeline)
    await db_session.flush()

    service = AIConversionService(db_session)
    json_content = '{"instance_id": "test_123", "snaps": [{"snap_type": "mapper"}]}'

    code = service._generate_template_code(json_content)
    assert "class SnapLogicPipeline:" in code
    assert "def execute(self)" in code
    assert "main()" in code


@pytest.mark.asyncio
async def test_validation_output_comparison(db_session, tmp_path):
    pipeline = Pipeline(
        name="Validation Test Pipeline",
        path="/projects/test/pipe2",
        project="Test Project",
        status=PipelineStatus.VALIDATING,
    )
    db_session.add(pipeline)
    await db_session.flush()

    # Create dummy matching outputs
    df1 = pd.DataFrame([{"id": 1, "val": "A"}, {"id": 2, "val": "B"}])
    df2 = pd.DataFrame([{"id": 1, "val": "A"}, {"id": 2, "val": "B"}])

    snap_file = tmp_path / "snap.json"
    py_file = tmp_path / "python.json"

    df1.to_json(snap_file, orient="records")
    df2.to_json(py_file, orient="records")

    validation_service = ValidationService(db_session)
    report = await validation_service.compare_outputs(
        pipeline.id,
        str(snap_file),
        str(py_file),
    )

    assert report.status == ValidationStatus.PASSED
    assert report.row_count_match is True
    assert report.column_count_match is True
    assert report.values_match is True
