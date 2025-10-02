# Import necessary libraries
import pandas as pd
import datetime
import os
import re

# --- Instructions for Running ---
# 1. Save this file as 'merge_health_data.py' in the SAME FOLDER as your exported CSV files.
# 2. Open a terminal or command prompt in that folder.
# 3. Make sure you have pandas installed:
#    pip install pandas
# 4. Run the script from your terminal:
#    python merge_health_data.py
# 5. Follow the on-screen prompts to specify which files you want to merge.
# --------------------------------

def merge_csv_files():
    """
    Prompts the user for a disease and date range, then merges the corresponding CSV files.
    """
    print("--- Health Data CSV Merger ---")
    
    # --- Get User Input ---
    disease_identifier_input = input("Enter the disease identifier from the filename (e.g., '34__COVID-19'): ")
    
    now = datetime.datetime.now()
    try:
        start_month_in = int(input(f"Enter the start month (1-12) [Default: {now.month}]: ") or now.month)
        start_year_in = int(input(f"Enter the start year [Default: {now.year}]: ") or now.year)
        end_month_in = int(input(f"Enter the end month (1-12) [Default: {now.month}]: ") or now.month)
        end_year_in = int(input(f"Enter the end year [Default: {now.year}]: ") or now.year)
    except ValueError:
        print("❌ Error: Please enter valid numbers for dates.")
        return

    # --- Generate and Check for Required Files ---
    try:
        date_range = pd.date_range(start=f'{start_year_in}-{start_month_in}-01', end=f'{end_year_in}-{end_month_in}-01', freq='MS')
    except ValueError:
        print("❌ Error: Invalid date range provided.")
        return

    required_files = []
    for dt in date_range:
        filename = f'jakarta_health_data_{disease_identifier_input}_{dt.strftime("%Y-%m")}.csv'
        required_files.append(filename)

    missing_files = [f for f in required_files if not os.path.exists(f)]

    if missing_files:
        print("\n❌ Error: Merging cancelled. The following required files were not found:")
        for f in missing_files:
            print(f"  - {f}")
        return

    print(f"\n✅ All {len(required_files)} required files found. Proceeding with merge...")

    # --- Read and Merge the Files ---
    all_dataframes = []
    try:
        for filename in required_files:
            df = pd.read_csv(filename)
            all_dataframes.append(df)
        
        if not all_dataframes:
            print("No data to merge.")
            return

        merged_df = pd.concat(all_dataframes, ignore_index=True)
        
        # --- Save the Merged File ---
        start_date_str = date_range[0].strftime("%Y-%m")
        end_date_str = date_range[-1].strftime("%Y-%m")
        output_filename = f'MERGED_jakarta_health_data_{disease_identifier_input}_{start_date_str}_to_{end_date_str}.csv'
        
        merged_df.to_csv(output_filename, index=False)
        
        print("\n" + "="*50)
        print("🎉 Merge Complete! 🎉")
        print(f"Successfully merged {len(merged_df)} rows from {len(required_files)} files.")
        print(f"Data has been exported to '{output_filename}'")
        print("="*50 + "\n")

    except Exception as e:
        print(f"\n❌ An error occurred during the merging process: {e}")

# --- Main execution block ---
if __name__ == "__main__":
    merge_csv_files()

