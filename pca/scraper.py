"""

    pca.pca
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

    def parse_contents(self):
        """Parse contents of the processed page."""
        # flags to control parsing on the line after the one that triggers parsing
        org_name_on, org_address_on = False, False
        lab_name_on, lab_address_on = False, False

        for line in self.contents.split("\n"):
            if "Akredytacja:" in line:
                if self.is_empty(line):
                    return None
            elif "Data ważności certyfikatu:" in line:
                expiredate_str = self.parse_expiredate(line)
                if not self.validate_lab(expiredate_str):
                    return None
            elif "Akredytacja od:" in line:
                self.certdate = self.parse_certdate(line)

            elif "Dane organizacji:" in line:
                org_name_on = True
            elif org_name_on:
                self.org_name = self.parse_name_address(line)
                org_name_on = False
                org_address_on = True
            elif org_address_on:
                self.org_address = self.parse_name_address(line)
                org_address_on = False

            elif "Dane laboratorium:" in line:
                lab_name_on = True
            elif lab_name_on:
                self.lab_name = self.parse_name_address(line)
                lab_name_on = False
                lab_address_on = True
            elif lab_address_on:
                self.lab_address = self.parse_name_address(line)
                lab_address_on = False

        raise ValueError("The processed page is not parsable.")
