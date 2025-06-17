from Models.traveller import Traveller
from Data.traveller_db import insert_traveller
from Data.input_validation import *

def create_traveller_from_input():
    first_name = input("First name: ")
    last_name = input("Last name: ")
    birthday = input("Birthday (YYYY-MM-DD): ")
    while not validate_birthday(birthday):
        birthday = input("Invalid date. Try again (YYYY-MM-DD): ")

    gender = input("Gender (male/female): ")
    while not validate_gender(gender):
        gender = input("Invalid gender. Enter 'male' or 'female': ")

    street = input("Street: ")
    house_number = input("House number: ")
    zip_code = input("ZIP code (e.g. 1234AB): ")
    while not validate_zip(zip_code):
        zip_code = input("Invalid ZIP. Try again: ")

    city = input("City: ")
    email = input("Email: ")
    mobile_phone = input("Mobile (start with 06, 10 digits total): ")
    while not validate_mobile(mobile_phone):
        mobile_phone = input("Invalid mobile. Try again: ")

    driving_license = input("Driving license (X/DDDDDDD or XXDDDDDDD): ")
    while not validate_driving_license(driving_license):
        driving_license = input("Invalid license. Try again: ")

    traveller = Traveller(first_name, last_name, birthday, gender, street,
                          house_number, zip_code, city, email,
                          mobile_phone, driving_license)

    insert_traveller(traveller)
    print("Traveller registered successfully!")
