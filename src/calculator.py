class Calculator:
    def add(self, a, b):
        return a + b

    def divide(self, a, b):
        try:
            return a / b
        except ZeroDivisionError:
            print("Cannot divide by zero")
            return None
