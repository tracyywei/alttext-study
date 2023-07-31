import json
import os
import random
import pandas as pd
from flask import Flask, request, render_template
from spellchecker import SpellChecker

app = Flask(__name__, template_folder='templates')
spell = SpellChecker()
data_folder = os.path.join(app.root_path, 'data')  # Path to the 'data' folder

# Function to read a random row from the CSV file
def get_random_data():
    csv_file = os.path.join(data_folder, 'generated_captions_web.csv')
    df = pd.read_csv(csv_file)
    random_row = df.sample(n=1)
    article_name = random_row['article_id'].values[0]
    image_url = random_row['image'].values[0]
    blip_beam_text = random_row['blip_beam'].values[0]
    context = random_row['context'].values[0]
    return image_url, blip_beam_text, context


@app.route('/', methods=["GET", "POST"])
def getText():
    image_url, blip_beam_text, context = get_random_data()
    if request.method == "POST":
        myText = request.form.get("myText")
        wordList = myText.split()
        misspelled = spell.unknown(wordList)
        corrected_text = ""
        suggestions = {}
        for word in wordList:
            if word in misspelled:
                corrected_text += '<span class="misspelled" data-word="' + \
                    word + '">' + word + '</span> '
                suggestions[word] = spell.correction(word)
            else:
                corrected_text += word + ' '

        return render_template("index.html", corrected_text=corrected_text, suggestions=json.dumps(suggestions), image_url=image_url, blip_beam_text=blip_beam_text, context=context)
        pass

    return render_template("index.html", corrected_text="", suggestions={}, image_url=image_url, blip_beam_text=blip_beam_text, context=context)


@app.route("/")
def index():
    image_url, blip_beam_text = get_random_data()
    return render_template("index.html", corrected_text="", suggestions={}, image_url=image_url, blip_beam_text=blip_beam_text, context=context)



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
