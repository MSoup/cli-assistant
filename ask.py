import json
import os
from openai import OpenAI
from dotenv import load_dotenv
import argparse
from abc import ABC, abstractmethod
import boto3


class Model(ABC):
    """
    Abstract class. Models must implement the below
    :abstractmethod: model()
    :abstractmethod: invoke()
    :abstractmethod: add_to_factory()
    """

    def __init__(self, model_ver: str):
        self.__model_ver = model_ver

    @property
    @abstractmethod
    def model(self):
        """
        Human readable model name
        """
        return self.__model_ver

    @property
    @abstractmethod
    def modelId(self):
        """
        Model identifier
        """
        raise NotImplementedError

    @abstractmethod
    def invoke(self, prompt: str):
        """
        Implement invoke method
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def add_to_factory():
        """
        Implement add_to_factory method
        """
        raise NotImplementedError


class ModelVersion:
    def __init__(self, model: Model, version: str):
        self.model = model
        self.version = version

    def __repr__(self):
        return f"{self.version}"


class ServiceFactory:
    """
    Service factory
    :param str model_name: Human readable model name to initialize
    :property dict AVAILABLE_MODELS: stores initializable models.\n
    Models should implement a class, add_to_factory(), that sets ServiceFactory.AVAILABLE_MODELS[ver] to a ModelVersion object
    Initializes a client for a model
    """

    AVAILABLE_MODELS = {}

    # AVAILABLE_MODELS: {human_readable_model_name: ModelVersion object}
    def __init__(self, model_name: str) -> None:
        self.client = self._get_client(model_name.lower())

    def get_available_models():
        return f"""Available Models:
        {list(ServiceFactory.AVAILABLE_MODELS.keys())}
        {"=" * 35}
        """

    def invoke(self, prompt) -> None:
        print(f">>> Invoking {self.client.model} assistant: ")
        return self.client.invoke(prompt)

    def _get_client(self, model_version: str) -> Model:
        if model_version in ServiceFactory.AVAILABLE_MODELS:
            client_params: ModelVersion = ServiceFactory.AVAILABLE_MODELS[model_version]
            client: Model = client_params.model(model_version)
        else:
            raise ValueError(
                f"Allowed versions: {ServiceFactory.AVAILABLE_MODELS.keys()}"
            )
        return client


class GPT(Model):
    """
    GPT Models by OpenAI. Requires valid OPENAI_API_KEY environment variables. Model is called through OpenAI library
    """

    VERSIONS = {"3.5": "gpt-3.5-turbo-1106", "4": "gpt-4-1106-preview"}

    def __init__(self, model_ver) -> None:
        if not model_ver in self.VERSIONS:
            raise ValueError("Allowed versions:", list(self.VERSIONS.items()))

        self.model_ver = model_ver
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)

        super().__init__(self.model_ver)

    @property
    def model(self):
        return f"GPT-{self.model_ver}"

    @property
    def modelId(self):
        return f"{self.VERSIONS[self.model_ver]}"

    @classmethod
    def add_to_factory(self):
        for k, v in self.VERSIONS.items():
            ServiceFactory.AVAILABLE_MODELS[k] = ModelVersion(GPT, v)

    def invoke(self, prompt) -> None:
        if not self.api_key:
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


# https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids-arns.html
class Claude(Model):
    VERSIONS = {"claude": "anthropic.claude-v2:1"}

    def __init__(self, version: str) -> None:
        self.version = version
        self.client = boto3.client("bedrock-runtime", region_name="us-east-1")

    @property
    def model(self):
        return self.version

    @property
    def modelId(self):
        return self.VERSIONS[self.version]

    @classmethod
    def add_to_factory(self):
        for k, v in self.VERSIONS.items():
            ServiceFactory.AVAILABLE_MODELS[k] = ModelVersion(Claude, v)

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
            "temperature": 0.1,
            "stop_sequences": ["\n\nHuman:"],
        }
        response = self.client.invoke_model(modelId=self.modelId, body=json.dumps(body))
        response_body = json.loads(response["body"].read())
        completion = response_body["completion"]
        return completion.strip()


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
    # Init invokable models
    GPT.add_to_factory()
    Claude.add_to_factory()

    # Init env variables
    load_dotenv()

    # Print available models
    ServiceFactory.get_available_models()

    parser = argparse.ArgumentParser(
        description="Sends a prompt to openai API or Claude, returns a GPT3.5, GPT4 or Claude 2.1 completion response"
    )

    parser.add_argument(
        "-v",
        "--version",
        type=str,
        default="claude",
        help="Model version (3.5, 4, or claude)'",
        choices=["3.5", "4", "claude"],
    )
    parser.add_argument("prompt_text", type=str, help="Prompt for the model")

    args = parser.parse_args()

    llm_to_invoke = args.version
    prompt = args.prompt_text

    client = ServiceFactory(llm_to_invoke)
    print(client.invoke(prompt))
