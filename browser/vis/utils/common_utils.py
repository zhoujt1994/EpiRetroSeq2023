import os
from cachetools import TTLCache, cached

cache = TTLCache(maxsize=100, ttl=3600)


def controlled_cached():
    def decorator(func):
        @cached(cache=cache)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


def handle_file_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as fnf_error:
            file_name = args[0] if args else kwargs.get('path')
            if file_name:
                file_name = os.path.basename(file_name)
                error_msg = f"File '{file_name}' not found."
            else:
                error_msg = "File not found."
            raise type(fnf_error)(error_msg) from fnf_error
        except Exception as e:
            raise type(e)(f"An error occurred: {e}") from e
    return wrapper


def find_key_by_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key


def calculate_zscore(data):
    mean_value = sum(data) / len(data)
    std_deviation = (sum((x - mean_value) ** 2 for x in data) / len(data)) ** 0.5

    normalized_gene_data = [(x - mean_value) / std_deviation for x in data]

    return normalized_gene_data

