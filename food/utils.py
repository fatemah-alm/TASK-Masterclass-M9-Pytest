import re


def get_case_insensitive_regex(values: list[str]) -> str:
    joined = "|".join([re.escape(n) for n in values])
    return rf"({joined})"
