import spacy
nlp = spacy.load("en_core_web_sm")

# capitalize proper nouns
def properNounFix(genText):
  doc = nlp(genText)

  text = ""

  for tok in doc:
    if tok.pos_ == "PROPN":
      text += str(tok).capitalize()
    else :
      text += str(tok)
    text += " "
  
  return text

# remove leading "an image of" and "there is"
def removeLeading(text):
  if text.index('an image of') == 0:
    text = text.replace('an image of', '')
  if text.index('there is') == 0:
    text = text.replace('there is', '')
  return text