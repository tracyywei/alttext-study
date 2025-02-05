# import pandas as pd
# import os
# from flask import Flask

# app = Flask(__name__, template_folder='templates')
# data_folder = app.root_path
# csv_file = os.path.join(data_folder, 'alttext-batch-cleaned.csv')
# df = pd.read_csv(csv_file)

# subset = df.sample(n=42)

# subset.to_csv("alttext_batch_subset.csv", index=False)

import hashlib

image_sets = {
    1: list(range(0, 21)),  # Image IDs for participants 1-3
    2: list(range(21, 42)),  # Image IDs for participants 4-6
}

def assign_image_set(prolific_pid):
    hash_value = int(hashlib.sha256(prolific_pid.encode()).hexdigest(), 16)
    set_index = (hash_value % 2) + 1
    return image_sets[set_index]

print(assign_image_set("677cdafcf353902f01b935b6"))
print(assign_image_set("634d72a4b1dc5f197ac4b8c6"))
print(assign_image_set("5623d483ed6e5a0005c803de"))
print(assign_image_set("661e2efbf26620b741872895"))
print(assign_image_set("67899bebbf12a390ddcc0848"))