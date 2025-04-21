import re

import pdfplumber


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
    # for group in groups:
    #     print("------------------------------------------------------")
    #     print(process_answer_lines(group))
    #     # for line in group:
    #     #     print(line)

    # for line in document_lines:
    #     print(line)
    final = {}
    for group in groups:
        final.update(process_answer_lines(group))
    return final


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


if __name__ == "__main__":
    question_pdf = "671731-june-2023-question-paper-21.pdf"  # Replace with your file
    mark_scheme_pdf = "671727-june-2023-mark-scheme-paper-21.pdf"  # Replace with your file

    # extract_questions(question_pdf)
    answers = extract_answers(mark_scheme_pdf)

    [print(f"{k}:\t{v}") for k, v in answers.items()]
