# agents/haiku_agent.py
import os
from openai import OpenAI

class HaikuAgent:
    description = "Writes inspiring haiku poems."

    def __init__(self):
        # Ensure the API key is set
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

        # Initialize the OpenAI client
        self.client = OpenAI(api_key=api_key)

    # Define function to write a haiku
    def haiku(self):
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Write a properly formatted haiku."},
                {"role": "user", "content": "Do it in English!"},
            ],
            model="gpt-3.5-turbo",
        )
        chatgpt_reply = chat_completion.choices[0].message.content
        return chatgpt_reply

if __name__ == "__main__":
    agent = HaikuAgent()
    print(agent.haiku())
