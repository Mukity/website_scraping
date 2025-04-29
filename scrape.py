import argparse
import multiprocessing

"""
name used to import submodule should be added to mode
"""
import vehicle_scraping as vehicle

cpus = multiprocessing.cpu_count()
parser = argparse.ArgumentParser(
    prog='website_scraping',
    description='Scraping data off websites'
)
parser.add_argument("mode", default="vehicle", choices=["vehicle"])
parser.add_argument("--threads", default=1, type=int)
parser.add_argument("--output_format", default="json", choices=["json", "csv"])

args = parser.parse_args()
if args.threads>cpus:
    args.threads=cpus