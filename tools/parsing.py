import re

def _parse_numeric(value: str) -> int:
    """Extract an integer from user-friendly strings like '500', '500+', '$150,000' or '150000'."""
    if not value:
        return 0
    s = str(value)
    digits = re.findall(r"\d+", s.replace(',', ''))
    if not digits:
        return 0
    # take the first large number
    num = int(digits[0])
    # if the string included a trailing + it probably meant "at least"
    return num


