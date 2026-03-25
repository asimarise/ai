import json
import os

import requests
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()


def get_weather(latitude, longitude):
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )

    data = response.json()
    print(data)
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
            "strict": True,
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
    # tool_choice="auto",
)

res = completion.model_dump()

print(res)


def call_function(name, args):
    if name == "get_weather":
        return get_weather(**args)


for tool_call in completion.choices[0].message.tool_calls:
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    messages.append(completion.choices[0].message)

    result = call_function(name, args)
    messages.append(
        {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result),
        }
    )


class WeatherReponse(BaseModel):
    temperature: float = Field(
        description="The current temperature in celsius for the given location"
    )
    reponse: str = Field(
        description="A natural language response to the user's question"
    )


completion_2 = client.chat.completions.parse(
    model="mistral-large-latest",
    messages=messages,
    tools=tools,
    # tool_choice="auto",
    response_format=WeatherReponse,
)

print(completion_2)
final_response = completion_2.choices[0].message.parsed


print(final_response)
