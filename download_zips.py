import argparse
import logging
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
import zipfile
from io import BytesIO

import pandas as pd

# Create SSL context for HTTPS requests
_ssl_context = ssl.create_default_context()

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def load_proxy_list(proxy_file):
    """
    Load proxy list from a text file.

    Args:
        proxy_file (str): Path to file containing one proxy per line.

    Returns:
        list: List of proxy URLs.
    """
    if not proxy_file or not os.path.exists(proxy_file):
        return []

    with open(proxy_file, "r") as f:
        proxies = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return proxies


def get_opener(proxy_url=None):
    """
    Create a URL opener with optional proxy support.

    Args:
        proxy_url (str, optional): Proxy URL (e.g., 'http://proxy:8080').

    Returns:
        urllib.request.OpenerDirector: Configured opener.
    """
    handlers = []

    if proxy_url:
        proxy_handler = urllib.request.ProxyHandler(
            {
                "http": proxy_url,
                "https": proxy_url,
            }
        )
        handlers.append(proxy_handler)

    # Add SSL context handler
    https_handler = urllib.request.HTTPSHandler(context=_ssl_context)
    handlers.append(https_handler)

    opener = urllib.request.build_opener(*handlers)
    return opener


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


def download_zip(url, movie_list_df, args, title, proxy_url=None):
    """
    Download and optionally extract a movie gallery from film-grab.com.

    Args:
        url (str): The URL of the movie gallery.
        movie_list_df (pd.DataFrame): The DataFrame containing movie information.
        args (argparse.Namespace): Command-line arguments.
        title (str): The movie title (pre-computed to avoid lookup issues).
        proxy_url (str, optional): Proxy URL to use for this request.

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

        logger.info(
            f"Attempting to download zip file for `{title}`"
            + (f" via proxy {proxy_url}" if proxy_url else "")
        )
        # Use urllib.request (built-in) to avoid external dependencies
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        opener = get_opener(proxy_url)
        try:
            with opener.open(req, timeout=30) as response:
                content = response.read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                logger.warning("Rate limited (429). Waiting 10 seconds before retrying...")
                time.sleep(10)
                with opener.open(req, timeout=30) as response:
                    content = response.read()
            else:
                raise

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
    parser.add_argument(
        "--proxy-list",
        "-p",
        default=None,
        help="Path to text file containing proxy URLs (one per line)",
    )
    args = parser.parse_args()

    # Load proxy list if provided
    proxies = load_proxy_list(args.proxy_list)
    if proxies:
        logger.info(f"Loaded {len(proxies)} proxies from {args.proxy_list}")

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
    for i, (url, gallery_id) in enumerate(zip(urls, movie_list_df["id"])):
        title = movie_list_df.loc[movie_list_df["id"] == gallery_id, "title"].item()
        # Rotate through proxies if available
        proxy_url = proxies[i % len(proxies)] if proxies else None
        result = download_zip(url, movie_list_df, args, title, proxy_url)
        results.append(result)
        # Add delay between downloads to avoid rate limiting
        if i < len(urls) - 1:
            time.sleep(1)

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
