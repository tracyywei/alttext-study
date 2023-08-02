from transformers import AutoTokenizer, AutoModelForMaskedLM

tokenizer = AutoTokenizer.from_pretrained('xlm-roberta-base')
model = AutoModelForMaskedLM.from_pretrained("xlm-roberta-base")

def calcSimilarity(text):
  
  # prepare input
  encoded_input = tokenizer(text, return_tensors='pt')

  # forward pass
  output = model(**encoded_input)