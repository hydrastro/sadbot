import random

# Define mental math methods, notes, and rules for generating equations
mental_math_methods = {
    "double_and_halve": {
        "notes": "Halve one number (preferably even) and double the other, then multiply. Example: 24 x 5 = (12 x 2) x (5 x 2) = 12 x 10 = 120",
        "generate_equation": lambda: (random.randint(10, 99)*2, random.randint(10, 99)//2)
    },
    "round_and_compensate": {
        "notes": "Round one number up or down to make multiplication easier, then adjust the product. Example: 47 x 9 = (47 x 10) - (47 x 1) = 470 - 47 = 423",
        "generate_equation": lambda: (random.randint(10, 99), random.randint(1, 10))
    },
    "distributive_property": {
        "notes": "Apply distributive property for multiplication over addition or subtraction. Example: 10 x (24 + 16) = 10 x 24 + 10 x 16 = 240 + 160 = 400",
        "generate_equation": lambda: (random.randint(10, 99), random.randint(10, 99) + random.randint(10, 99))
    },
    "bridge_to_ten": {
        "notes": "For addition, bridge numbers to the nearest ten. Example: 47 + 8 = 47 + 3 + 5 = 50 + 5 = 55",
        "generate_equation": lambda: (random.randint(1, 9), random.randint(1, 9))
    },
    "multiply_by_11": {
        "notes": "To multiply a two-digit number by 11, add the two digits and place the sum between them. Example: 72 x 11 = 792",
        "generate_equation": lambda: (random.randint(10, 99), 11)
    },
    "near_doubles": {
        "notes": "Double a number and then adjust. Example: 7 + 8 = double 7 + 1 = 15",
        "generate_equation": lambda: (random.randint(1, 9), random.randint(1, 9))
    },
    "compensation_strategy": {
        "notes": "Round the second number up to the closest ten, then compensate by subtracting. Example: 47 + 19 = (47 + 20) - 1 = 67 - 1 = 66",
        "generate_equation": lambda: (random.randint(10, 99), random.randint(1, 9))
    },
    "repeated_doubling": {
        "notes": "To multiply a number by 4 or 8, double it twice or three times respectively. Example: 12 x 4 = double(double(12))",
        "generate_equation": lambda: (random.randint(1, 9), random.choice([4, 8]))
    },
    # ... add more methods as needed
}

def generate_random_equation():
    # Select a random mental math method
    method_key = random.choice(list(mental_math_methods.keys()))
    method = mental_math_methods[method_key]
    
    # Generate a random equation based on the selected method
    equation = method["generate_equation"]()
    
    # Return equation, method notes, and the answer
    if method_key in ["double_and_halve", "round_and_compensate", "distributive_property", "multiply_by_11", "repeated_doubling"]:
        answer = equation[0] * equation[1]
    elif method_key in ["bridge_to_ten", "near_doubles", "compensation_strategy"]:
        answer = equation[0] + equation[1]
    # ... add more cases as needed
    
    return f"{equation[0]} x {equation[1]}", answer, method["notes"]

# Usage:
# equation, answer, method_notes = generate_random_equation()
# print(f"Equation: {equation}")
# print(f"Answer: {answer}")
# print(f"Method Notes: {method_notes}")
