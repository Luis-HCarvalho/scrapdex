#!.venv/bin/python

import json
import os
import sys

if len(sys.argv) > 1:
    index = int(sys.argv[1])
else:
    index = 0

length = 1
try:
    file = open("index_len.json", "r")
    data = json.load(file)
    index = data["index"]
    length = data["len"]
    file.close()
except:
    pass

if index < length:
    os.system(f"./.venv/bin/scrapy crawl scrapdex -a index={index}")
    os.system(f"./run.py {index + 1}")