import os
import google.generativeai as genai
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# Get the API key from an environment variable
google_api_key = os.getenv('GOOGLE_API_KEY')

# Configure the API with your key
genai.configure(api_key=google_api_key)

# Create a model instance
model = genai.GenerativeModel('gemini-1.0-pro-latest')

# Generate content with the prompt "What is the meaning of life?"
response = model.generate_content("What is the meaning of life?", stream=True)

# Iterate over each chunk in the response
for chunk in response:
    # Print the text of the chunk
    print(chunk.text)
    # Print a line of underscores for separation
    print("_"*80)



