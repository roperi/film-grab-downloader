import argparse
import os
import zipfile


def extract_and_delete_zips(target_dir):
    """Extract all zip files and delete them after successful extraction.

    Args:
        target_dir (str): The target folder where zip files are located.

    Returns:
        None
    """
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".zip"):
                zip_file_path = os.path.join(root, file)

                # Extract in the same folder
                try:
                    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                        zip_ref.extractall(root)

                    # Delete the zip file after successful extraction
                    os.remove(zip_file_path)
                except Exception as e:
                    print(f"Extraction failed for {zip_file_path}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract all zip files and delete them after successful extraction."
    )
    parser.add_argument(
        "--target-dir", required=True, help="Path to the target folder containing zip files."
    )
    args = parser.parse_args()

    extract_and_delete_zips(args.target_dir)


if __name__ == "__main__":
    main()
