import json
import time
import argparse
import multiprocessing

"""
name used to import submodule should be added to mode
"""
from vehicle_scraping import Vehicle


cpus = multiprocessing.cpu_count()
parser = argparse.ArgumentParser(
    prog='website_scraping',
    description='Scraping data off websites'
)
parser.add_argument("mode", default="vehicle", choices=["vehicle"])
parser.add_argument("region")
parser.add_argument("sub_mode")
parser.add_argument("--threads", default=1, type=int)
parser.add_argument("--output_format", default="json", choices=["json", "csv"])
parser.add_argument('--kwargs', default={}, type=json.loads)


args = parser.parse_args()
if args.threads>cpus:
    args.threads=cpus

args = vars(args)
mode = args.pop("mode").capitalize()
region = args.pop("region")
sub_mode = args.pop("sub_mode")
args.update(args.pop("kwargs"))

# calling mode as a class
st = time.time()
locals()[mode](region=region, sub_mode=sub_mode, **args)()
print("Total Time: ", time.time()-st)
# Example: python scrape.py vehicle usa cars --kwargs '{"headless":false}'