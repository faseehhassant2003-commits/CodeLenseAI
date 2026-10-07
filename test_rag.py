from app.services.rag_service import answer_question


question = "Where is authentication implemented?"

answer = answer_question(question)

print("\nCodeLense AI Answer:")
print(answer)