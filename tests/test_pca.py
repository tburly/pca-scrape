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
        self.assertEqual([url for url in itertools.islice(builder.urls, number - 1, number)][0], url)

    def test_url_with_arbitrary_threedigit_number(self):
        """
        Does URLBuilder object yield a proper URL?"
        """
        builder = URLBuilder()
        number = 445
        url = "https://www.pca.gov.pl/akredytowane-podmioty/akredytacje-aktywne/laboratoria-badawcze/AB%20445,podmiot.html"
        self.assertEqual([url for url in itertools.islice(builder.urls, number - 1, number)][0], url)

    def test_url_with_arbitrary_fourdigit_number(self):
        """
        Does URLBuilder object yield a proper URL?"
        """
        builder = URLBuilder()
        number = 1578
        url = "https://www.pca.gov.pl/akredytowane-podmioty/akredytacje-aktywne/laboratoria-badawcze/AB%201578,podmiot.html"
        self.assertEqual([url for url in itertools.islice(builder.urls, number - 1, number)][0], url)


class TestPageParser(unittest.TestCase):
    """Test case for class 'pca.scraper.PageParser"""

    def setUp(self):
        url = "https://www.pca.gov.pl/akredytowane-podmioty/akredytacje-aktywne/laboratoria-badawcze/AB%201327,podmiot.html"
        self.parser = PageParser(1327, url)
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
        line = "zmyslmar@imp.lodz.pl               </p>"
        email = "zmyslmar@imp.lodz.pl"
        self.assertEqual(self.parser.parse_contact_details(line, PageParser.EMAIL_REGEX),
                         email)

    def test_parse_email_invalid_line(self):
        """Does parsing invalid line return empty string?"""
        line = "brak               </p>"
        self.assertEqual(self.parser.parse_contact_details(line, PageParser.EMAIL_REGEX), "")

    def test_parse_www(self):
        """Does parsing valid line return a proper www address?"""
        line = "www.imp.lodz.pl               </p>"
        www = "www.imp.lodz.pl"
        self.assertEqual(self.parser.parse_contact_details(line, PageParser.WWW_REGEX),
                         www)

    def test_parse_www_invalid_line(self):
        """Does parsing invalid line return empty string?"""
        line = "</p>"
        self.assertEqual(self.parser.parse_contact_details(line, PageParser.WWW_REGEX), "")

    def test_parse_research_field(self):
        """Does parsing valid line return a proper research field?"""
        line = "<li>Badania dotyczące inżynierii środowiska (środowiskowe i klimatyczne) (G)</li>"
        research_field = "Badania dotyczące inżynierii środowiska (środowiskowe i klimatyczne) (G)"
        self.assertEqual(self.parser.parse_research_field_object(line), research_field)

    def test_parse_research_field_empty_line(self):
        """Does parsing empty line return a an empty string?"""
        line = "<li></li>"
        self.assertEqual(self.parser.parse_research_field_object(line), "")

    def test_parse_contents_no_cellphone_oneline_research_fields_and_objects(self):
        """
        Does parsing a valid page with:
        - not empty certification date line,
        - still valid certification,
        - no cellphone,
        - one line of research fields,
        - one line of research objects
        return a proper dict?
        """
        expected = {
            "number": "AB 1327",
            "certdate": "2012-04-03",
            "org_name": "P.P.U.H. Badania Nieniszczące SONOBAD Andrzej Zadura",
            "org_address": "Maszewo Duże, ul. Miła 8; 09-400 Płock",
            "lab_name": "P.P.U.H. Badania Nieniszczące SONOBAD Andrzej Zadura",
            "lab_address": "Maszewo Duże, ul. Miła 8; 09-400 Płock",
            "phone": "24 266-78-75",
            "cellphone": "",
            "email": "sonobad@sonobad.pl",
            "www": "www.sonobad.pl",
            "research_fields": ["Badania nieniszczące (L)"],
            "research_objects": ["Wyroby i materiały konstrukcyjne - w tym metale i kompozyty"]
        }
        self.assertEqual(self.parser.parse_contents(), expected)

    def test_parse_contents_expired(self):
        """Does parsing a valid page with expired certification returns 'None'"""
        url = "https://www.pca.gov.pl/akredytowane-podmioty/akredytacje-aktywne/laboratoria-badawcze/AB%20555,podmiot.html"
        parser = PageParser(555, url)
        self.assertIs(parser.parse_contents(), None)

    def test_parse_contents_no_cellphone_multiline_research_fields_and_objects(self):
        """
        Does parsing a valid page with:
        - not empty certification date line,
        - still valid certification,
        - no cellphone,
        - multiline research fields,
        - multiline research objects
        return a proper dict?
        """
        url = "https://www.pca.gov.pl/akredytowane-podmioty/akredytacje-aktywne/laboratoria-badawcze/AB%20333,podmiot.html"
        parser = PageParser(333, url)
        expected = {
            "number": "AB 333",
            "certdate": "2001-07-06",
            "org_name": "Okręgowa Stacja Chemiczno-Rolnicza w Kielcach",
            "org_address": "ul. Wapiennikowa 21; 25-112 Kielce",
            "lab_name": "Dział Laboratoryjny",
            "lab_address": "ul. Wapiennikowa 21; 25-112 Kielce",
            "phone": "41 361-01-51",
            "cellphone": "",
            "email": "kielce@schr.gov.pl",
            "www": "www.schr.gov.pl",
            "research_fields": ["Badania chemiczne, analityka chemiczna (C)", "Badania właściwości fizycznych (N)"],
            "research_objects": ["Produkty rolne - w tym pasze dla zwierząt", "Chemikalia, kosmetyki, wyroby chemiczne - w tym nawozy i farby", "Próbki środowiskowe, powietrze, woda, gleba, odpady, osady i ścieki"]
        }
        self.assertEqual(parser.parse_contents(), expected)

    def test_parse_contents_no_cellphone_no_email_oneline_research_fields_and_objects(self):
        """
        Does parsing a valid page with:
        - not empty certification date line,
        - still valid certification,
        - no cellphone,
        - no email,
        - one line of research fields,
        - one line of research objects
        return a proper dict?
        """
        url = "https://www.pca.gov.pl/akredytowane-podmioty/akredytacje-aktywne/laboratoria-badawcze/AB%20456,podmiot.html"
        parser = PageParser(456, url)
        expected = {
            "number": "AB 456",
            "certdate": "2004-02-12",
            "org_name": "Instytut Metali Nieżelaznych",
            "org_address": "ul. Sowińskiego 5; 44-100 Gliwice",
            "lab_name": "Laboratorium Zaawansowanych Materiałów Magnetycznych",
            "lab_address": "ul. Sowińskiego 5; 44-100 Gliwice",
            "phone": "32 238-02-81",
            "cellphone": "",
            "email": "",
            "www": "www.imn.gliwice.pl",
            "research_fields": ["Badania właściwości fizycznych (N)"],
            "research_objects": ["Wyroby i wyposażenie elektryczne, telekomunikacyjne i elektroniczne"]
        }
        self.assertEqual(parser.parse_contents(), expected)

    def test_parse_contents_arbitrary_URL(self):
        """Does parsing contents of an arbitrary page raise a ValueError?"""

        url = "https://www.google.pl"
        parser = PageParser(456, url)

        with self.assertRaises(ValueError):
            parser.parse_contents()
