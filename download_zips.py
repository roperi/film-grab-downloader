import os
import sys
import argparse
import zipfile
import requests
import pandas as pd
from multiprocessing import Pool, cpu_count
from functools import partial
from io import BytesIO
import logging


# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Get paths
scriptdir = os.path.dirname(os.path.abspath(__file__))
mypath = os.path.join(scriptdir, 'log', 'download.log')
# Create file handler which logs even DEBUG messages
fh = logging.FileHandler(mypath)
fh.setLevel(logging.DEBUG)
# Create console handler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('[%(levelname)s. %(name)s, (line #%(lineno)d) - %(asctime)s] %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add handlers to logger
logger.addHandler(fh)
logger.addHandler(ch)


# Functions

def get_title_from_id(movie_id, movie_list_df):
    """
    Get the movie title from the movie list based on the movie ID.

    Args:
        movie_id (int): The movie ID.
        movie_list_df (pd.DataFrame): The DataFrame containing movie information.

    Returns:
        str: The movie title.
    """
    return movie_list_df.loc[movie_list_df['id'] == movie_id, 'title'].item()


def download_zip(url, movie_list_df, args):
    """
    Download and optionally extract a movie gallery from film-grab.com.

    Args:
        url (str): The URL of the movie gallery.
        args (argparse.Namespace): Command-line arguments.
        movie_list_df (pd.DataFrame): The DataFrame containing movie information.

    Returns:
        dict: A dictionary containing information about the download and extraction.
              - 'status': Either 'success' or 'failure' based on the outcome.
              - 'movie_title': The title of the movie.
              - 'error_message' (optional): The error message if the download or extraction fails.
    """
    try:
        movie_id = int(url.split('gallery_id=')[1].split('&bwg=')[0])
        title = get_title_from_id(movie_id, movie_list_df)

        # Check if the destination zip file already exists
        zip_file_path = os.path.join(args.output_dir, title, f"{title}.zip")
        if os.path.exists(zip_file_path):
            logging.info(f"`{title}` has already been downloaded. Skipping.")
            return {'status': 'skipped', 'movie_title': title}

        logger.info(f'Attempting to download zip file for `{title}`')
        response = requests.get(url)

        # Create output directory if it doesn't exist
        output_dir = os.path.join(args.output_dir, title)
        os.makedirs(output_dir, exist_ok=True)

        # Save the zip file to the correct location
        zip_file_path = os.path.join(output_dir, f"{title}.zip")
        with open(zip_file_path, 'wb') as zip_file:
            zip_file.write(response.content)
        logging.info(f" Downloaded `{title.title()}`")

        if args.extract:
            logging.info(f'Extracting `{title.title()}')
            z = zipfile.ZipFile(BytesIO(response.content))
            z.extractall(f"{title}/")
            logging.info(f" Extracted {title.title()}")
            z.close()
        return {'status': 'success', 'movie_title': title}

    except Exception as e:
        logging.error(e)
        return {'status': 'failure', 'error_message': str(e)}


def main():
    """
    Main function to handle command-line arguments and initiate the download process.

    Returns:
        None
    """
    parser = argparse.ArgumentParser(description='Download and extract movie galleries from film-grab.com.')
    parser.add_argument('--movie-list', '-l', required=True, help='Path to the movie list JSON file')
    parser.add_argument(
        '--output-dir', '-o', default='output', help='Output directory for downloaded and extracted files')
    parser.add_argument(
        '--extract', action='store_true', help='Flag to indicate whether to extract the downloaded files')
    args = parser.parse_args()

    movie_list_df = pd.read_json(args.movie_list)

    urls = [
        (f'https://film-grab.com/wp-admin/admin-ajax.php?action=download_gallery&gallery_id={gallery_id}&bwg='
         f'0&type=gallery&tag_input_name=bwg_tag_id_bwg_thumbnails_masonry_0&bwg_tag_id_bwg_thumbnails_masonry_0&tag='
         f'0&bwg_search_0')
        for gallery_id in movie_list_df['id']
    ]

    logging.info(f"There are {cpu_count()} CPUs on this machine ")

    pool = Pool(cpu_count())
    download_func = partial(download_zip, movie_list_df=movie_list_df, args=args)
    results = pool.starmap(download_func, zip(urls))
    pool.close()
    pool.join()

    print("\n=== Status Report ===")
    for result in results:
        movie_title = result.get('movie_title', 'N/A')  # Use 'N/A' if 'movie_title' is not present
        status = result.get('status', 'Unknown')  # Use 'Unknown' if 'status' is not present
        error_message = result.get('error_message', None)

        print(f"Movie: {movie_title}, Status: {status}")
        if error_message:
            print(f"  Error Message: {error_message}")
        print("=====================")


if __name__ == "__main__":
    main()
