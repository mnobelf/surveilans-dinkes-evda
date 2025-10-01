# Import necessary libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import time
import re

# --- Instructions for Running ---
# 1. Save this file as 'jakarta_health_scraper.py'.
# 2. Open a terminal or command prompt.
# 3. Make sure you have the necessary libraries installed by running:
#    pip install requests beautifulsoup4 pandas
# 4. Run the script from your terminal:
#    python jakarta_health_scraper.py
# 5. Follow the on-screen prompts to enter your desired scraping parameters.
# 6. The results will be saved to individual CSV files for each month.
# --------------------------------

# Define the base URLs
base_url = 'https://surveilans-dinkes.jakarta.go.id/sarsbaru/'
rekap_url = f'{base_url}rs_rekap.php'
kabupaten_url = f'{base_url}zz_getkab.php'
kecamatan_url = f'{base_url}zz_getkec.php'

# --- Define Headers to Mimic a Browser ---
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': rekap_url,
    'X-Requested-With': 'XMLHttpRequest'
}

# --- Define the lists for iteration ---
kabupaten_map = {
    '1': 'Jakarta Pusat', '2': 'Jakarta Utara', '3': 'Jakarta Barat',
    '4': 'Jakarta Selatan', '5': 'Jakarta Timur', '6': 'Kab. Kep. Seribu',
}
status_penderita_map = {
    'SAKIT': 'Masih Dirawat', 'SEMBUH': 'Sembuh', 'MATI': 'Meninggal'
}
golongan_umur_map = {
    '1': '< 1 TH', '2': '1 - 4 TH', '3': '5 - 9 TH', '4': '10 - 14 TH',
    '5': '15 - 19 TH', '6': '20 - 44 TH', '7': '45 - 54 TH',
    '8': '55 - 64 TH', '9': '65 - 74 TH', '10': '75+ TH'
}
jenis_kelamin_map = {'L': 'Laki-Laki', 'P': 'Perempuan'}


