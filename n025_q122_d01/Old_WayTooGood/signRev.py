import pandas as pd
import os

# Replace 'path/to/csv/files' with the actual path to your CSV files
csv_folder = 'path/to/csv/files'

# List all CSV files in the specified folder
csv_files = ["1.csv", "2.csv", "3.csv", "4.csv", "5.csv", "6.csv", "7.csv", "8.csv", "9.csv","10.csv"]

# Function to reverse the sign of each number in a given DataFrame
def reverse_sign(df):
    return df.applymap(reverse_sign_except_zero)

def reverse_sign_except_zero(x):
    return -x if x != 0 else x

# Process each CSV file
for file in csv_files:
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file)

    # Reverse the sign of each number
    df_reversed = reverse_sign(df)

    # Save the modified DataFrame back to the CSV file
    df_reversed.to_csv(f'reversed_{file}', index=False)

print("Signs reversed and files saved successfully.")
