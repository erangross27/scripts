#!/usr/bin/env python3

"""
This script automatically updates a README.md file with descriptions of Python scripts in the same directory.

It performs the following steps:
1. Scans the directory for Python files.
2. Extracts the docstring from each Python file.
3. Uses the Anthropic API to generate a brief description of each script based on its docstring.
4. Updates the README.md file with the generated descriptions, maintaining existing content and structure.

The script requires an Anthropic API key to be set in the ANTHROPIC_API_KEY environment variable.

Usage: Run this script in the directory containing the Python files and README.md to be updated.
"""

import os
import anthropic
import re
from pathlib import Path

# Initialize the Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def get_docstring(filename):
    """Extract the docstring from a Python file."""
    with open(filename, 'r') as file:
        content = file.read()
    match = re.search(r'"""(.*?)"""', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        # If triple quotes not found, try single quotes
        match = re.search(r"'''(.*?)'''", content, re.DOTALL)
        return match.group(1).strip() if match else ""

def get_script_description(docstring):
    """Use Anthropic API to get a description of what the script does."""
    messages = [
        {
            "role": "user",
            "content": f"Based on this docstring, briefly describe what the script does in one sentence:\n\n{docstring}"
        }
    ]
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=100,
        temperature=0,
        messages=messages
    )
    return response.content[0].text.strip()
def update_readme(script_descriptions, current_content):
    """Update the README.md file with script descriptions."""
    messages = [
        {
            "role": "user",
            "content": f"""
            Given the current README.md content:

            {current_content}

            And the following new or updated script descriptions:

            {script_descriptions}

            Please provide an updated version of the README.md that incorporates these changes. Maintain the overall structure and any existing sections not related to script descriptions. For the script descriptions, use the following format:

            - **script_name.py**: Brief description of what the script does.

            Ensure all scripts are listed, adding new ones and updating existing ones as necessary.
            """
        }
    ]
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1000,
        temperature=0,
        messages=messages
    )
    return response.content[0].text.strip()

def main():
    # Get the directory of this script
    script_dir = Path(__file__).parent.resolve()
    readme_path = script_dir / "README.md"
    script_descriptions = {}

    # Read current README.md content
    current_content = ""
    if readme_path.exists():
        with open(readme_path, 'r') as readme:
            current_content = readme.read()

    # Iterate through all Python files in the directory
    for filename in os.listdir(script_dir):
        if filename.endswith('.py') and filename != Path(__file__).name:
            full_path = script_dir / filename
            docstring = get_docstring(full_path)
            if docstring:
                description = get_script_description(docstring)
                script_descriptions[filename] = description
            else:
                print(f"No docstring found for {filename}")

    # Update the README.md file
    updated_content = update_readme(script_descriptions, current_content)
    with open(readme_path, 'w') as readme:
        readme.write(updated_content)
    print("README.md has been updated.")

if __name__ == "__main__":
    main()
