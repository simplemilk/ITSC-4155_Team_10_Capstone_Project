from flask import Flask
from models import db
from routes import budget_bp
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///niner_finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.register_blueprint(budget_bp)
CORS(app)

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "Flask server is up."

if __name__ == "__main__":
    app.run(debug=True)
