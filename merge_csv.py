import os
import pandas as pd

# Specify the directory containing the CSV files
campaigns_dir = 'campaigns'
# Specify the filename for the merged CSV
output_csv_file = 'merged_campaigns.csv'

def merge_csv_files(campaigns_dir, output_csv_file):
    # Create an empty DataFrame to hold the merged data
    merged_df = pd.DataFrame()

    # Loop through all files in the directory
    for filename in os.listdir(campaigns_dir):
        if filename.endswith('.csv'):
            # Construct the full file path
            file_path = os.path.join(campaigns_dir, filename)
            # Read the CSV file and append it to the merged DataFrame
            df = pd.read_csv(file_path)
            merged_df = pd.concat([merged_df, df], ignore_index=True)
    
    # Save the merged DataFrame to a new CSV file
    merged_df.to_csv(output_csv_file, index=False)
    print(f'Merged {len(merged_df)} rows into {output_csv_file}')

# Call the function to merge the CSV files
merge_csv_files(campaigns_dir, output_csv_file)
