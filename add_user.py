import sqlite3
import random
import requests
from faker import Faker

# Initialisation de Faker pour générer des noms d'utilisateur
fake = Faker()

# Liste d'emojis que vous souhaitez utiliser
emojis = ["😊", "😎", "😇", "🥳", "😢", "😡", "🤔", "👍", "🎉", "🚀"]

# Connexion à la base de données SQLite
con = sqlite3.connect('./Analyse-sentiments/database.db')
cursor = con.cursor()

# Fonction pour vérifier si les coordonnées sont sur un continent
def is_on_continent(latitude, longitude, username):
    url = "http://api.geonames.org/countryCodeJSON"
    params = {
        "lat": latitude,
        "lng": longitude,
        "username": username
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return 'countryName' in data  # True si un pays est trouvé
    else:
        print("Erreur API:", response.status_code)
        return False

# Fonction pour créer des utilisateurs
def create_users(num_users, geonames_username):
    for _ in range(num_users):
        username = fake.user_name()  # Générer un nom d'utilisateur
        password_hash = fake.password()  # Générer un mot de passe (vous pouvez le hacher ici si besoin)
        
        # Trouver des coordonnées valides
        while True:
            latitude = random.uniform(-90, 90)
            longitude = random.uniform(-180, 180)
            
            # Vérifier si les coordonnées sont sur un continent
            if is_on_continent(latitude, longitude, geonames_username):
                break  # Sortir de la boucle si les coordonnées sont valides

        # Sélectionner un emoji aléatoire
        emoji = random.choice(emojis)
        
        # Requête pour insérer l'utilisateur dans la base de données
        query = """INSERT INTO user (username, password_hash, emotion, latitude, longitude) VALUES (?, ?, ?, ?, ?)"""
        cursor.execute(query, (username, password_hash, emoji, latitude, longitude))

    con.commit()  # Enregistrer les changements

# Créer 100 utilisateurs en utilisant le nom d'utilisateur Geonames
geonames_username = "Mederic_Charveriat"  # Remplace par ton nom d'utilisateur Geonames
create_users(100, geonames_username)

# Fermer la connexion à la base de données
con.close()
