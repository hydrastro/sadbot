"""Math rizz bot command"""

import random
from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.functions import safe_cast
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT

def fuck_you():
    return "What's the Riemann integral from 0 to +infinity of sin(x)/x in dx?", "pi/2", "fuck you lmao"

def double_and_halve():
    num1 = random.choice(range(10, 100, 2))  # Ensure num1 is even for easy halving
    num2 = random.randint(10, 99)  # Adjusted to have at least two digits
    answer = num1 * num2
    equation_str = f"{num1} x {num2}"
    method_notes = f"Halve {num1} and double {num2}, then multiply. Example: {equation_str} = ({num1//2} x 2) x ({num2} x 2) = {num1//2} x {num2*2} = {answer}"
    return equation_str, answer, method_notes

def round_and_compensate():
    num1 = random.randint(10, 99)  # Already two digits
    num2 = random.randint(10, 99)  # Adjusted to have at least two digits
    answer = num1 * num2
    rounded_num = num1 + (10 - (num1 % 10))
    compensation = rounded_num - num1
    equation_str = f"{num1} x {num2}"
    method_notes = f"Round {num1} to {rounded_num}, multiply, then subtract the compensation. Example: {equation_str} = ({rounded_num} x {num2}) - ({compensation} x {num2}) = {rounded_num * num2} - {compensation * num2} = {answer}"
    return equation_str, answer, method_notes

def distributive_property():
    num1 = random.randint(10, 99)  # Already two digits
    num2 = (random.randint(10, 50) + random.randint(10, 50))  # Adjusted to have at least two digits
    answer = num1 * num2
    equation_str = f"{num1} x {num2}"
    method_notes = f"Apply distributive property for multiplication over addition. Example: {equation_str} = {num1} x ({num2//2} + {num2//2}) = {num1} x {num2//2} + {num1} x {num2//2} = {num1*(num2//2)} + {num1*(num2//2)} = {answer}"
    return equation_str, answer, method_notes

def bridge_to_ten():
    num1 = random.randint(10, 99)  # Adjusted to have at least two digits
    num2 = random.randint(10, 99)  # Adjusted to have at least two digits
    answer = num1 + num2
    bridge = 10 - (num1 % 10)
    equation_str = f"{num1} + {num2}"
    method_notes = f"For addition, bridge numbers to the nearest ten. Example: {equation_str} = {num1} + {bridge} + ({num2} - {bridge}) = {num1 + bridge} + {num2 - bridge} = {answer}"
    return equation_str, answer, method_notes

