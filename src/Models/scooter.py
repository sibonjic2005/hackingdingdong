from datetime import datetime
import uuid

class Scooter:
    def __init__(self, brand, model, serial_number, top_speed, battery_capacity,
                 state_of_charge, target_soc_min, target_soc_max, latitude,
                 longitude, out_of_service, mileage, last_maintenance_date):
        
        self.scooter_id = str(uuid.uuid4())[:10]  # Can be customized
        self.brand = brand
        self.model = model
        self.serial_number = serial_number
        self.top_speed = top_speed
        self.battery_capacity = battery_capacity
        self.state_of_charge = state_of_charge
        self.target_soc_min = target_soc_min
        self.target_soc_max = target_soc_max
        self.latitude = latitude
        self.longitude = longitude
        self.out_of_service = out_of_service
        self.mileage = mileage
        self.last_maintenance_date = last_maintenance_date
        self.in_service_date = datetime.now().strftime('%Y-%m-%d')

    def as_dict(self):
        return {
            "scooter_id": self.scooter_id,
            "brand": self.brand,
            "model": self.model,
            "serial_number": self.serial_number,
            "top_speed": self.top_speed,
            "battery_capacity": self.battery_capacity,
            "state_of_charge": self.state_of_charge,
            "target_soc_min": self.target_soc_min,
            "target_soc_max": self.target_soc_max,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "out_of_service": self.out_of_service,
            "mileage": self.mileage,
            "last_maintenance_date": self.last_maintenance_date,
            "in_service_date": self.in_service_date
        }
