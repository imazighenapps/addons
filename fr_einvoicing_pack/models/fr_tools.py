# -*- coding: utf-8 -*-
"""Shared helpers: Luhn, VAT and totals checks for French e-invoicing."""
import re


def luhn_valid(number):
    """Return True if the digit string passes the Luhn checksum."""
    digits = re.sub(r"\D", "", number or "")
    if not digits:
        return False
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def clean_identifier(value):
    """Strip spaces, dots and dashes from SIREN/SIRET/VAT input."""
    return re.sub(r"[\s.\-]", "", value or "").upper()


def is_siren(value):
    value = clean_identifier(value)
    return len(value) == 9 and value.isdigit() and luhn_valid(value)


def is_siret(value):
    value = clean_identifier(value)
    return len(value) == 14 and value.isdigit() and luhn_valid(value)


def siren_from_siret(value):
    value = clean_identifier(value)
    if is_siret(value):
        return value[:9]
    return False


def is_fr_vat(value):
    """Very light FR intra-community VAT format check: FR + key + SIREN."""
    value = clean_identifier(value)
    if len(value) != 13 or not value.startswith("FR"):
        return False
    if not value[2:4].isalnum() or not value[4:].isdigit():
        return False
    return luhn_valid(value[4:])
