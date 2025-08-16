import torch
from transformers import DistilBertForSequenceClassification, AutoTokenizer


tokenizer=AutoTokenizer.from_pretrained('distilbert-base-uncased')
model=DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased')

def classify_text(text):
    encoded_input=tokenizer(text, return_tensors='pt')

    with torch.no_grad():
        logits = model(**encoded_input).logits

    predicted_class_id = logits.argmax().item()
    predicted_label = model.config.id2label[predicted_class_id]

    return predicted_label