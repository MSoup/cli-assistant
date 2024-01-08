import json
import os
from openai import OpenAI
from enum import Enum
from dotenv import load_dotenv
import argparse
from typing import Callable
from abc import ABC, abstractmethod
import boto3


class Model(ABC):
    @property
    @abstractmethod
    def model(self):
        """
        Model name
        """
        raise NotImplementedError

    @abstractmethod
    def invoke(self, prompt: str):
        """
        Implement invoke method
        """
        raise NotImplementedError

    # TODO
    # @abstractmethod
    # def cost(self, cost_per_1000_tokens: float):
    #     """
    #     Implement method to calculate cost of invocation
    #     """


# Requires valid OPENAI_API_KEY environment variable
class GPT(Model):
    VERSIONS = {"3.5": "gpt-3.5-turbo-1106", "4": "gpt-4-1106-preview"}

    def __init__(self, model_ver) -> None:
        if not model_ver in self.VERSIONS:
            raise ValueError("Allowed GPT versions: 3.5, 4")

        self.API_KEY = os.environ.get("OPENAI_API_KEY")
        self.model_ver = model_ver
        self.client = OpenAI(api_key=self.API_KEY)

        super().__init__()

    def model(self):
        return self.model_ver

    def invoke(self, prompt) -> None:
        if not self.API_KEY:
            raise ValueError("Please initialize OPENAI_API_KEY env variable")

        completion = self.client.chat.completions.create(
            model=self.VERSIONS[self.model_ver],
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


# Requires valid ~/.aws/credentials
class Claude(Model):
    VERSIONS = {"2.1": "anthropic.claude-v2:1"}

    def __init__(self, model_ver) -> None:
        if not model_ver in self.VERSIONS:
            raise ValueError("Allowed Claude versions: 2.1")

        self.API_KEY = os.environ.get("CLAUDE_API_KEY")
        self.model_ver = model_ver

        self.client = boto3.client("bedrock-runtime", region_name="us-east-1")

        super().__init__()

    def model(self):
        return self.model_ver

    def invoke(self, prompt):
        """
        Invokes the Anthropic Claude 2 model to run an inference using the input
        provided in the request body.

        :param prompt: The prompt that you want Claude to complete.
        :return: Inference response from the model.
        """

        # Claude requires you to enclose the prompt as follows:
        enclosed_prompt = "Human: " + prompt + "\n\nAssistant:"

        body = {
            "prompt": enclosed_prompt,
            "max_tokens_to_sample": 2000,
            "temperature": 0.5,
            "stop_sequences": ["\n\nHuman:"],
        }

        response = self.client.invoke_model(
            modelId=self.VERSIONS[self.model_ver], body=json.dumps(body)
        )

        response_body = json.loads(response.get("body").read())
        completion = response_body["completion"]

        print(completion.strip())
        return completion


class Service:
    def __init__(self, client: Model):
        self.client = client

    def get_response(self, prompt):
        print("Service get response")
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sends a prompt to openai API or Claude, returns a GPT3.5, GPT4 or Claude 2.1 completion response"
    )

    parser.add_argument(
        "-v",
        "--version",
        type=str,
        default="3.5",
        help="Model version (3.5, 4, or claude)'",
    )
    parser.add_argument("prompt_text", type=str, help="Prompt for the model")

    args = parser.parse_args()
    load_dotenv()

    if args.version.lower() in ["3.5", "4"]:
        client = GPT(model_ver=args.version.lower())
    else:
        client = Claude(model_ver="2.1")
    client.invoke(prompt=args.prompt_text)
