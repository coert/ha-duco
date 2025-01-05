def remove_val_fields(data):
    """Recursively remove 'Val' fields from the JSON-like dictionary."""

    if isinstance(data, dict):
        if "Val" in data and len(data) == 1:
            return data["Val"]
        return {key: remove_val_fields(value) for key, value in data.items()}

    elif isinstance(data, list):
        return [remove_val_fields(item) for item in data]

    return data
