import csv
import os
import re
import datetime
from tabulate import tabulate

# Reuse the input helpers already defined in customers.py
# so we do not duplicate validation logic across modules.
from customers import get_required_input, get_validated_input


# _________________Repairs Container____________

REPAIRS_CSV = "repairs.csv"

# CSV column names, in one place.
REPAIR_FIELDS = [
    "Repair ID",
    "Client ID",
    "Entry Date",
    "Item Type",
    "Metal Type",
    "Weight (g)",
    "Stones Count",
    "Fault Description",
    "Condition Notes",
    "Estimated Delivery",
    "Estimated Cost",
]


class Repair:
    # Class representing a single repair order (Job Order).

    def __init__(self, client_id, item_type, metal_type, weight_grams,
                 stones_count, fault_description, condition_notes,
                 estimated_delivery, estimated_cost,
                 entry_date=None, repair_id=None):

        # Auto-incremented ID (same pattern as Customer).
        self.repair_id = repair_id if repair_id else self.generate_id()

        # Foreign key to the customer.
        self.client_id = int(client_id)

        # Simple normalized strings.
        self.item_type = item_type.strip().title()
        self.metal_type = metal_type.strip().title()
        self.fault_description = fault_description.strip()
        self.condition_notes = condition_notes.strip()

        # Numeric fields.
        self.weight_grams = self.to_positive_number(weight_grams, "Weight (g)")
        self.stones_count = self.to_non_negative_int(stones_count, "Stones Count")
        self.estimated_cost = self.to_positive_number(estimated_cost, "Estimated Cost")

        # Dates: entry_date defaults to today.
        self.entry_date = entry_date if entry_date else str(datetime.date.today())
        self.estimated_delivery = self.check_date(estimated_delivery)

    # ____________________________________________
    # Auto-incremented repair ID.
    # ____________________________________________
    def generate_id(self):
        # First repair ever.
        if not os.path.exists(REPAIRS_CSV):
            return 1

        max_id = 0
        with open(REPAIRS_CSV, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get("Repair ID"):
                    current_id = int(row["Repair ID"])
                    if current_id > max_id:
                        max_id = current_id

        return max_id + 1

    # ____________________________________________
    # Validators (small, one job each).
    # ____________________________________________
    def to_positive_number(self, value, field_name):
        # Convert to float and require > 0.
        try:
            number = float(value)
        except ValueError:
            raise ValueError(f"{field_name} must be a number")

        if number <= 0:
            raise ValueError(f"{field_name} must be greater than zero")

        return number

    def to_non_negative_int(self, value, field_name):
        # Convert to int and require >= 0 (0 stones is valid).
        try:
            number = int(value)
        except ValueError:
            raise ValueError(f"{field_name} must be an integer")

        if number < 0:
            raise ValueError(f"{field_name} cannot be negative")

        return number

    def check_date(self, value):
        # Expect YYYY-MM-DD and verify it is a real date.
        value = value.strip()
        if not re.search(r"^\d{4}-\d{2}-\d{2}$", value):
            raise ValueError("Date must be in YYYY-MM-DD format")

        try:
            datetime.date.fromisoformat(value)
        except ValueError:
            raise ValueError("Date is not a valid calendar date")

        return value

    # ____________________________________________
    # Serialization.
    # ____________________________________________
    def to_dict(self):
        return {
            "Repair ID": self.repair_id,
            "Client ID": self.client_id,
            "Entry Date": self.entry_date,
            "Item Type": self.item_type,
            "Metal Type": self.metal_type,
            "Weight (g)": self.weight_grams,
            "Stones Count": self.stones_count,
            "Fault Description": self.fault_description,
            "Condition Notes": self.condition_notes,
            "Estimated Delivery": self.estimated_delivery,
            "Estimated Cost": self.estimated_cost,
        }


# _________________CSV helpers____________

def load_repairs():
    # Return the list of all repairs as dictionaries.
    # If the file does not exist yet, return an empty list.
    if not os.path.exists(REPAIRS_CSV):
        return []

    with open(REPAIRS_CSV, mode="r") as file:
        reader = csv.DictReader(file)
        return list(reader)


def save_repair_to_csv(data):
    # Write the header only if the file is brand new.
    file_exists = os.path.exists(REPAIRS_CSV)

    with open(REPAIRS_CSV, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=REPAIR_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)


# _________________Standalone validators for input____________
# These are wrappers used with get_validated_input.
# They mirror the class logic so validation happens IMMEDIATELY,
# not at the end after all fields have been typed.

def validate_positive_float(value):
    try:
        number = float(value)
    except ValueError:
        raise ValueError("must be a number")
    if number <= 0:
        raise ValueError("must be greater than zero")
    return number


def validate_non_negative_int(value):
    try:
        number = int(value)
    except ValueError:
        raise ValueError("must be an integer")
    if number < 0:
        raise ValueError("cannot be negative")
    return number


def validate_date(value):
    value = value.strip()
    if not re.search(r"^\d{4}-\d{2}-\d{2}$", value):
        raise ValueError("must be in YYYY-MM-DD format")
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        raise ValueError("is not a valid calendar date")
    return value


# _________________Standalone workflow____________

def add_new_repair_standalone():
    # Collects all data for one repair order and saves it.
    # Used only when repairs.py is run directly.

    print("\n--- NEW JOB ORDER ---")

    # The user must type the client ID manually here.
    # In project.py this value comes from the customer lookup.
    client_id = get_validated_input("Client ID: ", validate_non_negative_int)

    item_type = get_required_input("Item type (e.g. ring, necklace): ")
    metal_type = get_required_input("Metal type (e.g. gold, silver): ")
    weight_grams = get_validated_input("Weight in grams: ", validate_positive_float)
    stones_count = get_validated_input("Number of stones: ", validate_non_negative_int)

    fault_description = get_required_input("Fault description: ")
    condition_notes = input("Condition notes (optional): ").strip()

    print("Entry date will be set automatically to today.")
    estimated_delivery = get_validated_input("Estimated delivery (YYYY-MM-DD): ", validate_date)
    estimated_cost = get_validated_input("Estimated cost: ", validate_positive_float)

    # Build the Repair object. All fields are already validated,
    # but the constructor re-validates as a safety net.
    try:
        repair = Repair(
            client_id,
            item_type,
            metal_type,
            weight_grams,
            stones_count,
            fault_description,
            condition_notes,
            estimated_delivery,
            estimated_cost,
        )
    except ValueError as e:
        print(f"Unexpected error: {e}")
        return

    repair_data = repair.to_dict()

    # Preview table.
    summary_table = [[field, value] for field, value in repair_data.items()]
    print("\n--- JOB ORDER SUMMARY ---")
    print(tabulate(summary_table, headers=["Field", "Value"], tablefmt="grid"))

    confirm = input("Do you want to save this job order? (y/n): ").strip().lower()
    if confirm in ["y", "yes"]:
        save_repair_to_csv(repair_data)
        print("Job order saved successfully!")
    else:
        print("Operation cancelled.")


# _________________Entry point____________

if __name__ == "__main__":
    # When repairs.py is run directly, ask the user for one new job order.
    # When repairs.py is imported by project.py, this block does NOT run.
    add_new_repair_standalone()
