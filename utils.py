from time import time
import html
import re


def timer_func(func: callable):
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(f"Function {func.__name__!r} executed in {(t2 - t1):.4f}s")
        return result

    return wrap_func


def prepare_html(string: str) -> str:
    if string is None:
        return ""

    if isinstance(string, str):
        string = html.escape(string).replace("\n", "<br>")

    return string


def is_integer(value) -> bool:
    if isinstance(value, int):
        return value > 0

    if isinstance(value, str) and value.isdigit():
        return int(value) > 0

    return False


def parse_ids(ids) -> list:
    if isinstance(ids, str):
        if re.fullmatch(r"[\d,]+", ids):
            return [x for x in ids.split(",") if x]

    return []


def escape_query(query: str) -> str:
    escaped_query = query.replace('"', '""').replace(" ", " ")
    escaped_query = re.sub(r"[‘’]", "'", escaped_query)
    escaped_query = re.sub(r"[“”„]", '""', escaped_query)
    return f'"{escaped_query}"'
