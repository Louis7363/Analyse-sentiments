import sqlite3
import requests

# Configurer les informations d'API
GEONAMES_USERNAME = 'Mederic_Charveriat'  # Remplace par ton nom d'utilisateur GeoNames

def get_capital_from_country(country_name):
    """
    Utilise l'API GeoNames pour récupérer le nom de la capitale à partir du nom du pays.
    """
    url = f'http://api.geonames.org/searchJSON?q={country_name}&maxRows=1&username={GEONAMES_USERNAME}&featureCode=PPLC'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data['geonames']:
            capital_data = data['geonames'][0]
            return capital_data.get('name', 'Capital information not available.')
    except (requests.RequestException, ValueError):
        return 'Capital information not available.'

def update_capital_in_database(db_path):
    """
    Met à jour la colonne 'pays' dans la base de données pour chaque entrée sans pays défini.
    """
    # Connexion à la base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Récupérer les entrées sans pays
    cursor.execute("SELECT id, latitude, longitude FROM user WHERE capitale IS NULL")
    entries = cursor.fetchall()

    for entry in entries:
        entry_id, latitude, longitude = entry

        # Récupérer le pays à partir des coordonnées
        country = get_country_from_coordinates(latitude, longitude)

        # Si le pays est valide, récupérer la capitale
        if country != 'Country information not available.':
            capital = get_capital_from_country(country)
            if capital != 'Capital information not available.':
                # Mettre à jour la base de données avec le nom de la capitale
                cursor.execute("UPDATE user SET capitale = ? WHERE id = ?", (capital, entry_id))
            else:
                # Supprimer l'entrée si la capitale n'est pas disponible
                cursor.execute("DELETE FROM user WHERE id = ?", (entry_id,))

        # Sauvegarder les changements après chaque mise à jour/suppression
        conn.commit()

    # Fermer la connexion
    conn.close()

def get_country_from_coordinates(lat, lon):
    """
    Utilise l'API GeoNames pour récupérer le nom du pays à partir des coordonnées.
    """
    url = f'http://api.geonames.org/countryCodeJSON?lat={lat}&lng={lon}&username={GEONAMES_USERNAME}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        country_data = response.json()
        return country_data.get('countryName', 'Country information not available.')
    except (requests.RequestException, ValueError):
        return 'Country information not available.'

if __name__ == "__main__":
    # Remplace 'votre_base_de_donnees.db' par le chemin de ta base de données
    update_capital_in_database('database.db')
