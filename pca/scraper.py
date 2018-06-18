"""

    pca.scraper
    ~~~~~~~~~~~~~

    Scrape research laboratories data from the official PCA website.

"""

import requests
import datetime
import time
import json
import itertools


class URLBuilder:

    """Generator of proper URLs for requests."""

    BASEURL_PREFIX = "https://www.pca.gov.pl/akredytowane-podmioty/akredytacje-aktywne/laboratoria-badawcze/AB%20"
    BASEURL_SUFFIX = ",podmiot.html"

    def __init__(self):
        self.urls = (self.BASEURL_PREFIX + (str(i).zfill(3) if i < 1000 else str(i)) + self.BASEURL_SUFFIX for i in itertools.count())


class Lab:

    """Container for parsed data."""

    def __init__(self, number, certdate, org_name, org_address, lab_name, lab_address, phone, cellphone, email, www, research_fields, research_objects):
        self.number = number
        self.certdate = certdate
        self.org_name = org_name
        self.org_address = org_address
        self.lab_name = lab_name
        self.lab_address = lab_address
        self.phone = phone
        self.cellphone = cellphone
        self.email = email
        self.www = www
        self.research_fields = research_fields
        self.research_objects = research_objects


class Parser:

    """Parses data."""

    def __init__(self, number, url):
        self.number = number
        self.contents = requests.get(url).text

    def is_empty(self, line):
        """Check if currently processed page isn't empty."""
        if line.split(prefix)[1].strip() == "</strong> </p>":
            return True
        return False

    def parse_expiredate(self, line):
        """Parse expire date."""
        if line.split(prefix)[1].strip() == "</strong> </p>":
            raise ValueError("No expire date found in the contents of the processed page.")
        return line.split("</strong>")[-1].lstrip()[:-5]

    def validate_lab(self, expiredate_str):
        """Validate current lab based on expire date of its certificate."""
        day, month, year = [int(d) for d in expiredate_str.split("-")]
        expiredate = datetime.date(year, month, day)
        return expiredate > datetime.date.today()

    def parse_certdate(self, line):
        """Parse first certification date."""
        if line.split(prefix)[1].strip() == "</strong> </p>":
            raise ValueError("No expire date found in the contents of the processed page.")
        certdate = line.split("</strong>")[-1].lstrip()[:-5]
        day, month, year = certdate.split("-")
        return "-".join([year, month, day])

    def parse_name_address(self, line):
        """Parse organisation name or address. """
        line = line.split("<p>")[1]
        return line.split("</p>")[0].strip()

    def parse_phone(self, line):
        """Parse phone."""
        phone = []
        for char in line:
            if char == "w":
                break
            if char == "-" or char.isdigit():
                phone.append(char)
        return "".join(phone)

    def parse_email_www(self, line):
        """Parse email or website address."""
        line = line.split("</p>")[0]
        return line.strip()

    def parse_research_field_object(self, line):
        """Parse one reasearch field/object."""
        line = line.split("<li>")[1]
        return line.split("</li>")[0].strip()

    def parse_contents(self):
        """Parse contents of the processed page."""
        # sentinels
        certdate = None
        org_name, org_address, lab_name, lab_address = None, None, None, None, None
        phone, cellphone, email, www = None, None, None, None
        research_fields, research_objects = None, None
        # flags to control parsing on the line after the one that triggers parsing
        org_name_on, org_address_on = False, False
        lab_name_on, lab_address_on = False, False
        phone_on, email_on, www_on = False, False, False
        research_fields_on, research_objects_on = False, False

        for line in self.contents.split("\n"):
            if "Akredytacja:" in line:
                if self.is_empty(line):
                    return None
            elif "Data ważności certyfikatu:" in line:
                expiredate_str = self.parse_expiredate(line)
                if not self.validate_lab(expiredate_str):
                    return None
            elif "Akredytacja od:" in line:
                certdate = self.parse_certdate(line)

            elif "Dane organizacji:" in line:
                org_name_on = True
            elif org_name_on:
                org_name = self.parse_name_address(line)
                org_name_on = False
                org_address_on = True
            elif org_address_on:
                org_address = self.parse_name_address(line)
                org_address_on = False

            elif "Dane laboratorium:" in line:
                lab_name_on = True
            elif lab_name_on:
                lab_name = self.parse_name_address(line)
                lab_name_on = False
                lab_address_on = True
            elif lab_address_on:
                lab_address = self.parse_name_address(line)
                lab_address_on = False

            elif "Telefon:" in line:
                phone_on = True
            elif lab_name_on:
                phone = self.parse_phone(line)
                phone_on = False

            elif "Komórka:" in line:
                cellphone = self.parse_phone(line)

            elif "Email:" in line:
                email_on = True
            elif email_on:
                email = self.parse_email_www(line)
                email_on = False

            elif "www:" in line:
                www_on = True
            elif www_on:
                www = self.parse_email_www(line)
                www_on = False

            elif "Dziedziny badań:" in line:
                research_fields_on = True
                research_fields = []
            elif research_fields_on and "<li>" in line:
                research_fields.append(self.parse_research_field_object(line))

            elif "Obiekty:" in line:
                research_fields_on = False
                research_objects_on = True
                research_objects = []
            elif research_objects_on and "<li>" in line:
                research_objects.append(self.parse_research_field_object(line))
            elif research_objects_on and "</ul>" in line:
                research_objects_on = False
                break

        if any([True for var in [certdate, org_name, org_address, lab_name, lab_address, phone, cellphone, email, www, research_fields, research_objects] if var is None]):
            raise ValueError("The processed page is not parsable.")

        return Lab(self.number, certdate, org_name, org_address, lab_name, lab_address, phone, cellphone, email, www, research_fields, research_objects)
