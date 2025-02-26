def remove_val_fields(data):
    """Recursively remove 'Val' fields from the JSON-like dictionary."""

    if isinstance(data, dict):
        if "Val" in data and len(data) == 1:
            return data["Val"]
        return {key: remove_val_fields(value) for key, value in data.items()}

    elif isinstance(data, list):
        return [remove_val_fields(item) for item in data]

    return data


def str_to_bool(arg: bool | bytes | str | None) -> bool | None:
    """
    Convert a string to bool value
    :param arg:
    :return: (bool)
    """
    if arg is None:
        return False

    try:
        if isinstance(arg, bytes):
            bstr = arg.decode("utf-8").lower()

        elif isinstance(arg, str):
            bstr = arg.lower()

        elif isinstance(arg, bool):
            return arg
        elif isinstance(arg, bytes):
            bstr = arg.decode("utf-8").lower()
        else:
            bstr = arg.lower()

    except Exception:
        return False

    if bstr in ("yes", "true", "t", "y", "1"):
        return True

    elif bstr in ("no", "false", "f", "n", "0"):
        return False

    else:
        return None
