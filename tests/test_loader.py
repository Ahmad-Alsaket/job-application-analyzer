import unittest

from src.loader import parse_line


class TestParseLine(unittest.TestCase):
    def test_simple_line(self):
        app = parse_line("Initech - Data Analytics - July - rejected")
        self.assertEqual(app.company, "Initech")
        self.assertEqual(app.role, "Data Analytics")
        self.assertEqual(app.date, "July")
        self.assertEqual(app.status, "rejected")

    def test_quoted_line_with_em_dashes(self):
        app = parse_line('"Acme Corp — Data Analyst — applied ~March 2026 — rejected."')
        self.assertEqual(app.company, "Acme Corp")
        self.assertEqual(app.date, "~March 2026")
        self.assertEqual(app.status, "rejected")

    def test_role_containing_separator(self):
        app = parse_line("Globex -  Datenanalyse & Reporting - Qualität und Nachhaltigkeit  - June - rejected")
        self.assertEqual(app.role, "Datenanalyse & Reporting - Qualität und Nachhaltigkeit")

    def test_blank_line(self):
        self.assertIsNone(parse_line("   "))


if __name__ == "__main__":
    unittest.main()
