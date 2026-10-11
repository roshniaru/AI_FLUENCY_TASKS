
"""Step 2: Ask the vector database questions directly - no LLM involved yet."""

from lc_config import get_vectorstore

store = get_vectorstore()

questions = [
    "How much is the late fee for paying fees after the due date?",
    "What time should hostel students return?",
    "Can I write the exam with 70% attendance?",
    "What CGPA do I need to be eligible for placements?",
]

for q in questions:
    print(f"\nQ: {q}")

    # Score is cosine distance: smaller means more similar
    results = store.similarity_search_with_score(q, k=3)

    for doc, score in results:
        print(
            f"  {score:.3f}  "
            f"[{doc.metadata['source']}]  "
            f"{doc.page_content[:70]!r}"
        )

    # Confirm the top result for the CGPA question
    if q == "What CGPA do I need to be eligible for placements?":
        if results and results[0][0].metadata.get("source") == "placement_policy.md":
            print("  PASS: Top result is from placement_policy.md")
        else:
            print("  CHECK: Top result is NOT from placement_policy.md")

# Metadata filter: search ONLY inside one file
print("\nFiltered to library.md:")

for doc in store.similarity_search(
    "fine for late return",
    k=2,
    filter={"source": "library.md"},
):
    print(
        "  ",
        doc.metadata["source"],
        "->",
        doc.page_content[:80].replace("\n", " "),
    )
