from datetime import datetime
import uuid

class Traveller:
    def __init__(self, first_name, last_name, birthday, gender, street, house_number, zip_code,
                 city, email, mobile_phone, driving_license):
        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday
        self.gender = gender
        self.street = street
        self.house_number = house_number
        self.zip_code = zip_code
        self.city = city
        self.email = email
        self.mobile_phone = mobile_phone
        self.driving_license = driving_license

        self.registration_date = datetime.now().strftime('%Y-%m-%d')
        self.traveller_id = str(uuid.uuid4())[:10]  # Or a custom ID generator

    def as_dict(self):
        return {
            "traveller_id": self.traveller_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "birthday": self.birthday,
            "gender": self.gender,
            "street": self.street,
            "house_number": self.house_number,
            "zip_code": self.zip_code,
            "city": self.city,
            "email": self.email,
            "mobile_phone": self.mobile_phone,
            "driving_license": self.driving_license,
            "registration_date": self.registration_date
        }
