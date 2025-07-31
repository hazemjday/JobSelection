import logging
from flask import Flask
from flask_jwt_extended import JWTManager, get_jwt, jwt_required, create_access_token, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
import os
import time
import socket
from flask_cors import CORS 
logging.basicConfig(level=logging.INFO) 
from flask import Flask, request, jsonify
from datetime import timedelta
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])
# Connexion à MySQL via variables d’environnement
DB_USER = os.getenv("DB_USER", "hazem")
DB_PASSWORD = os.getenv("DB_PASSWORD", "hazem")
DB_HOST = os.getenv("DB_HOST", "mysql")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "users")

# Format : mysql+pymysql://user:password@host:port/dbname
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'votre_cle_secrete'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Modèle User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')


def wait_for_mysql(host, port):
    while True:
        try:
            socket.create_connection((host, int(port)), timeout=5)
            print(" MySQL est prêt.")
            break
        except OSError:
            print("En attente de MySQL...")
            time.sleep(2)



with app.app_context():
    wait_for_mysql(DB_HOST, DB_PORT)
    db.create_all()


# ajout de utulisateur


@app.route('/register', methods=['POST'])
@jwt_required()
def register():
    try:
        # Logging de la requête
        app.logger.info(f"\n{'='*50}\nNouvelle tentative d'enregistrement")
        # Récupération de l'utilisateur courant
        current_user = get_jwt_identity()
        claims = get_jwt() 
        app.logger.info(f"Utilisateur actuel: {current_user}")
        # Vérification des privilèges admin
        if claims.get('role') != "admin":
            app.logger.warning(f"Tentative non autorisée par {current_user}")
            return jsonify({
                "msg": "Accès refusé",
                "error": "admin_privilege_required",
                "required_role": "admin"
            }), 403           
        data = request.get_json()

        if not data:
            app.logger.error("Aucune donnée JSON reçue")
            return jsonify({"msg": "Données manquantes"}), 400
            
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'user').lower()  # Normalisation en minuscules
        app.logger.info(f"Tentative création utilisateur: {username} ({role})")
        
        # Validation des champs
        if not username or not password:
            app.logger.warning("Champs obligatoires manquants")
            return jsonify({
                "msg": "Nom d'utilisateur et mot de passe requis",
                "missing_fields": [
                    field for field in ['username', 'password'] 
                    if not data.get(field)
                ]
            }), 400
        
                # Vérification de l'unicité
        if User.query.filter_by(username=username).first():
            app.logger.warning(f"Nom d'utilisateur déjà utilisé: {username}")
            return jsonify({
                "msg": "Nom d'utilisateur indisponible"
            }), 409  

        # Création de l'utilisateur
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            username=username,
            password=hashed_password,
            role=role,
        )
        
        db.session.add(new_user)
        db.session.commit()
        app.logger.info(f"Utilisateur créé avec succès: {username} (ID: {new_user.id})")

        return jsonify({
            "msg": "Utilisateur créé",
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "role": new_user.role,
            }
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f"Erreur base de données: {str(e)}", exc_info=True)
        return jsonify({
            "msg": "Erreur de base de données",
            "error": "database_error"
        }), 500
        
    except Exception as e:
        app.logger.error(f"Erreur inattendue: {str(e)}", exc_info=True)
        return jsonify({
            "msg": "Erreur interne du serveur",
            "error": "server_error"
        }), 500


#login et reception de jwttoken
@app.route('/login', methods=['POST'])
def login():
    try:
        # Initialisation logging
        app.logger.info(f"\n{'='*50}\nNouvelle tentative de login ")
        
        # Récupération des données
        data = request.get_json()
        if not data:
            app.logger.error("Aucune donnée JSON reçue")
            return jsonify({"msg": "Données manquantes"}), 400

        username = data.get('username')
        password = data.get('password')
        app.logger.info(f"Tentative de connexion pour: {username}")

        # Validation des champs
        if not username or not password:
            app.logger.warning("Champs manquants")
            return jsonify({"msg": "Nom d'utilisateur et mot de passe requis"}), 400

        # Recherche utilisateur
        user = User.query.filter_by(username=username).first()
        if not user:
            app.logger.warning(f"Utilisateur {username} non trouvé")
            return jsonify({"msg": "Identifiants invalides"}), 401

        # Vérification mot de passe
        if not bcrypt.check_password_hash(user.password, password):
            app.logger.warning("Mot de passe incorrect")
            return jsonify({"msg": "Identifiants invalides"}), 401

        
        access_token = create_access_token(
           identity=user.username,  # doit être une string
          additional_claims={"role": user.role
                             }  
           )
        app.logger.info(f"Connexion réussie pour {username}")

        # Réponse
        return jsonify({
            "token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role
            }
        })

    except Exception as e:
        app.logger.error(f"ERREUR: {str(e)}", exc_info=True)
        return jsonify({
            "msg": "Erreur d'authentification",
            "error": str(e)
        }), 500


# avoir tous les utulisateurs

@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    try:
        # Vérifier si l'utilisateur est un administrateur
        current_user = get_jwt_identity()
        claims = get_jwt()
        if claims.get('role') != "admin":
            app.logger.warning(f"Tentative non autorisée par {current_user}")
            return jsonify({
                "msg": "Accès refusé",
                "error": "admin_privilege_required",
                "required_role": "admin"
            }), 403

        # Récupérer tous les utilisateurs
        users = User.query.all()
        user_data = [
            {
                "id": user.id,
                "username": user.username,
                "role": user.role,
            }
            for user in users
        ]

        return jsonify(user_data), 200

    except Exception as e:
        app.logger.error(f"Erreur lors de la récupération des utilisateurs: {str(e)}")
        return jsonify({"msg": "Erreur lors de la récupération des utilisateurs", "error": str(e)}), 500



@app.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        current_user = get_jwt_identity()
        claims = get_jwt()
        if claims.get('role') != "admin":
            app.logger.warning(f"Tentative non autorisée par {current_user}")
            return jsonify({
                "msg": "Accès refusé",
                "error": "admin_privilege_required",
                "required_role": "admin"
            }), 403

        # Rechercher l'utilisateur à supprimer
        user = User.query.get(user_id)
        if not user:
            app.logger.warning(f"Utilisateur avec ID {user_id} non trouvé")
            return jsonify({"msg": "Utilisateur non trouvé"}), 404

        # Supprimer l'utilisateur
        db.session.delete(user)
        db.session.commit()

        app.logger.info(f"Utilisateur avec ID {user_id} supprimé par {current_user}")
        return jsonify({"msg": "Utilisateur supprimé avec succès"}), 200

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erreur lors de la suppression de l'utilisateur : {str(e)}", exc_info=True)
        return jsonify({"msg": "Erreur interne du serveur", "error": str(e)}), 500
    


from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)  # Initialise Bcrypt

# ... tes autres imports + config Flask + modèle User ...

def create_admin_user():
    """Créer un utilisateur admin s'il n'existe pas déjà."""
    with app.app_context():
        admin_username = "admin"
        admin_password = "adminpass"  # 💡 Change ce mot de passe après le test
        existing_admin = User.query.filter_by(username=admin_username).first()

        if existing_admin:
            app.logger.info("Admin déjà présent.")
        else:
            hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')
            new_admin = User(username=admin_username, password=hashed_password, role="admin")
            db.session.add(new_admin)
            db.session.commit()
            app.logger.info(f"Admin '{admin_username}' créé avec succès.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)