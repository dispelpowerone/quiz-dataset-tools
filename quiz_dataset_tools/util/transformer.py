import csv
import os
from typing import Dict


class Transformer:
    CACHE_FILE_TEMPL = "cache/{}/{}.cache"
    CACHE_FILE_TEMP_TEMPL = "cache/{}/{}.cache.tmp"
    CACHE_UPDATES_TO_FLUSH = 20
    OVERRIDES_FILE_TEMPL = "cache/{}/{}.overrides"

    def __init__(self, domain: str, name: str):
        self.domain = domain
        self.name = name
        self.cache: Dict[str, str] = {}
        self.cache_updates = 0
        self.overrides: Dict[str, str] = {}

    def get(self, src_text: str):
        if not src_text:
            return ""
        override = self.overrides.get(src_text)
        if override:
            return override
        cached_result = self.cache.get(src_text)
        if cached_result:
            return cached_result
        result = self._get(src_text)
        self.cache[src_text] = result
        self.cache_updates += 1
        if self.cache_updates >= Transformer.CACHE_UPDATES_TO_FLUSH:
            self.save_cache()
            self.cache_updates = 0
        return result

    def save_cache(self):
        print(f"{self.name}::save_cache: size = {len(self.cache)}")
        cache_file_temp = Transformer.CACHE_FILE_TEMP_TEMPL.format(
            self.domain, self.name
        )
        cache_file = Transformer.CACHE_FILE_TEMPL.format(self.domain, self.name)
        head_tail = os.path.split(cache_file_temp)
        os.makedirs(head_tail[0], exist_ok=True)
        if os.path.exists(cache_file_temp):
            os.remove(cache_file_temp)
        with open(cache_file_temp, "w", newline="") as fd:
            writer = csv.writer(fd, delimiter=",", quoting=csv.QUOTE_ALL)
            for key, value in self.cache.items():
                writer.writerow([key, value])
        os.rename(cache_file_temp, cache_file)

    def load_cache(self):
        cache_file = Transformer.CACHE_FILE_TEMPL.format(self.domain, self.name)
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

    def load_overrides(self):
        overrides_file = Transformer.OVERRIDES_FILE_TEMPL.format(self.domain, self.name)
        overrides = {}
        if not os.path.exists(overrides_file):
            return overrides
        with open(overrides_file, newline="") as fd:
            reader = csv.reader(fd, delimiter=",")
            for row in reader:
                if len(row) != 2:
                    raise Exception(f"Invalid cache format: {row}")
                overrides[row[0]] = row[1]
        self.overrides = overrides
        print(f"{self.name}::load_overrides: {len(self.overrides)} records loaded")

    def _get(self, src_text: str):
        raise Exception(f"{self.name}::_get: isnt implemented")
