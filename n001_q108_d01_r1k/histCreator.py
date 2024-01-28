import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import os

# Get the current working directory
#current_directory = os.getcwd()

# Assuming all CSV files are in the same directory and follow a similar naming pattern, like data1.csv, data2.csv, etc.
file_names = ["1.csv", "2.csv", "3.csv", "4.csv", "5.csv", "6.csv", "7.csv", "8.csv", "9.csv","10.csv"]
#file_paths = [os.path.join(current_directory, file) for file in file_names]
# Read each CSV file and concatenate the data
data_frames = [pd.read_csv(file,header=None) for file in file_names]
combined_data = pd.concat(data_frames, ignore_index=True)
#print(combined_data.loc[0])
# Plot the histogram
plt.hist(combined_data[0], bins=50, edgecolor='black')

# Set the x-axis limits
plt.xlim(-1.0, 1.0)
# plt.ylim(0,5000)
# Define a function to format y-axis ticks as "1K", "2K", etc.
def format_ticks(value, _):
    if value >= 1000:
        return f'{value/1000:.0f}K'
    else:
        return int(value)

# Apply the formatter to the y-axis
plt.gca().yaxis.set_major_formatter(FuncFormatter(format_ticks))


plt.xticks(fontsize=28)
plt.yticks(fontsize=30)
plt.locator_params(axis='x', nbins=4)
plt.locator_params(axis='y', nbins=6)
# plt.title('Histogram of Floating Point Numbers')
# plt.xlabel('Value')
# plt.ylabel('Frequency')
plt.show()
