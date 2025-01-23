import json
import os
import random
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for
import time
from openai import OpenAI
import re

app = Flask(__name__, template_folder='templates')
data_folder = os.path.join(app.root_path, 'data')  # Path to the 'data' folder
questions_per_study = 20
attention_check_interval = 10

# Function to read a random row from the CSV file
def get_random_data():
    csv_file = os.path.join(data_folder, 'output_alt_texts_cleaned.csv')
    df = pd.read_csv(csv_file)
    random_row = df.sample(n=1)
    return random_row

def sanitize_text(text):
    return text.replace('"', '\\"').replace('\n', ' ').strip()

@app.route('/', methods=["GET", "POST"])
def startTutorial():
    prolific_pid = request.args.get("PROLIFIC_PID", "")
    return render_template("tutorial.html", prolific_pid=prolific_pid)

@app.route('/instruct', methods=["GET", "POST"])
def startInstructions():
    prolific_pid = request.args.get("PROLIFIC_PID", "")
    return render_template("instructions.html", prolific_pid=prolific_pid)

@app.route('/eval', methods=["GET", "POST"])
def getText():
    prolific_pid = request.args.get("PROLIFIC_PID", "")
    question_count = int(request.args.get('question_count', 0))

    is_attention_check = (question_count == 0 or question_count % attention_check_interval == 0)
    print(is_attention_check)
    print("[getText] question count: " + str(question_count))

    if question_count >= questions_per_study:  # ending the study sessiom
        return redirect('/complete')

    # rendering html
    if is_attention_check:
        correct_row = get_random_data()
        correct_alt_text = correct_row['yes_crt_yes_cnxt'].values[0].replace("Alt-text: ", "")

        # fetch three incorrect options from other rows
        incorrect_rows = [get_random_data() for _ in range(3)]
        incorrect_alt_texts = [
            row['no_crt_no_cnxt'].values[0].replace("Alt-text: ", "") for row in incorrect_rows
        ]
        all_options = [{"text": sanitize_text(correct_alt_text), "is_correct": True}] + [
            {"text": sanitize_text(alt_text), "is_correct": False} for alt_text in incorrect_alt_texts
        ]
        random.shuffle(all_options)

        return render_template("index.html",
                               image_url=correct_row['image_url'].values[0],
                               context=(re.sub(r'\[.*?\]', '', correct_row['context'].values[0]))[:1000],
                               article_name=(re.sub('_', ' ', correct_row['article_title'].values[0])),
                               options=all_options,
                               is_attention_check=is_attention_check,
                               question_count=question_count)
    else:
        random_row = get_random_data()
        options = [
            {"text": sanitize_text(random_row[col].values[0].replace("Alt-text: ", "")), "is_correct": True, 
            "type": col}
            for col in ['no_crt_no_cnxt', 'no_crt_yes_cnxt', 'yes_crt_no_cnxt', 'yes_crt_yes_cnxt']
        ]
        random.shuffle(options)

        return render_template("index.html",
                               image_url=random_row['image_url'].values[0],
                               context=(re.sub(r'\[.*?\]', '', random_row['context'].values[0]))[:1000],
                               article_name=(re.sub('_', ' ', random_row['article_title'].values[0])),
                               options=options,
                               is_attention_check=is_attention_check,
                               question_count=question_count)

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
        question_count = int(responses.pop('question_count', None))
        if question_count:
            responses['question_count'] = question_count

        if alttext_type == "none":
            question_count += 1
            return redirect(url_for('getText', question_count=question_count, PROLIFIC_PID=prolific_pid))

        print("[nextImg, before] question count: " + str(question_count))
        is_attention_check = (question_count == 0 or question_count % 4 == 0)
        print(is_attention_check)

        # If attention check and the user fails, redirect to failure page
        if is_attention_check:
            if alttext_type == 'incorrect': 
                print("REDIRECT")
                return redirect('/failed')

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

        question_count += 1
        print("[nextImg, after] question count: " + str(question_count))
        return redirect(url_for('getText', question_count=question_count, PROLIFIC_PID=prolific_pid))

@app.route('/complete')
def studyComplete():
    return render_template('confirmation.html')

@app.route('/failed')
def failed():
    return render_template('failed.html')

if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)
