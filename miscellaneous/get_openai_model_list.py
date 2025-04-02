import os
from openai import OpenAI

def list_openai_models(detailed=False, filter_prefix=None):
    """
    Fetches and displays available OpenAI models.

    Args:
        detailed (bool): Whether to display detailed information for each model
        filter_prefix (str, optional): Filter models that start with this prefix

    Returns:
        list: List of model objects if successful, None otherwise
    """
    # Get API key from environment variables
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OpenAI API key not found. Ensure the OPENAI_API_KEY environment variable is set.")

    try:
        # Initialize the client with the API key
        client = OpenAI(api_key=api_key)

        # Fetch the list of available models
        models = client.models.list()
        
        # Sort models by ID for consistent output
        sorted_models = sorted(models.data, key=lambda x: x.id)

        # Filter models if a prefix is specified
        if filter_prefix:
            sorted_models = [model for model in sorted_models if model.id.startswith(filter_prefix)]
        # Print the models
        for model in sorted_models:
            if detailed:
                print(f"ID: {model.id}")
                print(f"Created: {model.created}")
                print(f"Owner: {model.owned_by}")
                print("-" * 40)
            else:
                print(model.id)

        return sorted_models
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="List available OpenAI models")
    parser.add_argument("--detailed", action="store_true", help="Show detailed information about each model")
    parser.add_argument("--filter", type=str, help="Filter models by prefix")

    args = parser.parse_args()

    list_openai_models(detailed=args.detailed, filter_prefix=args.filter)
