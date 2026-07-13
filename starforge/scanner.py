"""Project scanner for analyzing repository structure and detecting tech stack."""

import os
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple


class ProjectScanner:
    """Scans a project directory to detect tech stack, file structure, and basic metrics."""

    # Directories and files to ignore
    IGNORE_DIRS = {
        ".git",
        ".github",
        "node_modules",
        ".venv",
        "venv",
        "env",
        "__pycache__",
        ".pytest_cache",
        ".tox",
        "dist",
        "build",
        ".mypy_cache",
        ".ruff_cache",
        ".vscode",
        ".idea",
        "target",
        ".gradle",
        "vendor",
    }

    IGNORE_PATTERNS = {
        r"\.git.*",
        r"__pycache__.*",
        r"\..*cache.*",
        r"\..*egg-info.*",
        r"node_modules.*",
        r"venv.*",
        r"env.*",
    }

    # Tech stack detection patterns
    TECH_PATTERNS = {
        "Python": [r"\.py$", r"pyproject\.toml", r"requirements\.txt", r"setup\.py", r"Pipfile"],
        "JavaScript": [r"\.js$", r"package\.json", r"\.tsx?$"],
        "TypeScript": [r"\.tsx?$", r"tsconfig\.json"],
        "Node.js": [r"package\.json", r"yarn\.lock", r"pnpm-lock\.yaml"],
        "React": [r"package\.json", r"\.jsx$", r"\.tsx$"],
        "Vue": [r"\.vue$", r"vue\.config\.js"],
        "Go": [r"\.go$", r"go\.mod"],
        "Rust": [r"\.rs$", r"Cargo\.toml"],
        "Java": [r"\.java$", r"pom\.xml", r"build\.gradle"],
        "C/C++": [r"\.c$", r"\.cpp$", r"\.h$", r"CMakeLists\.txt"],
        "Docker": [r"Dockerfile", r"docker-compose\.yml"],
        "GitHub Actions": [r"\.github/workflows.*\.yml"],
        "PostgreSQL": [r"\.sql$"],
        "MongoDB": [r"\.mongo$"],
        "Redis": [r"\.redis$"],
    }

    def __init__(self, project_path: str = "."):
        """Initialize the scanner with a project path."""
        self.project_path = Path(project_path).resolve()
        if not self.project_path.exists():
            raise ValueError(f"Project path does not exist: {self.project_path}")
        self._scan_cache = None

    def should_ignore(self, path: Path) -> bool:
        """Check if a path should be ignored."""
        name = path.name
        if name in self.IGNORE_DIRS:
            return True
        for pattern in self.IGNORE_PATTERNS:
            if re.match(pattern, name):
                return True
        return False

    def scan(self) -> Dict:
        """Scan the project and return structure, tech stack, and metrics."""
        # Return cached results if available
        if self._scan_cache is not None:
            return self._scan_cache

        file_types = defaultdict(int)
        tech_stack = set()
        total_files = 0
        total_lines = 0
        project_name = self.project_path.name

        # Scan files
        for root, dirs, files in os.walk(self.project_path):
            # Filter directories to ignore
            dirs[:] = [d for d in dirs if not self.should_ignore(Path(root) / d)]

            for file in files:
                file_path = Path(root) / file

                # Skip if hidden (except documented files)
                if file.startswith(".") and file not in [".gitignore"]:
                    continue

                total_files += 1
                ext = file_path.suffix or file

                # Count file types
                file_types[ext] += 1

                # Detect tech stack
                for tech, patterns in self.TECH_PATTERNS.items():
                    for pattern in patterns:
                        if re.search(pattern, str(file_path)):
                            tech_stack.add(tech)
                            break

                # Count lines for code files
                try:
                    if ext in [
                        ".py",
                        ".js",
                        ".ts",
                        ".tsx",
                        ".jsx",
                        ".go",
                        ".rs",
                        ".java",
                        ".cpp",
                        ".c",
                        ".h",
                    ]:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            total_lines += len(f.readlines())
                except (IOError, OSError):
                    pass

        # Try to detect project purpose from README or main files
        purpose = self._detect_purpose()

        self._scan_cache = {
            "name": project_name,
            "path": str(self.project_path),
            "file_count": total_files,
            "lines_of_code": total_lines,
            "file_types": dict(file_types),
            "tech_stack": sorted(list(tech_stack)),
            "purpose": purpose,
        }

        return self._scan_cache

    def _detect_purpose(self) -> str:
        """Try to detect project purpose from README or other files."""
        # Check README
        readme_paths = [
            self.project_path / "README.md",
            self.project_path / "README.rst",
            self.project_path / "README.txt",
        ]

        for readme_path in readme_paths:
            if readme_path.exists():
                try:
                    with open(readme_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # Extract first paragraph that looks like a description
                        lines = content.split("\n")
                        for line in lines:
                            line = line.strip()
                            if (
                                line
                                and not line.startswith("#")
                                and not line.startswith("-")
                                and len(line) > 10
                            ):
                                return line[:150]
                except (IOError, OSError):
                    pass

        return "A comprehensive project with multiple features"

    def get_framework_info(self) -> Dict:
        """Get framework-specific information if available."""
        info = {}

        # Check for Python info
        if "Python" in self.scan()["tech_stack"]:
            req_file = self.project_path / "requirements.txt"
            if req_file.exists():
                try:
                    with open(req_file, "r") as f:
                        info["python_deps"] = [line.strip() for line in f if line.strip()]
                except (IOError, OSError):
                    pass

        # Check for Node.js info
        package_json = self.project_path / "package.json"
        if package_json.exists():
            try:
                import json

                with open(package_json, "r") as f:
                    pkg_data = json.load(f)
                    info["npm_name"] = pkg_data.get("name")
                    info["npm_description"] = pkg_data.get("description")
            except (IOError, OSError, json.JSONDecodeError):
                pass

        return info
