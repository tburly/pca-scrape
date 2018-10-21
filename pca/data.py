"""

    pca.data
    ~~~~~~~~~~~~~

    Handle scraped data.

"""

import json
import csv
import xlwt

FILEPATH_TEMPLATE = "data/scraped_data.{}"
COL_HEADERS = ["number", "certdate", "org_name", "org_address", "lab_name",
               "lab_address", "phone", "cellphone", "email", "www", "research_fields",
               "research_objects"]


def to_json(scraped_data):
    """Write scraped data to JSON file."""
    with open(FILEPATH_TEMPLATE.format("json"), "w") as outfile:
        json.dump({"labs": scraped_data}, outfile, ensure_ascii=False)
        print(f"Data written to: '{path}'")  # debug


def from_json():
    """Load and return scraped JSON data."""
    path = FILEPATH_TEMPLATE.format("json")
    try:
        with open(path) as json_file:
            json_data = json.load(json_file)
    except OSError as ose:
        print(f"Cannot load scraped JSON data at {path} (OSError: {ose}")

    return json_data["labs"]


def to_lists(scraped_data):
    """
    Translate elements of scraped data (a list) from dicts to lists and return it. Convert 'research_fields' and 'research_objects' lists to ' :: '-delimited strings.
    """
    delimiter = " :: "
    return [[lab["number"], lab["certdate"], lab["org_name"], lab["org_address"], lab["lab_name"],
             lab["lab_address"], lab["phone"], lab["cellphone"], lab["email"], lab["www"],
             delimiter.join([rf for rf in lab["research_fields"]]),
             delimiter.join([ro for ro in lab["research_objects"]])] for lab in scraped_data]


def to_csv(scraped_data):
    """Write scraped data to '|'-delimited CSV file"""
    path = FILEPATH_TEMPLATE.format("csv")
    with open(path, "w") as csv_file:
        writer = csv.writer(csv_file, delimiter="|")
        writer.writerow(COL_HEADERS)
        print("Writing {} rows of data to {}}...".format(len(scraped_data), path))  # debug
        writer.writerows(to_lists(scraped_data))


def to_xls(scraped_data):
    """Write scraped data to Excel spreadsheet"""
    book = xlwt.Workbook()
    sheet = book.add_sheet("labs")

    data = [COL_HEADERS] + to_lists(scraped_data)

    for i, data_row in enumerate(data):
        sheet_row = sheet.row(i)
        for j, item in enumerate(data_row):
            sheet_row.write(j, item)

    book.save(FILEPATH_TEMPLATE.format("xls"))
