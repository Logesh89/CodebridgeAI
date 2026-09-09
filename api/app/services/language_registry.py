"""Centralized Language Registry for CodeBridge AI.

Defines all supported programming, scripting, and ETL languages,
their compilers, interpreters, extensions, syntax constraints, and execution requirements.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import shutil


@dataclass
class LanguageDefinition:
    id: str
    name: str
    extensions: List[str]
    target_ext: str
    mime_accept: str
    compiler_cmd: Optional[str] = None
    interpreter_cmd: Optional[str] = None
    syntax_checker_cmd: Optional[str] = None
    requires_main_wrapper: bool = False
    supports_compilation: bool = False
    supports_execution: bool = False
    system_prompt_rules: str = ""
    target_syntax_restrictions: str = ""

    def is_compiler_available(self) -> bool:
        if self.compiler_cmd:
            return shutil.which(self.compiler_cmd) is not None
        return False

    def is_interpreter_available(self) -> bool:
        if self.interpreter_cmd:
            # Handle commands like 'go run' or 'php -l'
            cmd = self.interpreter_cmd.split()[0]
            return shutil.which(cmd) is not None
        return False


LANGUAGE_REGISTRY: Dict[str, LanguageDefinition] = {
    "c": LanguageDefinition(
        id="c",
        name="C",
        extensions=[".c", ".h"],
        target_ext=".c",
        mime_accept=".c,.h",
        compiler_cmd="gcc",
        requires_main_wrapper=True,
        supports_compilation=True,
        supports_execution=True,
        system_prompt_rules=(
            "Must be ISO C compliant code. Include <stdio.h>, <stdlib.h>, <string.h>. "
            "Must define `int main()` entry point. Use `printf()` for output and `scanf()` for input. "
            "Declare all variables with explicit static C types (int, float, char*, double, long)."
        ),
        target_syntax_restrictions=(
            "DO NOT include Python syntax (def, print(), input(), if __name__, import). "
            "DO NOT include Java syntax (public class, System.out). "
            "Output ONLY valid C source code."
        ),
    ),
    "cpp": LanguageDefinition(
        id="cpp",
        name="C++",
        extensions=[".cpp", ".cc", ".cxx", ".hpp", ".h"],
        target_ext=".cpp",
        mime_accept=".cpp,.cc,.hpp",
        compiler_cmd="g++",
        requires_main_wrapper=True,
        supports_compilation=True,
        supports_execution=True,
        system_prompt_rules=(
            "Modern C++17/C++20. Include <iostream>, <vector>, <string>, <memory>. "
            "Use `using namespace std;`. Must define `int main()`. Use `cin` and `cout`."
        ),
        target_syntax_restrictions="DO NOT leak Python or C# syntax.",
    ),
    "java": LanguageDefinition(
        id="java",
        name="Java",
        extensions=[".java"],
        target_ext=".java",
        mime_accept=".java",
        compiler_cmd="javac",
        interpreter_cmd="java",
        requires_main_wrapper=True,
        supports_compilation=True,
        supports_execution=True,
        system_prompt_rules=(
            "Must define `public class MainProgram` with `public static void main(String[] args)`. "
            "Use `Scanner` for user input and `System.out.println()` for console output."
        ),
        target_syntax_restrictions="DO NOT use top-level script statements or Python def/print syntax.",
    ),
    "python": LanguageDefinition(
        id="python",
        name="Python",
        extensions=[".py"],
        target_ext=".py",
        mime_accept=".py",
        interpreter_cmd="python",
        supports_execution=True,
        system_prompt_rules=(
            "Clean PEP8 Python 3.12+ code. Include necessary stdlib imports. "
            "Use `if __name__ == '__main__':` entry block if executing top-level logic."
        ),
        target_syntax_restrictions="DO NOT include C/Java type declarations or semicolons.",
    ),
    "csharp": LanguageDefinition(
        id="csharp",
        name="C# / .NET",
        extensions=[".cs"],
        target_ext=".cs",
        mime_accept=".cs",
        compiler_cmd="dotnet",
        requires_main_wrapper=True,
        supports_compilation=True,
        supports_execution=True,
        system_prompt_rules=(
            "Include `using System;`. Must define `namespace MainProgram { class Program { static void Main(string[] args) { ... } } }`. "
            "Use `Console.WriteLine()` and `Console.ReadLine()`."
        ),
        target_syntax_restrictions="DO NOT output Python def or C++ std::cout syntax.",
    ),
    "javascript": LanguageDefinition(
        id="javascript",
        name="JavaScript / Node.js",
        extensions=[".js", ".mjs"],
        target_ext=".js",
        mime_accept=".js,.mjs",
        interpreter_cmd="node",
        supports_execution=True,
        system_prompt_rules="Modern ES6+ Node.js code. Use `console.log()` for output and `readline` or `fs` for input/IO.",
        target_syntax_restrictions="DO NOT include C/C++ includes or type annotations.",
    ),
    "typescript": LanguageDefinition(
        id="typescript",
        name="TypeScript",
        extensions=[".ts", ".tsx"],
        target_ext=".ts",
        mime_accept=".ts,.tsx",
        compiler_cmd="tsc",
        interpreter_cmd="node",
        supports_compilation=True,
        supports_execution=True,
        system_prompt_rules="Valid strict TypeScript with explicit type annotations for variables, parameters, and function return values.",
        target_syntax_restrictions="DO NOT use `any` unless dynamically unavoidable.",
    ),
    "go": LanguageDefinition(
        id="go",
        name="Go",
        extensions=[".go"],
        target_ext=".go",
        mime_accept=".go",
        compiler_cmd="go",
        interpreter_cmd="go run",
        requires_main_wrapper=True,
        supports_compilation=True,
        supports_execution=True,
        system_prompt_rules=(
            "Must specify `package main`. Import `fmt`, `os`, or `bufio`. "
            "Must define `func main()`. Use `fmt.Println()` and `fmt.Scanln()`."
        ),
        target_syntax_restrictions="DO NOT include C/Java keywords like class, public, void, or Python def.",
    ),
    "rust": LanguageDefinition(
        id="rust",
        name="Rust",
        extensions=[".rs"],
        target_ext=".rs",
        mime_accept=".rs",
        compiler_cmd="rustc",
        requires_main_wrapper=True,
        supports_compilation=True,
        supports_execution=True,
        system_prompt_rules="Valid idiomatic Rust. Must define `fn main()`. Use `println!` macro and `std::io` for input.",
        target_syntax_restrictions="DO NOT output Python def or C printf syntax.",
    ),
    "php": LanguageDefinition(
        id="php",
        name="PHP",
        extensions=[".php"],
        target_ext=".php",
        mime_accept=".php",
        interpreter_cmd="php",
        syntax_checker_cmd="php -l",
        supports_execution=True,
        system_prompt_rules="Valid PHP 8.x code starting with `<?php`. Use `echo` or `print_r()` for output.",
        target_syntax_restrictions="Must start with `<?php` tag.",
    ),
    "sql": LanguageDefinition(
        id="sql",
        name="SQL Query",
        extensions=[".sql"],
        target_ext=".sql",
        mime_accept=".sql",
        system_prompt_rules="Valid Standard ANSI SQL query statements ending with semicolons.",
    ),
    "pyspark": LanguageDefinition(
        id="pyspark",
        name="PySpark DataFrames",
        extensions=[".py", ".pyspark"],
        target_ext=".py",
        mime_accept=".py,.pyspark",
        system_prompt_rules="Valid PySpark code with SparkSession initialization and DataFrame operations.",
    ),
    "shell": LanguageDefinition(
        id="shell",
        name="Shell Script (Bash)",
        extensions=[".sh", ".bash"],
        target_ext=".sh",
        mime_accept=".sh,.bash",
        interpreter_cmd="bash",
        supports_execution=True,
        system_prompt_rules="Valid Bash shell script starting with `#!/bin/bash`.",
    ),
    "powershell": LanguageDefinition(
        id="powershell",
        name="PowerShell",
        extensions=[".ps1"],
        target_ext=".ps1",
        mime_accept=".ps1",
        interpreter_cmd="pwsh",
        supports_execution=True,
        system_prompt_rules="Valid PowerShell script code.",
    ),
    "snaplogic": LanguageDefinition(
        id="snaplogic",
        name="SnapLogic AST (JSON)",
        extensions=[".json", ".slp"],
        target_ext=".json",
        mime_accept=".json,.slp",
        system_prompt_rules="Valid SnapLogic pipeline AST JSON representation.",
    ),
    "iics": LanguageDefinition(
        id="iics",
        name="IICS JSON",
        extensions=[".json", ".iics"],
        target_ext=".json",
        mime_accept=".json,.iics",
        system_prompt_rules="Valid Informatica Intelligent Cloud Services (IICS) mapping JSON export.",
    ),
    "pentaho_ktr": LanguageDefinition(
        id="pentaho_ktr",
        name="Pentaho KTR (XML)",
        extensions=[".ktr", ".xml"],
        target_ext=".ktr",
        mime_accept=".ktr,.xml",
        system_prompt_rules="Valid Pentaho Data Integration Kettle KTR XML transformation file structure.",
    ),
    "json": LanguageDefinition(
        id="json",
        name="JSON Config",
        extensions=[".json"],
        target_ext=".json",
        mime_accept=".json",
        system_prompt_rules="Strictly valid JSON syntax.",
    ),
    "xml": LanguageDefinition(
        id="xml",
        name="XML Document",
        extensions=[".xml"],
        target_ext=".xml",
        mime_accept=".xml",
        system_prompt_rules="Strictly valid XML syntax.",
    ),
    "yaml": LanguageDefinition(
        id="yaml",
        name="YAML Config",
        extensions=[".yaml", ".yml"],
        target_ext=".yaml",
        mime_accept=".yaml,.yml",
        system_prompt_rules="Strictly valid YAML syntax.",
    ),
}


class LanguageRegistry:
    @staticmethod
    def get(lang_id: str) -> LanguageDefinition:
        key = lang_id.lower().replace("-", "").replace("_", "").replace(" ", "")
        for k, lang_def in LANGUAGE_REGISTRY.items():
            if k == key or lang_def.id == key or lang_def.name.lower() == key:
                return lang_def
        return LanguageDefinition(
            id=lang_id,
            name=lang_id.capitalize(),
            extensions=[".txt"],
            target_ext=".txt",
            mime_accept="text/plain",
            system_prompt_rules="Produce valid code in target language syntax.",
        )
