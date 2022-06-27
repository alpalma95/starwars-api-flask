"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    users = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users))

    return jsonify(all_users), 200

@app.route('/planets', methods=['GET'])
def planet_list():

    planets = Planet.query.all()
    planets_serialized = list(map(lambda x: x.serialize_basics(), planets))

    return jsonify(planets_serialized), 200

@app.route('/people', methods=['GET'])
def people_list():

    people = Character.query.all()
    people_serialized = list(map(lambda x: x.serialize_basics(), people))

    return jsonify(people_serialized), 200

@app.route('/people/<int:character_id>', methods=["GET"])
def get_character_details(character_id):
    character = Character.query.get(character_id)
    char_ser = character.serialize()

    return jsonify(char_ser)

@app.route('/planets/<int:planet_id>', methods=["GET"])
def get_planet_details(planet_id):
    planet = Planet.query.get(planet_id)
    planet_ser = planet.serialize()

    return jsonify(planet_ser)

@app.route('/favorites/<int:user_id>', methods=['POST'])
def add_favorite(user_id):
    request_body = request.get_json(force=True)

    user = User.query.get(user_id)
    uid = request_body["uid"]
    element_id = uid[2:]
    new_favorite = None

    if uid.startswith("c"):
        new_favorite = Favorite(user_id=user.id, character_id=element_id)
    else:
        new_favorite = Favorite(user_id=user.id, planet_id=element_id)

    db.session.add(new_favorite)
    db.session.commit()
    

    return jsonify(new_favorite.serialize())


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
