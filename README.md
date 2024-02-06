# Film Grab Downloader

Film Grab Downloader is a Python script that facilitates the downloading and optional extraction of movie galleries from film-grab.com. 

## Features
- Download and extract movie galleries from film-grab.com.
- Extract all zip files in their respective folders.
- Automatically delete zip files after successful extraction.
- Command-line interface for easy usage.
- Specify the movie list JSON file and output directory as command-line arguments.
- Optional flag to indicate whether to extract downloaded files.

## Installation

1. Clone repository
```commandline
git clone https://github.com/roperi/film-grab-downloader.git
cd film-grab-downloader/
```

2. Create a virtual environment and activate it (optional but recommended):
    ```bash
    virtualenv -p ~/pythonroot/bin/python3.10  # example with python 3.10
    source ~/.virtualenvs/film-grab/bin/activate # activate env
    ```

3. Install the required dependencies:
    ```bash
    pip install pandas requests Pyarrow
    ```

## Create a movie list

Make sure to create a movie list that includes the following keys: `id`, 'title` and `url`. The `id` can be taken from 
the download zip file button in the film-grab website.

Example:

```
# input/movie-list.json
[
  {
    "title":"25th Hour",
    "url":"https://film-grab.com/2010/11/17/25th-hour/",
    "id":"1482"
  },
  {
    "title":"24 Hour Party People",
    "url":"https://film-grab.com/2013/07/31/24-hour-party-people/",
    "id":"464"
  },
  {
    "title":"10 Cloverfield Lane",
    "url":"https://film-grab.com/2017/03/24/10-cloverfield-lane/",
    "id":"76"
  }
]

```

## Download an already prepared movie list

You can also use a non-updated movie list (contains about 3000 titles):

```commandline
pip install gdown
gdown 11bQOupeNBYatGLhm2iZIHljPl65axiNj
```
Once downloaded it, move the file to your input folder.


## Usage

### Create some useful folders 
```commandline
cd film-grab-downloader/
mkdir log output input
```

### Download and (optionally) Extract Movie Galleries

```bash
usage: download_zips.py [-h] --movie-list MOVIE_LIST [--output-dir OUTPUT_DIR] [--extract]

# Example:
python download_zips.py --movie-list input/movie-list.json --output-dir output --extract
```
Adjust the command-line arguments as needed based on your requirements.

#### Command-line Arguments
* `--movie-list`: Path to the movie list JSON file (required).
* `--output-dir`: Output directory for downloaded and extracted files (default: 'output').
* `--extract`: Flag to indicate whether to extract the downloaded files (optional).


### Extract All Zip Files
```bash
usage: extract_zips.py [-h] --output-dir OUTPUT_DIR

# Example
python extract_zips.py --output-dir output
```
### Command-line arguments

- `--output-dir`: Path to the output folder containing zip files for extraction.

Adjust the command-line arguments as needed based on your requirements.

## Contributing
Feel free to contribute to this project by submitting issues or pull requests.

## License
This project is licensed under the MIT License.


## TODO
- Fix unit tests