#!/usr/bin/env python3

from util.dbase import DriverTestDBase
from util.images import Images
from util.translation import Translator
from util.paraphrase import Paraphrase
from util.language import Language
from util.builder import DBBuilder
from usa.loader import USALoader


def main():
    images = Images("usa/data/images", "images")
    images.clean()

    translator = Translator("usa")
    translator.load_cache()

    paraphrase = Paraphrase("usa")
    paraphrase.load_cache()
    paraphrase.load_overrides()

    builder = DBBuilder()
    builder.set_images(images)
    builder.set_translator(translator)
    builder.set_paraphrase(paraphrase)
    builder.set_languages([Language.EN])
    builder.set_loader(USALoader())

    builder.build()


main()
