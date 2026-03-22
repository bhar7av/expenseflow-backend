from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from models import db
from auth import auth_bp
from routes import expenses_bp

app = Flask(__name__)

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenseflow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'expenseflow-super-secret-key-change-in-production'

# Extensions
db.init_app(app)
JWTManager(app)
CORS(app)

# Blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(expenses_bp, url_prefix='/api')

# Create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
    