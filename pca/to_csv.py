"""

    pca.to_csv
    ~~~~~~~~~~~~~

    Convert scraped JSON data to other formats.

"""

import json
import csv

JSON_PATH = "data/scraped_data.json"
CSV_PATH = "data/scraped_data.csv"


def to_csv():
    """Convert scraped data to '|'-delimited CSV."""

    try:
        with open(JSON_PATH) as json_file:
            json_data = json.load(json_file)
    except OSError as ose:
        print(f"Cannot load scraped JSON data at {JSON_PATH} (OSError: {ose}")

    labs = json_data["labs"]

    with open(CSV_PATH, "w") as csv_file:
        writer = csv.writer(csv_file, delimiter="|")
        writer.writerow(["number", "certdate", "org_name", "org_address", "lab_name",
                         "lab_address", "phone", "cellphone", "email", "www", "research_fields",
                         "research_objects"])
        print("Writing {} rows of data to {}}...".format(len(labs), CSV_PATH))  # debug
        writer.writerows(to_lst(labs))


def to_lst(labs):
    """
    Translate lab data from dicts to lists and return it. Convert 'research_fields' and 'research_objects' lists to ' :: '-delimited strings.
    """
    delimiter = " :: "
    return [[lab["number"], lab["certdate"], lab["org_name"], lab["org_address"], lab["lab_name"], lab["lab_address"], lab["phone"], lab["cellphone"], lab["email"], lab["www"],
             delimiter.join([rf for rf in lab["research_fields"]]),
             delimiter.join([ro for ro in lab["research_objects"]])] for lab in labs]
