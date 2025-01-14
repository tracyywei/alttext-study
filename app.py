import json
import os
import random
import pandas as pd
from flask import Flask, request, render_template, redirect
import time
from openai import OpenAI
import re

app = Flask(__name__, template_folder='templates')
data_folder = os.path.join(app.root_path, 'data')  # Path to the 'data' folder

# Function to read a random row from the CSV file
def get_random_data():
    csv_file = os.path.join(data_folder, 'output_alt_texts_full.csv')
    df = pd.read_csv(csv_file)
    random_row = df.sample(n=1)
    return random_row

@app.route('/', methods=["GET", "POST"])
def startTutorial():
    prolific_pid = request.args.get("PROLIFIC_PID", "")
    return render_template("tutorial.html", prolific_pid=prolific_pid)

@app.route('/eval', methods=["GET", "POST"])
def getText():
    prolific_pid = request.args.get("PROLIFIC_PID", "")
    random_row = get_random_data()
    return render_template("index.html",
                            image_url=random_row['image_url'].values[0], 
                            context=(re.sub(r'\[\d+\]', '', random_row['context'].values[0]))[:1000],
                            article_name=random_row['article_title'].values[0],
                            no_crt_no_cnxt=random_row['no_crt_no_cnxt'].values[0].replace("Alt-text: ", ""),
                            no_crt_yes_cnxt=random_row['no_crt_yes_cnxt'].values[0].replace("Alt-text: ", ""),
                            yes_crt_no_cnxt=random_row['yes_crt_no_cnxt'].values[0].replace("Alt-text: ", ""),
                            yes_crt_yes_cnxt=random_row['yes_crt_yes_cnxt'].values[0].replace("Alt-text: ", "")
                        )

@app.route('/nextImg', methods=["GET", "POST"])
def nextImg():

    if request.method == "POST":
        responses = request.json
        prolific_pid = responses.pop('prolificPID', None)
        if prolific_pid:
            responses['prolificPID'] = prolific_pid
        img_url = responses.pop('img_url', None)
        if img_url:
            responses['img_url'] = img_url
        article_name = responses.pop('article_name', None)
        if img_url:
            responses['article_name'] = article_name
        alttext_type = responses.pop('alttext_type', None)
        if img_url:
            responses['alttext_type'] = alttext_type

        dictionary = {
            "pid": prolific_pid,
            "img_url": img_url,
            "alttext_type": alttext_type,
            "article_name": article_name,
        }
        
        saved_file_path = os.path.join(data_folder, 'study_responses.json')
        
        existing_data = []
        if os.path.exists(saved_file_path):
            with open(saved_file_path, "r") as infile:
                existing_data = json.load(infile)
        
        existing_data.append(dictionary)
        
        with open(saved_file_path, "w") as outfile:
            json.dump(existing_data, outfile, indent=4)

        return redirect('/')

@app.route('/complete')
def studyComplete():
    return render_template('confirmation.html')

if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)
