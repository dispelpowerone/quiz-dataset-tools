#!/usr/bin/env python3

from driver_test_db.util.dbase import DriverTestDBase
from driver_test_db.util.images import Images
from driver_test_db.util.translation import Translator
from driver_test_db.util.language import Language
from driver_test_db.util.paraphrase import Paraphrase
from driver_test_db.util.builder import DBBuilder
from driver_test_db.icbc.loader import ICBCLoader


def main():
    images = Images("icbc/data/images", "images")
    images.clean()

    translator = Translator("icbc")
    translator.load_cache()

    paraphrase = Paraphrase("icbc")
    paraphrase.load_cache()
    paraphrase.load_overrides()

    builder = DBBuilder()
    builder.set_images(images)
    builder.set_translator(translator)
    builder.set_paraphrase(paraphrase)
    builder.set_languages([lang for lang in Language])
    builder.set_loader(ICBCLoader())

    builder.build()


main()
