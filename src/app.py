"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os, json
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, CharacterFavorite, Planet, PlanetFavorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
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

@app.route('/users', methods=['GET'])
def get_users():

    users = User.query.all()

    if users:
        serialized_users = list(map(lambda user: user.serialize(), users))
        return jsonify(serialized_users), 200
    else:
        return jsonify({"msg": "not found"}), 404


@app.route('/characters', methods=['GET'])
def get_characters():

    characters = Character.query.all()

    if characters:
        serialized_characters = list(map(lambda character: character.serialize(), characters))
        return jsonify(serialized_characters), 200
    else:
        return jsonify({"msg": "not found"}), 404
    

@app.route('/planets', methods=['GET'])
def get_planets():

    planets = Planet.query.all()

    if planets:
        serialized_planets = list(map(lambda planet: planet.serialize(), planets))
        return jsonify(serialized_planets), 200
    else:
        return jsonify({"msg": "not found"}), 404


@app.route('/user', methods=['POST'])
def create_one_user():
    body = json.loads(request.data)
    new_user = User(
        email = body["email"],
        password = body["password"],
        is_active = True
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": f"User {body['email']} created succesfull"}), 200


@app.route('/character', methods=['POST'])
def create_one_character():
    body = json.loads(request.data)
    new_character = Character(
        name = body["name"],
        eye_color = body["eye_color"],
        gender = body["gender"],
        weight = body ["weight"]
    )
    db.session.add(new_character)
    db.session.commit()
    return jsonify({"msg": f"Character {body['name']} created succesfull"}), 200


@app.route('/planet', methods=['POST'])
def create_one_planet():
    body = json.loads(request.data)
    new_planet = Planet(
        name = body["name"],
        diameter = body["diameter"],
        climate = body["climate"],
        
    )
    db.session.add(new_planet)
    db.session.commit()
    return jsonify({"msg": f"Planet {body['name']} created succesfull"}), 200

@app.route('/planet/<int:planet_id>', methods=['PUT'])
def modify_one_planet(planet_id):
    planet = Planet.query.get(planet_id)
    body = json.loads(request.data)

    if planet is None:
        raise APIException(f'Planet {planet_id} not found', status_code=404)

    for key in body:
        for col in planet.serialize():
            if key == col and key != "id":
                setattr(planet, col, body[key])
    
    db.session.commit()
    return jsonify({"msg": f"Planet {planet_id} modified succesfull"}), 200


@app.route('/character/favorite/<int:favorite_id>', methods=['DELETE'])
def delete_one_character_favorite(favorite_id):
    delete_character_favorite = CharacterFavorite.query.get(favorite_id)
    db.session.delete(delete_character_favorite)
    db.session.commit()
    return jsonify({"msg": f"Character favorite {favorite_id} deleted succesfully"}), 200

    

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_one_planet(planet_id):
    delete_planet = Planet.query.get(planet_id)
    db.session.delete(delete_planet)
    db.session.commit()
    return jsonify({"msg": f"Planet {planet_id} deleted succesfully"}), 200


@app.route('/character/<int:character_id>', methods=['DELETE'])
def delete_one_character(character_id):
    delete_character = Character.query.get(character_id)
    db.session.delete(delete_character)
    db.session.commit()
    return jsonify({"msg": f"Character {character_id} deleted succesfully"}), 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
