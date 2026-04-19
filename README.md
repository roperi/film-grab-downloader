# Film Grab Downloader

Film Grab Downloader is a Python script that facilitates the downloading and optional extraction of movie galleries from film-grab.com.

## Features

- Download and extract movie galleries from film-grab.com
- Extract all zip files in their respective folders
- Automatically delete zip files after successful extraction
- Command-line interface for easy usage
- Specify the movie list JSON file and output directory as command-line arguments
- Optional flag to indicate whether to extract downloaded files
- Parallel downloads using multiprocessing

## Installation

### Option 1: Using pip (recommended)

```bash
git clone https://github.com/roperi/film-grab-downloader.git
cd film-grab-downloader/

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Install as a package

```bash
pip install -e .
```

This allows you to use the commands `film-grab-download` and `film-grab-extract` from anywhere.


## Create a movie list

Make sure to create a movie list that includes the following keys: `id`, `title` and `url`. The `id` of the movie can be taken from
the download zip file button in the film-grab website.

An example file is provided at `input/movie-list-example.json`:

```json
[
  {
    "title": "25th Hour",
    "url": "https://film-grab.com/2010/11/17/25th-hour/",
    "id": "1482"
  },
  {
    "title": "24 Hour Party People",
    "url": "https://film-grab.com/2013/07/31/24-hour-party-people/",
    "id": "464"
  },
  {
    "title": "10 Cloverfield Lane",
    "url": "https://film-grab.com/2017/03/24/10-cloverfield-lane/",
    "id": "76"
  }
]
```

## Download an already prepared movie list

You can also use a non-updated movie list (contains about 3000 titles):

```bash
pip install gdown
gdown 11bQOupeNBYatGLhm2iZIHljPl65axiNj
```

Once downloaded, move the file to your `input` folder.

## Usage

### Setup directories

```bash
mkdir -p log output input
```

### Download and (optionally) Extract Movie Galleries

```bash
python download_zips.py --movie-list input/movie-list.json --output-dir output --extract
```

#### Command-line Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--movie-list`, `-l` | Yes | Path to the movie list JSON file |
| `--output-dir`, `-o` | No | Output directory (default: `output`) |
| `--extract` | No | Flag to extract downloaded files |

### Extract All Zip Files

```bash
python extract_and_delete_zips.py --target-dir output
```

#### Command-line Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--target-dir` | Yes | Path to folder containing zip files |

## Contributing

Feel free to contribute to this project by submitting issues or pull requests.

### Development Setup

```bash
# Clone and setup
git clone https://github.com/roperi/film-grab-downloader.git
cd film-grab-downloader
python -m venv venv
source venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest test_download_zips.py -v

# Run linting and formatting
ruff check .
ruff format .
```

## License

Copyright 2024 roperi.

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
