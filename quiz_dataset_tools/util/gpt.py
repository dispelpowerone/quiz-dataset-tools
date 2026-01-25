import time
import logging
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from typing import Any, Optional
from quiz_dataset_tools.config import config
from quiz_dataset_tools.util.cache import StringCache
from quiz_dataset_tools.util.image import load_image_as_base64


# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("openai").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=config["openai"]["api_key"])


class GPTService:
    def __init__(self, model: str, max_retries: int = 3, retry_delay: float = 100.0):
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def send_prompt(
        self,
        prompt: str,
        image_file: str | None = None,
        system_prompt: str | None = None,
    ) -> str:
        """
        Send a prompt to the OpenAI GPT API and return the response.
        Retries if the request fails.

        :param prompt: User message prompt.
        :param image_file: Optional image file name
        :param system_prompt: Optional system role message.
        :return: Response string.
        """
        content: list[Any] = [
            {"type": "text", "text": prompt},
        ]
        if image_file:
            base64_image = load_image_as_base64(image_file)
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                    },
                }
            )
        messages: list[Any] = [
            {
                "role": "user",
                "content": content,
            },
        ]
        if system_prompt:
            messages.append(
                {
                    "role": "developer",
                    "content": system_prompt,
                }
            )

        for attempt in range(1, self.max_retries + 1):
            try:
                completion = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                )
                print(completion)
                if not completion.choices:
                    break
                result = completion.choices[0].message.content
                if not result:
                    break
                return result
            except Exception as e:
                logger.warning(f"Request failed on attempt {attempt}: {e}")
                if attempt == self.max_retries:
                    raise
                time.sleep(self.retry_delay * attempt)  # exponential backoff
        raise Exception(f"Prompt failed: {prompt}")


class GPTServiceWithCache:
    impl: GPTService
    cache: StringCache

    def __init__(self, domain: str, model: str):
        self.impl = GPTService(model)
        self.cache = StringCache(domain, model)

    def send_prompt(self, prompt: str, image_file: str | None = None) -> str:
        cache_key = prompt
        if image_file:
            cache_key = f"{cache_key} image:{image_file}"
        return self.cache.get_or_retrieve(
            cache_key, lambda _: self.impl.send_prompt(prompt, image_file)
        )

    def save_cache(self) -> None:
        self.cache.save()

    def load_cache(self) -> None:
        self.cache.load()


'''
test_type = "G1 Driving Test Ontario"
question_content = "What does this road sign mean?"
answers_content = [
    "This road turns slightly right ahead.",
    "This road turns sharply right ahead.",
    "Traffic must exit to the right.",
    "Keep right."
]
right_answer = 1
image_dir = "/Users/gz/Workspace/quiz-dataset-tools/output/domains/on/prebuild/images/"
image_file = image_dir + "tild3939-3533-4432-b534-643939383866____72.png"
#image_file = "/Users/gz/Desktop/1.jpeg"
#image_file = None

service = GPTService("gpt-4o")
prompt = f"""
You are a {test_type} examiner. You work on a list of questions to assess knowledge of driving rules.
Give a concise explanation why for the given image attached and for the question
```
{question_content}
```
among the following answers
```
{"\n".join(answers_content)}
```
the right answer is
```
{answers_content[right_answer]}
```
Use a formal tone targeting an average-level audience.
Make your response as short as possible.
Do not include the answer in the response.
Give an advice on how to remember the right answer.
Start the advice with '💡' symbol.
        """
print(service.send_prompt(prompt, image_file))
'''
