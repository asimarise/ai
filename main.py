from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    api_key: SecretStr
    username: str

    @field_validator("username")
    def validator_username(cls, v: str):
        if " " in v:
            raise ValueError("Username error")
        return v.lower()


setting = Settings()

print(setting.username)
print(setting)


class User(BaseModel):
    model_config = ConfigDict(strict=True)
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Name of the user",
    )
    age: int = Field(
        ge=18,
        description="Age of the user",
    )


def greet_user(user: User) -> str:
    print(user)
    return f"Hello, {user.name}"


def load_user(data: dict) -> User:
    asd = User.model_validate(data).model_dump_json()
    print(asd)
    return User.model_validate_json(asd)


user = load_user({"name": "Hanzala", "age": 23})
message = greet_user(user)
print(message)


client = OpenAI(
    # base_url="https://openrouter.ai/api/v1",
    api_key=setting.api_key.get_secret_value(),
    base_url="https://api.mistral.ai/v1/",
)


class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[User]


completion = client.chat.completions.parse(
    model="mistral-small-2603",
    messages=[
        {"role": "system", "content": "Extract the event information."},
        {
            "role": "user",
            "content": "Alice and Bob are going to a science fair on Friday.",
        },
    ],
    max_tokens=1000,
    response_format=CalendarEvent,
)

print(completion.choices[0].message.parsed)


print(user)
