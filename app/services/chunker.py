def create_chunks(text: str, chunk_size: int = 500):

    lines = text.splitlines()

    chunks = []

    current_chunk = []
    current_length = 0
    start_line = 1

    for line_number, line in enumerate(lines, start=1):

        if current_length + len(line) > chunk_size and current_chunk:

            chunks.append({
                "content": "\n".join(current_chunk),
                "start_line": start_line,
                "end_line": line_number - 1
            })

            current_chunk = []
            current_length = 0
            start_line = line_number

        current_chunk.append(line)
        current_length += len(line) + 1

    if current_chunk:
        chunks.append({
            "content": "\n".join(current_chunk),
            "start_line": start_line,
            "end_line": len(lines)
        })

    return chunks