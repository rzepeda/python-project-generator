import os
import sys
import argparse
import json
from pathlib import Path
import shutil

# --- Valid Project Types ---
VALID_PROJECT_TYPES = ['data-centric', 'process-centric']

# --- Architecture Documentation Sources ---
ARCHITECTURE_DOCS = {
    'data-centric': {
        'architecture': 'ARCHITECTURE_DATA_CENTRIC.md',
        'principles': 'ARCHITECTURAL_PRINCIPLES_DATA_CENTRIC.md'
    },
    'process-centric': {
        'architecture': 'ARCHITECTURE_PROCESS_CENTRIC.md',
        'principles': 'ARCHITECTURAL_PRINCIPLES_PROCESS_CENTRIC.md'
    }
}


def load_structure_config(project_type, templates_dir):
    """Load the JSON structure configuration for the project type."""
    # Convert hyphens to underscores for filename
    filename = project_type.replace("-", "_")
    structure_file = Path(templates_dir) / f"structure_{filename}.json"
    
    if not structure_file.exists():
        print(f"Error: Structure file not found: {structure_file}")
        sys.exit(1)
    
    with open(structure_file, 'r') as f:
        return json.load(f)


def load_common_structure(templates_dir):
    """Load the common project structure."""
    common_file = Path(templates_dir) / "structure_common.json"
    
    if not common_file.exists():
        print(f"Error: Common structure file not found: {common_file}")
        sys.exit(1)
    
    with open(common_file, 'r') as f:
        return json.load(f)


def build_folder_from_json(folder_config):
    """Recursively build folder structure from JSON config."""
    result = {}
    
    # Add files if present
    if 'files' in folder_config:
        for filename, content in folder_config['files'].items():
            result[filename] = content
    
    # Add folders if present
    if 'folders' in folder_config:
        for folder_name, folder_data in folder_config['folders'].items():
            result[f"{folder_name}/"] = build_folder_from_json(folder_data)
    
    return result


def generate_core_from_config(config):
    """Generate core folder structure from config."""
    core_structure = {"__init__.py": ""}
    
    for folder_name, folder_info in config['core_structure'].items():
        core_structure[f"{folder_name}/"] = {
            "__init__.py": "",
            "README.md": f"# {folder_name.title()}\n{folder_info['description']}\n\n**Purpose:** {folder_info['purpose']}\n\n**Examples:** {', '.join(folder_info['examples'])}\n"
        }
    
    return core_structure


def generate_utils_from_config(config):
    """Generate utils folder structure from config."""
    utils_structure = {"__init__.py": ""}
    
    for file_name, description in config['utils_structure'].items():
        utils_structure[file_name] = f"# {description}\n"
    
    return utils_structure


def generate_tests_unit_from_config(config):
    """Generate unit test folder structure from config."""
    unit_structure = {"__init__.py": ""}
    
    for folder_name, description in config['test_structure']['unit'].items():
        unit_structure[f"{folder_name}/"] = {
            "__init__.py": "",
            "README.md": f"# {folder_name.title()} Tests\n{description}\n"
        }
    
    return unit_structure


