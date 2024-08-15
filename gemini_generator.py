import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting, FinishReason
import vertexai.preview.generative_models as generative_models

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
]

def generate():
    vertexai.init(project="gen-lang-client-0370757327", location="us-central1")
    model = GenerativeModel("gemini-1.5-flash-001")
    
    # Add a prompt or question here
    prompt = "Tell me a short story about a robot learning to paint."
    
    responses = model.generate_content(
        [prompt],  # Pass the prompt as a list
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )
    
    for response in responses:
        print(response.text, end="")

generate()
