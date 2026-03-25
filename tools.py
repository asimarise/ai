import os

import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_weather(latitude, longitude):
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}"
    )

    data = response.json()
    return data["current"]


client = OpenAI(
    # base_url="https://openrouter.ai/api/v1",
    base_url="https://api.mistral.ai/v1/",
    api_key=os.getenv("API_KEY"),
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                },
                "required": ["latitude", "longitude"],
            },
        },
    },
]


system_prompt = "You are a helpful weather assistant. That can access external functions. Please provide a reponse based on the information from these function calls"


messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "What's the weather like in Paris"},
]
completion = client.chat.completions.create(
    model="mistral-small-latest",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)

res = completion.model_dump()


print(res)
