import os
import typer
import json
import ast

from analyse_reqs import locate_requirements, extract_requirements, extract_metadata
from ignores import collect_ignored_files

app = typer.Typer()


def _get_pyfile_stats(f):
    stats = {
        "top_level_statements": 0,
        "decision_points": 0,
        "function_defs": 0,
        "imports": [],
    }
    # Extract the number of function or method definitions in a .py file
    # and build a list of imports. Ignore comments and docstrings.

    decision_nodes = (
        ast.If,
        ast.For,
        ast.While,
        ast.Try,
        ast.With,
        ast.AsyncFor,
        ast.AsyncWith,
    )
    tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, decision_nodes):
            stats["decision_points"] += 1
        if isinstance(node, ast.Import):
            for n in node.names:
                stats["imports"].append(n.name)
        elif isinstance(node, ast.ImportFrom):
            stats["imports"].append(node.module)
        elif isinstance(node, ast.Expr):
            if isinstance(node.value, ast.Str):
                continue
        elif isinstance(node, ast.FunctionDef) or isinstance(
            node, ast.AsyncFunctionDef
        ):
            stats["function_defs"] += 1
    stats["top_level_statements"] = len(tree.body)

    return stats


def get_file_info(root: str, py_file: str):
    file_path = os.path.join(root, py_file)
    file_info = {"name": py_file}
    # Extract the number of lines of code in a .py file
    with open(file_path) as f:
        stats = _get_pyfile_stats(f)
        file_info["tl_statements"] = stats["top_level_statements"]
        file_info["cyclomatic_complexity"] = stats["decision_points"] + 1
        if stats["imports"]:
            file_info["imports"] = stats["imports"]
        if stats["function_defs"] > 0:
            file_info["function_defs"] = stats["function_defs"]
    return file_info


def extract_package_structure(project_directory: str, ignored_files: list[str]):
    # Extract the structure of the project using os.walk
    # and return in compact form. Only include .py files.
    typer.echo(f"Extracting package structure from {project_directory}...")
    structure = {}
    # Ignore files that match is_file_ignored() as well as entire .git directory
    # Only include directories that contain .py files
    for root, dirs, files in os.walk(project_directory):
        if root in ignored_files:
            continue
        if ".git" in root:
            continue
        py_files = [f for f in files if f.endswith(".py")]
        if py_files:
            files_in_dir = []
            for f in py_files:
                file_info = get_file_info(root, f)
                if file_info["tl_statements"] > 0:
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

    ignored_files = collect_ignored_files(project_directory)

    roots: dict[str, str] = locate_requirements(project_directory, ignored_files)
    if not roots:
        typer.echo("No requirements.txt or pyproject.toml found. Skipping. ")
        roots[project_directory] = ""

    for root in roots:
        reqs_file = roots[root]
        root_summary = {}
        if reqs_file:
            reqs_type = (
                "requirements"
                if reqs_file.endswith("requirements.txt")
                else "pyproject"
            )
            root_summary["requirements"] = extract_requirements(reqs_file, reqs_type)
            if reqs_type == "pyproject":
                root_summary["metadata"] = extract_metadata(reqs_file)

        root_summary["structure"] = extract_package_structure(root, ignored_files)
        summary[root] = root_summary

    with open(output_file, "w") as f:
        json.dump(summary, f, indent=4)

    typer.echo(f"Summary written to {output_file}")


if __name__ == "__main__":
    app()
