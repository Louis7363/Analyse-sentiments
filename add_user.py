import sqlite3
import random
from faker import Faker

# Initialisation de Faker pour générer des noms d'utilisateur
fake = Faker()

# Liste d'emojis que vous souhaitez utiliser
emojis = ["😊", "😎", "😇", "🥳", "😢", "😡", "🤔", "👍", "🎉", "🚀"]

# Connexion à la base de données SQLite
con = sqlite3.connect('database.db')
cursor = con.cursor()

# Fonction pour créer des utilisateurs
def create_users(num_users):
    for _ in range(num_users):
        username = fake.user_name()  # Générer un nom d'utilisateur
        password_hash = fake.password()  # Générer un mot de passe (vous pouvez le hacher ici si besoin)
        
        # Générer des coordonnées aléatoires
        latitude = random.uniform(-90, 90)
        longitude = random.uniform(-180, 180)
        
        # Sélectionner un emoji aléatoire
        emoji = random.choice(emojis)
        
        # Requête pour insérer l'utilisateur dans la base de données
        query = """INSERT INTO user (username, password_hash,	emotion, latitude, longitude) VALUES (?, ?, ?, ?, ?)"""
        cursor.execute(query, (username, password_hash, emoji, latitude, longitude))

    con.commit()  # Enregistrer les changements

# Créer 100 utilisateurs
create_users(100)

# Fermer la connexion à la base de données
con.close()