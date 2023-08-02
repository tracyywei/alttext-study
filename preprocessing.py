import spacy
nlp = spacy.load("en_core_web_sm")

def pronounFix(genText):
  doc = nlp(genText)

  text = ""

  for tok in doc:
    if tok.pos_ == "PROPN":
      text += str(tok).capitalize()
    else :
      text += str(tok)
    text += " "
  
  print(text)
  return text