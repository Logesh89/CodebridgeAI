"""AI Code Conversion Pipeline & Multi-Stage Auto-Fix Engine for CodeBridge AI.

Orchestrates complete source-to-target language translation with AI models,
AST deterministic fallback, dependency resolution, strict compilation validation,
sandbox execution, self-healing error recovery, and output parity checking.
"""

import logging
import re
import time
from typing import Any, Dict, Optional, Tuple

import openai
from app.core.config import get_settings

settings = get_settings()
from app.services.ast_transpiler import DeterministicTranspiler
from app.services.dependency_manager import DependencyManager
from app.services.iics_ktr_engine import IICSKTREngine
from app.services.language_engine import LanguageEngine
from app.services.language_registry import LanguageRegistry

logger = logging.getLogger(__name__)


class PromptEngine:
    @staticmethod
    def build_system_prompt(from_lang: str, to_lang: str) -> str:
        native_comment = DeterministicTranspiler.get_native_comment_prefix(to_lang)
        return f"""You are a deterministic, zero-hallucination polyglot code compiler and AST-level interpreter.
Your objective is to convert source code from {from_lang} to {to_lang} with exact functional, behavioral, and output parity.

Critical Formatting Rules (Zero Exception):
1. Raw Executable Code Only: Output strictly valid, runnable code for {to_lang}.
2. No Markdown Backticks: Do NOT wrap code in ``` or ```{to_lang}.
3. No Conversational Preamble or Postscript: Do NOT write introductions, confirmations, notes, or explanations.
4. No Echoing/Commenting Source Code: Output ONLY the converted target logic.
5. Native Comment Syntax Only: Use strictly valid comments for {to_lang}:
   - Use '{native_comment.strip()}' for target comments.
6. Target Language Type Conversion Rules:
   - For Python: NEVER output C/Java-style type casts like '(int) ch' or '(double) x'. Use 'ord(ch)' for char to int ASCII, 'int(x)', or 'float(x)'.
7. Import & Dependency Parity:
   - Include all necessary imports, modules, and headers required for target execution.
"""

    @staticmethod
    def build_user_prompt(from_lang: str, to_lang: str, source_code: str, file_name: str = "") -> str:
        file_ctx = f" (File: {file_name})" if file_name else ""
        return f"Convert the following {from_lang} code{file_ctx} to strictly valid {to_lang}:\n\n{source_code}"

    @staticmethod
    def build_autofix_prompt(from_lang: str, to_lang: str, source_code: str, failed_code: str, error_msg: str, attempt: int) -> str:
        return f"""The previous conversion attempt from {from_lang} to {to_lang} failed validation/compilation.

SOURCE CODE ({from_lang}):
{source_code}

FAILED TARGET CODE ({to_lang}):
{failed_code}

COMPILER / RUNTIME ERROR LOG:
{error_msg}

INSTRUCTIONS FOR AUTO-FIX (Attempt {attempt}):
1. Fix the exact syntax, type cast, import, or compilation error shown above.
2. If converting to Python: DO NOT use '(int) var' syntax. Use 'ord(var)' for character ASCII values or 'int(var)'.
3. Output ONLY the fixed, fully executable {to_lang} target code. No markdown fences.
"""


