#!/usr/bin/env python3

import os
import anthropic
import re
from pathlib import Path
import tempfile
import shutil
import textwrap

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

def update_readme_for_script(current_content, script_name, script_description):
    """Update the README.md content for a single script."""
    messages = [
        {
            "role": "user",
            "content": f"""
            Given the current README.md content:

            {current_content}

            Update or add the description for the script "{script_name}" with the following description:

            {script_description}

            Please follow these guidelines:
            1. Maintain the overall structure and any existing sections not related to script descriptions.
            2. Use the following format for the script description, with word wrapping at 80 characters:
               - **{script_name}**: {script_description}
                 (wrapped at 80 characters and indented properly)
            3. If the script already exists in the README, update its description. If it's new, add it to the appropriate section.
            4. Preserve any existing sections like "License" or "Contributing" if present.
            5. If not present, add a "License" section at the end with the MIT License.
            6. Ensure proper Markdown formatting throughout the document.

            Return the entire updated README content.
            """
        }
    ]
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=2000,
        temperature=0,
        messages=messages
    )
    return response.content[0].text.strip()

def main():
    script_dir = Path(__file__).parent.resolve()
    readme_path = script_dir / "README.md"
    
    # Read current README.md content
    current_content = ""
    if readme_path.exists():
        with open(readme_path, 'r') as readme:
            current_content = readme.read()

    # Process files individually
    all_files = [f for f in os.listdir(script_dir) if f.endswith('.py') and f != Path(__file__).name]
    
    for i, filename in enumerate(all_files, 1):
        full_path = script_dir / filename
        docstring = get_docstring(full_path)
        if docstring:
            description = get_script_description(docstring)
            current_content = update_readme_for_script(current_content, filename, description)
            print(f"Processed file {i} of {len(all_files)}: {filename}")
        else:
            print(f"No docstring found for {filename}")

    # Write the updated content to README.md
    with open(readme_path, 'w') as readme:
        readme.write(current_content)

    print("README.md has been fully updated.")

if __name__ == "__main__":
    main()
