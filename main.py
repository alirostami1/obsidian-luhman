import os
import re
from pathlib import Path
import argparse


def split_luhmann_parts(input_string):
    """
    Splits a Luhmann-style string into parts of alternating numeric and alphabetic segments.
    Example: '1a2b3cc42a' -> ['1', 'a', '2', 'b', '3', 'cc', '42', 'a']
    """
    return re.findall(r'\d+|[a-z]+', input_string)


def convert_numeric_to_alpha(n):
    """
    Converts a number to its alphabetic representation.
    Example: 1 -> 'a', 2 -> 'b', 27 -> 'aa'
    """
    result = []
    while n > 0:
        n -= 1
        result.append(chr(n % 26 + 97))
        n //= 26
    return ''.join(reversed(result))


def convert_alpha_to_numeric(s):
    """
    Converts an alphabetic string to its numeric representation.
    Example: 'a' -> 1, 'b' -> 2, 'aa' -> 27
    """
    result = 0
    for char in s:
        result = result * 26 + (ord(char) - 96)
    return result


def check_and_convert(parts):
    """
    Checks for consecutive same-type elements in the parts list.
    If found, it processes the remaining elements using a custom logic.
    """
    for i in range(len(parts) - 1):
        if parts[i].isdigit() and parts[i + 1].isdigit():
            # print(f"Consecutive numeric elements found: {parts[i]} and {parts[i + 1]}")
            converted = convert_numeric_to_alpha(int(parts[i+1]))
            parts = parts[:i+1] + [converted] + parts[i+2:]

        elif parts[i].isalpha() and parts[i + 1].isalpha():
            # print(f"Consecutive alphabetic elements found: {parts[i]} and {parts[i + 1]}")
            converted = convert_alpha_to_numeric(parts[i+1])
            parts = parts[:i+1] + [str(converted)] + parts[i+2:]
    return parts 



def rename_luhmann_files(source_prefix, target_prefix, directory):
    """
    Renames files in the given directory from source_prefix to target_prefix while ensuring
    Luhmann-style validity.
    """
    for file_path in Path(directory).glob(f"{source_prefix}*"):
        if file_path.is_file():
            # Extract the file name
            file_name = file_path.name

            # Extract the luhman id (1a2c title) => split by space
            id = file_name.split(' ', 1)[0].strip()

            # Split the id into parts
            parts = split_luhmann_parts(id)
            # print(f"Parts: {parts}")

            # Split the target id into parts
            target_parts = split_luhmann_parts(target_prefix)
            # print(f"Target Parts: {target_parts}")

            # remove first elements of parts with length of source_prefix
            parts = parts[len(source_prefix):]
            # print(f"Parts after removing: {parts}")

            # append target_parts to parts
            parts = target_parts + parts
            # print(f"Parts after appending: {parts}")

            # Check and convert parts
            parts = check_and_convert(parts)
            # print(f"Parts after conversion: {parts}")

            # Reconstruct the new file name
            new_file_name = ''.join(parts) + file_name[len(id):]
            # print(f"new file name: {new_file_name}")

            # Combine the new file name with the directory
            new_file_name = file_path.parent / new_file_name
            # print(f"new file name with path: {new_file_name}")

            # Rename the file
            print(f"Renaming: {file_path} -> {new_file_name}")
            file_path.rename(new_file_name)

def main():
    # Set up command-line arguments
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

    # Parse arguments
    args = parser.parse_args()

    # Validate the directory
    directory_path = Path(args.directory)
    if not directory_path.is_dir():
        print(f"Error: Directory '{args.directory}' does not exist.")
        exit(1)

    # Perform renaming
    rename_luhmann_files(args.source_prefix, args.target_prefix, args.directory)


if __name__ == "__main__":
    main()
