from classification import Word
from dearAJ.src import ajconsole
import csv
import os
from pprint import pp

CSV_FILES = []
log = ajconsole.Message(enabled=True).log
warn = ajconsole.Message(enabled=True).warn

for file in os.listdir():
    if file.startswith("top") and file.endswith(".csv") and "akaWordFreq" in file:
        CSV_FILES.append(file)

STATS = []

for file in CSV_FILES:
    with open(file, 'r') as csv_file:
        stats = []
        log(f"{file}")
        reader = csv.reader(csv_file)
        next(reader)
        total_count: int = 0
        for row in reader:
            nth = file[6:10] + "_" + file[39:].replace(".csv", "")
            word = Word(row[0])
            count = int(row[1])
            total_count += count
            attrs = [attr for attr in dir(word) if not attr.startswith("_") and getattr(word, attr) is True]
            stats.append({word.word: {"labels": attrs, "count": count}})
        STATS.append({nth: {"stats": stats, "total": total_count}})

# pp(STATS)
for nth_and_table in STATS:
    #pp(nth_and_table)
    for title in nth_and_table:
        item = nth_and_table[title]
        total = item['total']
        words = item['stats']
        for word in words:
            for k in word:
                body = word[k]
                body['percentage'] = body['count'] / total

from collections import defaultdict
RESULT = defaultdict(dict)
# pp(STATS)

for ele in STATS:
    for k in ele:
        nth = k
        _result = defaultdict(float)
        body = ele[k]
        stats: list = body['stats']
        assert type(stats) == list
        for word in stats:
            for word_text in word:
                word_body = word[word_text]
                word_labels = word_body['labels']
                p = word_body['percentage']
                for label in word_labels:
                    _result[label] += p
        RESULT[nth] = _result

pp(RESULT)
