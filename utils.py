from time import time
import html

def timer_func(func: callable):
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(f'Function {func.__name__!r} executed in {(t2-t1):.4f}s')
        return result
    return wrap_func

def prepare_html(string: str) -> str:
    if string is None:
        return ''
    
    if isinstance(string, str):
        string = html.escape(string).replace('\n', '<br>')

    return string
