import requests
from textblob import TextBlob
import praw
import spacy

# Charger le modèle de langue de spaCy pour la reconnaissance d'entités nommées
nlp = spacy.load("en_core_web_sm")

# Initialisation de l'API Reddit avec OAuth
reddit = praw.Reddit(
    client_id="KMOXc7OPceOXjl-wBsz2cQ",
    client_secret="7YpcJZfiNVwylLRZFIpWNGpLTx9p3A",
    user_agent="HILARANT par /u/Electronic-Level4603",
)

# Fonction pour analyser le sentiment
def analyse_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

# Fonction pour détecter les lieux avec spaCy
def detect_location(text, subreddit_name):
    doc = nlp(text)
    # Extraire les lieux détectés par spaCy
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]  # GPE = lieux géographiques
    if not locations:
        locations = ["Localisation inconnue"]
    
    # Ajouter le nom du subreddit comme indice de localisation si pertinent
    if subreddit_name.lower() != "all" and subreddit_name.lower() not in locations:
        locations.append(subreddit_name.capitalize())
    
    return locations

# Récupérer les 100 posts les plus récents
subreddit_name = "all"  # Changez le nom du subreddit si nécessaire
posts = reddit.subreddit(subreddit_name).new(limit=100)

# Parcourir les publications et extraire les informations
for submission in posts:
    text = submission.selftext.strip() or submission.title.strip()
    
    # Recherche de la localisation via le flair ou le texte
    location_flair = submission.link_flair_text if submission.link_flair_text else "Pas de flair"
    location_in_text = detect_location(submission.title + " " + submission.selftext, subreddit_name)
    
    # Afficher les informations sur chaque post
    print("\n--- Publication ---")
    print("Titre :", submission.title)
    print("Texte extrait :", text)
    print("Localisation probable (via flair) :", location_flair)
    print("Localisation probable (via texte et NER) :", ", ".join(location_in_text))
    print("Score de sentiment :", analyse_sentiment(text))