def get_all_diseases(session):
    """Fetches the full list of diseases and displays them."""
    print("--- Fetching Full Disease List ---")
    try:
        # Added a timeout to prevent hanging
        response = session.get(rekap_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        penyakit_select = soup.find('select', id='penyakit')
        if penyakit_select:
            penyakit_options = penyakit_select.find_all('option')
            all_penyakit = {opt['value']: opt.text.strip() for opt in penyakit_options if opt.get('value') and opt['value'] != '0'}
            print("Please use one of the following codes for the disease input:")
            for code, name in all_penyakit.items():
                print(f"  Code: {code.ljust(4)} Name: {name}")
            return all_penyakit
        return None
    except (requests.RequestException, requests.exceptions.Timeout) as e:
        print(f"Failed to fetch disease list: {e}")
        return None

def get_kecamatan_list(session, prov_code, kab_code):
    """Fetches the list of kecamatan using a persistent session."""
    params = {'kp': prov_code, 'kk': kab_code}
    try:
        # Added a timeout for this quick request
        response = session.get(kecamatan_url, params=params, timeout=15)
        response.raise_for_status()
        matches = re.findall(r'new Option\s*\(\s*["\'](.+?)["\']\s*,\s*["\'](.+?)["\']\s*\)', response.text)
        return {code: name for name, code in matches if code != '0'}
    except (requests.RequestException, requests.exceptions.Timeout):
        return {}

def scrape_data(start_year, start_month, end_year, end_month, target_penyakit_code, headers_dict, disease_map):
    """The main function to scrape data based on user input."""
    print(f"\n⏳ Processing... this may take a very long time. Starting scrape for {start_month}/{start_year} to {end_month}/{end_year}...")
    
    try:
        date_range = pd.date_range(start=f'{start_year}-{start_month}-01', end=f'{end_year}-{end_month}-01', freq='MS')

        with requests.Session() as session:
            session.headers.update(headers_dict)
            # Added a timeout to prevent hanging
            session.get(rekap_url, timeout=30).raise_for_status()

            for dt in date_range:
                # This list will hold data for the current month only
                monthly_dataframes = []
                current_year, current_month = dt.year, dt.month
                print(f"\nProcessing Date: {dt.strftime('%B %Y')}...")

                for kab_code, kab_name in kabupaten_map.items():
                    prov_code = '1'
                    try:
                        # Added a timeout for the handshake request
                        session.get(kabupaten_url, params={'kp': prov_code}, timeout=15).raise_for_status()
                    except (requests.RequestException, requests.exceptions.Timeout):
                        continue
                    
                    kecamatan_list = get_kecamatan_list(session, prov_code, kab_code)
                    if not kecamatan_list:
                        continue

                    for kec_code, kec_name in kecamatan_list.items():
                        print(f"  Processing: {kab_name} -> {kec_name}")
                        for sp_code, sp_name in status_penderita_map.items():
                            for gu_code, gu_name in golongan_umur_map.items():
                                for jk_code, jk_name in jenis_kelamin_map.items():
                                    payload = {
                                        'prov': prov_code, 'kab': kab_code, 'kec': kec_code,
                                        'rs': '0', 'penyakit': target_penyakit_code, 'golum': gu_code,
                                        'jk': jk_code, 'sp': sp_code, 'jdata': '1',
                                        'hpar1': str(current_month), 'hpar2': str(current_year),
                                        'tbl_proses': 'P R O S E S'
                                    }
                                    
                                    # --- Retry Logic Added Here ---
                                    response = None
                                    max_retries = 3
                                    retry_delay = 5 # Start with a 5-second delay
                                    for attempt in range(max_retries):
                                        try:
                                            response = session.post(rekap_url, data=payload, timeout=30)
                                            response.raise_for_status() # Raise an exception for bad status codes
                                            break # If successful, exit the retry loop
                                        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                                            print(f"    - Network error: {e}. Retrying in {retry_delay}s... (Attempt {attempt + 1}/{max_retries})")
                                            time.sleep(retry_delay)
                                            retry_delay *= 2 # Exponential backoff
                                    
                                    if response is None:
                                        print(f"    - FAILED to fetch data for this combination after {max_retries} attempts. Skipping.")
                                        continue # Skip to the next iteration if all retries fail
                                    
                                    # --- End of Retry Logic ---

                                    soup = BeautifulSoup(response.text, 'html.parser')
                                    data_table = soup.find('table', id='example2a')

                                    if data_table and data_table.find('tbody') and data_table.find_all('tr'):
                                        headers_list = [th.text.strip() for th in data_table.find('thead').find_all('th')]
                                        rows_data = [[td.text.strip() for td in row.find_all('td')] for row in data_table.find('tbody').find_all('tr')]
                                        
                                        if rows_data:
                                            df_month = pd.DataFrame(rows_data, columns=headers_list)
                                            df_month = df_month.rename(columns={'Nama': 'Kelurahan'}).drop(columns=['No'], errors='ignore')
                                            
                                            id_vars = ['Kelurahan']
                                            value_vars = [h for h in headers_list if h.isdigit()]
                                            df_tidy = df_month.melt(id_vars=id_vars, value_vars=value_vars, var_name='Hari', value_name='Jumlah Kasus')

                                            df_tidy['Tanggal'] = pd.to_datetime(dict(year=current_year, month=current_month, day=df_tidy['Hari']), errors='coerce')
                                            df_tidy.dropna(subset=['Tanggal'], inplace=True)
                                            df_tidy['Jumlah Kasus'] = pd.to_numeric(df_tidy['Jumlah Kasus'], errors='coerce').fillna(0).astype(int)
                                            
                                            df_tidy = df_tidy[df_tidy['Jumlah Kasus'] > 0]

                                            if not df_tidy.empty:
                                                df_tidy.insert(0, 'Jenis Kelamin', jk_name)
                                                df_tidy.insert(0, 'Golongan Umur', gu_name)
                                                df_tidy.insert(0, 'Status Penderita', sp_name)
                                                df_tidy.insert(0, 'Kecamatan', kec_name)
                                                df_tidy.insert(0, 'Kabupaten/Kota', kab_name)
                                                monthly_dataframes.append(df_tidy.drop(columns=['Hari']))
                                    time.sleep(0.5)
                
                # --- EXPORT DATA FOR THE CURRENT MONTH ---
                if monthly_dataframes:
                    month_df = pd.concat(monthly_dataframes, ignore_index=True)
                    
                    disease_name = disease_map.get(target_penyakit_code, 'UnknownDisease')
                    safe_disease_name = re.sub(r'[^a-zA-Z0-9_-]', '_', disease_name)

                    output_filename = f'jakarta_health_data_{safe_disease_name}_{dt.strftime("%Y-%m")}.csv'
                    month_df.to_csv(output_filename, index=False)
                    print("\n" + "="*50)
                    print(f"✅ Success! Scraped {len(month_df)} rows for {dt.strftime('%B %Y')}.")
                    print(f"Data has been exported to '{output_filename}'")
                    print("="*50 + "\n")
                else:
                    print(f"\nℹ️ No data was found for {dt.strftime('%B %Y')}.")

    except (requests.RequestException, requests.exceptions.Timeout) as e:
        print(f"\n❌ A web request failed or timed out: {e}")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

# --- Main execution block ---
if __name__ == "__main__":
    with requests.Session() as s:
        s.headers.update(headers)
        print("Initializing session...")
        try:
            s.get(rekap_url, timeout=30).raise_for_status()
            print("Session initialized successfully.")
            
            available_diseases = get_all_diseases(s)

            if available_diseases:
                penyakit_code = input("\nEnter the disease code you want to scrape: ")
                while penyakit_code not in available_diseases:
                    print("Invalid code. Please choose a code from the list above.")
                    penyakit_code = input("Enter the disease code you want to scrape: ")

                now = datetime.datetime.now()
                start_month_in = input(f"Enter the start month (1-12) [Default: {now.month}]: ") or now.month
                start_year_in = input(f"Enter the start year [Default: {now.year}]: ") or now.year
                end_month_in = input(f"Enter the end month (1-12) [Default: {now.month}]: ") or now.month
                end_year_in = input(f"Enter the end year [Default: {now.year}]: ") or now.year

                scrape_data(
                    start_year=int(start_year_in), start_month=int(start_month_in),
                    end_year=int(end_year_in), end_month=int(end_month_in),
                    target_penyakit_code=penyakit_code, headers_dict=headers,
                    disease_map=available_diseases 
                )
            else:
                print("\nCould not fetch the list of diseases. Cannot proceed.")
        except (requests.RequestException, requests.exceptions.Timeout) as e:
            print(f"Failed to initialize session. The website may be down or blocking requests. Error: {e}")

