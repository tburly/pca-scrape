"""

    tests.test_pca
    ~~~~~~~~~~~~~~~~~~

    Unit tests for module 'pca.pca'.

"""

import unittest
import itertools

from pca.pca import URLBuilder, Parser


class TestURLBuilder(unittest.TestCase):
    """Test class 'pca.pca.URLBuilder'."""

    def test_url_with_arbitrary_threedigit_number(self):
        """
        Does URLBuilder object yield a proper URL?"
        """
        builder = URLBuilder()
        number = 445
        test_url = "https://www.pca.gov.pl/akredytowane-podmioty/akredytacje-aktywne/laboratoria-badawcze/AB%20445,podmiot.html"
        self.assertEqual([url for url in itertools.islice(builder.urls, number, number + 1)][0], test_url)

    def test_url_with_threedigit_number_less_than_ten_zfilled(self):
        """
        Does URLBuilder object yield a proper URL?"
        """
        builder = URLBuilder()
        number = 7
        test_url = "https://www.pca.gov.pl/akredytowane-podmioty/akredytacje-aktywne/laboratoria-badawcze/AB%20007,podmiot.html"
        self.assertEqual([url for url in itertools.islice(builder.urls, number, number + 1)][0], test_url)

    def test_url_with_arbitrary_fourdigit_number(self):
        """
        Does URLBuilder object yield a proper URL?"
        """
        builder = URLBuilder()
        number = 1578
        test_url = "https://www.pca.gov.pl/akredytowane-podmioty/akredytacje-aktywne/laboratoria-badawcze/AB%201578,podmiot.html"
        self.assertEqual([url for url in itertools.islice(builder.urls, number, number + 1)][0], test_url)
