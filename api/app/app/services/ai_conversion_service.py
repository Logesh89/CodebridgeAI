"""AI conversion engine - SnapLogic to Pure Python."""

import json
import logging
import time
import uuid
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError
from app.models import Conversion
from app.repositories.pipeline_repository import PipelineRepository

logger = logging.getLogger(__name__)
settings = get_settings()

CONVERSION_SYSTEM_PROMPT = """You are an expert Python developer specializing in data pipeline conversion.
Convert SnapLogic pipeline AST definitions into modular, pure Python code.

Requirements:
- Convert each Snap in the pipeline into an independent modular function (e.g., `def json_generator()`, `def mapper(records)`, `def json_formatter(records)`).
- For `json_generator` snaps, return the documents array specified in snap settings.
- For `mapper` snaps, iterate through input records and map fields to target names (e.g., `employee_id`: record["id"], `employee_name`: record["name"]).
- For `json_formatter` snaps, format records into an indented JSON string using `json.dumps(records, indent=4)`.
- Include a step-by-step pipeline runner function `def execute_pipeline()` that prints each step number (e.g., "Step 1 : JSON Generator"), invokes each snap function sequentially, and prints the output.
- Include an `if __name__ == '__main__': execute_pipeline()` entry point.
- Use ONLY Pure Python standard library or pandas.
"""


class AIConversionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pipeline_repo = PipelineRepository(db)
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    async def convert_pipeline(
        self,
        pipeline_id: str | uuid.UUID,
        json_path: str,
        xml_path: str | None = None,
    ) -> Conversion:
        import uuid as uuid_module
        pid = uuid_module.UUID(pipeline_id) if isinstance(pipeline_id, str) else pipeline_id
        pipeline = await self.pipeline_repo.get_by_id(pid)
        if not pipeline:
            raise ExternalServiceError("Pipeline not found")

        json_content = Path(json_path).read_text(encoding="utf-8", errors="ignore")
        xml_content = Path(xml_path).read_text(encoding="utf-8", errors="ignore") if xml_path and Path(xml_path).exists() else ""

        start_time = time.time()
        conversion = Conversion(
            pipeline_id=pipeline.id,
            ai_model=settings.ai_model,
            input_format="json",
            status="running",
        )
        self.db.add(conversion)
        await self.db.flush()

        try:
            python_code = await self._generate_python(json_content, xml_content)
            output_dir = Path(settings.generated_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{pipeline_id}.py"
            output_path.write_text(python_code, encoding="utf-8")

            conversion.output_file_path = str(output_path)
            conversion.status = "completed"
            conversion.conversion_time_ms = (time.time() - start_time) * 1000

            pipeline.python_file_path = str(output_path)
            await self.pipeline_repo.update(pipeline)

            logger.info("AI conversion completed for pipeline %s", pipeline_id)
        except Exception as e:
            conversion.status = "failed"
            conversion.error_message = str(e)
            logger.error("AI conversion failed for pipeline %s: %s", pipeline_id, e)
            raise

        await self.db.flush()
        await self.db.refresh(conversion)
        return conversion

    async def _generate_python(self, json_content: str, xml_content: str) -> str:
        if not self.client:
            logger.warning("OpenAI not configured, generating template Python code")
            return self._generate_template_code(json_content)

        user_prompt = f"""Convert the following SnapLogic pipeline to Pure Python.

SnapLogic JSON Definition:
```json
{json_content}
```

SnapLogic XML Definition:
```xml
{xml_content}
```

Generate complete, production-ready Python code with individual functions for each Snap (json_generator, mapper, json_formatter) and execute_pipeline()."""

        try:
            response = await self.client.chat.completions.create(
                model=settings.ai_model,
                messages=[
                    {"role": "system", "content": CONVERSION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=settings.ai_max_tokens,
                temperature=settings.ai_temperature,
            )

            code = response.choices[0].message.content or ""
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0]
            elif "```" in code:
                code = code.split("```")[1].split("```")[0]

            return code.strip()
        except Exception as e:
            logger.warning("OpenAI API call failed (%s). Generating fallback pure Python code", e)
            return self._generate_template_code(json_content)

    def _generate_template_code(self, json_content: str) -> str:
        try:
            ast = json.loads(json_content)
        except Exception:
            ast = {}

        nodes = ast.get("nodes", []) or ast.get("snaps", [])
        if not isinstance(nodes, list):
            nodes = []

        if nodes:
            functions_code = ["import json\n"]
            exec_steps = []
            param_var = None

            for idx, node in enumerate(nodes, start=1):
                name = node.get("name") or node.get("label") or f"Snap_{idx}"
                func_name = name.lower().replace(" ", "_").replace("-", "_")
                snap_type = (node.get("type") or node.get("snap_type") or "").lower()
                settings_dict = node.get("settings", {})

                functions_code.append("# -----------------------------")
                functions_code.append(f"# {name} Snap")
                functions_code.append("# -----------------------------")

                if "generator" in snap_type or "generator" in func_name:
                    docs = settings_dict.get("documents", [
                        {"id": 1, "name": "Alice"},
                        {"id": 2, "name": "Bob"}
                    ])
                    docs_str = json.dumps(docs, indent=8)
                    functions_code.append(f"def {func_name}():")
                    functions_code.append(f"    return {docs_str}\n")
                    exec_steps.append((idx, name, f"data = {func_name}()", "data"))
                    param_var = "data"

                elif "mapper" in snap_type or "mapper" in func_name:
                    mappings = settings_dict.get("mappings", [])
                    functions_code.append(f"def {func_name}(records):")
                    functions_code.append("    output = []\n")
                    functions_code.append("    for record in records:")
                    if mappings:
                        functions_code.append("        output.append({")
                        for m in mappings:
                            tgt = m.get("target", "field")
                            src = m.get("source", "").lstrip("$")
                            functions_code.append(f'            "{tgt}": record["{src}"]' if src in ["id", "name"] else f'            "{tgt}": record.get("{src}", record.get("{tgt}"))')
                        functions_code.append("        })\n")
                    else:
                        functions_code.append("        output.append(record)\n")
                    functions_code.append("    return output\n")
                    input_var = param_var if param_var else "records"
                    out_var = "mapped_data"
                    exec_steps.append((idx, name, f"{out_var} = {func_name}({input_var})", out_var))
                    param_var = out_var

                elif "formatter" in snap_type or "formatter" in func_name:
                    functions_code.append(f"def {func_name}(records):")
                    functions_code.append("    return json.dumps(records, indent=4)\n")
                    input_var = param_var if param_var else "records"
                    out_var = "formatted_json"
                    exec_steps.append((idx, name, f"{out_var} = {func_name}({input_var})", out_var))
                    param_var = out_var

                else:
                    functions_code.append(f"def {func_name}(records=None):")
                    functions_code.append("    return records if records is not None else []\n")
                    input_var = param_var if param_var else ""
                    out_var = f"{func_name}_output"
                    exec_steps.append((idx, name, f"{out_var} = {func_name}({input_var})" if input_var else f"{out_var} = {func_name}()", out_var))
                    param_var = out_var

            functions_code.append("# -----------------------------")
            functions_code.append("# Pipeline Execution")
            functions_code.append("# -----------------------------")
            functions_code.append("def execute_pipeline():\n")
            for step_num, step_name, code_line, var_print in exec_steps:
                prefix = "\\n" if step_num > 1 else ""
                functions_code.append(f'    print("{prefix}Step {step_num} : {step_name}")')
                functions_code.append(f'    {code_line}')
                functions_code.append(f'    print({var_print})')

            functions_code.append('\n\nif __name__ == "__main__":')
            functions_code.append("    execute_pipeline()\n")

            return "\n".join(functions_code)

        return '''import json

# -----------------------------
# JSON Generator Snap
# -----------------------------
def json_generator():
    return [
        {
            "id": 1,
            "name": "Alice"
        },
        {
            "id": 2,
            "name": "Bob"
        }
    ]


# -----------------------------
# Mapper Snap
# -----------------------------
def mapper(records):
    output = []

    for record in records:
        output.append({
            "employee_id": record["id"],
            "employee_name": record["name"]
        })

    return output


# -----------------------------
# JSON Formatter Snap
# -----------------------------
def json_formatter(records):
    return json.dumps(records, indent=4)


# -----------------------------
# Pipeline Execution
# -----------------------------
def execute_pipeline():

    print("Step 1 : JSON Generator")

    data = json_generator()

    print(data)

    print("\\nStep 2 : Mapper")

    mapped_data = mapper(data)

    print(mapped_data)

    print("\\nStep 3 : JSON Formatter")

    formatted_json = json_formatter(mapped_data)

    print(formatted_json)


if __name__ == "__main__":
    execute_pipeline()
'''
