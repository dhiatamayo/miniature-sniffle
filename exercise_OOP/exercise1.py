class Vehicle:
    color = "White"
    
    def __init__(self, name, maxSpeed, mileage):
        self.name = name
        self.maxSpeed = maxSpeed
        self.mileage = mileage
    
    def seating_capacity(self, capacity):
        return f"The seating capacity of a {self.name} is {capacity} passengers"
    
    def fare(self):
        return self.capacity * 100
    
    def print_result(self):
        print("Color: {}, Vehicle Name: {}, Speed: {}, Mileage: {}".format(Vehicle.color, self.name, self.maxSpeed, self.mileage))

class Bus(Vehicle):
    capacity = 50
    
    def seating_capacity(self, capacity=50):
        return super().seating_capacity(capacity)
    
    def fare(self):
        exst_fare = super().fare()
        exst_fare *= 1.1
        return exst_fare

class Car(Vehicle):
    pass



bus1 = Bus("Rosalia", 100, 1410)
car1 = Car("Avanza", 160, 142100)
#print("Total bus fare is: {}".format(bus1.fare()))
print(isinstance(bus1, Vehicle))