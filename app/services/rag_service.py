from app.services.vector_search import search_similar_chunks
from app.services.llm_service import generate_answer


def answer_question(question: str):

    # 1. Retrieve relevant code chunks
    results = search_similar_chunks(question, limit=5)

    # 2. Build context from retrieved chunks
    context_parts = []

    for result in results:
        context_parts.append(
            f"""
File: {result.file_path}
Chunk: {result.chunk_index}

{result.content}
"""
        )

    context = "\n".join(context_parts)

    # 3. Generate answer using Gemini
    answer = generate_answer(
        question=question,
        context=context
    )

    return answer