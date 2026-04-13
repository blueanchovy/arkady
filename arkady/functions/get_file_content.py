import os
from google.genai import types
from arkady.config import MAX_CHARS

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description=f"Prints the contents of a file at a specified path relative to the working directory, providing a string truncated at {MAX_CHARS} characters.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path of the file to print content of, relative to the working directory (default is the working directory itself)",
                default="."
            ),
        },
        required=["file_path"]
    ),
)

def get_file_content(working_directory, file_path):

    working_directory_abs = os.path.abspath(working_directory)
    target_dir = os.path.normpath(
        os.path.join(working_directory_abs, file_path)
    )

    try:
        is_valid_target_dir = os.path.commonpath(
            [working_directory_abs, target_dir]
        ) == working_directory_abs
    except ValueError:
        is_valid_target_dir = False

    if not is_valid_target_dir:
        error = f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        print(error)
        return error

    if not os.path.isfile(target_dir):
        error = f'Error: File not found or is not a regular file: "{file_path}"'
        print(f"Error: {error}")
        return error

    try:
        with open(target_dir, "r") as f:
            file_content_string = f.read(MAX_CHARS)

            # After reading the first MAX_CHARS...
            if f.read(1):
                file_content_string += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'

            print(file_content_string)
            return file_content_string

    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"
