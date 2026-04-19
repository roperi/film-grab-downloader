import unittest
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd

from download_zips import (
    download_zip,
    get_opener,
    get_safe_extension,
    get_title_from_id,
    load_proxy_list,
    sanitize_filename,
)


class TestDownloadZipFiles(unittest.TestCase):
    def setUp(self):
        self.movie_list_data = [
            {"id": 1, "title": "Movie1"},
            {"id": 2, "title": "Movie2"},
            {"id": 3, "title": "Movie3"},
        ]
        self.movie_list_df = pd.DataFrame(self.movie_list_data)

    def test_get_title_from_id(self):
        movie_id = 2
        expected_title = "Movie2"
        result = get_title_from_id(movie_id, self.movie_list_df)
        self.assertEqual(result, expected_title)

    @patch("download_zips.os.path.exists")
    @patch("download_zips.open", new_callable=mock_open)
    @patch("download_zips.os.makedirs")
    @patch("download_zips.urllib.request.build_opener")
    def test_download_zip_success_no_extract(
        self, mock_build_opener, mock_makedirs, mock_open_file, mock_exists
    ):
        mock_exists.return_value = False
        mock_response = MagicMock()
        mock_response.read.return_value = b"Test content"
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_opener = MagicMock()
        mock_opener.open.return_value = mock_response
        mock_build_opener.return_value = mock_opener

        args = MagicMock()
        args.output_dir = "test_output"
        args.extract = False

        test_url = "https://film-grab.com/wp-admin/admin-ajax.php?action=download_gallery&gallery_id=2&bwg=0"

        result = download_zip(test_url, self.movie_list_df, args, "Movie2")

        mock_opener.open.assert_called_once()
        mock_makedirs.assert_called_once()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["movie_title"], "Movie2")

    @patch("download_zips.os.path.exists")
    @patch("download_zips.open", new_callable=mock_open)
    @patch("download_zips.os.makedirs")
    @patch("download_zips.urllib.request.build_opener")
    def test_download_zip_skipped_when_exists(
        self, mock_build_opener, mock_makedirs, mock_open_file, mock_exists
    ):
        mock_exists.return_value = True

        args = MagicMock()
        args.output_dir = "test_output"
        args.extract = False

        test_url = "https://film-grab.com/wp-admin/admin-ajax.php?action=download_gallery&gallery_id=2&bwg=0"

        result = download_zip(test_url, self.movie_list_df, args, "Movie2")

        mock_build_opener.assert_not_called()
        self.assertEqual(result["status"], "skipped")

    @patch("download_zips.os.path.exists")
    @patch("download_zips.open", new_callable=mock_open)
    @patch("download_zips.os.makedirs")
    @patch("download_zips.urllib.request.build_opener")
    def test_download_zip_failure(
        self, mock_build_opener, mock_makedirs, mock_open_file, mock_exists
    ):
        mock_exists.return_value = False
        mock_opener = MagicMock()
        mock_opener.open.side_effect = Exception("Connection error")
        mock_build_opener.return_value = mock_opener

        args = MagicMock()
        args.output_dir = "test_output"
        args.extract = False

        test_url = "https://film-grab.com/wp-admin/admin-ajax.php?action=download_gallery&gallery_id=2&bwg=0"

        result = download_zip(test_url, self.movie_list_df, args, "Movie2")

        self.assertEqual(result["status"], "failure")
        self.assertIn("error_message", result)

    @patch("download_zips.zipfile.ZipFile")
    @patch("download_zips.os.path.exists")
    @patch("download_zips.open", new_callable=mock_open)
    @patch("download_zips.os.makedirs")
    @patch("download_zips.urllib.request.build_opener")
    def test_download_zip_success_with_extract(
        self, mock_build_opener, mock_makedirs, mock_open_file, mock_exists, mock_zipfile
    ):
        mock_exists.return_value = False
        mock_response = MagicMock()
        mock_response.read.return_value = b"Test content"
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_opener = MagicMock()
        mock_opener.open.return_value = mock_response
        mock_build_opener.return_value = mock_opener

        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance

        args = MagicMock()
        args.output_dir = "test_output"
        args.extract = True

        test_url = "https://film-grab.com/wp-admin/admin-ajax.php?action=download_gallery&gallery_id=2&bwg=0"

        result = download_zip(test_url, self.movie_list_df, args, "Movie2")

        mock_opener.open.assert_called_once()
        mock_makedirs.assert_called_once()
        mock_zipfile.assert_called_once()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["movie_title"], "Movie2")

    @patch("download_zips.os.path.exists")
    @patch("download_zips.open", new_callable=mock_open)
    @patch("download_zips.os.makedirs")
    @patch("download_zips.urllib.request.build_opener")
    def test_download_zip_with_proxy(
        self, mock_build_opener, mock_makedirs, mock_open_file, mock_exists
    ):
        mock_exists.return_value = False
        mock_response = MagicMock()
        mock_response.read.return_value = b"Test content"
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_opener = MagicMock()
        mock_opener.open.return_value = mock_response
        mock_build_opener.return_value = mock_opener

        args = MagicMock()
        args.output_dir = "test_output"
        args.extract = False

        test_url = "https://film-grab.com/wp-admin/admin-ajax.php?action=download_gallery&gallery_id=2&bwg=0"
        proxy_url = "http://proxy.example.com:8080"

        result = download_zip(test_url, self.movie_list_df, args, "Movie2", proxy_url)

        # Verify opener was created (proxy would be configured in build_opener)
        mock_build_opener.assert_called()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["movie_title"], "Movie2")


