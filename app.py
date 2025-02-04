import json
import os
import random
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for, session
import time
from openai import OpenAI
import re
import hashlib

app = Flask(__name__, template_folder='templates')
data_folder = os.path.join(app.root_path, 'data')  # Path to the 'data' folder

REAL_QUESTIONS_COUNT = 20
ATTENTION_CHECK_COUNT = 5
TOTAL_QUESTIONS = REAL_QUESTIONS_COUNT + ATTENTION_CHECK_COUNT  # 25 total questions

attention_checks_file = os.path.join(data_folder, 'hidden_attention_checks.csv')
attention_checks = pd.read_csv(attention_checks_file).to_dict('records')

####################

# pilot study subset (queue system with pre-computed images)

image_sets = {
    1: list(range(0, 21)),  # Image IDs for participants 1-3
    2: list(range(21, 42)),  # Image IDs for participants 4-6
}

def assign_image_set(prolific_pid):
    hash_value = int(hashlib.sha256(prolific_pid.encode()).hexdigest(), 16)
    set_index = (hash_value % 2) + 1
    return image_sets[set_index]

# Function to read a random row from the CSV file based on the image ID
def get_image_data(image_id):
    csv_file = os.path.join(data_folder, 'alttext_batch_subset.csv')
    df = pd.read_csv(csv_file)
    return df.iloc[image_id:image_id + 1]


####################

# Function to get a random attention check question
def get_random_attention_check():
    return random.choice(attention_checks)

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
    study_id = request.args.get("STUDY_ID", "")
    session_id = request.args.get("SESSION_ID", "")

    # log participant start time
    start_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    assigned_images = assign_image_set(prolific_pid)
    assigned_images = assigned_images[:REAL_QUESTIONS_COUNT]
    attention_check_positions = sorted([0] + random.sample(range(1, TOTAL_QUESTIONS), ATTENTION_CHECK_COUNT - 1))

    participant_log = {
        "prolific_pid": prolific_pid,
        "study_id": study_id,
        "session_id": session_id,
        "start_time": start_timestamp,
        "end_time": None,
        "assigned_images": assigned_images,     # pilot study
        "attention_check_positions": attention_check_positions
    }

    log_file_path = os.path.join(data_folder, 'participant_log.json')
    existing_logs = []
    if os.path.exists(log_file_path):
        with open(log_file_path, "r") as log_file:
            existing_logs = json.load(log_file)

    existing_logs.append(participant_log)

    with open(log_file_path, "w") as log_file:
        json.dump(existing_logs, log_file, indent=4)

    return render_template("tutorial.html", prolific_pid=prolific_pid, study_id=study_id, session_id=session_id)

@app.route('/instruct', methods=["GET", "POST"])
def startInstructions():
    prolific_pid = request.args.get("PROLIFIC_PID", "")
    study_id = request.args.get("STUDY_ID", "")
    session_id = request.args.get("SESSION_ID", "")
    return render_template("instructions.html", prolific_pid=prolific_pid, study_id=study_id, session_id=session_id)

