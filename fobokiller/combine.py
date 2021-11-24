import pandas as pd
import os
import glob

# Use glob to match the pattern ‘csv’

extension = 'csv'
all_filenames = [i for i in glob.glob('*.{}'.format(extension))]


# Combine all files in the list and export as CSV

#combine all files in the list
combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames])
#export to csv
combined_csv.to_csv("combined_csv.csv", index=False, encoding='utf-8-sig')
