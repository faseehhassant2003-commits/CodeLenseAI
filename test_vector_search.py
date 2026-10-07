from app.services.vector_search import search_similar_chunks

results = search_similar_chunks(
    "Where is authentication implemented?",
    limit=5
)

print("Results found:", len(results))

for result in results:
    print("\nFile:", result.file_path)
    print("Chunk:", result.chunk_index)
    print("Content:")
    print(result.content[:300])