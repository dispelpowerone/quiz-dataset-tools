import csv
import os


class TextOverrides:
    OVERRIDES_FILE_TEMPL = "output/{}/{}.overrides"
    OVERRIDES_FILE_TEMP_TEMPL = "output/{}/{}.overrides"

    MappingType = dict[tuple[str, str], str]

    def __init__(self, domain: str, name: str):
        self.domain = domain
        self.name = name
        self.overrides: TextOverrides.MappingType = {}

    def get(self, text: str, context: str = "") -> str | None:
        if not text:
            return ""
        return self.overrides.get((text, context))

    def put(self, text: str, context: str, override: str) -> None:
        self.overrides[(text, context)] = override

    def save(self) -> None:
        print(f"TextOverrides::save: size = {len(self.overrides)}")
        overrides_file_temp = TextOverrides.OVERRIDES_FILE_TEMP_TEMPL.format(
            self.domain, self.name
        )
        overrides_file = TextOverrides.OVERRIDES_FILE_TEMPL.format(
            self.domain, self.name
        )
        head_tail = os.path.split(overrides_file_temp)
        os.makedirs(head_tail[0], exist_ok=True)
        if os.path.exists(overrides_file_temp):
            os.remove(overrides_file_temp)
        with open(overrides_file_temp, "w", newline="") as fd:
            writer = csv.writer(fd, delimiter=",", quoting=csv.QUOTE_ALL)
            for key, value in self.overrides.items():
                writer.writerow([key[0], key[1], value])
        os.rename(overrides_file_temp, overrides_file)

    def load(self) -> None:
        overrides_file = TextOverrides.OVERRIDES_FILE_TEMPL.format(
            self.domain, self.name
        )
        overrides: TextOverrides.MappingType = {}
        if not os.path.exists(overrides_file):
            self.overrides = overrides
            return
        with open(overrides_file, newline="") as fd:
            reader = csv.reader(fd, delimiter=",")
            for row in reader:
                if len(row) != 3:
                    raise Exception(f"TextOverrides::load: Invalid cache format: {row}")
                overrides[(row[0], row[1])] = row[2]
        self.overrides = overrides
        print(f"TextOverrides::load: {len(self.overrides)} records loaded")