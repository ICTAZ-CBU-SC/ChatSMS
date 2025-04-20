import pdfplumber
import json

def extract_text_only(pdf_path, is_question_paper: bool, max_images=2):
    """
    Extracts text from a PDF, skipping pages with too many images (like diagrams).
    """
    text_pages = []

    at_beginning_pages = True

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):

            # Skip if page has too many images (likely a diagram-heavy page)
            if len(page.images) > max_images:
                print(f"Skipping page {i + 1} due to many images.")
                continue

            text = page.extract_text()

            # Skip if at beginning pages
            if at_beginning_pages:
                for line in text.split("\n"):
                    # print(f"DEBUG: {line[2:6]}")
                    if line.startswith("1 ") and line[2:6].lower() != "hour":
                        at_beginning_pages = False
                        break
                if at_beginning_pages:
                    continue

            print(f"Page {i + 1}: \n{text}\n\n")
            if text:
                text_pages.append(text)

    return "\n".join(text_pages)


def chunk_by_keywords(text, keywords):
    """
    Breaks text into chunks whenever a line starts with a keyword (like question numbers).
    """
    chunks = []
    current_chunk = []

    for line in text.split("\n"):
        if any(line.strip().lower().startswith(k.lower()) for k in keywords):
            if current_chunk:
                chunks.append("\n".join(current_chunk).strip())
                current_chunk = []
        current_chunk.append(line)

    if current_chunk:
        chunks.append("\n".join(current_chunk).strip())

    return chunks


def to_json_format(question_chunks, mark_chunks):
    """
    Loosely aligns question and answer chunks into a structured list.
    """
    combined = []
    max_len = max(len(question_chunks), len(mark_chunks))

    for i in range(max_len):
        question = question_chunks[i] if i < len(question_chunks) else ""
        mark_scheme = mark_chunks[i] if i < len(mark_chunks) else ""
        combined.append({
            "question_number": f"{i + 1}",
            "question": question,
            "mark_scheme": mark_scheme
        })

    return combined


def main(question_pdf_path, mark_scheme_pdf_path, output_json_path):
    # Extract text from both PDFs
    print("Extracting questions...")
    question_text = extract_text_only(question_pdf_path, is_question_paper=True)

    print("Extracting marking scheme...")
    mark_scheme_text = extract_text_only(mark_scheme_pdf_path, is_question_paper=False)

    # Define keywords (tweak depending on actual PDF style)
    question_keywords = ["1", "2", "3", "Section", "Question"]
    mark_keywords = ["Accept", "Award", "Mark", "1 mark", "Answers", "Q"]

    # Chunk into blocks
    print("Chunking questions...")
    question_chunks = chunk_by_keywords(question_text, question_keywords)

    print("Chunking mark scheme...")
    mark_chunks = chunk_by_keywords(mark_scheme_text, mark_keywords)

    # Combine into structured JSON
    print("Combining...")
    combined_data = to_json_format(question_chunks, mark_chunks)

    # # Save
    # with open(output_json_path, "w", encoding="utf-8") as f:
    #     json.dump(combined_data, f, indent=4, ensure_ascii=False)

    print(f"Done! Output saved to {output_json_path}")


# === RUN THIS ===
if __name__ == "__main__":
    question_pdf = "671731-june-2023-question-paper-21.pdf"         # Replace with your file
    mark_scheme_pdf = "671727-june-2023-mark-scheme-paper-21.pdf"      # Replace with your file
    output_file = "cambridge_output.json"

    main(question_pdf, mark_scheme_pdf, output_file)
