# Folderstats

NOTE! This is currently a rough side project that is fun, but is still very early in development and may be buggy or rough in any way.

## What is it?

In late 2023, I finally decided to code myself a solution which would give me the answer to a small question I'd had for a long time. How much audio in each format did I have on my drives? Thus this tiny WX python3 application, which, given a root location, recursively scans all subfolders and generates statistics about them which can be viewed at any zoom level in the resulting tree.

Be ware that do to this program's nature, potentially many files are scanned at once and thus this may be a strain on your discs. Use with care!

## Supported information

Currently, folderstats only supports fetching basic audio lengths via python tinytags as well as file sizes. However, the application was designed for more stat providers to be easily added, and any such are appreciated! I will probably switch from tinytags to mutagen.

## Running

```
pip install -r requirements.txt
python3 folderstats.py
```

## Support

Please feel free to use the issue tracker and to open pull requests. This is a side project of mine and thus may not receive as much professional love as other things here, nevertheless I hope to continue this project's development and see how many fun stats we can gather about our data (line numbers in code? word counts in documents? Number of SQLite table exist or number of spreadsheet columns?) Only time will tell. Have fun!
