#!/usr/bin/env python3

from util.dbase import DriverTestDBase
from util.images import Images
from util.translation import Translator
from util.language import Language
from util.builder import DBBuilder
from g1canada.loader import G1Loader


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
