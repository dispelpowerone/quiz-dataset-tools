import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
)
from quiz_dataset_tools.util.transformer import Transformer


"""
class Paraphrase(Transformer):
    REQUEST_TEMPL_1 = 'Reword text: "{text}"'
    REQUEST_TEMPL_2 = 'Reword for non native speaker: "{text}". Make it short and preserve meaning. Don\'t change if it is not possible.'

    def __init__(self, domain: str, request_templ: str = REQUEST_TEMPL_1):
        super().__init__(domain, "paraphrase")
        self._request_templ = Paraphrase.REQUEST_TEMPL_1

    def _get(self, src_text: str):
        result = self._ask_gpt(src_text)
        # Strip noice
        result = result.strip('" ')
        return result

    def _ask_gpt(self, src_text):
        request = self._request_templ.format(text=src_text)
        messages = [{"role": "system", "content": request}]
        chat = _chat_completion_with_backoff(model="gpt-3.5-turbo", messages=messages)
        print(f"paraphrase::_ask_gpt: {src_text} -> {chat.choices[0].message.content}")
        return chat.choices[0].message.content


openai.api_key = "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"

@retry(
    retry=retry_if_exception_type(
        (
            openai.error.APIError,
            openai.error.APIConnectionError,
            openai.error.RateLimitError,
            openai.error.ServiceUnavailableError,
            openai.error.Timeout,
        )
    ),
    wait=wait_random_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(10),
)
def _chat_completion_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)
"""
