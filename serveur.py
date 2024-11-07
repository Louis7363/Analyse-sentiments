
from flask import Flask, session, flash, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin
from markupsafe import Markup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yzdgiauaoi478GIEZ87Y2iad'  # Change à une clé secrète réelle
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_bdd.db'  # Tu peux mettre ta base ici
bcrypt = Bcrypt(app)  # Initialise la fonction Bcrypt

# Importation du module sqlite3 de gestion de base de données
import sqlite3
import requests
GEONAMES_USERNAME = 'Mederic_Charveriat'  # Nom d'utilisateur GeoNames
def update_capital_for_user(username, latitude, longitude):
    """
    Met à jour la capitale pour un utilisateur en fonction de ses coordonnées géographiques.
    """
    # Obtenir le nom du pays à partir des coordonnées
    country = get_country_from_coordinates(latitude, longitude, GEONAMES_USERNAME)

    # Si le pays est trouvé, obtenir la capitale
    if country != 'Country information not available.':
        capital = get_capital_from_country(country)
        
        # Si la capitale est trouvée, mettre à jour la base de données
        if capital != 'Capital information not available.':
            con = sqlite3.connect('database.db')
            cursor = con.cursor()
            cursor.execute("UPDATE user SET capitale = ? WHERE username = ?", (capital, username))
            con.commit()
            con.close()

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

def get_capital_coordinates(capitale):
    """
    Cette fonction doit être implémentée pour obtenir les coordonnées de la capitale à partir de son nom.
    Utilise l'API GeoNames pour récupérer la latitude et la longitude de la capitale.
    """
    url = f'http://api.geonames.org/searchJSON?q={capitale}&maxRows=1&username=Mederic_Charveriat&featureCode=PPLC'
    response = requests.get(url)
    data = response.json()
    if data['geonames']:
        lat = data['geonames'][0]['lat']
        lng = data['geonames'][0]['lng']
        return lat, lng
    return None, None
@app.route('/', methods=['GET'])
def index():
   
    con = sqlite3.connect('database.db')
    cursor = con.cursor()

    # Exécuter la requête pour obtenir toutes les données nécessaires, incluant la capitale
    requete2 = """SELECT username, emotion, latitude, longitude, capitale FROM user""" 
    cursor.execute(requete2)
    con.commit()
    data = cursor.fetchall()

    # Initialiser un dictionnaire pour regrouper les émojis par capitale
    grouped_data = {}
    geonames_username = "Mederic_Charveriat"  # Ton nom d'utilisateur GeoNames pour récupérer les capitales

    # Remplir le dictionnaire avec les données, en groupant les émojis par capitale
    for entry in data:
        username, emotion, latitude, longitude, capitale = entry
        
        # Vérifie si la capitale est déjà dans le dictionnaire
        if capitale not in grouped_data:
            # Obtenir les coordonnées de la capitale
            capital_lat, capital_lng = get_capital_coordinates(capitale)
            # Initialiser avec le nom de la capitale et ses coordonnées
            grouped_data[capitale] = [capitale, capital_lat, capital_lng, []]  # Liste pour les émotions

        # Ajouter l'émoji à la liste des émotions pour la capitale correspondante
        grouped_data[capitale][3].append(emotion)

    # Transformer le dictionnaire en liste de listes pour obtenir le résultat final
    final_result = list(grouped_data.values())

    # Afficher le résultat final
   # print(final_result) genere des bug selon la config du pc

    data = final_result
    username = session.get('username')  # Récupère le nom d'utilisateur de la session
    if not username:
        return render_template('index.html', emotion="🙂", data=data, user="invité", send_emoji="""<div id="connect" class="dessus"><a href="/login"><button class="connexion">se connecter</button></a> ou <br><a href="/inscription"><button class="connexion">creer un compte</button></a></div>""")  # Passe le nom d'utilisateur au template
    else:
        # Obtenir l'émotion de l'utilisateur connecté
        cursor.execute("""SELECT emotion FROM user WHERE id = ?""", (session['id'],))
        con.commit()
        emotion = cursor.fetchone()
        emotion = emotion[0] if emotion else "🙂"  # Valeur par défaut si pas d'émotion

        return render_template('index.html', emotion=emotion, user=username, data=data, send_emoji= """
<div id="sentiment" class="dessus">
    <form action="/send_emoji" method="post">
        <p>Comment vous sentez-vous ?</p>
        <label for="emoji-input">Entrez un emoji :</label>
        <input type="text" id="emoji-input" name="emoji-input" maxlength="2" placeholder="😊">
        <p id="message"></p>
        <button type="submit">Envoyer</button>
        <input type="hidden" name="latitude" id="latitude" />
        <input type="hidden" name="longitude" id="longitude" />
    </form>
</div>

<script>
    // Vérifie que le caractère est bien un emoji
    const emojiInput = document.getElementById("emoji-input");
    const message = document.getElementById("message");

    emojiInput.addEventListener("input", () => {
        const emojiPattern = /^[\\u{1F600}-\\u{1F64F}\\u{1F300}-\\u{1F5FF}\\u{1F680}-\\u{1F6FF}\\u{1F700}-\\u{1F77F}\\u{1F780}-\\u{1F7FF}\\u{1F800}-\\u{1F8FF}\\u{1F900}-\\u{1F9FF}\\u{1FA00}-\\u{1FA6F}\\u{1FA70}-\\u{1FAFF}\\u{2600}-\\u{26FF}\\u{2700}-\\u{27BF}]+$/u;
        const inputText = emojiInput.value;

        if (emojiPattern.test(inputText)) {
            message.textContent = "Emoji valide !";
            message.style.color = "green";
        } else {
            message.textContent = "Veuillez entrer une émotion valide (choisissez un emoji sur votre clavier).";
            message.style.color = "red";
        }
    });
</script>
""")

