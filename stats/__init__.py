"""This submodule of folderstats specifically deals with the stats themselves. You can add new files here for different formats or sets of formats following the specification provided by existing examples here, then simply import them into _all_stats.py in the order that files should be scanned. This submodule handles both stat formatting and the scanning for stats in files."""

import os

size_units = ["B", "KB", "MB", "GB", "TB", "PB"]

stat_type_numeric = 0
stat_type_elapsed = 1
stat_type_size = 2

file_scanners = [] # def file_scanner(path, results) should call stats.increase_stat when needed.

stats = {}
stat_ids=[]
class stat:
	"""The class for stat metadata. To be clear no stat values are actually stored here, but rather their formatting information as well as utilities for printing and formatting the stats."""
	def __init__(self, id, format, type = stat_type_numeric, print_if_0 = False, after = ""):
		global stats
		if id in stats: return # It is useful sometimes to allow stats to redeclare when they are found out dynamically without worrying about duplication.
		self.id = id
		self.format = format
		self.type = type
		self.print_if_0 = print_if_0
		if after: stat_ids.insert(stat_ids.index(after)+1, self.id)
		else: stat_ids.append(self.id)
		stats[id]=self
	def to_str(self, val):
		if not val and not self.print_if_0: return ""
		if self.type == stat_type_numeric: return self.format.format(val)
		elif self.type == stat_type_elapsed:
			weeks, days = divmod(val, 86400 * 7)
			days, hours = divmod(days, 86400)
			hours, minutes = divmod(hours, 3600)
			minutes, seconds = divmod(minutes, 60)
			timestr = []
			if weeks > 0: timestr.append(str(int(weeks)) + (" weeks" if weeks != 1 else " week"))
			if days > 0: timestr.append(str(int(days)) + (" days" if days != 1 else " day"))
			if hours > 0: timestr.append(str(int(hours)) + (" hours" if hours != 1 else " hour"))
			if minutes > 0: timestr.append(str(int(minutes)) + (" minutes" if minutes != 1 else " minute"))
			if seconds > 0: timestr.append(str(int(seconds)) + (" seconds" if seconds != 1 else " second"))
			if len(timestr) < 1: return self.format.format("0 seconds")
			elif len(timestr) > 1: timestr[-1] = "and " + timestr[-1]
			return self.format.format(", ".join(timestr))
		elif self.type == stat_type_size:
			for i in reversed(range(len(size_units))):
				if val >= 1024 ** i or i == 0: return self.format.format(f"{(val/1024 ** i):3.1f}{size_units[i]}")
			return self.format.format(f"{val}B")

def increase_stat(path, results, stat, val):
	"""This utility function is used by file scanners to easily increase stats. The function expects to receive a file path to add stats for, the application's results dictionary, the stat to increase and the value to increase it by. We fragment the path, adding stat totals to each parent directory in the path so long as the path exists in the results dictionary."""
	global stats
	if not stat in stats: return
	while True:
		old_path = path
		path = os.path.split(path)[0]
		if path == old_path: break
		if not path in results: break
		if not stat in results[path]: results[path][stat] = val
		else: results[path][stat] += val

def to_str(path, results):
	"""Creates the final string for a given path that will be printed to the results text field of the application."""
	if not path in results: return ""
	output = ""
	for s in stat_ids:
		s = stats[s]
		if not s.id in results[path]: continue
		r = s.to_str(results[path][s.id])
		if r: output += r + "\n"
	if not output: output = "No available stats for " + path
	else: output = path + ":\n" + output
	return output

def scan_file(path, results):
	"""This function is called by scanning threads which invoque it on each file, passing both the path and the results dictionary to add any stats to."""
	if not os.path.isfile(path): return
	for fs in file_scanners:
		if fs(path, results): break

