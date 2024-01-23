#!/usr/bin/env python
import json
import argparse
import csv
import os
import re

parser = argparse.ArgumentParser()

parser.add_argument('lcov_file')
parser.add_argument('code_file')
parser.add_argument('output_file')

args = parser.parse_args()
print(args.lcov_file, args.code_file, args.output_file)

class FileStats:
  def __init__(self, name):
    self.name = name
    self.stats = {}


  def add_value(self, name, value):
    self.stats[name] = value

  def get_value(self, name):
    if name in self.stats.keys():
      return self.stats[name]
    else:
      return 0
		


with open(args.code_file) as f:
  code_filenames = json.load(f)


# What each of the items mean: https://github.com/linux-test-project/lcov/issues/113
def get_file_stats(file_reader, filename):
  record_stats = FileStats(filename)
  while True:
    curr_line = f.readline().rstrip()
    if curr_line.startswith("end_of_record"):
      print(record_stats)
      return record_stats
    if curr_line.startswith("BRF:"):
    	record_stats.add_value('BRF', int(curr_line[4:]))
    if curr_line.startswith("BRH:"):
      record_stats.add_value('BRH', int(curr_line[4:]))
    if curr_line.startswith("LH:"):
      record_stats.add_value('LH', int(curr_line[3:]))
    if curr_line.startswith("LF:"):
      record_stats.add_value('LF', int(curr_line[3:]))

print("Starting to parse lcov file")
stats_by_filename = {}
with open(args.lcov_file) as f:
  line = f.readline().rstrip()
  while line:
    if line.startswith("SF:"):
      unprocessed_filename = line[3:].rstrip()
      re_result = re.search(r"(?<=home/hyperbase-tester/hyperbase/).*", unprocessed_filename)
      if re_result == None:
        line = f.readline().rstrip()
        continue
      else: 
        filename = re_result.group(0)
        if filename in code_filenames:
          print("found file " + filename) 
          stats = get_file_stats(f, filename)
          print("Analyzing " + filename)
          print(stats)
          stats_by_filename[filename] = stats
      
    line = f.readline().rstrip()

def get_linecount_for_file(filepath):
  absolute_filepath = os.path.expanduser("~/h/source/hyperbase/" + filepath)
  with open(absolute_filepath, "r") as f:
    lines = f.readlines()
    return len(lines)


with open(args.output_file, 'w', newline='') as csvfile:
  fieldnames = ["Filename", "Lines Found", "Lines Hit", "Line hit rate", "Branches Found", "Branches Hit", "Branch hit rate"]
  csvwriter = csv.DictWriter(csvfile, fieldnames)
  csvwriter.writeheader()

  
  total_branches_found = 0
  total_branches_hit = 0
  total_lines_found = 0
  total_lines_hit = 0

  for filename in code_filenames:
    if filename in stats_by_filename.keys():
      stats = stats_by_filename[filename]
      csvwriter.writerow({
        fieldnames[0]: filename, 
        fieldnames[1]: stats.get_value("LF"), 
        fieldnames[2]: stats.get_value("LH"), 
        fieldnames[3]: 0 if (stats.get_value("LF") == 0) else (1.0 * stats.get_value("LH") / stats.get_value("LF")), 
        fieldnames[4]: stats.get_value('BRF'), 
        fieldnames[5]: stats.get_value("BRH"), 
        fieldnames[6]: 0 if (stats.get_value("BRF") == 0) else (1.0 * stats.get_value("BRH") / stats.get_value("BRF"))
        })

      total_branches_found += stats.get_value('BRF')
      total_branches_hit += stats.get_value("BRH")
      total_lines_found += stats.get_value("LF")
      total_lines_hit += stats.get_value("LH")

    else:
      num_lines = get_linecount_for_file(filename)
      total_lines_found += num_lines
      csvwriter.writerow({
          fieldnames[0]: filename, 
          fieldnames[1]: num_lines, 
          fieldnames[2]: 0, 
          fieldnames[3]: 0, 
          fieldnames[4]: 0, 
          fieldnames[5]: 0, 
          fieldnames[6]: 0,
          })

  csvwriter.writerow({
          fieldnames[0]: "Total", 
          fieldnames[1]: total_lines_found, 
          fieldnames[2]: total_lines_hit, 
          fieldnames[3]: 1.0 * total_lines_hit / total_lines_found, 
          fieldnames[4]: total_branches_found, 
          fieldnames[5]: total_branches_hit, 
          fieldnames[6]: 0 if total_branches_found == 0 else 1.0 * total_branches_hit / total_branches_found,
          })









