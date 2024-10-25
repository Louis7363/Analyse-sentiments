from flask import Flask, render_template

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', test="🙂")  # Utilise un emoji directement ou texte
@app.route('/connect')
def connect():
    return render_template('connect.html')  # Utilise un emoji directement ou texte
@app.route('/connect-try',methods=['Post'])
def connect_try():
    
    return render_template('index.html')  # Utilise un emoji directement ou texte
if __name__ == '__main__':
    app.run(debug=True)
