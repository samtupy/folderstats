import os
import stats

stats.stat("dir_count", "{} directories") # This somewhat uniquely handled stat is increased in ../folderstats.py when scanning directories.
stats.stat("file_count", "{} files")
stats.stat("file_size", "{} of data", stats.stat_type_size)

def scanner(path, results):
	stats.increase_stat(path, results, "file_count", 1)
	try: stats.increase_stat(path, results, "file_size", os.stat(path).st_size)
	except: pass

stats.file_scanners.append(scanner)
