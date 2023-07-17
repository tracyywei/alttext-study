from flask import Flask, request, render_template
from spellchecker import SpellChecker

app = Flask(__name__, template_folder='templates')
spell = SpellChecker()

@app.route('/', methods =["GET", "POST"])
def getText():
    if request.method == "POST":
       myText = request.form.get("myText")
       wordList = myText.split()
       misspelled = spell.unknown(wordList)
       for word in misspelled:
        print(spell.candidates(word))
       return "Your text is: "+myText
    return render_template("index.html")

@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
