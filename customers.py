import csv
import re
import os
from tabulate import tabulate


# _________________Customers Container____________

# Path to the CSV file that stores all customers.
CUSTOMERS_CSV = "customers.csv"

# Column names of customers.csv, defined in one place so that both
# DictReader and DictWriter always agree on the structure.
CUSTOMER_FIELDS = [
    "Customer ID",
    "First Name",
    "Last Name",
    "Phone",
    "Email",
    "Country",
    "City",
    "Street",
    "Street Number",
]


class Customer:
    # Class representing a single customer.

    def __init__(self, first_name, last_name, phone, email, country, city, street, street_number, customer_id=None):
        # If customer_id was passed keep it.
        # Otherwise, generate a new incremental one.
        self.customer_id = customer_id if customer_id else self.generate_id()

        # Normalize text fields: strip whitespace, capitalize each word.
        self.first_name = first_name.strip().title()
        self.last_name = last_name.strip().title()

        # Phone and email go through dedicated validators.
        self.phone = self.clean_phone(phone)
        self.email = self.clean_email(email)

        # Address fields.
        self.country = country.strip().title()
        self.city = city.strip().title()
        self.street = street.strip().title()
        self.street_number = street_number.strip()

    def generate_id(self):
        # If the CSV doesn't exist yet, this is the first customer.
        if not os.path.exists(CUSTOMERS_CSV):
            return 1

        max_id = 0
        with open(CUSTOMERS_CSV, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get("Customer ID"):
                    try:
                        current_id = int(row["Customer ID"])
                    except ValueError:
                        # Skip rows with malformed IDs instead of crashing.
                        continue
                    if current_id > max_id:
                        max_id = current_id

        return max_id + 1

    def clean_phone(self, phone):
        # Remove everything except digits and a leading '+'.
        cleaned = re.sub(r"[^\d+]", "", phone.strip())

        # A phone number must start with an optional '+' and contain 7-15 digits.
        if not re.search(r"^\+?\d{7,15}$", cleaned):
            raise ValueError("Invalid phone number (7-15 digits, optional leading '+')")

        return cleaned

    def clean_email(self, email):
        clean_email = email.strip().lower()

        # Email is optional: an empty string is allowed.
        if clean_email == "":
            return clean_email

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.search(pattern, clean_email):
            raise ValueError("Invalid email format")

        return clean_email

    def to_dict(self):
        # Convert the object to a dictionary for CSV writing and tabulate.
        return {
            "Customer ID": self.customer_id,
            "First Name": self.first_name,
            "Last Name": self.last_name,
            "Phone": self.phone,
            "Email": self.email,
            "Country": self.country,
            "City": self.city,
            "Street": self.street,
            "Street Number": self.street_number,
        }


# _________________Input helpers____________

def get_required_input(prompt):
    # Keep asking until the user types something non-empty.
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field is required. Please try again.")


def get_validated_input(prompt, validator, optional=False):
    # Ask for input and validate it immediately.
    # - validator: a function that takes a string and returns the cleaned value,
    #              or raises ValueError if the input is invalid.
    # - optional:  if True, an empty input is accepted without calling the validator.
    while True:
        value = input(prompt).strip()

        # If the field is optional and the user left it empty, accept it.
        if optional and value == "":
            return value

        # If the field is required and empty, warn and loop again.
        if not optional and value == "":
            print("This field is required. Please try again.")
            continue

        try:
            # Try to validate the input. If valid, return the cleaned value.
            return validator(value)
        except ValueError as e:
            # If invalid, show the error and re-ask the SAME field.
            print(f"Error: {e}")


# _________________Standalone validators____________


def validate_phone(value):
    cleaned = re.sub(r"[^\d+]", "", value)
    if not re.search(r"^\+?\d{7,15}$", cleaned):
        raise ValueError("Invalid phone number (7-15 digits, optional leading '+')")
    return cleaned


def validate_email(value):
    clean = value.strip().lower()
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.search(pattern, clean):
        raise ValueError("Invalid email format")
    return clean


# _________________CSV helpers____________

def load_customers():
    # Return the list of all customers as dictionaries.
    # If the file does not exist yet, return an empty list instead of crashing.
    if not os.path.exists(CUSTOMERS_CSV):
        return []

    with open(CUSTOMERS_CSV, mode="r") as file:
        reader = csv.DictReader(file)
        return list(reader)


def save_customer_to_csv(data):
    # Write the header if the file does not exist OR is empty (0 bytes).
    write_header = (not os.path.exists(CUSTOMERS_CSV)) or os.path.getsize(CUSTOMERS_CSV) == 0

    with open(CUSTOMERS_CSV, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CUSTOMER_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow(data)


# _________________New Customer workflow____________

def add_new_customer():
    print("\n--- NEW CUSTOMER REGISTRATION ---")

    # Collect and validate each field IMMEDIATELY, one by one.
    first_name = get_required_input("First Name: ")
    last_name = get_required_input("Last Name: ")
    phone = get_validated_input("Phone: ", validate_phone)
    email = get_validated_input("Email (optional): ", validate_email, optional=True)
    country = get_required_input("Country: ")
    city = get_required_input("City: ")
    street = get_required_input("Street: ")
    street_number = get_required_input("Street Number: ")

    # Build the Customer object. Since inputs are already validated,
    # this should never raise, but we keep the try/except as a safety net.
    try:
        customer = Customer(
            first_name, last_name, phone, email, country, city, street, street_number
        )
    except ValueError as e:
        print(f"Unexpected error: {e}")
        return

    customer_data = customer.to_dict()

    # Preview the customer as a table before saving.
    summary_table = [[field, value] for field, value in customer_data.items()]
    print("\n--- CUSTOMER SUMMARY ---")
    print(tabulate(summary_table, headers=["Field", "Value"], tablefmt="grid"))

    confirm = input("Do you want to save this customer? (y/n): ").strip().lower()
    if confirm in ["y", "yes"]:
        save_customer_to_csv(customer_data)
        print("Customer saved successfully!")
    else:
        print("Operation cancelled.")


# _________________Entry point____________

if __name__ == "__main__":
    # When customers.py is run directly, register one new customer.
    # When it is imported by project.py, this block does NOT run.
    add_new_customer()
