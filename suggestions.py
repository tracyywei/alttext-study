import spacy
nlp = spacy.load("en_core_web_sm")

def suggestNames(context):
  doc = nlp(context)
  names = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
  return set(names)