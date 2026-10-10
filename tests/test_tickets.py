
import unittest

from campusflow.tickets import (
    calculate_priority,
    validate_title,
    validate_category,
    validate_urgency,
    validate_affected_users,
)


class TestPriority(unittest.TestCase):
    def test_high_urgency_and_many_users_is_critical(self):
        self.assertEqual(calculate_priority("high", 12), "critical")

    def test_high_urgency_with_few_users_is_high(self):
        self.assertEqual(calculate_priority("high", 2), "high")

    def test_many_users_with_low_urgency_is_medium(self):
        self.assertEqual(calculate_priority("low", 4), "medium")

    def test_low_urgency_with_one_user_is_low(self):
        self.assertEqual(calculate_priority("low", 1), "low")


class TestTitleValidation(unittest.TestCase):
    def test_valid_title(self):
        self.assertEqual(validate_title("Wi-Fi is down"), "Wi-Fi is down")

    def test_title_is_trimmed(self):
        self.assertEqual(
            validate_title("  Laptop broken  "),
            "Laptop broken",
        )

    def test_blank_title_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_title("   ")

    def test_non_string_title_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_title(None)


class TestCategoryValidation(unittest.TestCase):
    def test_category_is_normalized(self):
        self.assertEqual(validate_category(" NETWORK "), "Network")

    def test_invalid_category_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_category("Electricity")


class TestUrgencyValidation(unittest.TestCase):
    def test_urgency_is_normalized(self):
        self.assertEqual(validate_urgency(" HIGH "), "high")

    def test_invalid_urgency_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_urgency("urgent")


class TestAffectedUsersValidation(unittest.TestCase):
    def test_integer_string_is_converted(self):
        self.assertEqual(validate_affected_users("12"), 12)

    def test_zero_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_affected_users("0")

    def test_negative_number_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_affected_users("-3")

    def test_decimal_string_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_affected_users("2.5")

    def test_text_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_affected_users("many")


if __name__ == "__main__":
    unittest.main()
