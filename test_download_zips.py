import unittest
from unittest.mock import patch, MagicMock
from multiprocessing import cpu_count
import pandas as pd
from download_zips import get_title_from_id, download_zip, main


class TestDownloadZipFiles(unittest.TestCase):

    def setUp(self):
        # Set up some test data
        self.movie_list_data = [{'id': 1, 'title': 'Movie1'},
                                {'id': 2, 'title': 'Movie2'},
                                {'id': 3, 'title': 'Movie3'}]
        self.movie_list_df = pd.DataFrame(self.movie_list_data)

    def test_get_title_from_id(self):
        # Test if get_title_from_id returns the correct title
        movie_id = 2
        expected_title = 'Movie2'
        result = get_title_from_id(movie_id, self.movie_list_df)
        self.assertEqual(result, expected_title)

    @patch('requests.get')
    @patch('zipfile.ZipFile')
    def test_download_zip_success(self, mock_zipfile, mock_requests):
        # Mocking requests.get
        mock_response = MagicMock()
        mock_response.content = b'Test content'
        mock_requests.return_value = mock_response

        # Mocking zipfile.ZipFile
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value = mock_zip_instance

        # Set up arguments
        args = MagicMock()
        args.movie_list = 'input/movie-list-1.json'
        args.output_dir = 'test_output'
        args.extract = True

        # Set up URL
        test_url = 'https://film-grab.com/test-gallery'

        # Call the function
        result = download_zip(args, test_url, args)

        # Assertions
        mock_requests.assert_called_once_with(test_url)
        mock_zipfile.assert_called_once_with(mock_response.content)
        mock_zip_instance.extractall.assert_called_once_with(f"{args.output_dir}/MockMovie/")
        self.assertEqual(result, {'status': 'success', 'movie_title': 'MockMovie'})

    @patch('requests.get', side_effect=Exception("Mocked exception"))
    def test_download_zip_failure(self, mock_requests):
        # Set up arguments
        args = MagicMock()
        args.movie_list = 'input/movie-list-1.json'
        args.output_dir = 'test_output'
        args.extract = True

        # Set up URL
        test_url = 'https://film-grab.com/test-gallery'

        # Read the movie_list JSON file and construct a Pandas DataFrame
        movie_list = pd.read_json(args.movie_list)

        # Call the function
        try:
            download_zip(args, movie_list, args)  # Pass the correct arguments
        except Exception as e:
            print(f"Exception caught: {e}")
            self.assertEqual(str(e), 'Mocked exception')
        else:
            self.fail("Exception not raised")

        # Assertions
        mock_requests.assert_called_once_with(test_url)
        print(f"requests.get call count: {mock_requests.call_count}")


class TestMainFunction(unittest.TestCase):

    @patch('argparse.ArgumentParser.parse_args')
    @patch('pandas.read_json')
    @patch('download_zips.download_zip')
    @patch('multiprocessing.Pool')
    @patch('logging.info')
    def test_main(self, mock_logging, mock_pool, mock_download_zip, mock_read_json, mock_parse_args):
        # Set up mocks and return values
        mock_args = MagicMock()
        mock_args.movie_list = 'input/movie-list-1.json'
        mock_args.output_dir = 'test_output'
        mock_args.extract = True
        mock_parse_args.return_value = mock_args

        # Create a DataFrame with 'id' column
        mock_movie_list_df = pd.read_json('input/movie-list-1.json')
        mock_read_json.return_value = mock_movie_list_df

        mock_urls = [
            'https://film-grab.com/wp-admin/admin-ajax.php?action=download_gallery&gallery_id=1&bwg=0&type=gallery&tag_input_name=bwg_tag_id_bwg_thumbnails_masonry_0&bwg_tag_id_bwg_thumbnails_masonry_0&tag=0&bwg_search_0',
            'https://film-grab.com/wp-admin/admin-ajax.php?action=download_gallery&gallery_id=2&bwg=0&type=gallery&tag_input_name=bwg_tag_id_bwg_thumbnails_masonry_0&bwg_tag_id_bwg_thumbnails_masonry_0&tag=0&bwg_search_0',
            'https://film-grab.com/wp-admin/admin-ajax.php?action=download_gallery&gallery_id=3&bwg=0&type=gallery&tag_input_name=bwg_tag_id_bwg_thumbnails_masonry_0&bwg_tag_id_bwg_thumbnails_masonry_0&tag=0&bwg_search_0',
        ]

        # Call the main function
        main()

        # Assertions
        mock_read_json.assert_called_once_with(mock_args.movie_list)
        mock_logging.assert_called_once_with(f"There are {cpu_count()} CPUs on this machine ")

        # Check that Pool and map are called with the correct arguments
        mock_pool.assert_called_once_with(cpu_count())
        mock_pool_instance = mock_pool.return_value
        mock_pool_instance.map.assert_called_once_with(download_zip, mock_urls)
        mock_pool_instance.close.assert_called_once()
        mock_pool_instance.join.assert_called_once()

    # TO-DO : more tests as needed


if __name__ == '__main__':
    unittest.main()
