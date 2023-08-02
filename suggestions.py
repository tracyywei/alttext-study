import spacy
nlp = spacy.load("en_core_web_sm")

def applySugg(text, context):
  return text

def identityPpl(text):
  if text.index('woman') > -1 or text.index('man') > -1 or text.index('person') > -1:
    suggestNames(text)

def suggestNames(context):
  doc = nlp(context)
  names = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
  return set(names)

def checkNumber(text):
  return text