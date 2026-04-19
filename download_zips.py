import argparse
import logging
import os
import sys
import zipfile
from io import BytesIO
from threading import Lock

import pandas as pd
import requests

# Lock for sequential downloads
_download_lock = Lock()

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def setup_logging():
    """Set up logging handlers. Call this once at application startup."""
    # Guard against adding handlers multiple times
    if logger.handlers:
        return

    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(script_dir, "log", "download.log")

    # Create log directory if it doesn't exist
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # Create file handler which logs even DEBUG messages
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter(
        "[%(levelname)s. %(name)s, (line #%(lineno)d) - %(asctime)s] %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


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
    return movie_list_df.loc[movie_list_df["id"] == movie_id, "title"].item()


def download_zip(url, movie_list_df, args, title):
    """
    Download and optionally extract a movie gallery from film-grab.com.

    Args:
        url (str): The URL of the movie gallery.
        movie_list_df (pd.DataFrame): The DataFrame containing movie information.
        args (argparse.Namespace): Command-line arguments.
        title (str): The movie title (pre-computed to avoid lookup issues).

    Returns:
        dict: A dictionary containing information about the download and extraction.
              - 'status': Either 'success' or 'failure' based on the outcome.
              - 'movie_title': The title of the movie.
              - 'error_message' (optional): The error message if the download or extraction fails.
    """
    try:
        # Check if the destination zip file already exists
        zip_file_path = os.path.join(args.output_dir, title, f"{title}.zip")
        if os.path.exists(zip_file_path):
            logger.info(f"`{title}` has already been downloaded. Skipping.")
            return {"status": "skipped", "movie_title": title}

        logger.info(f"Attempting to download zip file for `{title}`")
        # Use a fresh session per request and lock to avoid race conditions
        with _download_lock:
            with requests.Session() as session:
                response = session.get(url, timeout=30)
                response.raise_for_status()
                content = response.content

        # Create output directory if it doesn't exist
        output_dir = os.path.join(args.output_dir, title)
        os.makedirs(output_dir, exist_ok=True)

        # Save the zip file to the correct location
        zip_file_path = os.path.join(output_dir, f"{title}.zip")
        with open(zip_file_path, "wb") as zip_file:
            zip_file.write(content)
        logger.info(f"Downloaded `{title}`")

        if args.extract:
            logger.info(f"Extracting `{title}`")
            z = zipfile.ZipFile(BytesIO(content))
            z.extractall(output_dir)
            logger.info(f"Extracted `{title}`")
            z.close()
        return {"status": "success", "movie_title": title}

    except Exception as e:
        logger.exception("Failed to download or extract movie gallery")
        return {"status": "failure", "error_message": str(e)}


def main():
    """
    Main function to handle command-line arguments and initiate the download process.

    Returns:
        None
    """
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Download and extract movie galleries from film-grab.com."
    )
    parser.add_argument(
        "--movie-list", "-l", required=True, help="Path to the movie list JSON file"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="output",
        help="Output directory for downloaded and extracted files",
    )
    parser.add_argument(
        "--extract",
        action="store_true",
        help="Flag to indicate whether to extract the downloaded files",
    )
    args = parser.parse_args()

    movie_list_df = pd.read_json(args.movie_list)

    urls = [
        (
            f"https://film-grab.com/wp-admin/admin-ajax.php?action=download_gallery&gallery_id={gallery_id}&bwg="
            f"0&type=gallery&tag_input_name=bwg_tag_id_bwg_thumbnails_masonry_0&bwg_tag_id_bwg_thumbnails_masonry_0&tag="
            f"0&bwg_search_0"
        )
        for gallery_id in movie_list_df["id"]
    ]

    logger.info(f"Downloading {len(urls)} movies sequentially to avoid race conditions")

    # Download sequentially to ensure each request gets the correct response
    results = []
    for url, gallery_id in zip(urls, movie_list_df["id"]):
        title = movie_list_df.loc[movie_list_df["id"] == gallery_id, "title"].item()
        result = download_zip(url, movie_list_df, args, title)
        results.append(result)

    print("\n=== Status Report ===")
    for result in results:
        movie_title = result.get("movie_title", "N/A")  # Use 'N/A' if 'movie_title' is not present
        status = result.get("status", "Unknown")  # Use 'Unknown' if 'status' is not present
        error_message = result.get("error_message", None)

        print(f"Movie: {movie_title}, Status: {status}")
        if error_message:
            print(f"  Error Message: {error_message}")
        print("=====================")


if __name__ == "__main__":
    main()
