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
        test_url = URLBuilder.BASEURL_PREFIX + str(number) + URLBuilder.BASEURL_SUFFIX
        self.assertEqual([url for url in itertools.islice(builder.urls, number, number + 1)][0], test_url)

    def test_url_with_threedigit_number_less_than_ten_zfilled(self):
        """
        Does URLBuilder object yield a proper URL?"
        """
        builder = URLBuilder()
        number = 7
        test_url = URLBuilder.BASEURL_PREFIX + str(number).zfill(3) + URLBuilder.BASEURL_SUFFIX
        self.assertEqual([url for url in itertools.islice(builder.urls, number, number + 1)][0], test_url)

    def test_url_with_arbitrary_fourdigit_number(self):
        """
        Does URLBuilder object yield a proper URL?"
        """
        builder = URLBuilder()
        number = 1578
        test_url = URLBuilder.BASEURL_PREFIX + str(number) + URLBuilder.BASEURL_SUFFIX
        self.assertEqual([url for url in itertools.islice(builder.urls, number, number + 1)][0], test_url)
