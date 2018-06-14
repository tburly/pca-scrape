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

    """Parses the data."""

    def __init__(self, number, url):
        self.number = number
        self.contents = requests.get(url).text

    def is_empty(self):
        """Check if currently processed page isn't empty."""
        pass

    def validate_lab(self, expiredate_str):
        """Validate current lab based on the listed expire date of its certificate."""
        day, month, year = [int(d) for d in expiredate_str.split("-")]
        expiredate = datetime.date(year, month, day)
        return expiredate >= datetime.date.today()

    def parse_expiredate(self):
        """Parse the expire date."""
        prefix = "Data ważności certyfikatu:"
        for line in self.contents.split("\n"):
            if prefix in line:
                return line.split("</strong>")[-1].lstrip()[:-5]
        raise ValueError("No expire date found on the processed page.")
