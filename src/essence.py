import os
import typer
import json
import pathspec

app = typer.Typer()


def locate_requirements(project_directory: str):
    # Try to locate requirements.txt or pyproject.toml
    # TODO: Try harder
    requirements_file = os.path.join(project_directory, "requirements.txt")
    if os.path.exists(requirements_file):
        return requirements_file
    pyproject_file = os.path.join(project_directory, "pyproject.toml")
    if os.path.exists(pyproject_file):
        return pyproject_file


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


def extract_loc(py_file: str):
    # Extract the number of lines of code in a .py file
    with open(py_file) as f:
        return len(f.readlines())


def extract_package_structure(project_directory: str, is_file_ignored: callable):
    # Extract the structure of the project using os.walk
    # and return in compact form. Only include .py files.
    typer.echo(f"Extracting package structure from {project_directory}...")
    structure = {}
    # Ignore files that match is_file_ignored() as well as entire .git directory
    # Only include directories that contain .py files
    for root, dirs, files in os.walk(project_directory):
        if is_file_ignored(root):
            continue
        if ".git" in root:
            continue
        py_files = [f for f in files if f.endswith(".py")]
        if py_files:
            structure[root] = [
                {"name": f, "loc": extract_loc(os.path.join(root, f))} for f in py_files
            ]

    return structure


@app.command("summarize")
def summarize_project(project_directory: str, output_file: str | None = None):
    if not output_file:
        output_file = os.path.join(project_directory, "essence.json")
    summary = {}
    reqs_file = locate_requirements(project_directory)
    if reqs_file is None:
        typer.echo("No requirements.txt or pyproject.toml found. Skipping. ")
    reqs_type = (
        "requirements" if reqs_file.endswith("requirements.txt") else "pyproject"
    )
    summary["requirements"] = extract_requirements(reqs_file, reqs_type)
    if reqs_type == "pyproject":
        summary["metadata"] = extract_metadata(reqs_file)

    # Check if there is a .gitignore file
    gitignore_file = os.path.join(project_directory, ".gitignore")
    if os.path.exists(gitignore_file):
        spec = pathspec.PathSpec.from_lines("gitwildmatch", open(gitignore_file))

        def is_file_ignored(path):
            return spec.match_file(path)

    summary["structure"] = extract_package_structure(project_directory, is_file_ignored)

    with open(output_file, "w") as f:
        json.dump(summary, f, indent=4)

    typer.echo(f"Summary written to {output_file}")


if __name__ == "__main__":
    app()
