class CoffeeMachine:
    def __init__(self):
        self.state = "Idle"
        self.water_level = 100
        self.beans_level = 100

    def transition_to_idle(self):
        self.state = "Idle"
        print("Transitioned to Idle state.")

    def transition_to_brewing(self):
        self.state = "Brewing"
        print("Transitioned to Brewing state.")

    def transition_to_serving(self):
        self.state = "Serving"
        print("Transitioned to Serving state.")

    def transition_to_maintenance(self):
        self.state = "Maintenance"
        print("Transitioned to Maintenance state.")

    def handle_event(self, event):
        if self.state == "Idle":
            if event == "select_coffee_type":
                if self.water_level >= 20 and self.beans_level >= 10:
                    self.transition_to_brewing()
                else:
                    self.transition_to_maintenance()
        elif self.state == "Brewing":
            # Simulating brewing process
            print("Brewing coffee...")
            self.transition_to_serving()
        elif self.state == "Serving":
            print("Coffee served.")
            self.transition_to_idle()
        elif self.state == "Maintenance":
            if event == "refill_water_and_beans":
                self.water_level = 100
                self.beans_level = 100
                print("Water and beans refilled.")
                self.transition_to_idle()


# Testing the FSM
coffee_machine = CoffeeMachine()
print("Initial state:", coffee_machine.state)
coffee_machine.handle_event("select_coffee_type")
print("Current state:", coffee_machine.state)
coffee_machine.handle_event("refill_water_and_beans")
print("Current state:", coffee_machine.state)
