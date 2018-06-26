"""

    tests.test_pca
    ~~~~~~~~~~~~~~~~~~

    Unit tests for module 'pca.pca'.

"""

import unittest
import itertools
import datetime

from pca.scraper import URLBuilder, PageParser


class TestURLBuilder(unittest.TestCase):
    """Test case for class 'pca.scraper.URLBuilder'."""

    def test_url_with_arbitrary_onedigit_number(self):
        """
        Does URLBuilder object yield a proper URL?"
        """
        builder = URLBuilder()
        number = 7
        url = "https://www.pca.gov.pl/akredytowane-podmioty/akredytacje-aktywne/laboratoria-badawcze/AB%20007,podmiot.html"
        self.assertEqual([url for url in itertools.islice(builder.urls, number, number + 1)][0], url)

    def test_url_with_arbitrary_threedigit_number(self):
        """
        Does URLBuilder object yield a proper URL?"
        """
        builder = URLBuilder()
        number = 445
        url = "https://www.pca.gov.pl/akredytowane-podmioty/akredytacje-aktywne/laboratoria-badawcze/AB%20445,podmiot.html"
        self.assertEqual([url for url in itertools.islice(builder.urls, number, number + 1)][0], url)

    def test_url_with_arbitrary_fourdigit_number(self):
        """
        Does URLBuilder object yield a proper URL?"
        """
        builder = URLBuilder()
        number = 1578
        url = "https://www.pca.gov.pl/akredytowane-podmioty/akredytacje-aktywne/laboratoria-badawcze/AB%201578,podmiot.html"
        self.assertEqual([url for url in itertools.islice(builder.urls, number, number + 1)][0], url)


