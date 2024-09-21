import re


def validate_ukrainian_letters(name: str) -> bool:
    """Validates that the name contains only Ukrainian Cyrillic letters, without numbers or special characters."""
    pattern = r'^[А-ЩЬЮЯЄІЇҐа-щьюяєіїґ\'\-]+$'
    return bool(re.match(pattern, name))


def validate_phone_number(phone_number: str) -> bool:
    """Validates that the phone number is in a correct international or local format."""
    pattern = r'^\+?\d{1,3}?[-.\s]?(\(?\d{1,4}?\)?[-.\s]?)?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$'
    return bool(re.match(pattern, phone_number))


def validate_discord_username(username: str) -> bool:
    """Validates that the new Discord username adheres to the new rules."""
    pattern = r'^(?!.*\.\.)[a-z0-9._]{2,32}$'
    return bool(re.match(pattern, username))
