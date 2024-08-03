from openai import OpenAI

def get_openai_models():
    # Set up the OpenAI client
    client = OpenAI(api_key=("sk-proj-nxMXTC13sPUuE13Ll6iBT3BlbkFJr6NrYaCEQ3xrdUGjAyH7"))

    try:
        # Retrieve the list of models
        models = client.models.list()

        # Extract the model IDs from the response
        model_list = [model.id for model in models.data]

        return model_list

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Call the function and print the results
if __name__ == "__main__":
    models = get_openai_models()
    
    if models:
        print("Available OpenAI models:")
        for model in models:
            print(f"- {model}")
    else:
        print("No models found or an error occurred.")
