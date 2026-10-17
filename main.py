import os
import sys
import csv
from tabulate import tabulate

# Import from our own modules.
# customers.py provides the Customer class, the input helpers,
# and the standalone workflow for registering a new customer.
# repairs.py provides the Repair class, its validators, and the CSV helpers.
from customers import (
    add_new_customer,
    load_customers,
    get_required_input,
    get_validated_input,
    validate_phone,
    validate_email,
)
from repairs import (
    Repair,
    save_repair_to_csv,
    load_repairs,
    REPAIR_FIELDS,
    validate_positive_float,
    validate_non_negative_int,
    validate_date,
)


# _________________HOME / MAIN MENU____________

def print_main_menu():
    # Show the main menu options.
    print("\n" + "=" * 40)
    print("            MAIN MENU")
    print("=" * 40)
    print("  1. View / Search Client")
    print("  2. Register New Client")
    print("  3. Exit")
    print("=" * 40)


def main():
    # Main loop: keeps showing the home menu until the user exits.
    while True:
        print_main_menu()
        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            search_client_flow()
        elif choice == "2":
            register_client_flow()
        elif choice == "3":
            exit_application()
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


# _________________CLIENT SEARCH____________

def search_client_flow():
    # Ask the user for a query and search customers.csv.
    print("\n--- SEARCH CLIENT ---")
    query = input("Search by First Name, Last Name, or Client ID: ").strip()

    if query == "":
        print("Empty search. Returning to main menu.")
        return

    customers = load_customers()
    if not customers:
        print("No customers found in the database.")
        return

    # Normalize the query for name comparison.
    # .title() matches the way we stored names in Customer.__init__.
    query_title = query.title()

    # Find matches: by ID (exact string) or by first/last name (case-insensitive).
    matches = []
    for c in customers:
        if (
            c.get("Customer ID") == query
            or c.get("First Name") == query_title
            or c.get("Last Name") == query_title
        ):
            matches.append(c)

    # No match found.
    if not matches:
        print(f'No customer found for "{query}".')
        return

    # Exactly one match: show the FULL PROFILE immediately,
    # then the action menu.
    if len(matches) == 1:
        client_actions_menu(matches[0])
        return

    # Multiple matches: show a numbered list, let the user pick,
    # then show the FULL PROFILE of the chosen one.
    print(f"\nFound {len(matches)} matching customers:")
    for i, c in enumerate(matches, start=1):
        print(f"  {i}. ID {c['Customer ID']} - {c['First Name']} {c['Last Name']} ({c['City']})")

    while True:
        pick = input(f"Choose a customer (1-{len(matches)}) or 0 to cancel: ").strip()
        if pick == "0":
            print("Search cancelled.")
            return
        if pick.isdigit() and 1 <= int(pick) <= len(matches):
            client_actions_menu(matches[int(pick) - 1])
            return
        print(f"Invalid choice. Enter a number between 1 and {len(matches)}.")


# _________________CLIENT REGISTRATION____________

def register_client_flow():
    # Reuse the standalone workflow from customers.py.
    # After registering, the user is sent back to the main menu.
    # We do NOT open the client actions menu automatically,
    # because add_new_customer does not return the saved customer.
    print("\n--- REGISTER NEW CLIENT ---")
    add_new_customer()


# _________________CLIENT ACTIONS____________

def print_client_actions_menu(customer):
    # Show the actions available once a customer is selected.
    full_name = f"{customer['First Name']} {customer['Last Name']}"
    print("\n" + "=" * 40)
    print(f"  CLIENT: {full_name} (ID {customer['Customer ID']})")
    print("=" * 40)
    print("  1. New Job Order")
    print("  2. Return to Main Menu")
    print("  3. Exit")
    print("=" * 40)


def client_actions_menu(customer):
    # IMPORTANT: show the FULL PROFILE first, then the action menu.
    # This is what makes the complete customer card appear
    # as soon as a client is found.
    show_client_profile(customer)

    while True:
        print_client_actions_menu(customer)
        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            new_job_order(customer)
        elif choice == "2":
            return
        elif choice == "3":
            exit_application()
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


def show_client_profile(customer):
    # Display the full profile of a single customer as a table.
    # Every field stored in the CSV is shown, one row per field.
    print("\n--- CLIENT PROFILE ---")
    table = [[field, value] for field, value in customer.items()]
    print(tabulate(table, headers=["Field", "Value"], tablefmt="grid"))


# _________________JOB ORDER____________

def new_job_order(customer):
    # Collect data for a new repair and save it to repairs.csv.
    client_id = customer["Customer ID"]

    print("\n--- NEW JOB ORDER ---")
    print(f"Client ID: {client_id}")

    item_type = get_required_input("Item type (e.g. ring, necklace): ")
    metal_type = get_required_input("Metal type (e.g. gold, silver): ")
    weight_grams = get_validated_input("Weight in grams: ", validate_positive_float)
    stones_count = get_validated_input("Number of stones: ", validate_non_negative_int)

    fault_description = get_required_input("Fault description: ")
    condition_notes = input("Condition notes (optional): ").strip()

    print("Entry date will be set automatically to today.")
    estimated_delivery = get_validated_input(
        "Estimated delivery (YYYY-MM-DD): ", validate_date
    )
    estimated_cost = get_validated_input("Estimated cost: ", validate_positive_float)

    # Build the Repair object. The client_id comes from the selected customer,
    # so the repair is automatically linked to them.
    try:
        repair = Repair(
            client_id=client_id,
            item_type=item_type,
            metal_type=metal_type,
            weight_grams=weight_grams,
            stones_count=stones_count,
            fault_description=fault_description,
            condition_notes=condition_notes,
            estimated_delivery=estimated_delivery,
            estimated_cost=estimated_cost,
        )
    except ValueError as e:
        print(f"Unexpected error: {e}")
        return

    repair_data = repair.to_dict()

    # Preview the job order as a table.
    summary_table = [[field, value] for field, value in repair_data.items()]
    print("\n--- JOB ORDER SUMMARY ---")
    print(tabulate(summary_table, headers=["Field", "Value"], tablefmt="grid"))

    confirm = input("Do you want to save this job order? (y/n): ").strip().lower()
    if confirm in ["y", "yes"]:
        save_repair_to_csv(repair_data)
        print("Job order saved successfully!")
    else:
        print("Operation cancelled.")


# _________________EXIT____________

def exit_application():
    # Clean exit from the program.
    print("\nGoodbye!")
    sys.exit(0)


# _________________ENTRY POINT____________

if __name__ == "__main__":
    main()
