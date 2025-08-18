import torch
from transformers import DistilBertForSequenceClassification, AutoTokenizer
import yaml

with open('config.yml', 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

tokenizer = config['tokenizer']
model = config['model']

class Classifier:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer)
        self.model = DistilBertForSequenceClassification.from_pretrained(model, ignore_mismatched_sizes=True)

    def classify_text(self, text):
        encoded_input = self.tokenizer(text, return_tensors='pt')

        with torch.no_grad():
            logits = self.model(**encoded_input).logits

        predicted_class_id = logits.argmax().item()
        predicted_label = self.model.config.id2label[predicted_class_id]

        return predicted_label