def generate_structure(project_name, project_type, type_config, common_config):
    """
    Generates the dictionary representing the folder structure.
    
    Args:
        project_name: Name of the project
        project_type: Type of project ('data-centric' or 'process-centric')
        type_config: Loaded JSON configuration for project type
        common_config: Loaded common structure configuration
    """
    
    # Standardize package name (replace hyphens with underscores)
    package_name = project_name.replace("-", "_")
    
    # Generate core, utils, and tests from type config
    core_structure = generate_core_from_config(type_config)
    utils_structure = generate_utils_from_config(type_config)
    tests_unit_structure = generate_tests_unit_from_config(type_config)
    
    # Build structure from common JSON
    structure = {}
    
    # Add agent_tools
    structure["agent_tools/"] = build_folder_from_json(common_config['structure']['agent_tools'])
    
    # Add resources
    structure["resources/"] = build_folder_from_json(common_config['structure']['resources'])
    
    # Add docs
    structure["docs/"] = build_folder_from_json(common_config['structure']['docs'])
    
    # Add workspace
    structure["workspace/"] = {}
    
    # Build src structure - cli and gui folders
    cli_folder = build_folder_from_json(common_config['structure']['src_common']['folders']['cli'])
    gui_folder = build_folder_from_json(common_config['structure']['src_common']['folders']['gui'])
    
    structure["src/"] = {
        f"{package_name}/": {
            "__init__.py": "",
            "core/": core_structure,
            "cli/": cli_folder,
            "gui/": gui_folder,
            "utils/": utils_structure,
        }
    }
    
    # Build tests structure
    tests_common = build_folder_from_json({'files': common_config['structure']['tests']['base_files']})
    tests_common_folders = {}
    for folder_name, folder_data in common_config['structure']['tests']['common_folders'].items():
        if folder_name == 'dependency_graph':
            # Special handling for dependency_graph - add package subfolders
            dep_graph = build_folder_from_json(folder_data)
            dep_graph[f"{package_name}/"] = {
                "core/": {},
                "cli/": {},
            }
            tests_common_folders[f"{folder_name}/"] = dep_graph
        else:
            tests_common_folders[f"{folder_name}/"] = build_folder_from_json(folder_data)
    
    structure["tests/"] = {
        **tests_common,
        **tests_common_folders,
        "unit/": tests_unit_structure,
        "integration/": {
            "__init__.py": "",
            "README.md": f"# Integration Tests\n{type_config['test_structure']['integration']}\n"
        }
    }
    
    # Add performance tests for process-centric
    if project_type == 'process-centric':
        structure["tests/"]["performance/"] = {
            "__init__.py": "",
            "README.md": f"# Performance Tests\n{type_config['test_structure']['performance']}\n"
        }
    
    # Add root files from common config
    for filename, content in common_config['root_files'].items():
        structure[filename] = content
    
    # Add generated files
    structure["requirements.txt"] = generate_requirements(type_config)
    structure["pyproject.toml"] = generate_pyproject_toml(project_name, type_config)
    structure[".gitignore"] = common_config['gitignore']
    
    # Add alembic if needed
    if type_config.get('requires_alembic', False):
        structure["alembic/"] = {
            "versions/": {},
            "env.py": "# Alembic env script (connects to src models)\n",
        }
        structure["alembic.ini"] = "[alembic]\nscript_location = alembic\nsqlalchemy.url = driver://user:pass@localhost/dbname\n"
    
    return structure


def generate_requirements(config):
    """Generate requirements.txt content based on config."""
    base_requirements = [
        "typer",
        "pydantic-settings",
        "pytest"
    ]
    
    if config.get('requires_database', False):
        base_requirements.extend(["sqlalchemy", "alembic"])
    
    return "\n".join(base_requirements) + "\n"


def generate_pyproject_toml(project_name, config):
    """Generate pyproject.toml content based on config."""
    base_deps = [
        '"typer"',
        '"pydantic-settings"',
        '"pytest"'
    ]
    
    if config.get('requires_database', False):
        base_deps.extend(['"sqlalchemy"', '"alembic"'])
    
    deps_str = ',\n    '.join(base_deps)
    
    return f"""[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{project_name}"
version = "0.1.0"
dependencies = [
    {deps_str}
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
"""


def create_structure(base_path, structure):
    """
    Recursively creates folders and files from a nested dictionary.
    """
    for name, content in structure.items():
        path = base_path / name
        
        if isinstance(content, dict):
            # It's a folder
            path.mkdir(parents=True, exist_ok=True)
            create_structure(path, content)
        else:
            # It's a file
            path.parent.mkdir(parents=True, exist_ok=True)
            if content:  # Only write if there's content
                path.write_text(content)
            else:
                path.touch()