@app.route('/eval', methods=["GET", "POST"])
def getText():
    prolific_pid = request.args.get("PROLIFIC_PID", "")
    study_id = request.args.get("STUDY_ID", "")
    session_id = request.args.get("SESSION_ID", "")
    question_count = int(request.args.get('question_count', 0))

    # pilot study
    log_file_path = os.path.join(data_folder, 'participant_log.json')
    with open(log_file_path, "r") as infile:
        logs = json.load(infile)
    participant_log = next((log for log in logs if log['prolific_pid'] == prolific_pid), None)

    if participant_log is None:
        return "Participant log not found.", 400

    attention_check_positions = participant_log.get("attention_check_positions", [])


    if question_count >= TOTAL_QUESTIONS:  # ending the study sessiom
        # log end timestamp on participant log
        for log in logs:
            if log['prolific_pid'] == prolific_pid:
                log['end_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        with open(log_file_path, "w") as outfile:
            json.dump(logs, outfile, indent=4)
        return redirect('/complete')

    is_attention_check = question_count in attention_check_positions

    if is_attention_check:
        attn_check = get_random_attention_check()
        incorrect_options = [attn_check["incorrect_1"], attn_check["incorrect_2"], attn_check["incorrect_3"]]
        all_options = [{"text": sanitize_text(attn_check["correct"]), "is_correct": True}] + \
                      [{"text": sanitize_text(opt.replace("Alt-text: ", "")), "is_correct": False} for opt in incorrect_options]
        random.shuffle(all_options)
        return render_template("index.html", image_url=attn_check['image_url'], context=attn_check['context'],
                               article_name=attn_check['article_title'], options=all_options,
                               is_attention_check=True, question_count=question_count)
    else:
        num_attention_checks_before = sum(1 for pos in attention_check_positions if pos < question_count)
        real_question_index = question_count - num_attention_checks_before
        if real_question_index >= len(participant_log["assigned_images"]):
            return "Error: Real question index out of bounds.", 500
        
        image_id = participant_log["assigned_images"][real_question_index]
        image_data = get_image_data(image_id)

        options = [
            {"text": sanitize_text(image_data[col].values[0].replace("Alt-text: ", "")), "is_correct": True, "type": col}
            for col in ['no_crt_no_cnxt', 'no_crt_yes_cnxt', 'yes_crt_no_cnxt', 'yes_crt_yes_cnxt']
        ]
        random.shuffle(options)

        return render_template("index.html",
                               image_url=image_data['image_url'].values[0],
                               context=(re.sub(r'\[.*?\]', '', image_data['context'].values[0]))[:1000],
                               article_name=(re.sub('_', ' ', image_data['article_title'].values[0])),
                               options=options,
                               is_attention_check=is_attention_check,
                               question_count=question_count)
    
    # [COMMENTING OUT FOR PILOT STUDY] rendering html for large dataset randomized images
    # if is_attention_check:
    #     correct_row = get_random_data()
    #     correct_alt_text = correct_row['yes_crt_yes_cnxt'].values[0].replace("Alt-text: ", "")

    #     # fetch three incorrect options from other rows
    #     incorrect_rows = [get_random_data() for _ in range(3)]
    #     incorrect_alt_texts = [
    #         row['no_crt_no_cnxt'].values[0].replace("Alt-text: ", "") for row in incorrect_rows
    #     ]
    #     all_options = [{"text": sanitize_text(correct_alt_text), "is_correct": True}] + [
    #         {"text": sanitize_text(alt_text), "is_correct": False} for alt_text in incorrect_alt_texts
    #     ]
    #     random.shuffle(all_options)

    #     return render_template("index.html",
    #                            image_url=correct_row['image_url'].values[0],
    #                            context=(re.sub(r'\[.*?\]', '', correct_row['context'].values[0]))[:1000],
    #                            article_name=(re.sub('_', ' ', correct_row['article_title'].values[0])),
    #                            options=all_options,
    #                            is_attention_check=is_attention_check,
    #                            question_count=question_count)
    # else:
    #     random_row = get_random_data()
    #     options = [
    #         {"text": sanitize_text(random_row[col].values[0].replace("Alt-text: ", "")), "is_correct": True, 
    #         "type": col}
    #         for col in ['no_crt_no_cnxt', 'no_crt_yes_cnxt', 'yes_crt_no_cnxt', 'yes_crt_yes_cnxt']
    #     ]
    #     random.shuffle(options)

    #     return render_template("index.html",
    #                            image_url=random_row['image_url'].values[0],
    #                            context=(re.sub(r'\[.*?\]', '', random_row['context'].values[0]))[:1000],
    #                            article_name=(re.sub('_', ' ', random_row['article_title'].values[0])),
    #                            options=options,
    #                            is_attention_check=is_attention_check,
    #                            question_count=question_count)

@app.route('/nextImg', methods=["GET", "POST"])
def nextImg():
    if request.method == "POST":
        responses = request.json
        prolific_pid = responses.pop('prolificPID', None)
        if prolific_pid:
            responses['prolificPID'] = prolific_pid
        study_id = responses.pop('studyID', None)
        if study_id:
            responses['studyID'] = study_id
        session_id = responses.pop('sessionID', None)
        if session_id:
            responses['sessionID'] = session_id
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

        is_attention_check = (question_count == 0 or question_count % 4 == 0)

        dictionary = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "pid": prolific_pid,
            "study_id": study_id,
            "session_id": session_id,
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
        
        # If attention check and the user fails, redirect to failure page
        if alttext_type == 'incorrect': 
            print("REDIRECT")
            return redirect('/failed')

        question_count += 1
        return redirect(url_for('getText', question_count=question_count, PROLIFIC_PID=prolific_pid, STUDY_ID=study_id, SESSION_ID=session_id))

@app.route('/complete')
def studyComplete():
    return render_template('confirmation.html')

@app.route('/failed')
def failed():
    return render_template('failed.html')

if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)
