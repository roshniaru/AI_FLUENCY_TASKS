"""Day 6: Compare unconstrained, JSON mode, and JSON Schema output."""

import json

from config import client, MODEL, banner


QUESTION = """
A student with ID 7376252AL203 wants to know their attendance
for the even semester. Extract the student ID, semester,
and whether the request is about attendance.

Return the result as JSON.
"""


SCHEMA = {
    "type": "object",
    "properties": {
        "student_id": {
            "type": "string"
        },
        "semester": {
            "type": "string",
            "enum": ["odd", "even"]
        },
        "asks_attendance": {
            "type": "boolean"
        }
    },
    "required": [
        "student_id",
        "semester",
        "asks_attendance"
    ],
    "additionalProperties": False
}


def show_result(title, response):
    print(f"\n{'=' * 60}")
    print(title)
    print("=" * 60)

    choice = response.choices[0]

    print("finish_reason:", choice.finish_reason)
    print("Raw output:")
    print(choice.message.content)

    try:
        parsed = json.loads(choice.message.content)
        print("\nParsed JSON:")
        print(json.dumps(parsed, indent=2))
    except Exception:
        print("\nOutput is not valid JSON.")


def run_demo():
    # 1. No output constraint
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": QUESTION}
        ],
        temperature=0
    )

    show_result("1. NO CONSTRAINT", response)

    # 2. JSON mode
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": QUESTION}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )

    show_result("2. JSON MODE", response)

    # 3. JSON Schema mode
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": QUESTION}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "attendance_request",
                    "strict": True,
                    "schema": SCHEMA
                }
            },
            temperature=0
        )

        show_result("3. JSON SCHEMA MODE", response)

    except Exception as error:
        print("\n" + "=" * 60)
        print("3. JSON SCHEMA MODE")
        print("=" * 60)
        print("Schema mode failed:")
        print(type(error).__name__, "-", error)


if __name__ == "__main__":
    banner("STRUCTURED OUTPUT DEMO")
    run_demo()