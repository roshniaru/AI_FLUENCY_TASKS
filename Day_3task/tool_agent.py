
"""Ask the LLM questions using a calculator tool."""

import json

from config import client, MODEL, banner
from tools import calculator


QUESTIONS = [
    (
        "Q1 - Calculation",
        "CS101 costs Rs. 12000 and AI202 costs Rs. 18000. "
        "A 10% scholarship applies to the combined fee. "
        "What is the final fee?"
    ),
    (
        "Q2 - General Knowledge",
        "Explain what a scholarship means in simple words."
    ),
    (
        "Q3 - Total Fee",
        "Three courses cost Rs. 12000, Rs. 18000, and Rs. 15000. "
        "An additional laboratory charge is Rs. 4500. "
        "What is the total amount?"
    ),
]


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": (
                "Calculate mathematical expressions. "
                "Use this tool whenever a question requires arithmetic."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A mathematical expression."
                    }
                },
                "required": ["expression"],
                "additionalProperties": False
            }
        }
    }
]


def ask_with_tool(question):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful college assistant. "
                "Use the calculator tool for arithmetic calculations. "
                "Use the actual tool result in your final answer. "
                "For general questions, answer directly without a tool."
            )
        },
        {
            "role": "user",
            "content": question
        }
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0
    )

    message = response.choices[0].message

    if not message.tool_calls:
        print("Tool call: None")
        return message.content or ""

    messages.append({
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
    })

    for call in message.tool_calls:
        name = call.function.name
        arguments = json.loads(call.function.arguments or "{}")

        if name == "calculator":
            result = calculator(**arguments)
        else:
            result = f"Unknown tool: {name}"

        print("Tool call:", name)
        print("Arguments:", arguments)
        print("Tool result:", result)

        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": str(result)
        })

    final_response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0
    )

    return final_response.choices[0].message.content or ""


if __name__ == "__main__":
    banner("LLM WITH CALCULATOR TOOL")

    for title, question in QUESTIONS:
        print(f"\n{'=' * 55}")
        print(title)
        print("Question:", question)

        try:
            answer = ask_with_tool(question)
            print("Final answer:", answer)

        except Exception as error:
            print("Error:", type(error).__name__, error)
