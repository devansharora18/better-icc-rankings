import os
import requests
import zipfile
import shutil
import subprocess
import time

# Define directories and file URLs
files = {
	"ipl": "https://cricsheet.org/downloads/ipl_male_json.zip",
	"odi": "https://cricsheet.org/downloads/odis_male_json.zip",
	"t20i": "https://cricsheet.org/downloads/t20s_male_json.zip",
	"tests": "https://cricsheet.org/downloads/tests_male_json.zip"
}

base_dir = os.path.dirname(os.path.abspath(__file__))

def download_and_extract(folder, url):
	"""Delete existing ZIP, download, and extract the ZIP file into a clean folder."""
	folder_path = os.path.join(base_dir, folder)
	zip_folder = folder

	if folder == "t20i":
		zip_folder = "t20s"
	elif folder == "odi":
		zip_folder = "odis"

	zip_path = os.path.join(folder_path, f"{zip_folder}_male_json.zip")
	extract_path = os.path.join(folder_path, f"{zip_folder}_male_json")

	# Delete existing ZIP file if present
	if os.path.exists(zip_path):
		print(f"Deleting old ZIP file: {zip_path}")
		os.remove(zip_path)

	# Delete extracted folder if present
	if os.path.exists(extract_path):
		print(f"Deleting old extracted folder: {extract_path}")
		shutil.rmtree(extract_path)

	# Download ZIP file
	print(f"Downloading {url} to {zip_path}...")
	response = requests.get(url, stream=True)
	response.raise_for_status()

	with open(zip_path, "wb") as file:
		for chunk in response.iter_content(chunk_size=8192):
			file.write(chunk)

	# Ensure ZIP file exists before extracting
	if not os.path.exists(zip_path):
		print(f"Error: ZIP file {zip_path} was not downloaded!")
		return False

	# Extract ZIP file
	print(f"Extracting {zip_path} into {extract_path}...")
	os.makedirs(extract_path, exist_ok=True)

	with zipfile.ZipFile(zip_path, "r") as zip_ref:
		zip_ref.extractall(extract_path)

	# Ensure extraction was successful
	time.sleep(2)  # Short delay to ensure extraction is completed
	if not os.path.exists(extract_path):
		print(f"Error: Extraction failed for {extract_path}!")
		return False

	return True  # Indicate success

def run_scraper(folder):
	"""Run the scraper.py script inside the specified folder."""
	scraper_folder = folder

	if folder == "t20s":
		scraper_folder = "t20i"

	scraper_path = os.path.join(base_dir, scraper_folder, f"{scraper_folder}_scraper.py")
	
	print(scraper_path)
	
	if os.path.exists(scraper_path):
		print(f"Running {scraper_path}...")
		subprocess.run(["python", scraper_path], check=True, cwd=base_dir)
	else:
		print(f"Scraper not found in {folder}!")

if __name__ == "__main__":
	# Ask user for input
	choice = input("Enter which formats you want to run (all, tests, t20i, odi, ipl): ").strip().lower()

	if choice == "all":
		selected_files = files.keys()
	else:
		selected_files = [choice] if choice in files else []

	if not selected_files:
		print("Invalid selection. Exiting.")
	else:
		for folder in selected_files:
			success = download_and_extract(folder, files[folder])
			if success:
				run_scraper(folder)
			else:
				print(f"Skipping {folder} due to extraction failure!")

		print("All tasks completed successfully! 🚀")
