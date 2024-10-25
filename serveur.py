from flask import Flask, session, flash, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yzdgiauaoi478GIEZ87Y2iad'  # Change à une clé secrète réelle
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_bdd.db'  # Tu peux mettre ta base ici
bcrypt = Bcrypt(app)  # Initialise la fonction Bcrypt

# Importation du module sqlite3 de gestion de base de données
import sqlite3


@app.route('/', methods=['GET'])
def index():
    username = session.get('username')  # Récupère le nom d'utilisateur de la session
    return render_template('index.html', test="🙂", user=username)  # Passe le nom d'utilisateur au template


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
