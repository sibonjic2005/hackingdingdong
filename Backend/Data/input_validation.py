import re

def is_valid_zip(zip_code: str) -> bool:
    return bool(re.fullmatch(r"\d{4}[A-Z]{2}", zip_code))

def is_valid_mobile(mobile: str) -> bool:
    return bool(re.fullmatch(r"\d{8}", mobile))  # Only 8 digits entered by user

def is_valid_license(license_num: str) -> bool:
    return bool(re.fullmatch(r"([A-Z]{2}\d{7}|[A-Z]{1}\d{7})", license_num))

def is_valid_email(email: str) -> bool:
    return bool(re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email))

def is_valid_username(username: str) -> bool:
    return bool(re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_.'']{7,9}", username.lower()))

def is_valid_password(password: str) -> bool:
    # Length 12–30, at least one upper, lower, digit, special char
    return (
        12 <= len(password) <= 30 and
        re.search(r"[a-z]", password) and
        re.search(r"[A-Z]", password) and
        re.search(r"\d", password) and
        re.search(r"[~!@#$%&_+=`\|\(\)\{\}\[\]:;'<>,.?/-]", password)
    )
