import os
from openai import OpenAI

""" ChatGPT API is only allowed to work as user prompt interpreter as we emphasize data privacy """

api_key = os.environ.get("OPENAI_API_KEY")
if api_key is None:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

client = OpenAI(api_key=api_key)

def interpret_prompt(prompt, system_prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        model="gpt-3.5-turbo",
    )
    chatgpt_reply = chat_completion.choices[0].message.content
    return chatgpt_reply
