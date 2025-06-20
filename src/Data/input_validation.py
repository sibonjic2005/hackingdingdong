import re
from datetime import datetime

def validate_zip(zip_code: str) -> bool:
    return bool(re.fullmatch(r"\d{4}[A-Z]{2}", zip_code))

def validate_mobile(mobile: str) -> bool:
    return bool(re.fullmatch(r"\d{10}", mobile))

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
    if len(password) < 12 or len(password) > 30:
        print("❌ Password must be between 12 and 30 characters.")
        return False
    if not re.search(r"[a-z]", password):
        print("❌ Password must contain at least one lowercase letter.")
        return False
    if not re.search(r"[A-Z]", password):
        print("❌ Password must contain at least one uppercase letter.")
        return False
    if not re.search(r"\d", password):
        print("❌ Password must contain at least one digit.")
        return False
    if not re.search(r"[~!@#$%&_+=`\|\(\)\{\}\[\]:;'<>,.?/-]", password):
        print("❌ Password must contain at least one special character.")
        return False
    return True
def validate_serial_number(serial: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9]{10,17}", serial))

def validate_soc(soc: int) -> bool:
    return 0 <= soc <= 100

def validate_lat(lat: float) -> bool:
    return 51,85 <= lat <= 52,00

def validate_long(lon: float) -> bool:
    return 4,35 <= lon <= 4,55

def validate_iso_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_positive_float(val: float) -> bool:
    return val >= 0,0

def validate_positive_int(val: int) -> bool:
    return val >= 0
