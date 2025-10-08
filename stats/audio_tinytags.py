import os
import tinytag
import stats

stats.stat("audio", "{} of audio in total", stats.stat_type_elapsed)

def scanner(path, results):
	if not tinytag.TinyTag.is_supported(path): return
	try:
		r = tinytag.TinyTag.get(path, tags = False)
	except: return
	if not r.duration: return
	format = os.path.splitext(r._filename)[1].lower()
	if format.startswith("."): format = format[1:]
	stats.stat("audio_" + format, "{} of " + format + " audio in total", stats.stat_type_elapsed, after = "audio")
	stats.increase_stat(path, results, "audio", r.duration)
	stats.increase_stat(path, results, "audio_"+format, r.duration)

stats.file_scanners.append(scanner)