import spacy
nlp = spacy.load("en_core_web_sm")
import json

def applySugg(text, context):
  wordList = text.split()
  corrected_text = ""
  names = suggestNames(context)
  suggestions = {}
  for word in wordList:
      if word == "woman" or word == "man" or word == "men" or word == "women":
          corrected_text += '<span class="misspelled" data-word="' + \
              word + '">' + word + '</span> '
          if not names:
            suggestions[word] = "no suggested names"
          else:
            suggestions[word] = names
      else:
          corrected_text += word + ' '
  suggestions_json = json.dumps(suggestions)

  return corrected_text, suggestions_json

def suggestNames(context):
  doc = nlp(context)
  names = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
  names = set(names)
  nameList = ""
  for n in names:
    nameList += n + ", "
  
  # cleaning string format
  if len(nameList) > 1:
    nameList = nameList.rstrip(nameList[-1])
  nameList = nameList.replace("'s", "")
  return nameList

def checkNumber(text):
  return text


from spellchecker import SpellChecker

def spellCheck(text):
  spell = SpellChecker()
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
  suggestions_json = json.dumps(suggestions)

  return corrected_text, suggestions_json