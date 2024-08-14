#!/usr/bin/env python3

import click
from quiz_dataset_tools.util.language import Language
from quiz_dataset_tools.util.builder import DatabaseBuilder
from quiz_dataset_tools.util.dbase import DriverTestDBase
from quiz_dataset_tools.util.fs import prepare_output_dir
from quiz_dataset_tools.util.text_overrides import TextOverrides
from quiz_dataset_tools.prebuild.prebuild import PrebuildBuilder
from quiz_dataset_tools.parser.parser import Parser
from quiz_dataset_tools.parser.dbase import DatabaseParser
from quiz_dataset_tools.parser.usa import (
    USADatabaseNYParser,
    USADatabaseTXParser,
    USADatabaseCAParser,
)
from quiz_dataset_tools.parser.tilda import TildaParser
from quiz_dataset_tools.parser.songs import SongsParser
from quiz_dataset_tools.translation.translation import Translator


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
    type=click.Choice(
        ["dbase", "genius-ny", "genius-tx", "genius-ca", "tilda", "songs"]
    ),
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


option_fallback_language = click.option(
    "--fallback-language",
    type=click.Choice([l.name for l in Language]),
    help="Fallback localization.",
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
def prebuild_init(
    domain: str,
    translate: bool,
    text_overrides: bool,
    parser: str,
    data_path: str,
    continue_from_stage: str | None,
) -> None:
    languages = [lang for lang in Language]

    builder = PrebuildBuilder()
    builder.set_data_path(data_path)
    builder.set_output_dir(get_prebuild_dir(domain))
    builder.set_parser(get_parser(parser, data_path))
    builder.set_languages(languages)

    translator = None
    if translate:
        translator = Translator(domain=domain)
        translator.load_cache()
        builder.set_translator(translator)

    if text_overrides:
        overrides = TextOverrides(data_path=data_path)
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
def prebuild_translate(
    domain: str,
    languages: str,
) -> None:
    translator = Translator(domain=domain)
    translator.load_cache()

    builder = PrebuildBuilder()
    builder.set_output_dir(get_prebuild_dir(domain))
    builder.set_languages(get_languages_list(languages))
    builder.set_translator(translator)
    builder.run_translate()

    translator.save_cache()


@main.command()
@option_domain
@option_data_path
def prebuild_override(
    domain: str,
    data_path: str,
) -> None:
    languages = [lang for lang in Language]

    overrides = TextOverrides(data_path=data_path)
    overrides.load()

    builder = PrebuildBuilder()
    builder.set_output_dir(get_prebuild_dir(domain))
    builder.set_languages(languages)
    builder.set_overrides(overrides)
    builder.run_override()


@main.command()
@option_domain
@option_languages
@option_data_path
def prebuild_dump_overrides(
    domain: str,
    languages: str,
    data_path: str,
) -> None:
    overrides = TextOverrides(data_path=data_path)
    overrides.load()

    builder = PrebuildBuilder()
    builder.set_output_dir(get_prebuild_dir(domain))
    builder.set_languages(get_languages_list(languages))
    builder.set_overrides(overrides)
    builder.run_dump_overrides()

    overrides.save()


@main.command()
@option_domain
def prebuild_doctor(
    domain: str,
) -> None:
    builder = PrebuildBuilder()
    builder.set_output_dir(get_prebuild_dir(domain))
    builder.run_doctor()


@main.command()
@option_domain
@option_languages
@option_fallback_language
@option_data_path
def build(domain: str, languages: str, fallback_language: str, data_path: str) -> None:
    prebuild_data_dir = f"{get_prebuild_dir(domain)}/data"
    build_dir = get_build_dir(domain)

    prepare_output_dir(build_dir)

    dbase = DriverTestDBase(f"{build_dir}/main.db")
    dbase.open()

    builder = DatabaseBuilder(data_path, build_dir)
    builder.set_database(dbase)
    builder.set_languages(get_languages_list(languages))
    if fallback_language:
        builder.set_fallback_language(get_language(fallback_language))
    builder.set_prebuild_tests(PrebuildBuilder.load_tests(prebuild_data_dir))
    builder.set_prebuild_questions(PrebuildBuilder.load_questions(prebuild_data_dir))
    builder.build()

    dbase.close()


def get_parser(parser: str, data_path: str) -> Parser:
    if parser == "dbase":
        return DatabaseParser(data_path)
    elif parser == "genius-ny":
        return USADatabaseNYParser()
    elif parser == "genius-tx":
        return USADatabaseTXParser()
    elif parser == "genius-ca":
        return USADatabaseCAParser()
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
        languages_list.append(get_language(language_name))
    return languages_list


def get_language(language_name: str) -> Language:
    language = Language.from_name(language_name)
    if not language:
        raise Exception(f"Unknown language: {language_name}")
    return language
