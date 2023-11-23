#!/usr/bin/env python3

import click
from driver_test_db.util.text_overrides import TextOverrides
from driver_test_db.util.language import Language
from driver_test_db.util.builder import DatabaseBuilder
from driver_test_db.prebuild.prebuild import PrebuildBuilder
from driver_test_db.parser.parser import Parser
from driver_test_db.parser.dbase import DatabaseParser
from driver_test_db.parser.usa import USADatabaseParser
from driver_test_db.translation.translation import Translator


@click.group()
def main():
    pass


option_domain = click.option(
    "--domain",
    required=True,
    type=str,
    help="Domain to work with.",
)


option_translate = click.option(
    "--translate",
    is_flag=True,
    show_default=True,
    default=False,
    help="Enable automatic translations.",
)


option_parser = click.option(
    "--parser",
    show_default=True,
    default="dbase",
    type=str,
    help="Parser to use to read tests data.",
)


@main.command()
@option_domain
@option_translate
@option_parser
def prebuild(domain: str, translate: bool, parser: str) -> None:
    languages = [lang for lang in Language]

    builder = PrebuildBuilder()
    builder.set_output_dir(get_prebuild_dir(domain))
    builder.set_parser(get_parser(parser, domain))
    builder.set_languages(languages)

    translator: Translator = None
    if translate:
        translator = Translator(domain)
        translator.load_cache()
    builder.set_translator(translator)

    builder.build()

    # Flush translator's cache
    if translator:
        translator.save_cache()


@main.command()
@option_domain
def build(domain: str) -> None:
    languages = [lang for lang in Language]
    prebuild_dir = get_prebuild_dir(domain)

    builder = DatabaseBuilder()
    builder.set_languages(languages)
    builder.set_prebuid_tests(PrebuildBuilder.load_tests(prebuild_dir))
    builder.set_prebuild_questions(PrebuildBuilder.load_questions(prebuild_dir))
    builder.build()


def get_parser(parser: str, domain: str) -> Parser:
    if parser == "dbase":
        return DatabaseParser(f"data/{domain}/main.db")
    elif parser == "gn":
        return USADatabaseParser()
    raise Exception(f"Unknown parser '{parser}'")


def get_prebuild_dir(domain: str):
    return f"output/{domain}/prebuild"
