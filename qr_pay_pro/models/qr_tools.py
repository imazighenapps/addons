# -*- coding: utf-8 -*-
"""RF (ISO 11649), QRR (mod10r) and EPC payload helpers."""
import re


def _to_digits(text):
    out = []
    for ch in text.upper():
        if ch.isdigit():
            out.append(ch)
        elif ch.isalpha():
            out.append(str(ord(ch) - 55))
        elif ch in (" ", "-", ".", "/", ":"):
            continue
        else:
            return None
    return "".join(out)


def rf_check_digits(base):
    """Compute the 2 ISO 11649 check digits for base (alphanumeric, <=21 chars)."""
    digits = _to_digits(base + "RF00")
    if digits is None:
        return False
    remainder = 0
    for ch in digits:
        remainder = (remainder * 10 + int(ch)) % 97
    return "%02d" % (98 - remainder)


def make_rf_reference(base):
    base = re.sub(r"[\s\-.,/:]", "", base or "").upper()
    if not base or len(base) > 21 or not re.fullmatch(r"[A-Z0-9]+", base):
        return False
    check = rf_check_digits(base)
    return "RF%s%s" % (check, base) if check else False


def is_rf_reference(value):
    value = re.sub(r"[\s\-.,/:]", "", value or "").upper()
    if not re.fullmatch(r"RF[0-9]{2}[A-Z0-9]{1,21}", value):
        return False
    digits = _to_digits(value[4:] + value[:4])
    if digits is None:
        return False
    remainder = 0
    for ch in digits:
        remainder = (remainder * 10 + int(ch)) % 97
    return remainder == 1


def mod10r(number):
    """Recursive mod10 used for Swiss QRR (27 digits incl. check)."""
    digits = re.sub(r"\D", "", number or "")
    carry = 0
    table = (0, 9, 4, 6, 8, 2, 7, 1, 3, 5)
    for ch in digits:
        carry = table[(carry + int(ch)) % 10]
    return str((10 - carry) % 10)


def make_qrr_reference(base26):
    """Build a 27-digit QRR from a numeric base (left-trimmed, mod10r key)."""
    digits = re.sub(r"\D", "", base26 or "")[-26:].zfill(26)
    return digits + mod10r(digits)


def is_qrr_reference(value):
    digits = re.sub(r"\D", "", value or "")
    return len(digits) == 27 and mod10r(digits[:-1]) == digits[-1]


def is_qr_iban(iban):
    """QR-IBAN: CH/LI IBAN whose institution code (pos 5-9) is 30000-31999."""
    clean = re.sub(r"\s", "", iban or "").upper()
    if len(clean) < 9 or clean[:2] not in ("CH", "LI"):
        return False
    try:
        return 30000 <= int(clean[4:9]) <= 31999
    except ValueError:
        return False


def build_epc_payload(name, iban, amount, currency="EUR", bic="", purpose="",
                      rf_reference="", remittance="", charset="1"):
    """Build an EPC069-12 (v002) payload, enforcing RF/remittance exclusivity."""
    lines = ["BCD", "002", charset, "SCT", bic or "", (name or "")[:70],
             re.sub(r"\s", "", iban or "")]
    if currency != "EUR":
        return False, "EPC supports EUR only."
    lines.append("EUR%.2f" % amount if amount else "")
    lines.append(purpose or "")
    if rf_reference and remittance:
        return False, "RF reference and free remittance are mutually exclusive."
    lines.append(rf_reference or "")
    lines.append("" if rf_reference else (remittance or "")[:140])
    lines.append("")
    payload = "\n".join(lines)
    if len(payload.encode("utf-8")) > 331:
        return False, "Payload exceeds 331 bytes."
    return True, payload


def decode_epc_payload(payload):
    """Decode an EPC/SEPA QR text payload into a dict (for vendor bills)."""
    parts = (payload or "").replace("\r\n", "\n").split("\n")
    keys = ["service", "version", "charset", "identification", "bic",
            "beneficiary", "iban", "amount", "purpose", "rf_reference",
            "remittance", "hint"]
    out = dict(zip(keys, parts + [""] * (len(keys) - len(parts))))
    if out["service"] != "BCD":
        return False
    return out
