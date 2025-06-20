from datetime import datetime

class Scooter:
    def __init__(self, brand, model, serial_number, top_speed, battery_capacity,
                 state_of_charge, target_soc_min, target_soc_max, location_lat,
                 location_long, out_of_service, mileage, last_maintenance_date):
        
        self.brand = brand
        self.model = model
        self.serial_number = serial_number
        self.top_speed = top_speed
        self.battery_capacity = battery_capacity
        self.state_of_charge = state_of_charge
        self.target_soc_min = target_soc_min
        self.target_soc_max = target_soc_max
        self.location_lat = location_lat
        self.location_long = location_long
        self.out_of_service = out_of_service
        self.mileage = mileage
        self.last_maintenance_date = last_maintenance_date
        self.in_service_date = datetime.now().strftime('%Y-%m-%d')

    def as_dict(self):
        return {
            "brand": self.brand,
            "model": self.model,
            "serial_number": self.serial_number,
            "top_speed": self.top_speed,
            "battery_capacity": self.battery_capacity,
            "state_of_charge": self.state_of_charge,
            "target_soc_min": self.target_soc_min,
            "target_soc_max": self.target_soc_max,
            "location_lat": self.location_lat,
            "location_long": self.location_long,
            "out_of_service": self.out_of_service,
            "mileage": self.mileage,
            "last_maintenance_date": self.last_maintenance_date,
            "in_service_date": self.in_service_date
        }
