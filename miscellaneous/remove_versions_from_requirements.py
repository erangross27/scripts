"""
This script handles remove versions from requirements.
"""

import re

def remove_versions(input_file='requirements.txt', output_file='requirements_no_versions.txt'):
    """
    Remove version specifiers and comments from a requirements file.

    This function reads a requirements file, removes version specifiers and comments
    from each line, and writes the cleaned requirements to a new file.

    Parameters:
    input_file (str): The path to the input requirements file. Default is 'requirements.txt'.
    output_file (str): The path to the output file where cleaned requirements will be written.
                       Default is 'requirements_no_versions.txt'.

    The function performs the following operations:
    1. Reads the input file line by line.
    2. Removes inline comments (anything after '#' on a line).
    3. Removes version specifiers (e.g., ==1.0, >=2.1, <3.0).
    4. Strips whitespace from the beginning and end of each line.
    5. Writes non-empty cleaned lines to the output file.

    After processing, it prints a success message indicating the name of the new file created.

    Note: This function modifies files on the filesystem. Ensure you have appropriate permissions
    and be cautious when specifying input and output file paths.
    """
    # Open and read the input file
    with open(input_file, 'r') as f:
        requirements = f.readlines()

    # Remove versions and comments
    cleaned_requirements = []
    for req in requirements:
        # Remove inline comments
        req = re.sub(r'#.*$', '', req)
        # Remove version specifiers (e.g., ==1.0, >=2.1, <3.0)
        req = re.sub(r'[=<>]=.*', '', req)
        # Strip whitespace from the beginning and end of the line
        req = req.strip()
        # If the requirement is not empty after cleaning, add it to the list
        if req:
            cleaned_requirements.append(req + '\n')

    # Write the cleaned requirements to the output file
    with open(output_file, 'w') as f:
        f.writelines(cleaned_requirements)

    # Print a success message
    print(f"Versions removed. New file created: {output_file}")

# If this script is run directly (not imported as a module)
if __name__ == "__main__":
    # Call the remove_versions function with default parameters
    remove_versions()
