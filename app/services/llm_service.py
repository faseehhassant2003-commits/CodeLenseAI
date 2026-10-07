import os 
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key=os.getenv("GEMINI_API_KEY")

client=genai.Client(api_key=api_key)

def generate_answer(question:str ,context:str):
        prompt = f"""
You are CodeLense AI, a code repository intelligence assistant.

Answer the user's question using ONLY the provided repository context.

If the context does not contain enough information to answer the question,
say that the information was not found in the repository.

User question:
{question}

Repository context:
{context}
"""
        response=client.interactions.create(
            model="gemini-3.8-flash",
            input=prompt
        )

        return response.output_text