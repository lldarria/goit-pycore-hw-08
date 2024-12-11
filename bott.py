import pickle
from datetime import datetime, timedelta
from collections import UserDict
import re
import os

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value.strip():
            raise ValueError("Name cannot be empty.")
        super().__init__(value.strip())

class Phone(Field):
    def __init__(self, value):
        if not self._validate(value):
            raise ValueError("Phone number must be exactly 10 digits.")
        super().__init__(value)

    @staticmethod
    def _validate(value):
        return bool(re.fullmatch(r"\d{10}", value))

class Birthday(Field):
    def __init__(self, value):
        if not self.validate_birthday(value):
            raise ValueError("Date must be in format DD.MM.YYYY.")
        super().__init__(value)

    @staticmethod
    def validate_birthday(value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
            return True
        except ValueError:
            return False

class Record:
    def __init__(self, name: Name, phone: Phone = None, birthday: Birthday = None):
        self.name = name
        self.phones = []
        if phone:
            self.phones.append(phone)
        self.birthday = birthday

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for idx, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[idx] = Phone(new_phone)
                return
        raise ValueError(f"Phone number {old_phone} not found.")

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = datetime.now()
        bday = datetime.strptime(self.birthday.value, "%d.%m.%Y").replace(year=today.year)
        if bday < today:
            bday = bday.replace(year=today.year + 1)
        return (bday - today).days

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        birthday = self.birthday.value if self.birthday else "N/A"
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"
    
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name.strip())

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError(f"Contact {name} not found.")

    def upcoming_birthdays(self, days=7):
        today = datetime.now()
        upcoming = []
        for record in self.data.values():
            if record.birthday:
                bday = datetime.strptime(record.birthday.value, "%d.%m.%Y").replace(year=today.year)
                if bday < today:
                    bday = bday.replace(year=today.year + 1)
                if 0 <= (bday - today).days < days:
                    upcoming.append(record)
        return upcoming

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook() 

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f"Error: {str(e)}"
    return wrapper

@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        return "Error: Provide both name and phone number."
    name, phone = args[0], args[1]
    record = book.find(name)
    if not record:
        record = Record(Name(name))
        book.add_record(record)
    record.add_phone(phone)
    return f"Contact '{name}' added or updated."

@input_error
def change_contact(args, book: AddressBook):
    if len(args) < 3:
        return "Error: Provide name, old phone, and new phone."
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return f"Phone for '{name}' updated."
    return f"Contact '{name}' not found."

@input_error
def show_phone(args, book: AddressBook):
    if len(args) < 1:
        return "Error: Provide a contact name."
    name = args[0]
    record = book.find(name)
    if record:
        phones = ", ".join(phone.value for phone in record.phones)
        return f"{name}: {phones}"
    return f"Contact '{name}' not found."

def show_all(book: AddressBook):
    if not book.data:
        return "No contacts found."
    return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book: AddressBook):
    if len(args) < 2:
        return "Error: Provide a name and birthday in DD.MM.YYYY format."
    name, birthday = args[0], args[1]
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday for '{name}' added."
    return f"Contact '{name}' not found."

@input_error
def show_birthdays(book: AddressBook, days=7):
    upcoming = book.upcoming_birthdays(days)
    if not upcoming:
        return "No upcoming birthdays."
    return "\n".join(f"{record.name.value}: {record.birthday.value}" for record in upcoming)

def parse_input(user_input):
    parts = user_input.strip().split(" ", 1)
    cmd = parts[0].lower()
    args = parts[1].split() if len(parts) > 1 else []
    return cmd, args

def main():
    FILENAME = "addressbook.pkl"
    book = load_data(FILENAME) 

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book, FILENAME)  
            print("Data saved. Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "birthdays":
            print(show_birthdays(book))

        else:
            print("Invalid command.")
    
    save_data(book)

if __name__ == "__main__":
    main()