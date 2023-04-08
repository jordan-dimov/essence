import os

import typer


def locate_requirements(project_directory: str):
    # Try to locate requirements.txt or pyproject.toml
    # TODO: Try harder
    pyproject_file = os.path.join(project_directory, "pyproject.toml")
    if os.path.exists(pyproject_file):
        return pyproject_file
    # Try in sub-directories:
    for root, dirs, files in os.walk(project_directory):
        pyproject_file = os.path.join(root, "pyproject.toml")
        if os.path.exists(pyproject_file):
            return pyproject_file

    # Try requirements.txt
    requirements_file = os.path.join(project_directory, "requirements.txt")
    if os.path.exists(requirements_file):
        return requirements_file

    # Try in sub-directories:
    for root, dirs, files in os.walk(project_directory):
        requirements_file = os.path.join(root, "requirements.txt")
        if os.path.exists(requirements_file):
            return requirements_file


def extract_requirements(requirements_file: str, reqs_type: str = "requirements"):
    # Extract requirements from requirements.txt or pyproject.toml
    dependencies = []
    typer.echo(f"Extracting requirements from {requirements_file}...")
    with open(requirements_file) as f:
        if reqs_type == "requirements":
            dependencies = f.readlines()
        elif reqs_type == "pyproject":
            # Find the section [tool.poetry.dependencies] and extract the dependencies
            in_dependencies = False
            for line in f:
                if in_dependencies:
                    if line.startswith("["):
                        break
                    else:
                        clean_line = line.strip()
                        if clean_line:
                            dependencies.append(clean_line)
                elif line.startswith("[tool.poetry.dependencies]"):
                    in_dependencies = True
    return dependencies


def extract_metadata(pyproject_toml_file: str):
    # Extract name and description from [tool.poetry] section of pyproject.toml
    metadata = {}
    typer.echo(f"Extracting metadata from {pyproject_toml_file}...")
    with open(pyproject_toml_file) as f:
        in_poetry = False
        for line in f:
            if in_poetry:
                if line.startswith("["):
                    break
                else:
                    if line.startswith("name"):
                        metadata["name"] = line.split("=")[1].strip().strip('"')
                    elif line.startswith("description"):
                        metadata["description"] = line.split("=")[1].strip().strip('"')
            elif line.startswith("[tool.poetry]"):
                in_poetry = True
    return metadata
