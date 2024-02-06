import os
import zipfile
import argparse


def extract_all_zips(output_dir):
    """
    Extract all zip files in their respective folders and delete the zip files if extraction is successful.

    Args:
        output_dir (str): The output folder where zip files are located.

    Returns:
        None
    """
    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".zip"):
                zip_file_path = os.path.join(root, file)

                # Extract in the same folder
                try:
                    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                        zip_ref.extractall(root)

                    # Delete the zip file after successful extraction
                    os.remove(zip_file_path)
                except Exception as e:
                    print(f"Extraction failed for {zip_file_path}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Extract all zip files in their respective folders and delete zips if extraction is successful.')
    parser.add_argument('--output-dir', required=True, help='Path to the output folder containing zip files.')
    args = parser.parse_args()

    extract_all_zips(args.output_dir)


if __name__ == "__main__":
    main()