def generate_project_structure_doc(project_name, project_type, type_config, common_config):
    """Generate PROJECT_STRUCTURE.md documentation from configs."""
    package_name = project_name.replace("-", "_")
    
    doc = f"""# **PROJECT STRUCTURE - {project_name}**

**Project Type:** {project_type}  
**Description:** {type_config['description']}

---

## **Overview**

This document describes the complete folder structure of this project, including the purpose and usage of each directory.

---

## **Source Code Structure**

### **src/{package_name}/core/**

The core business logic organized by architectural pattern.

"""
    
    # Add core structure from type config
    for folder_name, folder_info in type_config['core_structure'].items():
        doc += f"""#### **core/{folder_name}/**
- **Description:** {folder_info['description']}
- **Purpose:** {folder_info['purpose']}
- **Examples:** {', '.join(folder_info['examples'])}

"""
    
    # Add CLI/GUI
    doc += f"""### **src/{package_name}/cli/**
- **Description:** {common_config['structure']['src_common']['folders']['cli']['description']}
- **Files:** main.py (CLI entry point using Typer/Click)

### **src/{package_name}/gui/**
- **Description:** {common_config['structure']['src_common']['folders']['gui']['description']}
- **Files:** app.py (GUI entry point using PyQt/Tkinter)

### **src/{package_name}/utils/**
- **Description:** Infrastructure utilities
- **Files:**
"""
    
    # Add utils files from type config
    for file_name, description in type_config['utils_structure'].items():
        doc += f"  - `{file_name}`: {description}\n"
    
    doc += "\n---\n\n## **Test Structure**\n\n"
    
    # Add test structure
    doc += f"""### **tests/unit/**

Unit tests organized by component type.

"""
    
    for folder_name, description in type_config['test_structure']['unit'].items():
        doc += f"""#### **tests/unit/{folder_name}/**
- **Purpose:** {description}

"""
    
    # Add other test folders
    for test_type, description in type_config['test_structure'].items():
        if test_type != 'unit':
            doc += f"""### **tests/{test_type}/**
- **Purpose:** {description}

"""
    
    # Add common test folders
    doc += """### **tests/mocks/**
- **Purpose:** Shared mock objects for tests
- **Usage:** Reusable mocks across different test suites

### **tests/dependency_graph/**
- **Purpose:** Impact analysis - JSON maps linking source files to tests
- **Critical for Agent:** Agent uses these mappings to determine which tests to run when source files change
- **Structure:**
  ```
  dependency_graph/
  └── {package_name}/
      ├── core/
      └── cli/
  ```

### **tests/cli/**
- **Purpose:** CLI interface tests

### **tests/gui/**
- **Purpose:** GUI interface tests

"""
    
    doc += "---\n\n## **Agent Development Tools**\n\n"
    
    # Add agent_tools
    doc += f"""### **agent_tools/**
- **Description:** {common_config['structure']['agent_tools']['description']}
- **Status:** IMMUTABLE - Do not modify
- **Files:**
  - `definitions.py`: Tool schemas for the Agent
  - `handlers.py`: Python functions the Agent calls
  - `runner.py`: Script to launch the Agent loop
- **Prompts:**
  - `prompts/system_architect.md`: System prompt for Architecture tasks
- **Templates:**
  - `templates/ARCHITECTURE_{project_type.upper().replace('-', '_')}.md`: Architecture template for agent to fill

"""
    
    # Add resources
    doc += f"""### **resources/**
- **Description:** {common_config['structure']['resources']['description']}
- **Templates:**
  - `templates/test_case.j2`: Jinja2 template for generating tests

"""
    
    # Add workspace
    doc += f"""### **workspace/**
- **Description:** {common_config['structure']['workspace']['description']}
- **Usage:** Temporary sandbox for agent experimentation
- **Status:** Ignored by git

"""
    
    doc += "---\n\n## **Documentation Structure**\n\n"
    
    # Add docs structure
    for folder_name, folder_data in common_config['structure']['docs']['folders'].items():
        doc += f"""### **docs/{folder_name}/**
- **Description:** {folder_data['description']}
"""
        if 'folders' in folder_data:
            for subfolder_name, subfolder_data in folder_data['folders'].items():
                doc += f"  - `{subfolder_name}/`: {subfolder_data.get('description', 'Subfolder')}\n"
        doc += "\n"
    
    # Add alembic if needed
    if type_config.get('requires_alembic', False):
        doc += """---

## **Database Migrations**

### **alembic/**
- **Purpose:** Database schema version control
- **Files:**
  - `versions/`: Migration scripts
  - `env.py`: Alembic environment configuration
- **Config:** `alembic.ini` (root level)

"""
    
    doc += """---

## **Root Files**

- **`.env`**: Environment variables (ignored by git)
- **`.env.example`**: Example environment configuration
- **`.gitignore`**: Git ignore rules
- **`requirements.txt`**: Python dependencies
- **`pyproject.toml`**: Project configuration and metadata

---

## **Key Principles**

"""
    
    if project_type == 'data-centric':
        doc += """### **Data-Centric Architecture**
- **Entities** are framework-independent
- **Services** orchestrate business workflows
- **Repositories** handle data access (Entity ↔ Model)
- **Models** are ORM-only (SQLAlchemy)
- Dependencies flow: CLI/GUI → Services → Repositories → Models

"""
    else:
        doc += """### **Process-Centric Architecture**
- **Processors** are small, focused operations
- **Pipelines** orchestrate workflows
- **Strategies** provide algorithm choices
- **Handlers** manage cross-cutting concerns
- **Interfaces** define contracts
- Components are composable and stateless

"""
    
    doc += """---

## **For More Information**

- **Architecture Details:** See `docs/architecture/ARCHITECTURE_*.md`
- **Architectural Principles:** See `docs/architecture/ARCHITECTURAL_PRINCIPLES_*.md`
- **Coding Standards:** See `docs/standards/style_and_restrictions.md`
"""
    
    return doc


