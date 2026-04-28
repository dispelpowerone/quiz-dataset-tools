# AGENT.md

## Project Overview

**quiz-dataset-tools** is a Python toolset for managing multilingual quiz/test datasets (primarily driving tests). It handles parsing source data, translating questions into multiple languages via GPT/DeepL, building SQLite databases, and serving content through a FastAPI server.

## Tech Stack

- **Python 3.12** with `uv` as package manager
- **Click** CLI framework (entry point: `quiz_dataset_tools/tool/tool.py`)
- **SQLAlchemy** for database ORM
- **FastAPI + Uvicorn** for the HTTP server
- **OpenAI API** for GPT-based translations and paraphrasing
- **DeepL** as alternate translation backend
- **Pillow** for image processing
- **hatchling** build backend

## Key Commands

```bash
make all        # Run mypy + black + tests
make mypy       # Type checking
make fmt        # Format with black
make test       # Run unittest suite (TQDM_DISABLE=1)
make server     # Start FastAPI dev server on 0.0.0.0:8000
make install    # pip install the package
```

## Project Structure

```
quiz_dataset_tools/
├── tool/          # CLI commands (click): prebuild-translate, build, etc.
├── parser/        # Parsers for various data sources (dbase, USA states, tilda, songs)
├── prebuild/      # Prebuild pipeline: translate, override, doctor stages
├── build/         # Final database builder (SQLite output)
├── server/        # FastAPI server with models/ and services/
├── paraphrase/    # GPT-based question paraphrasing
├── util/          # Shared utilities (language, dbase, gpt, image, cache, etc.)
├── config.py      # API keys configuration
└── constants.py   # Project constants
tests/             # unittest-based tests (discover pattern)
output/            # Generated domain outputs (prebuild + build artifacts)
```

## Pipeline Flow

1. **Parse** – Read source questions from various formats (DB, web scraping, etc.)
2. **Prebuild Translate** – Translate content into target languages
3. **Prebuild Override** – Apply manual text overrides
4. **Build** – Compile final SQLite database (`main.db`) per domain
5. **Serve** – Expose data via FastAPI REST API

## Supported Languages

EN (English), FR (French), ZH (Chinese), ES (Spanish), RU (Russian), FA (Farsi), PA (Punjabi), PT (Portuguese-BR)

## Conventions

- Type checking with `mypy` (strict enough to be in the default `make all`)
- Formatting with `black`
- Tests use Python's built-in `unittest` framework
- Domain-based organization: each quiz domain gets its own `output/domains/{domain}/` directory
- Translation caching to avoid redundant API calls
