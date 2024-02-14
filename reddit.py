#!/usr/bin/env python
"""Collects age/gender counts from Reddit submissions."""

import argparse
import collections
import json
import logging
import re

import pyzstd

# This is hack that tells the system that these files were compressed with
# a very long compression window.
PARAMS = {pyzstd.DParameter.windowLogMax: 31}


def main(args: argparse.Namespace) -> None:
    ages: collections.Counter[int] = collections.Counter()
    ages_genders: collections.Counter[tuple[int, str]] = collections.Counter()
    with pyzstd.open(args.zst, "rt", level_or_option=PARAMS) as source:
        for line in source:
            post = json.loads(line)
            title = post["title"]
            for expr in re.finditer(r"(\d+)(f|F|m|m|nb|NB)", title):
                age = int(expr.group(1))
                gender = expr.group(2).upper()
                ages[age] += 1
                ages_genders[age, gender] += 1
    age, count = ages.most_common(1)[0]
    logging.info(f"The most common age is {age} with {count:,} mentions")
    (age, gender), count = ages_genders.most_common(1)[0]
    logging.info(
        f"The most common age/gender pair is [{age}{gender}] "
        f"with {count:,} mentions"
    )


if __name__ == "__main__":
    logging.basicConfig(level="INFO", format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zst", help="input .zst file")
    main(parser.parse_args())
