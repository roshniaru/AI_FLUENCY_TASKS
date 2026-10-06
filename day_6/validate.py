"""Day 6: Validate tool arguments against their JSON Schema."""


TYPES = {
    "string": str,
    "number": (int, float),
    "integer": int,
    "boolean": bool,
    "array": list,
    "object": dict,
}


def validate_arguments(arguments, schema):
    """
    Return None when arguments are valid.
    Otherwise return a clear error message.
    """

    # 1. Arguments must be a JSON object
    if not isinstance(arguments, dict):
        return "Arguments must be a JSON object."

    properties = schema.get("properties", {})

    # 2. Check required arguments
    for name in schema.get("required", []):
        if name not in arguments:
            return (
                f"Missing required argument '{name}'. "
                f"Expected: {', '.join(properties)}."
            )

    # 3. Reject invented extra arguments
    if schema.get("additionalProperties") is False:
        extra = [key for key in arguments if key not in properties]

        if extra:
            return (
                f"Unexpected argument(s): {', '.join(extra)}. "
                f"Allowed: {', '.join(properties)}."
            )

    # 4. Check types and enum values
    for name, value in arguments.items():

        rule = properties.get(name, {})

        expected = TYPES.get(rule.get("type"))

        # Wrong type
        if expected and not isinstance(value, expected):
            return (
                f"Argument '{name}' must be a {rule['type']}, "
                f"but got {type(value).__name__}: {value!r}."
            )

        # Value outside enum
        if "enum" in rule and value not in rule["enum"]:
            return (
                f"Argument '{name}' must be one of "
                f"{rule['enum']}, got {value!r}."
            )

    return None


# Simple standalone test
if __name__ == "__main__":

    from tools_v2 import SCHEMAS

    schema = SCHEMAS["get_attendance"]

    cases = [
        {"student_id": "7376252AL203"},
        {"student_id": "7376252AL203", "semester": "even"},
        {},
        {"student_id": 203},
        {"student_id": "7376252AL203", "semester": "summer"},
        {"student_id": "7376252AL203", "year": 2026},
    ]

    for case in cases:
        result = validate_arguments(case, schema)

        print(
            f"{str(case):<55} -> "
            f"{result or 'OK'}"
        )