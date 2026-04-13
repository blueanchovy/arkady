import os
from google.genai import types

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes the specified content to a file at a specified path relative to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path of the file to write to, relative to the working directory",
                default="."
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Content to be written inside the file specified at the provided file path.",
                default=""
            ),
        },
        required=["file_path", "content"]
    ),
)

def write_file(working_directory, file_path, content):

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

    print("valid target dir")
    if os.path.isdir(target_dir):
        error = f'Error: Cannot write to "{file_path}" as it is a directory'
        print(f"Error: {error}")
        return error

    #checks for existing parent directory and creates if not present
    parent_dir = os.path.dirname(target_dir)
    os.makedirs(parent_dir, exist_ok=True)

    try:
        with open(target_dir, "w") as f:
            f.write(content)
            print(f'Successfully wrote to "{file_path}" ({len(content)} characters written)')
    except Exception as e:
        print(f"Error: {e}")
        return e
