import os

from dotenv import load_dotenv
from groq import Groq


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")


# =========================================================
# GROQ CLIENT
# =========================================================

client = Groq(
    api_key=api_key
)


# =========================================================
# GENERATE ANSWER
# =========================================================

def generate_answer(question: str, context: str):

    prompt = f"""
You are CodeLense AI, a code repository intelligence assistant.

Your job is to answer questions about the user's GitHub repository.

IMPORTANT RULES:

1. Answer the user's question using ONLY the provided repository context.

2. Do not invent information that is not present in the context.

3. When mentioning a file, ALWAYS use the repository-relative path
   provided after "File:".

4. NEVER mention local filesystem paths such as:
   repositories/repository-9/

5. If line numbers are provided, mention them when useful.

6. If the context does not contain enough information to answer the question,
   clearly say that the information was not found in the repository.

7. Be concise but explain the important technical details.

8. When possible, explain:
   - which file contains the implementation
   - what the relevant code does
   - how the files are connected

User question:
{question}

Repository context:
{context}
"""

    # =========================================================
    # GROQ REQUEST
    # =========================================================

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content