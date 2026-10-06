"""Day 6: Robust tool-calling agent with validation and retry."""

import json

from config import client, MODEL, banner
from tools_v2 import TOOLS, TOOL_FUNCTIONS, SCHEMAS
from validate import validate_arguments


SYSTEM_PROMPT = (
    "You are a college attendance assistant. "
    "Use get_attendance when the user asks about attendance. "
    "Use calculate_fine when the user asks about an absence fine. "
    "Valid semesters are odd and even. "
    "If the user asks for attendance and fine, use both tools. "
    "If no tool is needed, answer directly."
)


MAX_TOKENS = 500
REPEAT_LIMIT = 3


def handle_tool_call(call, log=True):
    """Safely process one model-generated tool call."""

    name = call.function.name
    raw = call.function.arguments or "{}"

    # --------------------------------
    # 1. Parse JSON
    # --------------------------------
    try:
        arguments = json.loads(raw)

    except json.JSONDecodeError as error:
        return (
            f"Argument error: invalid JSON ({error}). "
            f"Send valid JSON for '{name}'."
        )

    # --------------------------------
    # 2. Look up the tool
    # --------------------------------
    function = TOOL_FUNCTIONS.get(name)

    if function is None:
        return (
            f"Unknown tool: {name}. "
            f"Available tools: {', '.join(TOOL_FUNCTIONS)}."
        )

    # --------------------------------
    # 3. Validate arguments
    # --------------------------------
    problem = validate_arguments(
        arguments,
        SCHEMAS[name]
    )

    if problem:
        return f"Argument error: {problem}"

    # --------------------------------
    # 4. Execute tool
    # --------------------------------
    try:
        result = str(function(**arguments))

    except Exception as error:
        result = (
            f"Tool error in {name}: "
            f"{type(error).__name__}: {error}"
        )

    if log:
        print(
            f"      {name}({arguments}) -> "
            f"{result[:100]}"
        )

    return result


def agent(question, max_steps=6, verbose=True):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": question
        }
    ]

    seen = {}

    max_tokens = MAX_TOKENS

    for step in range(1, max_steps + 1):

        # --------------------------------
        # Ask the model
        # --------------------------------
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            temperature=0,
            max_tokens=max_tokens
        )

        choice = response.choices[0]
        message = choice.message

        # --------------------------------
        # Handle truncated response
        # --------------------------------
        if choice.finish_reason == "length":

            if max_tokens >= 2000:
                return (
                    "Stopped: the reply was still "
                    "truncated at 2000 tokens."
                )

            max_tokens *= 2

            if verbose:
                print(
                    f"   step {step}: truncated, "
                    f"retrying with max_tokens={max_tokens}"
                )

            continue

        # --------------------------------
        # No tool call -> final answer
        # --------------------------------
        if not message.tool_calls:
            return (message.content or "").strip()

        # --------------------------------
        # Add assistant tool-call message
        # --------------------------------
        messages.append(
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments
                        }
                    }
                    for call in message.tool_calls
                ]
            }
        )

        if verbose:
            print(
                f"   step {step}: "
                f"{len(message.tool_calls)} tool call(s)"
            )

        # --------------------------------
        # Handle ALL tool calls
        # --------------------------------
        for call in message.tool_calls:

            signature = (
                call.function.name,
                call.function.arguments
            )

            seen[signature] = seen.get(signature, 0) + 1

            # --------------------------------
            # Repeat detection
            # --------------------------------
            if seen[signature] >= REPEAT_LIMIT:

                return (
                    f"Stopped: {call.function.name} "
                    f"was called {REPEAT_LIMIT} times "
                    f"with the same arguments and made no progress."
                )

            result = handle_tool_call(
                call,
                log=verbose
            )

            # One tool message for every tool_call_id
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result
                }
            )

    return (
        "Stopped: maximum steps reached "
        "without a final answer."
    )


if __name__ == "__main__":

    banner("ROBUST ATTENDANCE AGENT")

    questions = [

        # 1. Single tool
        "What is the odd semester attendance of student 7376252AL203?",

        # 2. Two tools
        "For student 7376252AL203, tell me the odd semester attendance and calculate the fine for 3 absent days.",

        # 3. Invalid value temptation
        "What is the attendance of student 7376252AL203 in the summer semester?",

        # 4. No tool
        "Write a one-line welcome message for new students."
    ]

    for question in questions:

        print("\nQ:", question)

        answer = agent(question)

        print("A:", answer)