class TestFilenameSanitization(unittest.TestCase):
    """Test machine-friendly filename conversion."""

    def test_sanitize_filename_lowercase(self):
        self.assertEqual(sanitize_filename("MOVIE.JPG"), "movie.jpg")

    def test_sanitize_filename_spaces(self):
        self.assertEqual(sanitize_filename("my movie.jpg"), "my-movie.jpg")

    def test_sanitize_filename_unicode(self):
        self.assertEqual(sanitize_filename("Amélie.jpg"), "amelie.jpg")

    def test_sanitize_filename_special_chars(self):
        self.assertEqual(sanitize_filename("What's New?"), "whats-new")

    def test_sanitize_filename_multiple_hyphens(self):
        self.assertEqual(sanitize_filename("my---movie"), "my-movie")

    def test_sanitize_filename_leading_trailing(self):
        self.assertEqual(sanitize_filename("---movie.jpg---"), "movie.jpg")

    def test_sanitize_filename_underscores(self):
        self.assertEqual(sanitize_filename("my_movie_name"), "my-movie-name")

    def test_sanitize_filename_empty(self):
        self.assertEqual(sanitize_filename(""), "unnamed")

    def test_get_safe_extension_jpg(self):
        self.assertEqual(get_safe_extension("image.jpg"), ".jpg")

    def test_get_safe_extension_jpeg_normalized(self):
        self.assertEqual(get_safe_extension("image.JPEG"), ".jpg")

    def test_get_safe_extension_png(self):
        self.assertEqual(get_safe_extension("image.PNG"), ".png")

    def test_get_safe_extension_default(self):
        self.assertEqual(get_safe_extension("noextension"), ".jpg")


class TestProxyFunctions(unittest.TestCase):
    @patch("download_zips.os.path.exists")
    def test_load_proxy_list(self, mock_exists):
        mock_exists.return_value = True

        # Create a mock file with content
        import io

        mock_file = io.StringIO(
            "http://proxy1.example.com:8080\n"
            "http://proxy2.example.com:3128\n"
            "# This is a comment\n"
            "\n"
        )

        with patch("builtins.open", return_value=mock_file):
            proxies = load_proxy_list("proxies.txt")

        self.assertEqual(len(proxies), 2)
        self.assertEqual(proxies[0], "http://proxy1.example.com:8080")
        self.assertEqual(proxies[1], "http://proxy2.example.com:3128")

    def test_load_proxy_list_file_not_exists(self):
        proxies = load_proxy_list("nonexistent.txt")
        self.assertEqual(len(proxies), 0)

    @patch("download_zips.urllib.request.ProxyHandler")
    @patch("download_zips.urllib.request.HTTPSHandler")
    @patch("download_zips.urllib.request.build_opener")
    def test_get_opener_with_proxy(self, mock_build_opener, mock_https_handler, mock_proxy_handler):
        mock_proxy = MagicMock()
        mock_https = MagicMock()
        mock_proxy_handler.return_value = mock_proxy
        mock_https_handler.return_value = mock_https

        get_opener("http://proxy.example.com:8080")

        mock_proxy_handler.assert_called_once_with(
            {
                "http": "http://proxy.example.com:8080",
                "https": "http://proxy.example.com:8080",
            }
        )
        mock_build_opener.assert_called()

    @patch("download_zips.urllib.request.HTTPSHandler")
    @patch("download_zips.urllib.request.build_opener")
    def test_get_opener_no_proxy(self, mock_build_opener, mock_https_handler):
        mock_https = MagicMock()
        mock_https_handler.return_value = mock_https

        get_opener()

        mock_https_handler.assert_called_once()
        mock_build_opener.assert_called_once()


if __name__ == "__main__":
    unittest.main()