@app.route('/send_emoji', methods=['POST'])
def send_emoji():
    emoji = request.form.get('emoji-input')  # Récupère l'emoji envoyé par le formulaire
    latitude = request.form.get('latitude')
    longitude =request.form.get('longitude')
    print(emoji)
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    requete = """UPDATE user SET emotion = ?, latitude = ?, longitude = ? WHERE id = ?""" 
    cursor.execute(requete, (emoji,latitude, longitude,session['id']))
    con.commit()
    return redirect(url_for('index'))


@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if 'username' in session:  # Vérifie si l'utilisateur est connecté
        return redirect(url_for('index'))
    else:
        return render_template('signup.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    verifPassword = request.form.get('Verif')
    if password == verifPassword:
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        con = sqlite3.connect('database.db')
        cursor = con.cursor()
        requete = """INSERT INTO user (username, password_hash) VALUES (?, ?)"""
        try:
            cursor.execute(requete, (username, password_hash))
            con.commit()
        except:
            erreur = 'Ce nom d\'utilisateur est déjà pris'
            return render_template('signup.html', erreur=erreur)
        return redirect(url_for('connexion'))
    else:
        erreur = "Les 2 mots de passes ne sont pas identiques ! Veuillez réessayer"
        return render_template('signup.html', erreur=erreur)


@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    return render_template('login.html')

def get_country_from_coordinates(lat, lon, geonames_username):
    """
    Utilise l'API GeoNames pour récupérer le nom du pays à partir des coordonnées.
    """
    url = f'http://api.geonames.org/countryCodeJSON?lat={lat}&lng={lon}&username={geonames_username}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        country_data = response.json()
        return country_data.get('countryName', 'Country information not available.')
    except (requests.RequestException, ValueError):
        return 'Country information not available.'

@app.route("/login", methods=['GET', 'POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Connexion à la base de données SQLite pour récupérer les informations utilisateur
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    requete = """SELECT password_hash, latitude, longitude FROM user WHERE username = ?"""
    
    cursor.execute(requete, (username,))
    user = cursor.fetchone()
    con.close()

    if user and bcrypt.check_password_hash(user[0], password):
        # Enregistrer l'utilisateur dans la session
        session['username'] = username  
        latitude, longitude = user[1], user[2]  # Récupérer les coordonnées

        # Appeler la fonction pour mettre à jour la capitale
        update_capital_for_user(username, latitude, longitude)

        # Obtenir l'ID de l'utilisateur pour la session
        con = sqlite3.connect('database.db')
        cursor = con.cursor()
        cursor.execute("SELECT id FROM user WHERE username = ?", (username,))
        userData = cursor.fetchone()
        con.close()

        session['id'] = userData[0]
        return redirect(url_for('index'))
    else:
        erreur = 'Mot de passe ou identifiant incorrect'
        return render_template('login.html', erreur=erreur)

if __name__ == '__main__':
    app.run(debug=True)
