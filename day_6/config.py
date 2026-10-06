import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("MODEL", "openai/gpt-oss-120b")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

def banner(title):
    print("=" * 60)
    print(title)
    print("=" * 60)