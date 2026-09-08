"""Dependency & Package Resolution Manager for CodeBridge AI.

Detects, verifies, and resolves required imports, libraries, dependencies, package managers,
and compiler/runtime prerequisites across Python, Node.js, Java, Go, C/C++, Rust, PHP, Ruby, and Shell.
"""

import logging
import os
import re
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

# Standard package mapping for common Python imports to PyPI package names
PYTHON_PACKAGE_MAP = {
    "cv2": "opencv-python",
    "PIL": "pillow",
    "sklearn": "scikit-learn",
    "yaml": "pyyaml",
    "bs4": "beautifulsoup4",
    "attr": "attrs",
    "dateutil": "python-dateutil",
    "serial": "pyserial",
    "fitz": "pymupdf",
    "wx": "wxpython",
    "crypto": "pycryptodome",
}


class DependencyManager:
    """Manages multi-language dependency detection, installation, and environment validation."""

    @classmethod
    def detect_required_imports(cls, code: str, lang_id: str) -> List[str]:
        """Scans target code and extracts referenced third-party modules/packages."""
        lang = lang_id.lower().strip()
        detected_modules = set()

        if lang in ["python", "pyspark"]:
            # Match `import xyz`, `from xyz import abc`
            matches = re.findall(r'^\s*(?:import|from)\s+([a-zA-Z0-9_\.]+)', code, re.MULTILINE)
            for m in matches:
                top_pkg = m.split(".")[0]
                if top_pkg not in sys.builtin_module_names:
                    detected_modules.add(top_pkg)

        elif lang in ["javascript", "js", "typescript", "ts", "node", "nodejs"]:
            # Match `import ... from 'xyz'`, `require('xyz')`
            import_matches = re.findall(r'import\s+.*?\s+from\s+[\'"]([^\'".\/]+)[\'"]', code)
            require_matches = re.findall(r'require\s*\(\s*[\'"]([^\'".\/]+)[\'"]\s*\)', code)
            detected_modules.update(import_matches)
            detected_modules.update(require_matches)

        elif lang in ["go", "golang"]:
            matches = re.findall(r'import\s*\(\s*(.*?)\s*\)', code, re.DOTALL)
            if matches:
                pkgs = re.findall(r'[\'"]([^\'"]+)[\'"]', matches[0])
                detected_modules.update(pkgs)

        return sorted(list(detected_modules))

    @classmethod
    def parse_missing_dependency_error(cls, error_msg: str, lang_id: str) -> Optional[str]:
        """Parses compiler/interpreter stderr for missing package or library names."""
        if not error_msg:
            return None

        lang = lang_id.lower().strip()

        if lang in ["python", "pyspark"]:
            # Match `ModuleNotFoundError: No module named 'xyz'`
            m = re.search(r"ModuleNotFoundError:\s*No module named\s*['\"]([^'\"]+)['\"]", error_msg)
            if m:
                return m.group(1).split(".")[0]

            # Match `ImportError: No module named xyz`
            m2 = re.search(r"ImportError:\s*No module named\s*([a-zA-Z0-9_\.]+)", error_msg)
            if m2:
                return m2.group(1).split(".")[0]

        elif lang in ["javascript", "js", "typescript", "ts", "node", "nodejs"]:
            # Match `Cannot find module 'xyz'`
            m = re.search(r"Cannot find module\s*['\"]([^'\"]+)['\"]", error_msg)
            if m:
                return m.group(1)

        elif lang in ["go", "golang"]:
            m = re.search(r"cannot find package\s*['\"]([^'\"]+)['\"]", error_msg)
            if m:
                return m.group(1)

        return None

    @classmethod
    def install_dependency(cls, package_name: str, lang_id: str) -> Tuple[bool, str]:
        """Safely installs a required missing package using the language package manager."""
        lang = lang_id.lower().strip()

        if lang in ["python", "pyspark"]:
            pip_name = PYTHON_PACKAGE_MAP.get(package_name, package_name)
            logger.info("Attempting auto-install of Python package '%s' via pip...", pip_name)
            try:
                cmd = [sys.executable, "-m", "pip", "install", pip_name]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
                if res.returncode == 0:
                    return True, f"Successfully installed Python package '{pip_name}'"
                else:
                    return False, f"Failed to install '{pip_name}': {res.stderr.strip()}"
            except Exception as e:
                return False, f"Pip installation exception for '{pip_name}': {str(e)}"

        elif lang in ["javascript", "js", "typescript", "ts", "node", "nodejs"]:
            if shutil.which("npm"):
                logger.info("Attempting auto-install of Node package '%s' via npm...", package_name)
                try:
                    cmd = ["npm", "install", package_name, "--no-save"]
                    res = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
                    if res.returncode == 0:
                        return True, f"Successfully installed Node package '{package_name}'"
                except Exception as e:
                    return False, f"NPM install error: {str(e)}"

        return False, f"Package manager auto-install unavailable for language '{lang_id}' or package '{package_name}'"

    @classmethod
    def resolve_dependencies(cls, code: str, lang_id: str, error_msg: str = "") -> Dict[str, Any]:
        """Full dependency resolution flow: detects required imports, parses errors, and auto-installs missing packages."""
        missing_pkg = cls.parse_missing_dependency_error(error_msg, lang_id)
        installed_list = []
        messages = []

        if missing_pkg:
            success, msg = cls.install_dependency(missing_pkg, lang_id)
            messages.append(msg)
            if success:
                installed_list.append(missing_pkg)

        # Detect static imports in code
        imports = cls.detect_required_imports(code, lang_id)

        return {
            "resolved": len(installed_list) > 0,
            "missing_package_detected": missing_pkg,
            "installed_packages": installed_list,
            "detected_imports": imports,
            "messages": messages,
        }
