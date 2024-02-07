## How to run
Run ```workspace.py``` to start the simulation.<br>
The paramenters such as Noise, Q (Percentage of grid that is color A vs Color B), D (Percentage doing voter model vs majority voting) and communication range can be adjusted in ```constants.py``` in the swarmy folder

## Results
Results for the last 1000 timesteps will be saved in a csv ```last_values.csv``` file. <br>
A example histogram creator called ```histCreator.py``` exists in the repository. It will take 10 csv files named 1.csv, 2.csv, 3.csv....10.csv  to create the histogram.