import tarfile
import os

def extract_tar(tar_path, extract_to):

    if not os.path.exists(tar_path):
        print(f"Error: File '{tar_path}' does not exist.")
        return
    
    os.makedirs(extract_to, exist_ok=True)

    try:
        with tarfile.open(tar_path, 'r') as tar:
            print(f"Extracting files from '{tar_path}' to '{extract_to}'...")
            tar.extractall(path=extract_to)
            print("Extraction completed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    tar_file_path = "data/archive/nuforc_dataset.tar" 
    output_directory = "data/raw" 

    extract_tar(tar_file_path, output_directory)
