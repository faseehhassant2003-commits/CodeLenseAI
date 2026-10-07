from app.services.vector_search import search_similar_chunks
from app.services.llm_service import generate_answer
from pathlib import Path


def answer_question(question: str, repository_id: int):

    # 1. Retrieve relevant chunks from the selected repository
    results = search_similar_chunks(
        question=question,
        repository_id=repository_id,
        limit=5
    )

    # 2. Build context for Gemini
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

    # 4. Build clean source information
    sources = []

    for result in results:

        clean_path = Path(result.file_path)

        parts = clean_path.parts

        # Repository folder is different for every repository
        repository_folder = f"repository-{repository_id}"

        if repository_folder in parts:
            index = parts.index(repository_folder)

            # Remove:
            # repositories/repository-5/
            # and keep the actual project path
            clean_path = Path(*parts[index + 1:])

        sources.append({
            "file": str(clean_path).replace("\\", "/"),
            "chunk": result.chunk_index,
            "start_line": result.start_line,
            "end_line": result.end_line
        })

    # 5. Return answer and sources
    return {
        "answer": answer,
        "sources": sources
    }