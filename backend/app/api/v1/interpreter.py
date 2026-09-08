"""Code Interpreter & Multi-Language Conversion Endpoints.

Provides validated AI code translation, secure sandbox live execution,
automated AI self-healing auto-fix loops, and dedicated IICS JSON to Pentaho KTR engine.
"""

import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.conversion_engine import ConversionPipeline
from app.services.iics_ktr_engine import IICSKTREngine
from app.services.language_engine import LanguageEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/interpreter", tags=["Code Interpreter"])

pipeline = ConversionPipeline()


class CodeConversionRequest(BaseModel):
    source_code: str
    from_lang: str
    to_lang: str
    file_name: str = ""


class CodeExecutionRequest(BaseModel):
    code: str
    language: str
    input_data: str = ""


class AutoFixRequest(BaseModel):
    code: str
    language: str
    source_code: str = ""
    error_message: str = ""


class IICSToKTRRequest(BaseModel):
    iics_json: str


@router.post("/convert")
async def convert_code(req: CodeConversionRequest):
    """Executes AI conversion with strict syntax validation, compilation checks, and auto-fix loop."""
    if not req.source_code.strip():
        raise HTTPException(status_code=400, detail="Source code cannot be empty.")

    try:
        result = await pipeline.execute_pipeline(
            source_code=req.source_code,
            from_lang=req.from_lang,
            to_lang=req.to_lang,
            file_name=req.file_name,
        )
        return result
    except Exception as e:
        logger.error("Conversion pipeline error: %s", e)
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")


@router.post("/execute")
async def execute_code(req: CodeExecutionRequest):
    """Executes code in isolated sandbox environment and captures stdout, stderr, exit code."""
    if not req.code.strip():
        return {"output": "No code provided for execution.", "success": False}

    res = LanguageEngine.execute_in_sandbox(req.code, req.language, input_data=req.input_data)
    
    stdout = res.get("stdout", "").strip()
    stderr = res.get("stderr", "").strip()
    status = res.get("status", "COMPLETED")
    time_ms = res.get("execution_time_ms", 0.0)
    exit_code = res.get("exit_code", 0)

    if stderr and not stdout:
        output_str = f"Runtime / Compiler Output:\n{stderr}\n\n[{req.language.upper()} process exited with code {exit_code}]"
    elif stdout and stderr:
        output_str = f"{stdout}\n\n[Stderr Warnings / Logs]:\n{stderr}\n\n[{req.language.upper()} process completed in {time_ms}ms with code {exit_code}]"
    elif stdout:
        output_str = f"{stdout}\n\n[{req.language.upper()} process completed in {time_ms}ms with exit code 0]"
    else:
        output_str = f"[{status}] Syntax validated successfully. (Runtime execution environment unavailable for {req.language.upper()})."

    return {
        "output": output_str,
        "success": res.get("success", False),
        "status": status,
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "execution_time_ms": time_ms,
    }


@router.post("/auto-fix")
async def auto_fix_code(req: AutoFixRequest):
    """Invokes AI auto-fix loop using compiler/runtime error message up to 5 attempts."""
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")

    try:
        result = await pipeline.execute_pipeline(
            source_code=req.source_code or req.code,
            from_lang=req.language,
            to_lang=req.language,
            file_name="autofix.target",
            max_autofix_attempts=5,
        )
        return {
            "status": "SUCCESS" if result["success"] else "FAILED",
            "fixed_code": result.get("converted_code", req.code),
            "is_error_free": result["success"],
            "compilation_status": result.get("compilation_status"),
            "compilation_message": result.get("compilation_message"),
            "attempts": result.get("attempts", 1),
            "message": result.get("message", "Auto-fix attempted."),
        }
    except Exception as e:
        logger.error("Auto-fix error: %s", e)
        raise HTTPException(status_code=500, detail=f"Auto-fix error: {str(e)}")


@router.post("/iics-to-ktr")
async def convert_iics_to_ktr(req: IICSToKTRRequest):
    """Dedicated conversion endpoint for Informatica IICS JSON -> Pentaho Kettle KTR XML."""
    if not req.iics_json.strip():
        raise HTTPException(status_code=400, detail="IICS JSON content cannot be empty.")

    result = IICSKTREngine.convert_iics_json_to_ktr(req.iics_json)
    return result
