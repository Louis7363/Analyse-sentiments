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


@app.route('/', methods=['GET'])
def index():
    username = session.get('username')  # Récupère le nom d'utilisateur de la session
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    requete2 = """SELECT username,emotion,latitude,longitude FROM user""" 
    cursor.execute(requete2)
    con.commit()
    data=cursor.fetchall()
    if not username:
        return render_template('index.html', emotion="🙂",data=data, user="invité",send_emoji="""<div id="connect" class="dessus"><a href="/login"><button class="connexion">se connecter</button></a><br><a href="/inscription"><button class="connexion">creer un compte</button></a></div>""")  # Passe le nom d'utilisateur au template
    else:
        con = sqlite3.connect('database.db')
        cursor = con.cursor()
        requete = """SELECT emotion FROM user WHERE id = ?""" 
        cursor.execute(requete, (session['id'],))
        con.commit()
        emotion= cursor.fetchone()
        emotion = emotion[0]
        
        

        return render_template('index.html', emotion=emotion, user=username ,data=data, send_emoji= """
<div id="sentiment" class="dessus">
    <form action="/send_emoji" method="post">
        <p>Comment vous sentez-vous ?</p>
        <label for="emoji-input">Entrez un emoji :</label>
        <input type="text" id="emoji-input" name="emoji-input" maxlength="2" placeholder="😊">
        <p id="message"></p>
        <button class="connexion" type="submit">Envoyer</button>
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


@app.route("/login", methods=['GET', 'POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Connexion à la base de données SQLite
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    requete = """SELECT password_hash FROM user WHERE username = ?"""
    # Rechercher l'utilisateur dans la base de données
    cursor.execute(requete, (username,))
    user = cursor.fetchone()
    con.close()

    if user and bcrypt.check_password_hash(user[0], password):
        session['username'] = username  # Enregistrer l'utilisateur dans la session
        con = sqlite3.connect('database.db')
        cursor = con.cursor()
        requete = """SELECT id FROM user WHERE username = ?"""
        cursor.execute(requete, (username,))
        userData = cursor.fetchone()
        id = userData[0]
        session['id'] = id
        return redirect(url_for('index'))
    else:
        erreur = 'Mot de passe ou identifiant incorrect'
        return render_template('login.html', erreur=erreur)

if __name__ == '__main__':
    app.run(debug=True)