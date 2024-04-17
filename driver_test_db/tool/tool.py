#!/usr/bin/env python3

import click
from driver_test_db.util.language import Language
from driver_test_db.util.builder import DatabaseBuilder
from driver_test_db.util.dbase import DriverTestDBase
from driver_test_db.util.fs import prepare_output_dir
from driver_test_db.util.text_overrides import TextOverrides
from driver_test_db.prebuild.prebuild import PrebuildBuilder
from driver_test_db.parser.parser import Parser
from driver_test_db.parser.dbase import DatabaseParser
from driver_test_db.parser.usa import USADatabaseParser
from driver_test_db.parser.tilda import TildaParser
from driver_test_db.parser.songs import SongsParser
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


option_text_overrides = click.option(
    "--text-overrides",
    is_flag=True,
    show_default=True,
    default=False,
    help="Enable original text overrides.",
)


option_parser = click.option(
    "--parser",
    show_default=True,
    default="dbase",
    type=click.Choice(["dbase", "genius", "tilda", "songs"]),
    help="Parser to use to read tests data.",
)


option_data_path = click.option(
    "--data-path",
    required=True,
    type=str,
    help="Source data path.",
)


option_languages = click.option(
    "--languages",
    show_default=True,
    default=f"{','.join([l.name for l in Language])}",
    type=str,
    help="Comma separated list of languages.",
)


option_continue_from_stage = click.option(
    "--continue-from-stage",
    type=click.Choice(["init", "compose", "overrides", "translate"]),
    help="Prebuild stage to continue from.",
)


@main.command()
@option_domain
@option_translate
@option_text_overrides
@option_parser
@option_data_path
@option_continue_from_stage
def prebuild(
    domain: str,
    translate: bool,
    text_overrides: bool,
    parser: str,
    data_path: str,
    continue_from_stage: str | None,
) -> None:
    languages = [lang for lang in Language]

    builder = PrebuildBuilder()
    builder.set_output_dir(get_prebuild_dir(domain))
    builder.set_parser(get_parser(parser, data_path))
    builder.set_languages(languages)

    translator = None
    if translate:
        translator = Translator(domain=domain)
        translator.load_cache()
        builder.set_translator(translator)

    if text_overrides:
        overrides = TextOverrides(domain=domain)
        overrides.load()
        builder.set_overrides(overrides)

    if continue_from_stage:
        builder.set_continue_from_stage(continue_from_stage)

    builder.build()

    # Flush translator's cache
    if translator:
        translator.save_cache()


@main.command()
@option_domain
@option_languages
@option_data_path
def build(domain: str, languages: str, data_path: str) -> None:
    languages_list = get_languages_list(languages)
    prebuild_final_dir = f"{get_prebuild_dir(domain)}/final"
    build_dir = get_build_dir(domain)

    prepare_output_dir(build_dir)

    dbase = DriverTestDBase(f"{build_dir}/main.db")
    dbase.open()

    builder = DatabaseBuilder(data_path)
    builder.set_database(dbase)
    builder.set_languages(languages_list)
    builder.set_prebuild_tests(PrebuildBuilder.load_tests(prebuild_final_dir))
    builder.set_prebuild_questions(PrebuildBuilder.load_questions(prebuild_final_dir))
    builder.build()

    dbase.close()


def get_parser(parser: str, data_path: str) -> Parser:
    if parser == "dbase":
        return DatabaseParser(data_path)
    elif parser == "genius":
        return USADatabaseParser()
    elif parser == "tilda":
        return TildaParser(data_path)
    elif parser == "songs":
        return SongsParser(data_path)
    raise Exception(f"Unknown parser '{parser}'")


def get_prebuild_dir(domain: str):
    return f"output/{domain}/prebuild"


def get_build_dir(domain: str):
    return f"output/{domain}/build"


def get_languages_list(languages: str) -> list[Language]:
    languages_list: list[Language] = []
    for language_name in languages.strip().split(","):
        language = Language.from_name(language_name)
        if not language:
            raise Exception(f"Unknown language: {language_name}")
        languages_list.append(language)
    return languages_list
