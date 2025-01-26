import pandas as pd
import os
from flask import Flask

app = Flask(__name__, template_folder='templates')
data_folder = app.root_path
csv_file = os.path.join(data_folder, 'output_alt_texts_cleaned.csv')
df = pd.read_csv(csv_file)

subset = df.sample(n=42)

subset.to_csv("alttext_subset.csv", index=False)