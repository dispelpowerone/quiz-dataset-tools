from quiz_dataset_tools.util.language import TextLocalizations


def strip_text(text: TextLocalizations) -> TextLocalizations:
    return text.transform(lambda s: s.strip())


def remove_echo_text(text: TextLocalizations) -> TextLocalizations:
    return text.transform(_remove_echo_from_string)


def _remove_echo_from_string(text: str) -> str:
    text_len = len(text)
    if text_len < 3:
        return text
    text_len_mid = text_len // 2
    if text[text_len_mid] == "/":
        text_first = text[0:text_len_mid].strip()
        text_second = text[text_len_mid + 1 :].strip()
        if text_first == text_second:
            return text_first
    return text
