from dataclasses import fields, is_dataclass


def remove_val_fields(data):
    """Recursively remove 'Val' fields from the JSON-like dictionary."""

    if isinstance(data, dict):
        if "Val" in data and len(data) == 1:
            return data["Val"]
        return {key: remove_val_fields(value) for key, value in data.items()}

    elif isinstance(data, list):
        return [remove_val_fields(item) for item in data]

    return data


def from_dict(data_class, data_dict):
    """
    Recursively convert a dictionary to a dataclass instance, including nested dataclasses.
    """
    if not is_dataclass(data_class):
        raise TypeError(f"{data_class} is not a dataclass.")

    field_values = {}
    for field in fields(data_class):
        field_name = field.name
        field_type = field.type
        field_value = data_dict.get(field_name)

        # Check if the field type is another dataclass
        if is_dataclass(field_type) and isinstance(field_value, dict):
            field_values[field_name] = from_dict(field_type, field_value)
        elif hasattr(field_type, "__origin__") and field_type.__origin__ is list:
            # Handle list of dataclasses
            item_type = field_type.__args__[0]
            if is_dataclass(item_type) and isinstance(field_value, list):
                field_values[field_name] = [
                    from_dict(item_type, item) for item in field_value
                ]
            else:
                field_values[field_name] = field_value
        else:
            field_values[field_name] = field_value

    return data_class(**field_values)  # type: ignore


def safe_get(data, *keys):
    """Safely get nested keys from a dict."""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key)
        else:
            return None
    return data
