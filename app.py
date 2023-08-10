import json
import os
import random
import pandas as pd
from flask import Flask, request, render_template
from preprocessing import preprocess
from suggestions import applySugg

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

    # preprocessing
    myText = preprocess(blip_beam_text)

    # analyze text for suggestions
    corrected_text, suggestions = applySugg(myText, context)

    if request.method == "POST":
        edited_text = request.form.get("editedText", "")
        print(edited_text)
        with open("data/saved.txt", "w") as file:
            file.write(blip_beam_text)

    return render_template("index.html", corrected_text=corrected_text, suggestions=suggestions, image_url=image_url, blip_beam_text=blip_beam_text, context=context, article_name=article_name, caption=caption)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
