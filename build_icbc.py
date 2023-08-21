#!/usr/bin/env python3

from util.dbase import DriverTestDBase
from util.images import Images
from util.translation import Translator
from util.language import Language
from util.paraphrase import Paraphrase
from util.builder import DBBuilder
from icbc.loader import ICBCLoader


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
