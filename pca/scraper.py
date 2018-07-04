"""

    pca.scraper
    ~~~~~~~~~~~~~

    Scrape research laboratories data from the official PCA website.

"""

import requests
import datetime
import time
import itertools
import re

from . import data


CEILING = 1700  # on 28th June 2018 there were 1688 accredited laboratories


class URLBuilder:

    """Generator of proper URLs for Requests."""

    BASEURL_PREFIX = "https://www.pca.gov.pl/akredytowane-podmioty/akredytacje-aktywne/laboratoria-badawcze/AB%20"
    BASEURL_SUFFIX = ",podmiot.html"

    def __init__(self):
        self.urls = (self.BASEURL_PREFIX + (str(i).zfill(3) if i < 1000 else str(i)) + self.BASEURL_SUFFIX for i in itertools.count(1))


class PageParser:

    """Parse page at given URL."""

    PHONE_REGEX = r"(?:\(?\+?48)?(?:[-\.\(\)\s]*\d){9}\)?"  # matches both cellphone and landline formats with optional prefix '(+48)'
    EMAIL_REGEX = r"\b[\w\.%+-]+@(?:[\w\.-])+\.[a-zA-Z]{2,}\b"  # a simplified version that matches email in most popular (99% cases) form
    WWW_REGEX = r"\b(?:[\w\.-])+\.[a-zA-Z]{2,}\b"

    def __init__(self, number, url):
        self.number = "AB " + str(number).zfill(3)
        time.sleep(0.05)
        print("Creating #{} page parser...".format(str(number).zfill(4)))  # debug
        self.contents = requests.get(url).text

    def is_empty(self, line, pattern):
        """Check if currently processed page isn't empty."""
        if line.split(pattern)[1] == "</strong> </p>":
            return True
        return False

    def lose_cruft(self, line, pattern):
        """Strip line of unwanted characters."""
        line = line.split(pattern)[1]
        line = line.replace("</strong>", "").replace("</p>", "")
        return line.strip()

    def parse_expiredate(self, line, pattern):
        """Parse expire date."""
        if self.is_empty(line, pattern):
            raise ValueError("No expire date found in the contents of the processed page.")
        return self.lose_cruft(line, pattern)

    def validate_lab(self, expiredate_str):
        """Validate current lab based on expire date of its certificate."""
        day, month, year = [int(d) for d in expiredate_str.split("-")]
        expiredate = datetime.date(year, month, day)
        return expiredate > datetime.date.today()

    def parse_certdate(self, line, pattern):
        """Parse first certification date."""
        if self.is_empty(line, pattern):
            raise ValueError("No certification date found in the contents of the processed page.")
        certdate = self.lose_cruft(line, pattern)
        day, month, year = certdate.split("-")
        return "-".join([year, month, day])

    def parse_name_address(self, line):
        """Parse organisation name or address. """
        line = line.split("<p>")[1]
        return line.split("</p>")[0].strip()

    def parse_contact_details(self, line, regex):
        """Parse contact details (landline phone, cellphone, email and www)."""
        match = re.search(regex, line)
        if match is None:
            return ""
        return match.group()

    def parse_research_field_object(self, line):
        """Parse one reasearch field/object."""
        line = line.split("<li>")[1]
        return line.split("</li>")[0].strip()

    def parse_contents(self):
        """Parse contents of processed page."""
        # sentinels
        certdate = None
        org_name, org_address, lab_name, lab_address = None, None, None, None
        phone, cellphone, email, www = None, None, None, None

        research_fields, research_objects = "", ""  # default values in case these sections are missing on the parsed page

        # flags to control parsing on the line after the one that triggers parsing
        org_name_on, org_address_on = False, False
        lab_name_on, lab_address_on = False, False
        phone_on, email_on, www_on = False, False, False
        research_fields_on, research_objects_on = False, False

        for line in self.contents.split("\n"):
            line = line.strip()

            if "Akredytacja:" in line:
                if self.is_empty(line, "Akredytacja:"):
                    return None
            elif "Data ważności certyfikatu:" in line:
                expiredate_str = self.parse_expiredate(line, "Data ważności certyfikatu:")
                try:
                    if not self.validate_lab(expiredate_str):
                        return None
                except ValueError as ve:
                    print(f"Cannot validate expire date (ValueError: {ve}). Skipping...")
                    return None
            elif "Akredytacja od:" in line:
                certdate = self.parse_certdate(line, "Akredytacja od:")

            elif "Dane organizacji:" in line:
                org_name_on = True
                continue
            elif org_name_on:
                org_name = self.parse_name_address(line)
                org_name_on = False
                org_address_on = True
                continue
            elif org_address_on:
                org_address = self.parse_name_address(line)
                org_address_on = False

            elif "Dane laboratorium:" in line:
                lab_name_on = True
                continue
            elif lab_name_on:
                lab_name = self.parse_name_address(line)
                lab_name_on = False
                lab_address_on = True
                continue
            elif lab_address_on:
                lab_address = self.parse_name_address(line)
                lab_address_on = False

            elif "Telefon:" in line:
                phone_on = True
                continue
            elif phone_on:
                phone = self.parse_contact_details(line, self.PHONE_REGEX)
                phone_on = False

            elif "Komórka:" in line:
                cellphone = self.parse_contact_details(line, self.PHONE_REGEX)

            elif "Email:" in line:
                email_on = True
                continue
            elif email_on:
                email = self.parse_contact_details(line, self.EMAIL_REGEX)
                email_on = False

            elif "www:" in line:
                www_on = True
                continue
            elif www_on:
                www = self.parse_contact_details(line, self.WWW_REGEX)
                www_on = False

            elif "Dziedziny badań:" in line:
                research_fields_on = True
                research_fields = []
                continue
            elif research_fields_on and "<li>" in line:
                research_fields.append(self.parse_research_field_object(line))

            elif "Obiekty:" in line:
                research_fields_on = False
                research_objects_on = True
                research_objects = []
                continue
            elif research_objects_on and "<li>" in line:
                research_objects.append(self.parse_research_field_object(line))
            elif research_objects_on and "</ul>" in line:
                research_objects_on = False
                break

        if any([True for var in [certdate, org_name, org_address, lab_name, lab_address, phone,
                                 cellphone, email, www]
                if var is None]):
            raise ValueError("The processed page is not parsable.")

        return {
            "number": self.number,
            "certdate": certdate,
            "org_name": org_name,
            "org_address": org_address,
            "lab_name": lab_name,
            "lab_address": lab_address,
            "phone": phone,
            "cellphone": cellphone,
            "email": email,
            "www": www,
            "research_fields": research_fields,
            "research_objects": research_objects
        }


def scrape():
    """Scrape data of PCA accredited reasearch laboratories from PCA official website."""

    builder = URLBuilder()
    print("Parsing contents...")  # debug

    labs = []
    for n, url in zip(range(1, CEILING), builder.urls):
        parser = PageParser(n, url)
        lab = parser.parse_contents()
        if lab is not None:
            labs.append(lab)

    data.to_json(labs)
