import time
from pathlib import Path

from app.services.vector_search import search_similar_chunks
from app.services.llm_service import generate_answer


def answer_question(question: str, repository_id: int):

    total_start = time.perf_counter()

    # =========================================================
    # 1. RETRIEVAL
    # =========================================================

    retrieval_start = time.perf_counter()

    results = search_similar_chunks(
        question=question,
        repository_id=repository_id,
        limit=5
    )

    retrieval_time = time.perf_counter() - retrieval_start

    print("=" * 50)
    print(f"Retrieval time: {retrieval_time:.2f}s")
    print("=" * 50)

    # =========================================================
    # 2. BUILD CLEAN REPOSITORY CONTEXT
    # =========================================================

    context_parts = []

    for result in results:

        # Convert absolute/local path into repository-relative path
        clean_path = Path(result.file_path)

        parts = clean_path.parts

        repository_folder = f"repository-{repository_id}"

        if repository_folder in parts:

            index = parts.index(repository_folder)

            clean_path = Path(*parts[index + 1:])

        clean_path = str(clean_path).replace("\\", "/")

        context_parts.append(
            f"""
File: {clean_path}
Lines: {result.start_line}-{result.end_line}
Chunk: {result.chunk_index}

{result.content}
"""
        )

    context = "\n".join(context_parts)

    # =========================================================
    # 3. SEND CONTEXT TO GROQ
    # =========================================================

    llm_start = time.perf_counter()

    print(">>> Starting Groq request...")

    answer = generate_answer(
        question=question,
        context=context
    )

    llm_time = time.perf_counter() - llm_start

    # =========================================================
    # 4. TOTAL TIME
    # =========================================================

    total_time = time.perf_counter() - total_start

    print(f"Groq time: {llm_time:.2f}s")
    print(f"Total time: {total_time:.2f}s")
    print("=" * 50)

    # =========================================================
    # 5. BUILD SOURCES
    # =========================================================

    sources = []

    for result in results:

        clean_path = Path(result.file_path)

        parts = clean_path.parts

        repository_folder = f"repository-{repository_id}"

        if repository_folder in parts:

            index = parts.index(repository_folder)

            clean_path = Path(*parts[index + 1:])

        sources.append({
            "file": str(clean_path).replace("\\", "/"),
            "chunk": result.chunk_index,
            "start_line": result.start_line,
            "end_line": result.end_line
        })

    # =========================================================
    # 6. RETURN RESULT
    # =========================================================

    return {
        "answer": answer,
        "sources": sources
    }