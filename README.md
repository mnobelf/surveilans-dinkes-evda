# surveilans-dinkes-evda


This project contains two Python scripts designed to scrape and manage public health data from the Jakarta Health Office's epidemiological surveillance website.

scraper.py: Scrapes detailed, daily health data for a specified disease and date range, saving the results into monthly CSV files.
merger.py: Merges the monthly CSV files created by the scraper into a single, comprehensive dataset.

## Prerequisites

Before you begin, ensure you have the following installed on your system:
- Python 3: The scripts are written in Python. You can download it from python.org.
- pip: Python's package installer, which usually comes with Python 3.
You will also need to install the required Python libraries. You can do this by running the following command in your terminal or command prompt:
- pip install requests beautifulsoup4 pandas

## How to Use
Follow these two main steps to scrape and then merge the data.
### Step 1: Scrape the Data (scraper.py)
This script connects to the website, asks for your scraping criteria, and saves the data in monthly chunks.

1\. Place the Script:
Save scraper.py in a new, empty folder on your computer. This folder is where all the monthly data files will be saved.

2\. Run the Script:
Open a terminal or command prompt, navigate to the folder where you saved the script, and run it with the following command:
python scraper.py

3\. Follow the Prompts:
The script will first fetch a list of all available diseases and display them with their corresponding codes.

--- Fetching Full Disease List ---
Please use one of the following codes for the disease input:
&nbsp; Code: 1    Name: 01. GED
&nbsp; Code: 2    Name: 02. CAMPAK
&nbsp; Code: 3    Name: 03. DIPHTERI
&nbsp; ...
&nbsp; Code: 34   Name: 34. COVID-19

You will then be prompted to enter your desired scraping parameters:

Disease Code: Enter the code for the disease you want to scrape (e.g., 34).
Start/End Month \& Year: Specify the date range for the data you want. Press Enter to use the current month/year as the default.

4\. Let it Run:
The script will begin the scraping process, which can be very long depending on the date range. It will print its progress and save a new CSV file for each month it completes (e.g., jakarta\_health\_data\_34\_\_COVID-19\_2025-09.csv).

If a network error occurs, the script will automatically retry a few times before skipping the problematic item and continuing.

### Step 2: Merge the Scraped Files (merger.py)

After the scraper has finished and you have multiple monthly CSV files, you can use this script to combine them.

1\. Place the Script:
Make sure merger.py is in the same folder as scraper.py and all the generated CSV files.

2\. Run the Script:
In your terminal, run the script:
python merger.py

3\. Follow the Prompts:
The script will ask for the information needed to identify the files you want to merge:

Disease Identifier: Enter the identifier exactly as it appears in the filenames (e.g., 34\_\_COVID-19).
Start/End Month \& Year: Specify the date range of the files you want to combine.

4\. Check the Output:
The script will first verify that all required monthly files exist. If they do, it will merge them and save the result to a new file with the MERGED\_ prefix (e.g., MERGED\_jakarta\_health\_data\_34\_\_COVID-19\_2025-09\_to\_2025-11.csv).

## Important Notes
Run Location: Both scripts and all CSV files must be located in the same folder for them to work correctly.
Scraping Time: The scraping process is extremely time-consuming due to the nested loops (Districts > Status > Age Group > Gender). Be prepared to leave the script running for a long time.

Website Dependency: The scripts depend on the structure and availability of the surveilans-dinkes.jakarta.go.id website. If the website changes, these scripts may no longer work.

