import os
from openai import OpenAI
from enum import Enum
from dotenv import load_dotenv
import argparse
from typing import Callable

"""

"""


class Model(Enum):
    GPT3_5 = "gpt-3.5-turbo-1106"
    GPT4 = "gpt-4-1106-preview"

    @classmethod
    def get_model_by_version(cls, version):
        if version == "3.5":
            return cls.GPT3_5
        elif version == "4":
            return cls.GPT4
        else:
            raise ValueError("Invalid version")


# WRAPPER
def token_usage(func: Callable) -> Callable:
    """
    Decorates a function that returns a completion object
    """
    COST_FOR_1000_TOKENS = {Model.GPT3_5.value: 0.003, Model.GPT4.value: 0.04}

    def wrapper(*args, **kwargs):
        completion_object = func(*args, **kwargs)
        try:
            model = completion_object.model
            token_usage = completion_object.usage.total_tokens
            # cost is tokens used * cost per token. We know cost per 1000, so we divide the cost for 1000 tokens by 1000
            cost_per_token = COST_FOR_1000_TOKENS[model] / 1000
            actual_cost = round(token_usage * cost_per_token, 4)
            print("==================================")
            print(
                f"Model: {model} | Token usage: {token_usage} | Cost: {actual_cost} USD"
            )
        except AttributeError:
            print("The decorated function must return a completion object")
        return completion_object

    return wrapper


@token_usage
def get_response(selected_model: Model = Model.GPT3_5, prompt: str = ""):
    if not prompt:
        raise ValueError("Prompt required")

    completion = client.chat.completions.create(
        model=selected_model.value,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            {"role": "user", "content": prompt},
        ],
    )

    response = completion.choices[0].message.content

    print(response)

    return completion


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sends a prompt to openai API, returns a GPT3.5 or GPT4 completion response"
    )

    parser.add_argument(
        "-v",
        "--version",
        type=str,
        default="3.5",
        help="Model version (3.5 or 4)'",
    )
    parser.add_argument("prompt_text", type=str, help="Prompt for the model")

    args = parser.parse_args()

    load_dotenv()
    API_KEY = os.environ.get("OPENAI_API_KEY")

    if not API_KEY:
        raise ValueError("Please initialize OPENAI_API_KEY env variable")

    client = OpenAI(api_key=API_KEY)

    selected_model = Model.get_model_by_version(args.version)
    prompt = args.prompt_text

    get_response(selected_model, prompt)
