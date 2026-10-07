from app.services.llm_service import generate_answer


answer = generate_answer(
    "What is JWT?",
    "JWT stands for JSON Web Token. It is commonly used for authentication."
)

print("\nGemini response:")
print(answer)