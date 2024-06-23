import anthropic
import logging

class AnthropicClient:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)

    def get_response(self, message, model):
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=4096,
                temperature=0,
                messages=[{"role": "user", "content": message}]
            )
            return response.content[0].text
        except Exception as e:
            logging.error(f"Error getting response from Anthropic API: {str(e)}")
            return "Sorry, I encountered an error while processing your request."