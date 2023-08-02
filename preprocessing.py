import spacy
nlp = spacy.load("en_core_web_sm")

# perform all preprocessing tasks
def preprocess(text):
  text = removeRepeat(text)
  text = removeLeading(text)
  text = properNounFix(text)
  # add preprocessing tasks here
  return text

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
  if text.startswith('an image of'):
    text = text.replace('an image of', '')
  elif text.startswith('there is'):
    text = text.replace('there is', '')
  elif text.startswith('this is'):
    text = text.replace('this is', '')
  return text

# remove consecutive duplicate words
def removeRepeat(text):
  words = text.split()
  result = [words[0]]  # Initialize the result list with the first word

  # Iterate through the rest of the words and check for consecutive duplicates
  for word in words[1:]:
    if word != result[-1]:  # If the current word is not the same as the last word in the result list
      result.append(word)  # Add the word to the result list

  return ' '.join(result)