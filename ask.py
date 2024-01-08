import json
import os
from openai import OpenAI
from dotenv import load_dotenv
import argparse
from abc import ABC, abstractmethod
import boto3


class Model(ABC):
    """
    Abstract class that models must implement
    """

    def __init__(self, model_ver: str):
        self.__model_ver = model_ver

    @property
    @abstractmethod
    def model(self):
        """
        Model name
        """
        return self.__model_ver

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


class GPT(Model):
    """
    GPT Models by OpenAI. Requires valid OPENAI_API_KEY environment variables. Model is called through OpenAI library
    """

    VERSIONS = {"3.5": "gpt-3.5-turbo-1106", "4": "gpt-4-1106-preview"}

    def __init__(self, model_ver) -> None:
        if not model_ver in self.VERSIONS:
            raise ValueError("Allowed GPT versions: 3.5, 4")

        self.API_KEY = os.environ.get("OPENAI_API_KEY")
        self.model_ver = model_ver
        self.client = OpenAI(api_key=self.API_KEY)

        super().__init__(model_ver)

    @property
    def model(self):
        return f"GPT-{self.model_ver}"

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
        return response


class Claude(Model):
    """
    Claude Model by Anthropic. Requires valid ~/.aws/credentials. Model is called through boto3 bedrock-runtime
    """

    VERSIONS = {"2.1": "anthropic.claude-v2:1"}

    def __init__(self, model_ver) -> None:
        if not model_ver in self.VERSIONS:
            raise ValueError("Allowed Claude versions: 2.1")

        self.model_ver = model_ver

        self.client = boto3.client("bedrock-runtime", region_name="us-east-1")

        super().__init__(self.model_ver)

    @property
    def model(self):
        return f"Claude-{self.model_ver}"

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

        return completion.strip()


class ServiceFactory:
    """
    Model factory
    :param str model:
    """

    def __init__(self, model: str) -> None:
        self.client = self._get_client(model)

    def invoke(self, prompt) -> None:
        print(f"{self.client.model} assistant: ")
        return self.client.invoke(prompt)

    def _get_client(self, model_version) -> Model:
        if model_version == "3.5":
            client = GPT("3.5")
        elif model_version == "4":
            client = GPT("4")
        elif model_version.lower() == "claude":
            client = Claude("2.1")
        else:
            raise ValueError("Allowed versions: 3.5, 4, 2.1")
        return client


# WRAPPER
# def token_usage(func: Callable) -> Callable:
#     """
#     Decorates a function that returns a completion object
#     """
#     COST_FOR_1000_TOKENS = {Model.GPT3_5.value: 0.003, Model.GPT4.value: 0.04}

#     def wrapper(*args, **kwargs):
#         completion_object = func(*args, **kwargs)
#         try:
#             model = completion_object.model
#             token_usage = completion_object.usage.total_tokens
#             # cost is tokens used * cost per token. We know cost per 1000, so we divide the cost for 1000 tokens by 1000
#             cost_per_token = COST_FOR_1000_TOKENS[model] / 1000
#             actual_cost = round(token_usage * cost_per_token, 4)
#             print("==================================")
#             print(
#                 f"Model: {model} | Token usage: {token_usage} | Cost: {actual_cost} USD"
#             )
#         except AttributeError:
#             print("The decorated function must return a completion object")
#         return completion_object

#     return wrapper

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
        choices=["3.5", "4", "claude"],
    )
    parser.add_argument("prompt_text", type=str, help="Prompt for the model")

    args = parser.parse_args()
    load_dotenv()

    client = ServiceFactory(model=args.version)

    print(client.invoke(prompt=args.prompt_text))
