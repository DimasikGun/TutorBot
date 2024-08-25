from unittest import TestCase, main

from bot.common.services import validate_ukrainian_letters, validate_phone_number, validate_discord_username


class TestValidation(TestCase):
    def test_validation_ukrainian_letters_true(self):
        text = 'Українською'
        result = validate_ukrainian_letters(text)
        self.assertEqual(result, True)

    def test_validation_ukrainian_letters_false(self):
        text = '1n english'
        result = validate_ukrainian_letters(text)
        self.assertEqual(result, False)

    def test_validation_phone_number_true(self):
        number = '+380682642724'
        result = validate_phone_number(number)
        self.assertEqual(result, True)

    def test_validation_phone_number_false(self):
        number = '48942g2'
        result = validate_phone_number(number)
        self.assertEqual(result, False)

    def test_validation_discord_true(self):
        discord = 'smth000'
        result = validate_discord_username(discord)
        self.assertEqual(result, True)

    def test_validation_discord_false(self):
        discord = 'IMTB'
        result = validate_discord_username(discord)
        self.assertEqual(result, False)

if __name__ == '__main__':
    main()