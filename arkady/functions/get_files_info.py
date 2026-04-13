import os
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
                default="."
            ),
        },
        required=["directory"]
    ),
)

def get_files_info(working_directory, directory="."):

    working_directory_abs = os.path.abspath(working_directory)
    target_dir = os.path.normpath(
        os.path.join(working_directory_abs, directory)
    )

    try:
        valid_target_dir = os.path.commonpath(
            [working_directory_abs, target_dir]
        ) == working_directory_abs
    except ValueError:
        valid_target_dir = False

    if not valid_target_dir:
        error = f'Cannot list "{directory}" as it is outside the permitted working directory'
        print(f"Error: {error}")
        return error

    if not os.path.isdir(target_dir):
        error = f'Cannot list "{directory}" as it is not a directory'
        print(f"Error: {error}")
        return error

    result = []

    def list_files(dir):
        contents = os.listdir(dir)
        for val in contents:
            full_path = os.path.join(dir, val)
            size = os.path.getsize(full_path)

            if os.path.isdir(full_path) == True:
                print(f"  - {val}: file_size={size} bytes, is_dir=True")
                result.append({
                    "name": val,
                    "file_size": size,
                    "is_dir": True
                })

            elif os.path.isfile(full_path):
                print(f"  - {val}: file_size={size} bytes, is_dir=False")
                result.append({
                    "name": val,
                    "file_size": os.path.getsize(full_path),
                    "is_dir": False
                })
        print("\n")
        return result

    try:
        res = list_files(target_dir)
        return res
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"  # ← and this
