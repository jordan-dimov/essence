import os
import typer
import re

app = typer.Typer()


@app.command("summarize")
def summarize_project(project_directory: str):
    pass

if __name__ == "__main__":
    app()

