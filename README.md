# Film Grab Downloader

Film Grab Downloader is a Python script that facilitates the downloading and optional extraction of movie galleries from film-grab.com. It leverages multiprocessing to improve the efficiency of the download process.

## Installation

1. Create a virtual environment (optional but recommended):
    ```bash
    virtualenv -p ~/pythonroot/bin/python3.10
    source ~/.virtualenvs/film-grab/bin/activate #FilmGrab
    ```

2. Install the required dependencies:
    ```bash
    pip install pandas requests Pyarrow
    ```

## Create a movie list

Make sure to create a movie list that includes the following keys: `id`, 'title` and `url`. 

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


## Usage

### Download and (optionally) Extract Movie Galleries

```bash
usage: download_zips.py [-h] --movie-list MOVIE_LIST [--output-dir OUTPUT_DIR] [--extract]

# Example:
python download_zips.py --movie-list input/movie-list.json --output-dir output --extract
```
Adjust the command-line arguments as needed based on your requirements.

#### Command-line Arguments
* `--movie-list`: Path to the movie list JSON file (required).
* `--output-dir`: Output directory for downloaded and extracted files (default: 'downloads').
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

