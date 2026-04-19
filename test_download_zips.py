import unittest
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd

from download_zips import download_zip, get_title_from_id


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
    @patch("download_zips.requests.Session")
    def test_download_zip_success_no_extract(
        self, mock_session_class, mock_makedirs, mock_open_file, mock_exists
    ):
        mock_exists.return_value = False
        mock_response = MagicMock()
        mock_response.content = b"Test content"

        # Set up Session mock
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        args = MagicMock()
        args.output_dir = "test_output"
        args.extract = False

        test_url = "https://film-grab.com/wp-admin/admin-ajax.php?action=download_gallery&gallery_id=2&bwg=0"

        result = download_zip(test_url, self.movie_list_df, args, "Movie2")

        mock_session.get.assert_called_once_with(test_url, timeout=30)
        mock_response.raise_for_status.assert_called_once()
        mock_makedirs.assert_called_once()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["movie_title"], "Movie2")

    @patch("download_zips.os.path.exists")
    @patch("download_zips.open", new_callable=mock_open)
    @patch("download_zips.os.makedirs")
    @patch("download_zips.requests.Session")
    def test_download_zip_skipped_when_exists(
        self, mock_session_class, mock_makedirs, mock_open_file, mock_exists
    ):
        mock_exists.return_value = True

        args = MagicMock()
        args.output_dir = "test_output"
        args.extract = False

        test_url = "https://film-grab.com/wp-admin/admin-ajax.php?action=download_gallery&gallery_id=2&bwg=0"

        result = download_zip(test_url, self.movie_list_df, args, "Movie2")

        mock_session_class.assert_not_called()
        self.assertEqual(result["status"], "skipped")

    @patch("download_zips.os.path.exists")
    @patch("download_zips.open", new_callable=mock_open)
    @patch("download_zips.os.makedirs")
    @patch("download_zips.requests.Session")
    def test_download_zip_failure(
        self, mock_session_class, mock_makedirs, mock_open_file, mock_exists
    ):
        mock_exists.return_value = False

        # Set up Session mock to raise an exception
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session
        mock_session.get.side_effect = Exception("Connection error")
        mock_session_class.return_value = mock_session

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
    @patch("download_zips.requests.Session")
    def test_download_zip_success_with_extract(
        self, mock_session_class, mock_makedirs, mock_open_file, mock_exists, mock_zipfile
    ):
        mock_exists.return_value = False
        mock_response = MagicMock()
        mock_response.content = b"Test content"

        # Set up Session mock
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        # Set up ZipFile mock with proper context manager support
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance

        args = MagicMock()
        args.output_dir = "test_output"
        args.extract = True

        test_url = "https://film-grab.com/wp-admin/admin-ajax.php?action=download_gallery&gallery_id=2&bwg=0"

        result = download_zip(test_url, self.movie_list_df, args, "Movie2")

        mock_session.get.assert_called_once_with(test_url, timeout=30)
        mock_response.raise_for_status.assert_called_once()
        mock_makedirs.assert_called_once()
        mock_zipfile.assert_called_once()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["movie_title"], "Movie2")


if __name__ == "__main__":
    unittest.main()
