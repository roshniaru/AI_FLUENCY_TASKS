"""Ask the LLM questions without using any tools."""

from config import client, MODEL, banner


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


def ask_without_tool(question):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful college assistant. "
                    "Answer clearly and explain calculations briefly."
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        temperature=0,
    )

    return response.choices[0].message.content or ""


if __name__ == "__main__":
    banner("PLAIN LLM - NO TOOL")

    for title, question in QUESTIONS:
        print(f"\n{'=' * 55}")
        print(title)
        print("Question:", question)

        try:
            answer = ask_without_tool(question)
            print("Answer:", answer)

        except Exception as error:
            print("Error:", type(error).__name__, error)