def copy_dev_tools(project_path, templates_dir):
    """
    Copy dev-tools folder contents to project's agent_tools folder.
    
    Args:
        project_path: Path to the project root
        templates_dir: Directory containing the templates (parent contains dev-tools)
    """
    # The dev-tools folder should be next to architecture_templates
    templates_path = Path(templates_dir)
    dev_tools_src = templates_path.parent / "dev-tools"
    agent_tools_dst = project_path / "agent_tools"
    
    if not dev_tools_src.exists():
        print(f"✗ Warning: dev-tools folder not found at: {dev_tools_src}")
        print(f"  Skipping dev-tools copy.")
        return
    
    print(f"Copying dev-tools to agent_tools...")
    
    # Copy all files and folders from dev-tools to agent_tools
    # Skip common Python artifacts and __pycache__
    ignore_patterns = shutil.ignore_patterns(
        '__pycache__', 
        '*.pyc', 
        '*.pyo', 
        '.pytest_cache',
        '*.egg-info'
    )
    
    # Copy each item from dev-tools
    for item in dev_tools_src.iterdir():
        src_item = dev_tools_src / item.name
        dst_item = agent_tools_dst / item.name
        
        if src_item.is_dir():
            # Copy directory (will merge with existing)
            if dst_item.exists():
                # Merge: copy contents into existing folder
                shutil.copytree(src_item, dst_item, dirs_exist_ok=True, ignore=ignore_patterns)
            else:
                # New folder: just copy
                shutil.copytree(src_item, dst_item, ignore=ignore_patterns)
        else:
            # Copy file (overwrite if exists, except for __init__.py which stays)
            if item.name != '__init__.py':
                shutil.copy2(src_item, dst_item)
    
    print(f"✓ Copied dev-tools contents to agent_tools/")


