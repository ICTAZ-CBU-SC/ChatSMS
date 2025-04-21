import pdfplumber
import json
import re

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


def clean_text(text):
    """
    Removes unwanted lines from the text. E.g. page number, provision for students to answer, etc
    """
    if not text:
        return ""

    cleaned_lines = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue

        # Skip lines containing specific patterns
        if any([
            "© UCLES" in line,
            "5090/21/m/j/23" in line,
            "cambridge o level" in line.lower(),
            "BLANK PAGE" in line.upper(),
            "turn over" in line.lower(),
            "Fig. " in line,
            "figure" in line.lower(),
        ]): 
            continue

        if re.search(r"\[\s*total\s*:\s*\d+\s*\]", line, re.IGNORECASE):
            continue
        if re.search(r"\[\s*\d+\s*\]", line, re.IGNORECASE):
            continue
        if re.search(r"\s*\d+\s*", line, re.IGNORECASE):
            continue

        # Skip table-related instructions or table headings
        if "Complete Table" in line or "Table " in line:
            continue

        # Skip lines that are dotted lines or mostly dots
        if "...." in line or line.count(".") > len(line) * 0.3:
            continue

        # Remove answer lines (dots)
        line = re.sub(r'\.{3,}', '', line)

        # If after removing dots the line is empty, skip it
        if not line.strip():
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def extract_questions(question_pdf_path: str, max_images: int = 2) -> str:
    """
    Extracts text from a PDF, skipping pages with too many images (like diagrams).
    """
    text_pages = []
    at_beginning_pages = True
    with pdfplumber.open(question_pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            # Skip if page has too many images (likely a diagram-heavy page)
            if len(page.images) > max_images:
                print(f"Skipping page {i + 1} due to many images.")
                continue

            # Extract text with tighter tolerances to preserve formatting
            text = page.extract_text(x_tolerance=1, y_tolerance=1)
            if not text or not text.strip():
                print(f"Page {i + 1} has no text or is whitespace only.")
                continue

            # Process for beginning pages
            if at_beginning_pages:
                found_question_start = False
                for line in text.split("\n"):
                    if line.startswith("1 ") and line[2:6].lower() != "hour":
                        at_beginning_pages = False
                        found_question_start = True
                        break
                if at_beginning_pages and not found_question_start:
                    print(f"Skipping beginning page {i + 1}")
                    continue

            # Apply cleaning function
            cleaned_text = clean_text(text)
            if not cleaned_text.strip():
                print(f"Page {i + 1} is empty after cleaning.")
                continue

            print(f"Cleaned page {i + 1}: \n{cleaned_text}\n\n")
            text_pages.append(cleaned_text)

    final_text = "\n\n".join(text_pages)
    with open("extracted_questions.txt", "w", encoding="utf-8") as f:
        f.write(final_text)

    return final_text


def extract_answers(mark_scheme_pdf_path: str):
    text_pages = []
    document_lines = []

    at_beginning_pages = True

    with pdfplumber.open(mark_scheme_pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            page_lines = page_text.split("\n")

            # Skip if at beginning pages
            if at_beginning_pages:
                for line_index, line in enumerate(page_lines):

                    if "Question Answer Marks Guidance" in line:
                        at_beginning_pages = False
                        break
                if at_beginning_pages:
                    continue

            for line in page_lines:
                line = process_marking_scheme_line(line)
                if line:
                    document_lines.append(line)

    groups = extract_all_groups(document_lines)
    for group in groups:
        print("------------------------------------------------------")
        print(process_answer_lines(group))
        # for line in group:
        #     print(line)

    # for line in document_lines:
    #     print(line)

    return "\n".join(text_pages)


def process_answer_lines(lines: list[str]):
    if len(lines) == 0:
        return None

    lines = lines.copy()
    question_id = lines[0].split(" ")[0]
    lines[0] = lines[0][len(question_id):].strip()

    cleaned_lines = []
    for i in range(len(lines)):
        line_split = lines[i].split()[:-1]
        if ";" in line_split:
            line_split = line_split[:line_split.index(";")]
        lines[i] = " ".join(line_split)

        if not (lines[i].lower().startswith("any") and "from" in lines[i].lower()):
            cleaned_lines.append(lines[i])

    answer_text = ". ".join(cleaned_lines)
    return {question_id: answer_text}


def extract_all_groups(lines: list[str]) -> list[list[str]]:
    """
    Splits the input lines into groups where each group starts with a line
    that begins with a numeric+parentheses pattern (e.g., 1(a), 2(b)(ii), etc.).

    Each group includes all lines up until the next match.
    """
    pattern = re.compile(r"^\d+(\([a-zA-Z]+\))+")
    groups = []
    current_group = []

    for line in lines:
        if pattern.match(line):
            if current_group:
                groups.append(current_group)
            current_group = [line]
        else:
            if current_group:
                current_group.append(line)
            else:
                # If content exists before any matching pattern, treat it as its own group
                current_group = [line]

    if current_group:
        groups.append(current_group)

    return groups


def process_marking_scheme_line(line: str):
    def starts_with_subject_code(s: str) -> bool:
        """
        Returns True if the string starts with the format 'YYYY/MM' where:
        - YYYY is a 4-digit number
        - MM is a 2-digit number
        """
        return bool(re.match(r"^\d{4}/\d{2}", s))

    # print(line.startswith("Question Answer Marks Guidance"), line)
    if any([
        starts_with_subject_code(line),
        line.startswith("PUBLISHED"),
        line.startswith("Question Answer Marks Guidance"),
        line.startswith("©"),
        line.startswith("Max")
    ]):
        return ""

    return line


# def main(question_pdf_path, mark_scheme_pdf_path, output_json_path):
#     # Extract text from both PDFs
#     print("Extracting questions...")
#     question_text = extract_text_only(question_pdf_path, is_question_paper=True)
#
#     print("Extracting marking scheme...")
#     mark_scheme_text = extract_text_only(mark_scheme_pdf_path, is_question_paper=False)
#
#     # Define keywords (tweak depending on actual PDF style)
#     question_keywords = ["1", "2", "3", "Section", "Question"]
#     mark_keywords = ["Accept", "Award", "Mark", "1 mark", "Answers", "Q"]
#
#     # Chunk into blocks
#     print("Chunking questions...")
#     question_chunks = chunk_by_keywords(question_text, question_keywords)
#
#     print("Chunking mark scheme...")
#     mark_chunks = chunk_by_keywords(mark_scheme_text, mark_keywords)
#
#     # Combine into structured JSON
#     print("Combining...")
#     combined_data = to_json_format(question_chunks, mark_chunks)
#
#     # # Save
#     # with open(output_json_path, "w", encoding="utf-8") as f:
#     #     json.dump(combined_data, f, indent=4, ensure_ascii=False)
#
#     print(f"Done! Output saved to {output_json_path}")


# === RUN THIS ===
if __name__ == "__main__":
    question_pdf = "671731-june-2023-question-paper-21.pdf"  # Replace with your file
    mark_scheme_pdf = "671727-june-2023-mark-scheme-paper-21.pdf"  # Replace with your file

    # extract_questions(question_pdf)
    extract_answers(mark_scheme_pdf)

    # output_file = "cambridge_output.json"
    # main(question_pdf, mark_scheme_pdf, output_file)
