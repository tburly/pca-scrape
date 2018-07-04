"""

    pca.data
    ~~~~~~~~~~~~~

    Handle scraped data.

"""

import json
import csv
import xlwt

JSON_PATH = "data/scraped_data.json"
CSV_PATH = "data/scraped_data.csv"
XLS_PATH = "data/scraped_data.xls"
COL_HEADERS = ["number", "certdate", "org_name", "org_address", "lab_name",
               "lab_address", "phone", "cellphone", "email", "www", "research_fields",
               "research_objects"]


def to_json(labs):
    """Write scraped data to JSON file."""
    with open(JSON_PATH, "w") as outfile:
        json.dump({"labs": labs}, outfile, ensure_ascii=False)
        print(f"Data written to: '{path}'")  # debug


def from_json():
    """Load and return scraped JSON data."""
    try:
        with open(JSON_PATH) as json_file:
            json_data = json.load(json_file)
    except OSError as ose:
        print(f"Cannot load scraped JSON data at {JSON_PATH} (OSError: {ose}")

    return json_data["labs"]


def to_csv():
    """Convert scraped data to '|'-delimited CSV."""
    labs = from_json()

    with open(CSV_PATH, "w") as csv_file:
        writer = csv.writer(csv_file, delimiter="|")
        writer.writerow(COL_HEADERS)
        print("Writing {} rows of data to {}}...".format(len(labs), CSV_PATH))  # debug
        writer.writerows(to_lst(labs))


def to_lst(labs):
    """
    Translate lab data from dicts to lists and return it. Convert 'research_fields' and 'research_objects' lists to ' :: '-delimited strings.
    """
    delimiter = " :: "
    return [[lab["number"], lab["certdate"], lab["org_name"], lab["org_address"], lab["lab_name"],
             lab["lab_address"], lab["phone"], lab["cellphone"], lab["email"], lab["www"],
             delimiter.join([rf for rf in lab["research_fields"]]),
             delimiter.join([ro for ro in lab["research_objects"]])] for lab in labs]


def to_xls():
    """Convert scraped data to Excel spreadsheet."""
    book = xlwt.Workbook()
    sheet = book.add_sheet("labs")

    labs = from_json()
    data = [COL_HEADERS] + to_lst(labs)

    for i, data_row in enumerate(data):
        sheet_row = sheet.row(i)
        for j, item in enumerate(data_row):
            sheet_row.write(j, item)

    book.save(XLS_PATH)
