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
    # TODO: poprawić względem zmian w klasie testowanej

    def setUp(self):
        self.number = 1527
        self.url = "https://www.pca.gov.pl/akredytowane-podmioty/akredytacje-aktywne/laboratoria-badawcze/AB%201527,podmiot.html"
        self.parser = PageParser(self.number, self.url)

        self.today = datetime.date.today()
        self.timedelta = datetime.timedelta(days=100)

    def test_parse_expiredate(self):
        """Does parsing proper line returns proper expire date string?"""
        line = "               <p><strong>Data ważności certyfikatu:</strong> 03-08-2018</p>"
        expiredate = "03-08-2018"
        self.assertEqual(self.parser.parse_expiredate(line, "Data ważności certyfikatu:"), expiredate)

    def test_parse_expiredate_line_from_blank_page(self):
        """
        Does parsing line from a blank page (with URL based on a number greater than the number of existing acredited laboratories) raises a ValueError?
        """
        line = "                <p><strong>Data ważności certyfikatu:</strong> </p>"
        with self.assertRaises(ValueError):
            self.parser.parse_expiredate(line, "Data ważności certyfikatu:")

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
