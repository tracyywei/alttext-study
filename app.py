import json
import os
import random
import pandas as pd
from flask import Flask, request, render_template, redirect
from preprocessing import preprocess
from suggestions import applySugg
import time

app = Flask(__name__, template_folder='templates')
data_folder = os.path.join(app.root_path, 'data')  # Path to the 'data' folder

# Function to read a random row from the CSV file
def get_random_data():
    csv_file = os.path.join(data_folder, 'generated_captions_web.csv')
    df = pd.read_csv(csv_file)
    random_row = df.sample(n=1)
    article_name = random_row['articlenames'].values[0]
    image_url = random_row['image'].values[0]
    blip_beam_text = random_row['blip_beam'].values[0]
    context = random_row['context'].values[0]
    caption = random_row['caption'].values[0]
    return image_url, blip_beam_text, context, article_name, caption


@app.route('/', methods=["GET", "POST"])
def getText():
    image_url, blip_beam_text, context, article_name, caption = get_random_data()
    start_time = time.time()

    # preprocessing
    myText = preprocess(blip_beam_text)

    # analyze text for suggestions
    corrected_text, suggestions = applySugg(myText, context)

    if request.method == "POST":

        orig_text = request.form.get("ogText", "")
        edited_text = request.form.get("editedText", "")
        image = request.form.get("ogImg", "")

        end_time = time.time()

        dictionary = {
            "start_time": start_time,
            "end_time": end_time,
            "orig_text": orig_text,
            "edited_text": edited_text,
            "image": image
        }
        
        # Writing to json
        saved_file_path = os.path.join(data_folder, 'sample.json')
        
        # Load existing data from the file if available
        existing_data = []
        if os.path.exists(saved_file_path):
            with open(saved_file_path, "r") as infile:
                existing_data = json.load(infile)
        
        # Append the new data entry
        existing_data.append(dictionary)
        
        # Write the updated data back to the file
        with open(saved_file_path, "w") as outfile:
            json.dump(existing_data, outfile, indent=4)

    return render_template("index.html", corrected_text=corrected_text, suggestions=suggestions, image_url=image_url, blip_beam_text=blip_beam_text, context=context, article_name=article_name, caption=caption)

@app.route('/skip', methods=["GET", "POST"])
def skip():

    if request.method == "POST":

        orig_text = request.form.get("ogText-skip", "")
        image = request.form.get("ogImg-skip", "")
        reason = request.form['options']

        dictionary = {
            "orig_text": orig_text,
            "image": image,
            "reason": reason
        }
        
        # Writing to json
        saved_file_path = os.path.join(data_folder, 'skipped.json')
        
        # Load existing data from the file if available
        existing_data = []
        if os.path.exists(saved_file_path):
            with open(saved_file_path, "r") as infile:
                existing_data = json.load(infile)
        
        # Append the new data entry
        existing_data.append(dictionary)
        
        # Write the updated data back to the file
        with open(saved_file_path, "w") as outfile:
            json.dump(existing_data, outfile, indent=4)

        return redirect('/')

if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)
