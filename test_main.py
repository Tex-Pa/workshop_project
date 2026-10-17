import os
import pytest

from customers import (
    Customer,
    validate_phone,
    validate_email,
    load_customers,
    CUSTOMERS_CSV,
)
from repairs import (
    Repair,
    validate_positive_float,
    validate_non_negative_int,
    validate_date,
    load_repairs,
    REPAIRS_CSV,
)


# _________________Customer validators____________

def test_validate_phone_valid():
    assert validate_phone("+39 351 5123456") == "+393515123456"


def test_validate_phone_minimum_length():
    # 7 digits is the minimum accepted length.
    assert validate_phone("1234567") == "1234567"


def test_validate_phone_too_short():
    # 5 digits must be rejected.
    with pytest.raises(ValueError):
        validate_phone("35151")


def test_validate_phone_letters_removed():
    # Letters and separators are stripped; the remaining digits are valid.
    assert validate_phone("abc-351-512-3456") == "3515123456"


def test_validate_phone_no_digits():
    with pytest.raises(ValueError):
        validate_phone("hello")


def test_validate_email_valid():
    assert validate_email("Cristian@Example.COM") == "cristian@example.com"


def test_validate_email_invalid():
    with pytest.raises(ValueError):
        validate_email("not-an-email")


def test_validate_email_missing_tld():
    with pytest.raises(ValueError):
        validate_email("user@domain")


# _________________Customer class____________

def test_customer_normalizes_fields():
    # Names and city should be stripped and title-cased.
    c = Customer("  mario ", "rossi", "3515123456", "", "italy", "ragusa", "via roma", "10")

    assert c.first_name == "Mario"
    assert c.last_name == "Rossi"
    assert c.country == "Italy"
    assert c.city == "Ragusa"
    assert c.street == "Via Roma"


def test_customer_empty_email_is_allowed():
    # Email is optional: an empty string must be accepted.
    c = Customer("Mario", "Rossi", "3515123456", "", "Italy", "Ragusa", "Via Roma", "10")
    assert c.email == ""


def test_customer_to_dict_has_expected_keys():
    c = Customer("Mario", "Rossi", "3515123456", "", "Italy", "Ragusa", "Via Roma", "10")
    d = c.to_dict()

    assert "Customer ID" in d
    assert d["First Name"] == "Mario"
    assert d["Last Name"] == "Rossi"
    assert d["Country"] == "Italy"


# _________________Repair validators____________

def test_validate_positive_float_valid():
    assert validate_positive_float("12.5") == 12.5


def test_validate_positive_float_zero_rejected():
    with pytest.raises(ValueError):
        validate_positive_float("0")


def test_validate_positive_float_negative_rejected():
    with pytest.raises(ValueError):
        validate_positive_float("-3")


def test_validate_positive_float_text_rejected():
    with pytest.raises(ValueError):
        validate_positive_float("abc")


def test_validate_non_negative_int_zero_allowed():
    assert validate_non_negative_int("0") == 0


def test_validate_non_negative_int_negative_rejected():
    with pytest.raises(ValueError):
        validate_non_negative_int("-1")


def test_validate_non_negative_int_text_rejected():
    with pytest.raises(ValueError):
        validate_non_negative_int("three")


def test_validate_date_valid():
    assert validate_date("2026-11-15") == "2026-11-15"


def test_validate_date_wrong_format():
    with pytest.raises(ValueError):
        validate_date("15/11/2026")


def test_validate_date_impossible():
    # Regex matches, but the calendar rejects the day.
    with pytest.raises(ValueError):
        validate_date("2026-02-30")


# _________________Repair class____________

def test_repair_normalizes_strings():
    r = Repair(
        client_id="2",
        item_type="ring",
        metal_type="gold",
        weight_grams="12.5",
        stones_count="3",
        fault_description="broken clasp",
        condition_notes="minor scratches",
        estimated_delivery="2026-11-15",
        estimated_cost="80",
    )

    assert r.item_type == "Ring"
    assert r.metal_type == "Gold"
    assert r.client_id == 2
    assert r.weight_grams == 12.5
    assert r.stones_count == 3
    assert r.estimated_cost == 80.0


def test_repair_to_dict_has_expected_keys():
    r = Repair(
        client_id="2",
        item_type="ring",
        metal_type="gold",
        weight_grams="12.5",
        stones_count="3",
        fault_description="broken clasp",
        condition_notes="",
        estimated_delivery="2026-11-15",
        estimated_cost="80",
    )
    d = r.to_dict()

    assert d["Client ID"] == 2
    assert d["Item Type"] == "Ring"
    assert "Repair ID" in d
    assert "Entry Date" in d


# _________________load_* with missing file____________

def test_load_customers_missing_file_returns_empty_list(tmp_path, monkeypatch):
    # Point CUSTOMERS_CSV to a non-existent path inside a temp folder,
    # so we do not touch the real customers.csv.
    fake_path = os.path.join(str(tmp_path), "nope.csv")
    monkeypatch.setattr("customers.CUSTOMERS_CSV", fake_path)

    assert load_customers() == []


def test_load_repairs_missing_file_returns_empty_list(tmp_path, monkeypatch):
    fake_path = os.path.join(str(tmp_path), "nope.csv")
    monkeypatch.setattr("repairs.REPAIRS_CSV", fake_path)

    assert load_repairs() == []
