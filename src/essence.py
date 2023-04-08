import os
import typer
import json
import pathspec

from analyse_reqs import locate_requirements, extract_requirements, extract_metadata

app = typer.Typer()


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
            files_in_dir = []
            for f in py_files:
                file_info = {"name": f, "lines": extract_loc(os.path.join(root, f))}
                if file_info["lines"] > 0:
                    files_in_dir.append(file_info)
            if files_in_dir:
                dir_label = root.replace(project_directory, "").strip("/")
                structure[dir_label] = files_in_dir
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

    is_file_ignored = get_ignore_checker(project_directory)

    summary["structure"] = extract_package_structure(project_directory, is_file_ignored)

    with open(output_file, "w") as f:
        json.dump(summary, f, indent=4)

    typer.echo(f"Summary written to {output_file}")


def get_ignore_checker(project_directory):
    specs = []

    # Check if there is a .gitignore file
    gitignore_file = os.path.join(project_directory, ".gitignore")
    if os.path.exists(gitignore_file):
        specs.append(pathspec.PathSpec.from_lines("gitwildmatch", open(gitignore_file)))

    # Check in sub-directories
    for root, dirs, files in os.walk(project_directory):
        gitignore_file = os.path.join(root, ".gitignore")
        if os.path.exists(gitignore_file):
            specs.append(
                pathspec.PathSpec.from_lines("gitwildmatch", open(gitignore_file))
            )

    def is_file_ignored(path):
        return any(spec.match_file(path) for spec in specs)

    return is_file_ignored


if __name__ == "__main__":
    app()
