from bot.common.services import validate_ukrainian_letters, validate_phone_number, validate_discord_username


def test_validation_ukrainian_letters_true():
    text = 'Українською'
    result = validate_ukrainian_letters(text)
    assert result is True


def test_validation_ukrainian_letters_false():
    text = '1n english'
    result = validate_ukrainian_letters(text)
    assert result is False


def test_validation_phone_number_true():
    number = '+380682642724'
    result = validate_phone_number(number)
    assert result is True


def test_validation_phone_number_false():
    number = '48942g2'
    result = validate_phone_number(number)
    assert result is False


def test_validation_discord_true():
    discord = 'smth000'
    result = validate_discord_username(discord)
    assert result is True


def test_validation_discord_false():
    discord = 'IMTB'
    result = validate_discord_username(discord)
    assert result is False
