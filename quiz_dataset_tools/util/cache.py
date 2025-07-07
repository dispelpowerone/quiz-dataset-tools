import csv
import os
from typing import Dict, Callable


class StringCache:
    CACHE_FILE_TEMPL = "cache/{}/{}.cache"
    CACHE_FILE_TEMP_TEMPL = "cache/{}/{}.cache.tmp"
    CACHE_UPDATES_TO_FLUSH = 20

    def __init__(self, domain: str, name: str):
        self.domain = domain
        self.name = name
        self.cache: Dict[str, str] = {}
        self.cache_updates = 0

    def get_or_retrieve(self, src_text: str, retriever: Callable[[str], str]):
        if not src_text:
            return ""
        cached_result = self.cache.get(src_text)
        if cached_result:
            return cached_result
        result = retriever(src_text)
        self.cache[src_text] = result
        self.cache_updates += 1
        if self.cache_updates >= StringCache.CACHE_UPDATES_TO_FLUSH:
            self.save()
            self.cache_updates = 0
        return result

    def save(self):
        print(f"{self.name}::save_cache: size = {len(self.cache)}")
        cache_file_temp = StringCache.CACHE_FILE_TEMP_TEMPL.format(
            self.domain, self.name
        )
        cache_file = StringCache.CACHE_FILE_TEMPL.format(self.domain, self.name)
        head_tail = os.path.split(cache_file_temp)
        os.makedirs(head_tail[0], exist_ok=True)
        if os.path.exists(cache_file_temp):
            os.remove(cache_file_temp)
        with open(cache_file_temp, "w", newline="") as fd:
            writer = csv.writer(fd, delimiter=",", quoting=csv.QUOTE_ALL)
            for key, value in self.cache.items():
                writer.writerow([key, value])
        os.rename(cache_file_temp, cache_file)

    def load(self):
        cache_file = StringCache.CACHE_FILE_TEMPL.format(self.domain, self.name)
        cache = {}
        if not os.path.exists(cache_file):
            return cache
        with open(cache_file, newline="") as fd:
            reader = csv.reader(fd, delimiter=",")
            for row in reader:
                if len(row) != 2:
                    raise Exception(f"Invalid cache format: {row}")
                cache[row[0]] = row[1]
        self.cache = cache
        print(f"{self.name}::load_cache: {len(self.cache)} records loaded")