class ConversionPipeline:
    def __init__(self):
        if settings.openai_api_key:
            self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        else:
            self.client = None

    async def execute_pipeline(
        self,
        source_code: str,
        from_lang: str,
        to_lang: str,
        file_name: str = "",
        max_autofix_attempts: int = 5,
    ) -> Dict[str, Any]:
        start_time = time.time()
        from_clean = from_lang.lower().strip()
        to_clean = to_lang.lower().strip()

        # Handle Dedicated IICS JSON -> Pentaho KTR Conversion
        if ("iics" in from_clean or from_clean in ["json", "iics_json"]) and ("ktr" in to_clean or "pentaho" in to_clean or to_clean in ["xml", "ktr_xml"]):
            res = IICSKTREngine.convert_iics_json_to_ktr(source_code)
            res["conversion_time_ms"] = round((time.time() - start_time) * 1000, 2)
            res["model"] = "CodeBridge Dynamic IICS Engine"
            return res

        # Stage 1: Initial Translation Generation
        generated_code, model_used, gen_err = await self._generate_code(source_code, from_clean, to_clean, file_name)

        if gen_err and not generated_code:
            return {
                "success": False,
                "status": "FAILED",
                "converted_code": None,
                "error": gen_err,
                "message": f"AI Generation Failed: {gen_err}",
                "attempts": 1,
            }

        current_code = self._clean_code_output(generated_code, to_clean)

        # Stage 2: Initial Dependency Detection & Syntax Validation
        dep_res = DependencyManager.resolve_dependencies(current_code, to_clean)
        valid, syntax_msg, is_real_comp = LanguageEngine.validate_syntax(current_code, to_clean)
        exec_res = LanguageEngine.execute_in_sandbox(current_code, to_clean)

        # Stage 3: Multi-Stage Auto-Fix & Dependency Self-Healing Loop (Up to 5 attempts)
        attempt = 1
        autofix_history = []

        while not valid and attempt < max_autofix_attempts:
            error_to_fix = syntax_msg if not valid else exec_res.get("stderr", "")
            logger.info("Auto-fix attempt %d for %s -> %s (Error: %s)", attempt, from_clean, to_clean, error_to_fix[:100])

            # First: Attempt automated dependency installation if missing package error
            dep_fix = DependencyManager.resolve_dependencies(current_code, to_clean, error_to_fix)
            if dep_fix.get("resolved"):
                valid, syntax_msg, is_real_comp = LanguageEngine.validate_syntax(current_code, to_clean)
                exec_res = LanguageEngine.execute_in_sandbox(current_code, to_clean)
                if valid:
                    autofix_history.append({"attempt": attempt, "error": f"Auto-installed package '{dep_fix.get('installed_packages')}'", "success": True})
                    break

            # Second: LLM Auto-Fix for logic or syntax errors
            fixed_code, _, fix_err = await self._autofix_code(
                source_code=source_code,
                failed_code=current_code,
                error_msg=error_to_fix,
                from_lang=from_clean,
                to_lang=to_clean,
                attempt=attempt,
            )

            if fixed_code:
                current_code = self._clean_code_output(fixed_code, to_clean)
                valid, syntax_msg, is_real_comp = LanguageEngine.validate_syntax(current_code, to_clean)
                exec_res = LanguageEngine.execute_in_sandbox(current_code, to_clean)
                autofix_history.append({"attempt": attempt, "error": error_to_fix, "success": valid})

            attempt += 1

        # Stage 4: Output Parity & Status Calculation
        src_exec = LanguageEngine.execute_in_sandbox(source_code, from_clean)
        
        # Check if source and target outputs match
        if src_exec["stdout"].strip() and exec_res["stdout"].strip():
            output_match = (src_exec["stdout"].strip() == exec_res["stdout"].strip())
        elif not src_exec["stdout"].strip() and not exec_res["stdout"].strip():
            output_match = True
        else:
            output_match = False

        # Honest Status Assignment Rules:
        # PRODUCTION_READY requires valid syntax AND target execution exit code 0 AND output match!
        if valid and exec_res["success"] and output_match and (is_real_comp or exec_res.get("is_virtual_runtime")):
            final_status = "PRODUCTION_READY"
        elif valid and exec_res["success"] and not output_match:
            final_status = "OUTPUT_MISMATCH"
        elif valid and not is_real_comp:
            final_status = "SYNTAX_HEURISTIC_ONLY"
        elif valid:
            final_status = "PARTIALLY_VALIDATED"
        else:
            final_status = "FAILED"

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "success": valid,
            "status": final_status,
            "converted_code": current_code,
            "model": model_used,
            "attempts": attempt,
            "compilation_status": "SUCCESS" if valid else "FAILED",
            "compilation_message": syntax_msg,
            "runtime_status": exec_res.get("status", "UNAVAILABLE"),
            "source_output": src_exec.get("stdout", "") or src_exec.get("stderr", ""),
            "target_output": exec_res.get("stdout", "") or exec_res.get("stderr", ""),
            "output_match": output_match,
            "autofix_history": autofix_history,
            "dependency_info": dep_res,
            "conversion_time_ms": elapsed_ms,
            "message": f"Conversion completed ({final_status}) in {elapsed_ms}ms with {attempt} attempt(s).",
        }

    async def _generate_code(
        self, source_code: str, from_lang: str, to_lang: str, file_name: str
    ) -> Tuple[str, str, Optional[str]]:
        if not self.client or not settings.openai_api_key:
            code = DeterministicTranspiler.transpile(source_code, from_lang, to_lang)
            return code, "CodeBridge Transpiler", None

        try:
            sys_prompt = PromptEngine.build_system_prompt(from_lang, to_lang)
            user_prompt = PromptEngine.build_user_prompt(from_lang, to_lang, source_code, file_name)

            response = await self.client.chat.completions.create(
                model=settings.ai_model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=settings.ai_temperature,
                max_tokens=settings.ai_max_tokens,
            )
            code = response.choices[0].message.content or ""
            return code, settings.ai_model, None
        except Exception as e:
            logger.warning("OpenAI API call failed (%s). Using deterministic logic transpiler.", e)
            code = DeterministicTranspiler.transpile(source_code, from_lang, to_lang)
            return code, "Deterministic Transpiler", str(e)

    async def _autofix_code(
        self, source_code: str, failed_code: str, error_msg: str, from_lang: str, to_lang: str, attempt: int
    ) -> Tuple[str, str, Optional[str]]:
        if not self.client or not settings.openai_api_key:
            code = DeterministicTranspiler.transpile(source_code, from_lang, to_lang)
            return code, "Deterministic Transpiler", None

        try:
            sys_prompt = PromptEngine.build_system_prompt(from_lang, to_lang)
            fix_prompt = PromptEngine.build_autofix_prompt(from_lang, to_lang, source_code, failed_code, error_msg, attempt)

            response = await self.client.chat.completions.create(
                model=settings.ai_model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": fix_prompt},
                ],
                temperature=0.1,
                max_tokens=settings.ai_max_tokens,
            )
            code = response.choices[0].message.content or ""
            return code, settings.ai_model, None
        except Exception as e:
            code = DeterministicTranspiler.transpile(source_code, from_lang, to_lang)
            return code, "Deterministic Transpiler", str(e)

    @staticmethod
    def _clean_code_output(code: str, to_lang: str) -> str:
        clean = code.strip()

        # Extract content inside markdown code fences if LLM outputs markdown
        fence_match = re.search(r'```(?:\w+)?\n([\s\S]*?)\n```', clean)
        if fence_match:
            clean = fence_match.group(1).strip()
        elif "```" in clean:
            lines = clean.split("\n")
            code_lines = [l for l in lines if not l.startswith("```")]
            clean = "\n".join(code_lines).strip()

        # Remove prepended conversational text if present
        if clean.lower().startswith("here is") or clean.lower().startswith("sure") or clean.lower().startswith("certainly"):
            clean = re.sub(r'^(?:here is|sure|certainly).*\n', '', clean, flags=re.IGNORECASE).strip()

        # Clean lingering C/Java explicit type casts in Python code
        if to_lang.lower().strip() in ["python", "py", "pyspark"]:
            clean = DeterministicTranspiler.clean_python_casts(clean)

        return clean
