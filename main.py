import os
import re
from pathlib import Path
import argparse


def split_luhmann_parts(input_string):
    return re.findall(r'\d+|[a-z]+', input_string)


def convert_numeric_to_alpha(n):
    result = []
    while n > 0:
        n -= 1
        result.append(chr(n % 26 + 97))
        n //= 26
    return ''.join(reversed(result))


def convert_alpha_to_numeric(s):
    result = 0
    for char in s:
        result = result * 26 + (ord(char) - 96)
    return result


def check_and_convert(parts):
    for i in range(len(parts) - 1):
        if parts[i].isdigit() and parts[i + 1].isdigit():
            converted = convert_numeric_to_alpha(int(parts[i + 1]))
            parts = parts[:i + 1] + [converted] + parts[i + 2:]
        elif parts[i].isalpha() and parts[i + 1].isalpha():
            converted = convert_alpha_to_numeric(parts[i + 1])
            parts = parts[:i + 1] + [str(converted)] + parts[i + 2:]
    return parts


def update_references(directory, old_file, new_file):
    """
    Updates references to the old Luhmann ID with the new one in all .md files within the directory.
    """
    for file_path in Path(directory).glob("**/*.md"):  # Only process .md files
        if file_path.is_file():
            with open(file_path, "r", encoding="latin-1") as file:
                content = file.read()
            
            # Replace old ID with new ID in file content
            updated_content = content.replace(old_file, new_file)
            
            # If any replacements were made, write back the updated content
            if content != updated_content:
                print(f"Updating references in: {file_path}")
                with open(file_path, "w", encoding="latin-1") as file:
                    file.write(updated_content)


def change_file_id(source_prefix, target_prefix, directory):
    """
    Changes the Luhmann-style ID of files in the directory from source_prefix to target_prefix.
    For example '1a 2b 3c 4d.md' -> '1a 2b 3c 5e.md' if source_prefix='4d' and target_prefix='5e'.
    """
    for file_path in Path(directory).glob(f"{source_prefix}*"):
        if file_path.is_file():
            source_file_name = file_path.name
            file_id = source_file_name.split(' ', 1)[0].strip()

            file_id_parts = split_luhmann_parts(file_id)
            source_id_parts = split_luhmann_parts(source_prefix)
            target_id_parts = split_luhmann_parts(target_prefix)

            file_id_parts = file_id_parts[len(source_id_parts):]
            constructed_id_parts = target_id_parts + file_id_parts
            constructed_id_parts = check_and_convert(constructed_id_parts)

            new_file_name = ''.join(constructed_id_parts) + source_file_name[len(file_id):]

            rename_files_and_update_references(directory, source_file_name, new_file_name)

def rename_files_and_update_references(directory, old_file_name, new_file_name):
    """
    Renames the old file to the new file and updates references to the old file in all .md files within the directory.
    """
    old_file_path = Path(directory) / old_file_name
    new_file_path = Path(directory) / new_file_name

    if not old_file_path.is_file():
        print(f"Error: File '{old_file_name}' does not exist in the directory.")
        exit(1)
    print(f"Renaming: {old_file_path} -> {new_file_path}")

    old_file_path.rename(new_file_path)

    # Update references to the old file name
    print(f"Updating references from {old_file_name[:-3]} to {new_file_name[:-3]} in: {directory}")
    update_references(directory, old_file_name[:-3], new_file_name[:-3])
    


def main():
    parser = argparse.ArgumentParser(
        description="Rename files in a directory using Luhmann-style numbering."
    )
    parser.add_argument(
        "source_prefix", type=str, help="The source prefix to match files."
    )
    parser.add_argument(
        "target_prefix", type=str, help="The target prefix for renamed files."
    )
    parser.add_argument(
        "directory", type=str, help="The directory containing the files to rename."
    )

    args = parser.parse_args()
    directory_path = Path(args.directory)
    if not directory_path.is_dir():
        print(f"Error: Directory '{args.directory}' does not exist.")
        exit(1)

    change_file_id(args.source_prefix, args.target_prefix, args.directory)


if __name__ == "__main__":
    main()

