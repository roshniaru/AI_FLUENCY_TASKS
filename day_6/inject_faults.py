"""Day 6: Deliberate fault injection for the robust tool-calling agent."""

from robust_agent import handle_tool_call


class FakeFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class FakeCall:
    def __init__(self, name, arguments):
        self.function = FakeFunction(name, arguments)


FAULTS = [
    (
        "Invalid JSON",
        FakeCall(
            "get_attendance",
            '{"student_id": "7376252AL203"',
        ),
    ),

    (
        "Unknown tool",
        FakeCall(
            "send_notification",
            '{"student_id": "7376252AL203"}',
        ),
    ),

    (
        "Missing required argument",
        FakeCall(
            "get_attendance",
            "{}",
        ),
    ),

    (
        "Wrong type",
        FakeCall(
            "get_attendance",
            '{"student_id": 203}',
        ),
    ),

    (
        "Enum violation",
        FakeCall(
            "get_attendance",
            '{"student_id": "7376252AL203", "semester": "summer"}',
        ),
    ),

    (
        "Invented extra argument",
        FakeCall(
            "get_attendance",
            '{"student_id": "7376252AL203", "year": 2026}',
        ),
    ),

    # Own fault 1
    (
        "Unknown student ID",
        FakeCall(
            "get_attendance",
            '{"student_id": "999999"}',
        ),
    ),

    # Own fault 2
    (
        "Negative absence days",
        FakeCall(
            "calculate_fine",
            '{"days_absent": -5}',
        ),
    ),

    # Additional fault
    (
        "Arguments are not an object",
        FakeCall(
            "calculate_fine",
            "[]",
        ),
    ),
]


if __name__ == "__main__":
    print("=" * 60)
    print("FAULT INJECTION TEST")
    print("=" * 60)

    for number, (label, call) in enumerate(FAULTS, start=1):
        print(f"\n[{number}] {label}")
        result = handle_tool_call(call)
        print(f"Result: {result}")