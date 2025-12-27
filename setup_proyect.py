import os
import sys
import argparse
from pathlib import Path

# --- Constants ---
GITIGNORE_CONTENT = """# --- Python Core ---
__pycache__/
*.py[cod]
*.so
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/

# --- Environments ---
.env
.venv/
env/
venv/
ENV/

# --- Database ---
*.db
*.sqlite3

# --- IDEs ---
.vscode/
.idea/
*.swp
*.ds_store

# --- Agent Sandbox ---
workspace/
logs/
*.log
"""

def generate_structure(project_name):
    """
    Generates the dictionary representing the folder structure.
    """
    
    # Standardize package name (replace hyphens with underscores)
    package_name = project_name.replace("-", "_")

    return {
        "src/": {
            f"{package_name}/": {
                "__init__.py": "",
                "core/": {
                    "__init__.py": "",
                    "models.py": "# SQLAlchemy Models go here\n",
                    "engine.py": "# Pure business logic goes here\n",
                },
                "cli/": {
                    "__init__.py": "",
                    "main.py": "# CLI Entry point (Typer/Click)\n",
                },
                "gui/": {
                    "__init__.py": "",
                    "app.py": "# GUI Entry point (PyQt/Tkinter)\n",
                },
                "utils/": {
                    "__init__.py": "",
                    "config.py": "# Pydantic Settings / Env loader\n",
                },
            },
        },
        "agent_tools/": {
            "__init__.py": "",
            "definitions.py": "# Tool schemas for the Agent\n",
            "handlers.py": "# Python functions the Agent calls\n",
            "runner.py": "# Script to launch the Agent loop\n",
        },
        "resources/": {
            "prompts/": {
                "system_architect.md": "# System prompt for Architecture tasks\n",
            },
            "templates/": {
                "test_case.j2": "# Jinja2 template for generating tests\n",
            },
        },
        "tests/": {
            "__init__.py": "",
            "conftest.py": "# Global Pytest fixtures\n",
            "unit/": {"__init__.py": ""},
            "integration/": {"__init__.py": ""},
            "cli/": {"__init__.py": ""},
            "gui/": {"__init__.py": ""},
            "mocks/": {
                "__init__.py": "",
                "README.md": "Shared mock objects for tests\n",
            },
            "dependency_graph/": {
                f"{package_name}/": {
                    "core/": {},
                    "cli/": {},
                },
                "README.md": "JSON maps linking source files to tests for the Agent\n",
            },
        },
        "docs/": {
            # FLATTENED STRUCTURE FOR AGENT EFFICIENCY
            "epics/": {
                 "README.md": "# Epics\nHigh-level business requirements go here.\n"
            },
            "stories/": {
                 "README.md": "# User Stories\nSpecific, implementable tasks go here.\n"
            },
            "architecture/": {
                 "decisions/": {},
                 "diagrams/": {},
            },
            "standards/": {
                 "style_and_restrictions.md": "# Project Coding Standards & Technical Restrictions\n\n## 1. Code Style\n- Python: PEP8 compliant\n- Formatter: Black\n\n## 2. Restrictions\n- No circular imports\n- No shell commands in Core\n"
            },
            "reference/": {},
        },
        "alembic/": {
            "versions/": {},
            "env.py": "# Alembic env script (connects to src models)\n",
        },
        "workspace/": {},
        
        # Root Level Files
        ".env.example": "DATABASE_URL=sqlite:///./dev.db\nDEBUG=True\n",
        ".env": "DATABASE_URL=sqlite:///./dev.db\nDEBUG=True\n",
        "alembic.ini": "[alembic]\nscript_location = alembic\nsqlalchemy.url = driver://user:pass@localhost/dbname\n",
        "requirements.txt": "typer\nsqlalchemy\nalembic\npydantic-settings\npytest\n",
        "pyproject.toml": f"""[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{project_name}"
version = "0.1.0"
dependencies = [
    "typer",
    "sqlalchemy",
    "alembic",
    "pydantic-settings",
    "pytest"
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
""",
    }