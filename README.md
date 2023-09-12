# essence - CLI tool to extract and summarise the essential structure of large Python codebases in JSON format

## Overview

Essence is a CLI (Command-Line Interface) tool designed to extract and summarise the structure of large Python codebases. It analyses the project requirements, maps the package structure, and extracts metadata from Python files. Whether you are troubleshooting a bug or getting familiar with new repositories, Essence enhances your productivity by providing crucial insights into the code structure, complexity and requirements of your project.

## Requirements

Essence requires Python 3.10 and is built around two key Python libraries:

- Typer, for building the CLI applications.
- Pathspec, for pattern matching on file paths.

It also uses the standard Python module `ast` for parsing and extracting information from Python source code files. 

## Installation

We recommend using `poetry` for managing dependencies. If not installed yet, get it with:

```bash
pip install poetry
```

Once installed, clone this repository and navigate into the project's root directory. Then, run:

```bash
poetry install
```

This command will install all the necessary dependencies for the project.

## Usage

To run Essence and analyse a Python codebase, use the following command:

```bash
poetry run python src/essence.py /path/to/python_codebase/
```

Here, replace `/path/to/python_codebase/` with the file path of the Python project you want to analyse. 

Once the command finishes running, Essence will generate a file named `essence.json` in the target directory. This JSON file encapsulates information about the structure of the Python codebase, including:

- Project's requirements.
- Package structure.
- Metadata from Python files.
- Cyclomatic complexity measurement of the different components.
- Number of top-level statements (excluding class or function definitions).

For each Python file analysed in the codebase, Essence provides a concise yet semantically rich summary of various aspects of the code:

- Indicates the file name and lists all the imports made in it. 
- Provides insight into the number of pathways through the file and its overall complexity. 
- Lists the functions defined within the file, along with a categorisation of all function calls associated with each function. This catalogue of function calls gives a clear picture of what other modules or functions each method interacts with. 

By detailing these elements for each Python file, Essence helps the user understand the structure and intricacies of the Python codebase, simplifying navigation through extensive and complex repositories.

## Contact

If you run into problems, feel free to open an issue on the GitHub repository.

