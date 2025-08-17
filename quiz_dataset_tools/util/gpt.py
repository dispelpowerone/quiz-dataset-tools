import time
import logging
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from typing import Optional
from quiz_dataset_tools.config import config
from quiz_dataset_tools.util.cache import StringCache


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=config["openai"]["api_key"])


class GPTService:
    def __init__(self, model: str, max_retries: int = 3, retry_delay: float = 100.0):
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def send_prompt(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Send a prompt to the OpenAI GPT API and return the response.
        Retries if the request fails.

        :param prompt: User message prompt.
        :param system_prompt: Optional system role message.
        :return: Response string.
        """
        messages: list[ChatCompletionMessageParam] = []
        if system_prompt:
            messages.append(
                {
                    "role": "developer",
                    "content": system_prompt,
                }
            )
        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        response = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                )
                content = response.choices[0].message.content
                if content is None:
                    break
                return content
            except Exception as e:
                logger.warning(f"Request failed on attempt {attempt}: {e}")
                if attempt == self.max_retries:
                    raise
                time.sleep(self.retry_delay * attempt)  # exponential backoff
        raise Exception(f"Prompt failed: {prompt}, result: {response}")


class GPTServiceWithCache:
    impl: GPTService
    cache: StringCache

    def __init__(self, domain: str, model: str):
        self.impl = GPTService(model)
        self.cache = StringCache(domain, model)

    def send_prompt(self, prompt: str) -> str:
        return self.cache.get_or_retrieve(
            prompt, lambda prompt: self.impl.send_prompt(prompt)
        )

    def save_cache(self) -> None:
        self.cache.save()

    def load_cache(self) -> None:
        self.cache.load()


'''
service = GPTService("gpt-4o")
prompt = """
You are a G1 Driving Test Ontario examiner. You work on a list of questions to assess knowledge of driving rules.
Give a concise explanation why for the question
```
A driver is convicted of fleeing a police officer who signaled them to pull over. For how long will their licence be suspended?
```
among the following answers
```
1. 5 years.
2. 5 weeks.
3. 5 months.
4. 3 days.
```
the right answer is
```
1. 5 years.
```
Use a formal tone targeting an average-level audience.
Keep the answer as short as possible.
Do not include the answer in the response.
"""
print(service.send_prompt(prompt))
'''