def copy_architecture_docs(project_path, project_type, templates_dir):
    """
    Copy architecture documentation files to the project.
    
    Templates go to agent_tools/templates/ for the agent to use.
    Principles go to docs/architecture/ for reference.
    
    Args:
        project_path: Path to the project root
        project_type: Type of project ('data-centric' or 'process-centric')
        templates_dir: Directory containing the architecture template files
    """
    agent_templates_path = project_path / "agent_tools" / "templates"
    docs_arch_path = project_path / "docs" / "architecture"
    
    agent_templates_path.mkdir(parents=True, exist_ok=True)
    docs_arch_path.mkdir(parents=True, exist_ok=True)
    
    arch_docs = ARCHITECTURE_DOCS.get(project_type)
    if not arch_docs:
        print(f"Warning: No architecture docs defined for project type '{project_type}'")
        return
    
    templates_path = Path(templates_dir)
    
    # Copy architecture template to agent_tools/templates/ (for agent to use)
    arch_template_src = templates_path / arch_docs['architecture']
    arch_template_dst = agent_templates_path / arch_docs['architecture']
    
    if arch_template_src.exists():
        shutil.copy2(arch_template_src, arch_template_dst)
        print(f"✓ Copied {arch_docs['architecture']} to agent_tools/templates/")
    else:
        print(f"✗ Warning: Template file not found: {arch_template_src}")
    
    # Copy principles guide to docs/architecture/ (for reference)
    principles_src = templates_path / arch_docs['principles']
    principles_dst = docs_arch_path / arch_docs['principles']
    
    if principles_src.exists():
        shutil.copy2(principles_src, principles_dst)
        print(f"✓ Copied {arch_docs['principles']} to docs/architecture/")
    else:
        print(f"✗ Warning: Template file not found: {principles_src}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Python project structure with architecture documentation"
    )
    parser.add_argument(
        "project_name",
        help="Name of the project (e.g., my-awesome-project)"
    )
    parser.add_argument(
        "--type",
        "-t",
        dest="project_type",
        choices=VALID_PROJECT_TYPES,
        default="data-centric",
        help=f"Type of project architecture (default: data-centric)"
    )
    parser.add_argument(
        "--templates-dir",
        "-d",
        default="./architecture_templates",
        help="Directory containing architecture template files (default: ./architecture_templates)"
    )
    parser.add_argument(
        "--output",
        "-o",
        default=".",
        help="Output directory for the project (default: current directory)"
    )
    
    args = parser.parse_args()
    
    # Validate project name
    if not args.project_name:
        print("Error: Project name cannot be empty")
        sys.exit(1)
    
    # Load structure configurations
    type_config = load_structure_config(args.project_type, args.templates_dir)
    common_config = load_common_structure(args.templates_dir)
    
    # Create project path
    output_path = Path(args.output).resolve()
    project_path = output_path / args.project_name
    
    if project_path.exists():
        print(f"Error: Directory '{project_path}' already exists")
        sys.exit(1)
    
    print(f"Creating {args.project_type} project: {args.project_name}")
    print(f"Output directory: {project_path}")
    print()
    
    # Generate structure
    structure = generate_structure(args.project_name, args.project_type, type_config, common_config)
    
    # Create folders and files
    create_structure(project_path, structure)
    
    # Copy dev-tools to agent_tools
    print("\nCopying development tools...")
    copy_dev_tools(project_path, args.templates_dir)
    
    # Copy architecture documentation
    print("\nCopying architecture documentation...")
    copy_architecture_docs(project_path, args.project_type, args.templates_dir)
    
    # Generate project structure documentation
    print("Generating project structure documentation...")
    structure_doc = generate_project_structure_doc(
        args.project_name, 
        args.project_type, 
        type_config, 
        common_config
    )
    structure_doc_path = project_path / "docs" / "PROJECT_STRUCTURE.md"
    structure_doc_path.write_text(structure_doc)
    print(f"✓ Created PROJECT_STRUCTURE.md in docs/")
    
    print(f"\n✓ Project '{args.project_name}' created successfully!")
    print(f"\nProject type: {args.project_type}")
    print(f"Description: {type_config['description']}")
    print(f"\nNext steps:")
    print(f"  1. cd {args.project_name}")
    print(f"  2. Review docs/PROJECT_STRUCTURE.md for complete folder layout")
    print(f"  3. Agent: Use agent_tools/templates/{ARCHITECTURE_DOCS[args.project_type]['architecture']} to generate docs/architecture/ARCHITECTURE.md")
    print(f"  4. Read docs/architecture/{ARCHITECTURE_DOCS[args.project_type]['principles']} for guidance")
    print(f"  5. Create a virtual environment: python -m venv .venv")
    print(f"  6. Activate it and install dependencies: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