class TestPageParser(unittest.TestCase):
    """Test case for class 'pca.scraper.PageParser"""

    def setUp(self):
        self.number = 1527
        self.url = "https://www.pca.gov.pl/akredytowane-podmioty/akredytacje-aktywne/laboratoria-badawcze/AB%201527,podmiot.html"
        self.parser = PageParser(self.number, self.url)
        self.pattern = "Data ważności certyfikatu:"

        self.today = datetime.date.today()
        self.timedelta = datetime.timedelta(days=100)

    def test_is_empty_with_empty(self):
        """Does passing a line with no information to parse return 'True'?"""
        line = "<p><strong>Data ważności certyfikatu:</strong> </p>"
        self.assertTrue(self.parser.is_empty(line, self.pattern))

    def test_is_empty_with_not_empty(self):
        """Does passing a line with some valid information to parse return 'False'?"""
        line = "<p><strong>Data ważności certyfikatu:</strong> 03-08-2018</p>"
        self.assertFalse(self.parser.is_empty(line, self.pattern))

    def test_lose_cruft(self):
        """Does valid line get stripped of unwanted characters?"""
        line = "<p><strong>Data ważności certyfikatu:</strong> 03-08-2018</p>"
        self.assertEqual(self.parser.lose_cruft(line, self.pattern), "03-08-2018")

    def test_parse_expiredate(self):
        """Does parsing valid line return proper expire date string?"""
        line = "<p><strong>Data ważności certyfikatu:</strong> 03-08-2018</p>"
        expiredate = "03-08-2018"
        self.assertEqual(self.parser.parse_expiredate(line, self.pattern), expiredate)

    def test_parse_expiredate_with_empty(self):
        """Does parsing line with no information to parse raise a 'ValueError'?"""
        line = "<p><strong>Data ważności certyfikatu:</strong> </p>"
        with self.assertRaises(ValueError):
            self.parser.parse_expiredate(line, self.pattern)

    def test_validate_lab_date_later_than_today(self):
        """Does expire date greater than today validates processed lab?"""
        expiredate = self.today + self.timedelta
        year, month, day = str(expiredate).split("-")
        expiredate_str = "-".join([day, month, year])
        self.assertTrue(self.parser.validate_lab(expiredate_str))

    def test_validate_lab_date_equal_today(self):
        """Does expire date equal to today validates processed lab?"""
        expiredate = self.today
        year, month, day = str(expiredate).split("-")
        expiredate_str = "-".join([day, month, year])
        self.assertFalse(self.parser.validate_lab(expiredate_str))

    def test_validate_lab_date_lesser_than_today(self):
        """Does expire date lesser than today validates processed lab?"""
        expiredate = self.today - self.timedelta
        year, month, day = str(expiredate).split("-")
        expiredate_str = "-".join([day, month, year])
        self.assertFalse(self.parser.validate_lab(expiredate_str))

    def test_parse_certdate(self):
        """Does parsing valid line return proper certification date string?"""
        line = "<p><strong>Akredytacja od:</strong> 04-08-2014</p>"
        pattern = "Akredytacja od:"
        certdate = "2014-08-04"
        self.assertEqual(self.parser.parse_certdate(line, pattern), certdate)

    def test_parse_certdate_with_empty(self):
        """Does parsing line with no information to parse raise a 'ValueError'?"""
        line = "<p><strong>Akredytacja od:</strong> </p>"
        pattern = "Akredytacja od:"
        with self.assertRaises(ValueError):
            self.parser.parse_certdate(line, pattern)

    def test_parse_name_address(self):
        """
        Does parsing line with valid information return organization name/organization adress/lab name/lab address?
        """
        lines = [
            "<p> Wojewódzki Inspektorat Weterynarii z/s w Krośnie </p>",
            "<p> ul. Ściegiennego 6A; 38-400 Krosno </p>",
            "<p> Zakład Higieny Weterynaryjnej w Krośnie </p>",
            "<p> ul. Ściegiennego 6A; 38-400 Krosno </p>"
        ]
        names_addresses = [
            "Wojewódzki Inspektorat Weterynarii z/s w Krośnie",
            "ul. Ściegiennego 6A; 38-400 Krosno",
            "Zakład Higieny Weterynaryjnej w Krośnie",
            "ul. Ściegiennego 6A; 38-400 Krosno"
        ]
        for line, output in zip(lines, names_addresses):
            with self.subTest(tested_line=line, expected_output=output):
                self.assertEqual(self.parser.parse_name_address(line), output)

    def test_parse_landline_phone(self):
        """Does parsing valid line return a proper ladnline phone number?"""
        line = "13 432-59-23                    wew.: brak              </p>"
        landline = "13 432-59-23"
        self.assertEqual(self.parser.parse_contact_details(line, PageParser.PHONE_REGEX),
                         landline)

    def test_parse_cellphone(self):
        """Does parsing valid line return a proper cellphone number?"""
        line = "602-606-272                    wew.: brak              </p>"
        landline = "602-606-272"
        self.assertEqual(self.parser.parse_contact_details(line, PageParser.PHONE_REGEX),
                         landline)

    def test_parse_phone_invalid_line(self):
        """Does parsing invalid line return empty string?"""
        line = "432-59-23                    wew.: brak              </p>"
        self.assertEqual(self.parser.parse_contact_details(line, PageParser.PHONE_REGEX), "")

    def test_parse_email(self):
        """Does parsing valid line return a proper email?"""
        line = "                    zmyslmar@imp.lodz.pl               </p>"
        email = "zmyslmar@imp.lodz.pl"
        self.assertEqual(self.parser.parse_contact_details(line, PageParser.EMAIL_REGEX),
                         email)

    def test_parse_email_invalid_line(self):
        """Does parsing invalid line return empty string?"""
        line = "                   brak               </p>"
        self.assertEqual(self.parser.parse_contact_details(line, PageParser.EMAIL_REGEX), "")

    def test_parse_www(self):
        """Does parsing valid line return a proper www address?"""
        line = "                    www.imp.lodz.pl               </p>"
        www = "www.imp.lodz.pl"
        self.assertEqual(self.parser.parse_contact_details(line, PageParser.WWW_REGEX),
                         www)

    def test_parse_www_invalid_line(self):
        """Does parsing invalid line return empty string?"""
        line = "                                  </p>"
        self.assertEqual(self.parser.parse_contact_details(line, PageParser.WWW_REGEX), "")
