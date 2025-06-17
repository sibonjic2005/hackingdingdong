import re
from datetime import datetime

def validate_zip(zip_code: str) -> bool:
    return bool(re.fullmatch(r"\d{4}[A-Z]{2}", zip_code))

def validate_mobile(mobile: str) -> bool:
    return bool(re.fullmatch(r"\d{8}", mobile))  # Only 8 digits entered by user

def validate_driving_license(license_num: str) -> bool:
    return bool(re.fullmatch(r"([A-Z]{2}\d{7}|[A-Z]{1}\d{7})", license_num))

def validate_email(email: str) -> bool:
    return bool(re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email))

def validate_birthday(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_gender(gender):
    return gender.lower() in ["male", "female"]

def validate_username(username: str) -> bool:
    return bool(re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_.'']{7,9}", username.lower()))

def validate_password(password: str) -> bool:
    # Length 12–30, at least one upper, lower, digit, special char
    return (
        12 <= len(password) <= 30 and
        re.search(r"[a-z]", password) and
        re.search(r"[A-Z]", password) and
        re.search(r"\d", password) and
        re.search(r"[~!@#$%&_+=`\|\(\)\{\}\[\]:;'<>,.?/-]", password)
    )
