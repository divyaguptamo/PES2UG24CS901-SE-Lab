def format_course_code(code):
    """
    Formats 'cs 301' as 'CS301'.
    Expects exactly two words: an alphabetic department and a numeric course number.
    Returns None for any input that is not a valid course code instead of crashing.
    """
    if not isinstance(code, str):
        return None

    words = code.split()
    if len(words) != 2:
        return None

    dept, number = words
    if not (dept.isascii() and dept.isalpha()):
        return None
    if not (number.isascii() and number.isdigit()):
        return None

    return dept.upper() + number


def total_credits(text):
    """
    Adds up comma-separated course credits.
    Every value must be a non-negative whole number (spaces around values are allowed).
    Returns None for any input that is not a valid credit list instead of crashing.
    """
    if not isinstance(text, str) or not text.strip():
        return None

    total = 0
    for credit in text.split(','):
        credit = credit.strip()
        if not (credit.isascii() and credit.isdigit()):
            return None          # empty entry, letters, decimals, signs, etc.
        if len(credit) > 3:
            return None          # unrealistically large credit value
        total += int(credit)
    return total


def parse_student_record(line):
    """
    Parses 'SRN|name|status' into a dictionary.
    Requires exactly three non-empty fields.
    Returns None for any input that is not a valid record instead of crashing.
    """
    if not isinstance(line, str):
        return None

    parts = [part.strip() for part in line.split('|')]
    if len(parts) != 3 or not all(parts):
        return None

    srn, name, status = parts
    return {"srn": srn.upper(),
            "name": name,
            "status": status.lower()}


def main():
    print("==== Running format_course_code ====")
    value = input("Enter a course code as DEPT NUMBER (e.g. cs 301): ")
    result = format_course_code(value)
    if result is None:
        print("Invalid course code. Expected format: DEPT NUMBER (e.g. cs 301)")
    else:
        print("Formatted course code:", result)

    print("\n==== Running total_credits ====")
    value = input("Enter course credits separated by commas (e.g. 4,3,4): ")
    result = total_credits(value)
    if result is None:
        print("Invalid credits. Expected whole numbers separated by commas (e.g. 4,3,4)")
    else:
        print("Total credits:", result)

    print("\n==== Running parse_student_record ====")
    value = input("Enter a student record as SRN|name|status (e.g. pes1ug23cs001|Asha|regular): ")
    result = parse_student_record(value)
    if result is None:
        print("Invalid student record. Expected format: SRN|name|status")
    else:
        print("Student record:", result)


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled.")
