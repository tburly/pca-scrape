#!/usr/bin/env python3

"""

    Starting the script.

"""

from pca.scraper import scrape
from pca.data import to_json


def main():
    """Run the script."""
    to_json(scrape())


if __name__ == "__main__":
    main()
