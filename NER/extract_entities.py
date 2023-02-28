import spacy
from transformers import AutoTokenizer


tokenizer = AutoTokenizer.from_pretrained("gpt2")
nlp = spacy.load("en_core_web_lg")


def extract_entity_spacy(text):
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        entities.append((ent.text, ent.label_))
    return entities


def extract_entities_spacy(text, size=2800):
    # split text into many parts
    tokens = tokenizer.encode(text)
    parts = [tokenizer.decode(tokens[i:i+size])
             for i in range(0, len(tokens), size)]
    print("Number of parts:", len(parts))
    # call OpenAI API for each part
    entities = []
    for part in parts:
        entities += extract_entity_spacy(part)
    return entities
