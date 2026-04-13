import os
from pathlib import Path
import subprocess
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a python file at a specified path relative to the working directory, supplemented with additional arguments if specified.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path of the python file to be run, relative to the working directory",
                default="."
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING)
            )
        },
        required=["file_path"]
    ),
)

def run_python_file(working_directory, file_path, args=None):

    working_directory_abs = os.path.abspath(working_directory)
    absolute_file_path = os.path.normpath(
        os.path.join(working_directory_abs, file_path)
    )

    try:
        is_valid_target_dir = os.path.commonpath(
            [working_directory_abs, absolute_file_path]
        ) == working_directory_abs
    except ValueError:
        is_valid_target_dir = False

    if not is_valid_target_dir:
        error = f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        print(error)
        return error

    if not os.path.isfile(absolute_file_path):
        print(f'Error: "{file_path}" does not exist or is not a regular file')

    filepath = Path(absolute_file_path)
    if filepath.suffix != ".py":
        print(f'Error: "{file_path}" is not a Python file')

    command = ["python", absolute_file_path]
    if args:
        command.extend(args)

    result = subprocess.run(
        command,
        cwd=working_directory_abs,
        capture_output=True,
        text=True,
        timeout=30,
    )

    output = ""

    try:
        if result.returncode != 0:
            output += f"Process exited with code {result.returncode}\n"

        if result.stdout:
            output += f"STDOUT: {result.stdout}"
        elif result.stderr:
            output += f"STDERR: {result.stderr}"
        else:
            output += f"No output produced"

        print(output)
        return output
    except Exception as e:
        print(f"Error: executing Python file: {e}")
