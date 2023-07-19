import json
from flask import Flask, request, render_template
from spellchecker import SpellChecker

app = Flask(__name__, template_folder='templates')
spell = SpellChecker()


@app.route('/', methods=["GET", "POST"])
def getText():
    if request.method == "POST":
        myText = request.form.get("myText")
        wordList = myText.split()
        misspelled = spell.unknown(wordList)
        corrected_text = ""
        suggestions = {}
        for word in wordList:
            if word in misspelled:
                corrected_text += '<span class="misspelled" data-word="' + word + '">' + word + '</span> '
                suggestions[word] = spell.correction(word)
            else:
                corrected_text += word + ' '
        return render_template("index.html", corrected_text=corrected_text, suggestions=json.dumps(suggestions))
    return render_template("index.html", corrected_text="", suggestions={})


@app.route("/")
def index():
    return render_template("index.html", corrected_text="", suggestions={})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
