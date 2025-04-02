import requests
import json

import pywhatkit as pwk
from typing import List, Dict

import keyboard

from datetime import datetime
import time

import re

from pywhatkit.core.exceptions import InternetException


def get_data_from_url(url: str) -> List[Dict]:
    """
    Gets data from given url
    :param url: the website url
    :type url: str
    :return: list with dictionaries containing data from given url
    :rtype: List[Dict]
    """
    page = requests.get(url)

    start_index = page.text.find('"name":"כניסת שבת ירושלים" ,')
    end_index = page.text.find("</script>", start_index)
    parse_data = '[' + page.text[start_index - 78: end_index - 5]
    return json.loads(parse_data)


def parse_list_data(data: List[Dict]) -> None:
    """
    Parses data from given list
    :param data: the data to parse
    :type data: List[Dict]
    :return: None.
    :rtype: None
    """
    final_text = f"*כניסת שבת {data[0]['startDate'].split()[0]}*\n\n"
    for city in data:
        fixed_name = " ".join(city['name'].split()[2:])

        fixed_start_time = city["startDate"].split()[1][:-3]
        fixed_end_time = city["endDate"].split()[1][:-3]

        final_text += f'*{fixed_name}*\n'
        final_text += f'כניסת שבת: {fixed_start_time}\n'
        final_text += f'יציאת שבת: {fixed_end_time}\n\n'

    send_time = {
        'hour': int(data[0]["startDate"].split()[1][:-3].split(':')[0]) - 2,
        'min': int(data[0]["startDate"].split()[1][:-3].split(':')[1])
    }

    send_whatsapp_message(final_text, send_time)


def close_tabs(numbers_length: int) -> None:
    """
    Closes tabs
    :param numbers_length: the number of tabs
    :type numbers_length: int
    :return: None.
    :rtype: None
    """
    for _ in range(numbers_length):
        keyboard.press_and_release('ctrl+w')
        time.sleep(1)
        keyboard.press_and_release('enter')


def send_whatsapp_message(message: str, send_time: Dict) -> None:
    """
    Sends whatsapp message
    :param send_time: the time to send the message
    :type send_time: Dict
    :param message: the message to send
    :type message: str
    :return: None.
    :rtype: None
    """
    # pwk.sendwhatmsg(phone_number, message, send_time['hour'], send_time['min'])
    phone_numbers = get_phone_numbers()
    for phone_number in phone_numbers:
        if phone_number == '':
            continue
        try:
            pwk.sendwhatmsg(phone_number, message, datetime.now().hour, datetime.now().minute+2, 32)
        except InternetException:
            exit('You Are Not Connected!')
        print("Message Sent!")

    time.sleep(10)
    close_tabs(len(phone_numbers))


def validate_phone_number(phone_number: str) -> bool:
    """
    Validates phone number
    :param phone_number: the phone number to validate
    :type phone_number: str
    :return: Valid or not
    :rtype: bool
    """
    pattern = re.compile(r"^\+972(-)?(([23489]\d{7})|5[0-9]\d{7})$")
    match = re.search(pattern, phone_number)
    if match:
        return True
    return False


def add_phone_number() -> None:
    """
    Adds phone number to database
    :return: None.
    :rtype: None
    """
    name = input("Enter your name: ")
    phone_number = input("Enter your phone number with prefix (example: +972500000000): ")
    if phone_number == '':
        return

    if not validate_phone_number(phone_number):
        exit('Invalid Phone Number')

    with open("phone_numbers.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        if phone_number not in data:
            data.update({phone_number: name})
        else:
            exit('Phone Number Already Exists')

    with open("phone_numbers.json", "w", encoding="utf-8") as file:
        json.dump(data, file)


def get_phone_numbers() -> List:
    """
    Gets phone numbers from database
    :return: the phone numbers
    :rtype: List
    """
    with open("phone_numbers.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        return data.keys()


def main() -> None:
    """
    The main function of the program.
    :return: None.
    :rtype: None
    """
    add_phone_number()
    done_data = datetime.now().date()
    done = False
    while True:
        if datetime.now().weekday() != 4:  # Works only on Friday (4)
            print('bad day')
            if done_data != datetime.now().date():
                print('reset')
                done = False
            continue
        if done:
            continue
        done_data = datetime.now().date()
        done = True
        try:
            data_in_json = get_data_from_url('https://www.kipa.co.il/%D7%9B%D7%A0%D7%99%D7%A1%D7%AA-%D7%A9%D7%91%D7%AA/')
        except requests.exceptions.ConnectionError:
            exit('You Are Not Connected!')

        parse_list_data(data_in_json)

        print("Done!")


if __name__ == '__main__':
    main()
