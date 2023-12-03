import csv
import os
from driver_test_db.util.language import Language


class TextOverrides:
    SCHEMA = ["source_lang", "source_text", "context", "dest_lang", "dest_text"]
    OVERRIDES_FILE_TEMPL = "data/{}/overrides.csv"
    OVERRIDES_FILE_TEMP_TEMPL = "data/{}/overrides.csv.temp"

    MappingType = dict[tuple[str, str, str, str], str]

    def __init__(self, domain: str):
        self.domain = domain
        self.overrides: TextOverrides.MappingType = {}

    def get(
        self, lang: Language, text: str, context: str, override_lang: Language
    ) -> str | None:
        return self.overrides.get((lang.name, text, context, override_lang.name))

    def put(
        self,
        lang: Language,
        text: str,
        context: str,
        override_lang: Language,
        override: str,
    ) -> None:
        self.overrides[(lang.name, text, context, override_lang.name)] = override

    def save(self) -> None:
        print(f"TextOverrides::save: size = {len(self.overrides)}")
        overrides_file_temp = TextOverrides.OVERRIDES_FILE_TEMP_TEMPL.format(
            self.domain
        )
        overrides_file = TextOverrides.OVERRIDES_FILE_TEMPL.format(self.domain)
        head_tail = os.path.split(overrides_file_temp)
        os.makedirs(head_tail[0], exist_ok=True)
        if os.path.exists(overrides_file_temp):
            os.remove(overrides_file_temp)
        with open(overrides_file_temp, "w", newline="") as fd:
            writer = csv.writer(fd, delimiter=",", quoting=csv.QUOTE_ALL)
            writer.writerow(TextOverrides.SCHEMA)
            for key, value in self.overrides.items():
                writer.writerow([key[0], key[1], key[2], key[3], value])
        os.rename(overrides_file_temp, overrides_file)

    def load(self) -> None:
        overrides_file = TextOverrides.OVERRIDES_FILE_TEMPL.format(self.domain)
        overrides: TextOverrides.MappingType = {}
        if not os.path.exists(overrides_file):
            self.overrides = overrides
            return
        with open(overrides_file, newline="") as fd:
            reader = csv.reader(fd, delimiter=",")
            header = next(reader)
            assert header == TextOverrides.SCHEMA
            for row in reader:
                if len(row) != len(TextOverrides.SCHEMA):
                    raise Exception(f"TextOverrides::load: Invalid format: {row}")
                overrides[(row[0], row[1], row[2], row[3])] = row[4]
        self.overrides = overrides
        print(f"TextOverrides::load: {len(self.overrides)} records loaded")