def multiply_by_11():
    num1 = random.randint(10, 99)
    answer = num1 * 11
    sum_digits = (num1 // 10) + (num1 % 10)
    equation_str = f"{num1} x 11"
    method_notes = f"To multiply a two-digit number by 11, add the two digits and place the sum between them. Example: {equation_str} = {num1 // 10}{sum_digits}{num1 % 10} = {answer}"
    return equation_str, answer, method_notes

def near_doubles():
    num1 = random.randint(10, 90)  # Adjusted to have at least two digits
    num2 = num1 + 1  # ensuring numbers are near doubles
    answer = num1 + num2
    equation_str = f"{num1} + {num2}"
    method_notes = f"Double {num1} and then adjust. Example: {equation_str} = double {num1} + 1 = {num1*2 + 1} = {answer}"
    return equation_str, answer, method_notes

def compensation_strategy():
    num1 = random.randint(10, 99)
    num2 = random.randint(10, 99)  # Adjusted to have at least two digits
    answer = num1 + num2
    rounded_num = num1 + (10 - (num1 % 10))
    compensation = rounded_num - num1
    equation_str = f"{num1} + {num2}"
    method_notes = f"Round {num1} up to {rounded_num}, then compensate by subtracting. Example: {equation_str} = ({rounded_num} + {num2}) - {compensation} = {rounded_num + num2} - {compensation} = {answer}"
    return equation_str, answer, method_notes

def repeated_doubling():
    num1 = random.randint(10, 25)  # Adjusted to have at least two digits
    num2 = random.choice([4, 8])
    answer = num1 * num2
    equation_str = f"{num1} x {num2}"
    if num2 == 4:
        method_notes = f"To multiply {num1} by 4, double it twice. Example: {equation_str} = double(double({num1})) = double({num1*2}) = {num1*2*2} = {answer}"
    else:
        method_notes = f"To multiply {num1} by 8, double it three times. Example: {equation_str} = double(double(double({num1}))) = double(double({num1*2})) = double({num1*2*2}) = {num1*2*2*2} = {answer}"
    return equation_str, answer, method_notes

def double_and_divide():
    num1 = random.randint(10, 200) * 5
    num2 = 5
    answer = num1 / num2
    equation_str = f"{num1} ÷ {num2}"
    method_notes = f"To divide {num1} by five mentally: Double {num1} to get {num1*2}, then divide by ten to get {answer}. Example: {equation_str} = {num1*2} ÷ 10 = {answer}"
    return equation_str, answer, method_notes

def subtract_in_parts():
    num1 = random.randint(10, 99)
    num2 = random.randint(10, 99)  # Adjusted to have at least two digits
    answer = num1 - num2
    ten_comp = 10 - (num1 % 10)
    equation_str = f"{num1} - {num2}"
    method_notes = f"First, subtract to the previous whole ten, then the rest. Example: {equation_str} = {num1} - {ten_comp} - ({num2 - ten_comp}) = {num1 - ten_comp} - {num2 - ten_comp} = {answer}"
    return equation_str, answer, method_notes

def counting_back_and_up():
    num1 = random.randint(10, 99)
    num2 = random.randint(10, 99)  # Adjusted to have at least two digits
    answer = num1 - num2
    equation_str = f"{num1} - {num2}"
    method_notes = f"Count up from {num2} to {num1}. Example: {equation_str} = {answer} by counting up from {num2} to {num1}."
    return equation_str, answer, method_notes

def thinking_addition():
    num1 = random.randint(10, 99)
    num2 = random.randint(10, 99)  # Adjusted to have at least two digits
    answer = num1 - num2
    equation_str = f"{num1} - {num2}"
    method_notes = f"Think of subtraction as finding the difference by adding up from {num2} to {num1}. Example: {equation_str} = {answer} by adding {answer} to {num2} to get {num1}."
    return equation_str, answer, method_notes

def splitting_for_addition():
    num1 = random.randint(30, 99)
    num2 = random.randint(30, 99)
    answer = num1 + num2
    equation_str = f"{num1} + {num2}"
    tens_num2 = (num2 // 10) * 10
    units_num2 = num2 % 10
    method_notes = f"Split {num2} into tens and units, then add. Example: {equation_str} = {num1} + ({tens_num2} + {units_num2}) = {num1 + tens_num2} + {units_num2} = {answer}"
    return equation_str, answer, method_notes

def adding_numbers_ending_in_9():
    num1 = random.randint(100, 999)
    num2 = random.randint(10, 99) + 9  # Ensure num2 ends in 9
    answer = num1 + num2
    equation_str = f"{num1} + {num2}"
    method_notes = f"Add the next number, then subtract 1. Example: {equation_str} = {num1} + ({num2 + 1} - 1) = {num1 + num2 + 1} - 1 = {answer}"
    return equation_str, answer, method_notes

def adding_11():
    num1 = random.randint(100, 999)
    answer = num1 + 11
    equation_str = f"{num1} + 11"
    method_notes = f"Add the tens, then add 1. Example: {equation_str} = {num1} + 10 + 1 = {num1 + 10} + 1 = {answer}"
    return equation_str, answer, method_notes

def rounding_up_to_nearest_ten():
    num1 = random.randint(30, 99)
    num2 = random.randint(30, 99)
    answer = num1 + num2
    equation_str = f"{num1} + {num2}"
    round_up_num1 = (num1 // 10 + 1) * 10
    round_up_num2 = (num2 // 10 + 1) * 10
    extra = (round_up_num1 - num1) + (round_up_num2 - num2)
    method_notes = f"Round up to the nearest ten, save the extras, then subtract. Example: {equation_str} = {round_up_num1} + {round_up_num2} - {extra} = {round_up_num1 + round_up_num2} - {extra} = {answer}"
    return equation_str, answer, method_notes

def generate_random_equation():
    # List of method functions
    methods = [
        double_and_halve, 
        round_and_compensate, 
        distributive_property, 
        bridge_to_ten, 
        multiply_by_11, 
        near_doubles, 
        compensation_strategy, 
        repeated_doubling, 
        double_and_divide, 
        subtract_in_parts, 
        counting_back_and_up, 
        thinking_addition,
        fuck_you, 
        splitting_for_addition, 
        adding_numbers_ending_in_9, 
        adding_11, 
        rounding_up_to_nearest_ten
    ]
    # Select a random mental math method function
    method_func = random.choice(methods)
    # Call the selected method function to generate the equation, answer, and method notes
    return method_func()

class MentalMathBotCommand(CommandInterface):
    """This is the Mental Math bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the mental math command"""
        return r"(!|\.)[Rr][Ii][Zz]{2}.*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Generates a random mental math equation"""
        if message is None or message.text is None:
            return None
        equation, answer, method_notes = generate_random_equation()
        reply_text = (
            f"Equation: {equation}\n"
            f"Answer: <span class='tg-spoiler'>{answer}\n</span>"
            f"Method Notes: <span class='tg-spoiler'>{method_notes}</span>"
        )
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text, reply_spoiler=True, reply_text_parse_mode="HTML")]

# Usage:
# equation, answer, method_notes = generate_random_equation()
# print(f"Equation: {equation}")
# print(f"Answer: {answer}")
# print(f"Method Notes: {method_notes}")
