#!/usr/bin/env python3

from driver_test_db.util.dbase import DriverTestDBase
from driver_test_db.util.images import Images
from driver_test_db.util.translation import Translator
from driver_test_db.util.language import Language
from driver_test_db.util.builder import DBBuilder
from driver_test_db.g1canada.loader import G1Loader


def main():
    images = Images("g1canada/data/images", "images")
    images.clean()

    translator = Translator("on")
    translator.load_cache()

    builder = DBBuilder()
    builder.set_images(images)
    builder.set_translator(translator)
    builder.set_languages([lang for lang in Language])
    builder.set_loader(G1Loader())

    builder.build()


main()
