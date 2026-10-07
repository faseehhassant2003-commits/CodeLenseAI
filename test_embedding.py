from app.services.embedding_service import create_embedding

text="JWT token validation"

embedding=create_embedding(text)

print("vector diamentions:",len(embedding))
print("first 10 values: ",embedding[:10])