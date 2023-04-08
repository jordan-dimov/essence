import os
import pathspec


def collect_ignored_files(path):
    ignored_files = []
    gitignore_files = []

    for root, dirs, files in os.walk(path):
        for file in files:
            if file == ".gitignore":
                gitignore_files.append(os.path.join(root, file))

    for gitignore_file in gitignore_files:
        with open(gitignore_file, "r") as f:
            ignore_patterns = f.read()

        spec = pathspec.PathSpec.from_lines(
            pathspec.patterns.GitWildMatchPattern, ignore_patterns.splitlines()
        )
        base_path = os.path.dirname(gitignore_file)

        for root, dirs, files in os.walk(base_path):
            for file in files:
                file_path = os.path.join(root, file)
                if spec.match_file(file_path):
                    ignored_files.append(file_path)

    return ignored_files
