# AGENTS.md

```text
film-grab-downloader/
├── README.md                                   user documentation and installation guide
├── LICENSE                                     MIT license
├── pyproject.toml                              package metadata, dependencies, tool config
├── requirements.txt                            minimal runtime dependencies
├── AGENTS.md                                   repo tree
│
├── .github/
│   └── workflows/
│       └── ci.yml                              GitHub Actions CI (test + lint on push/PR)
│
├── .pre-commit-config.yaml                     pre-commit hooks (ruff, formatting, hygiene)
├── .editorconfig                               editor consistency rules
├── .gitignore                                  git ignore patterns
│
├── input/
│   ├── movie-list-example.json                 example movie list with 3 sample entries
│   └── proxy-list-example.txt                  example proxy list template
│
├── log/                                        runtime log files (download.log)
├── output/                                     downloaded and extracted movie galleries
│
├── download_zips.py                            main downloader: CLI, HTTP download, extraction
├── extract_and_delete_zips.py                  standalone zip extractor
├── test_download_zips.py                       unit tests (22 tests)
│
└── venv/                                       Python virtual environment (git-ignored)
```
