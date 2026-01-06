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
from models import db, User, Character, Planet, FavoriteCharacter, FavoritePlanet
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
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


@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    print(users)
    users_serialized = []
    for user in users:
        users_serialized.append(user.serialize())
    print(users_serialized)
    return jsonify({'data': users_serialized})


@app.route('/user', methods=['POST'])
def add_user():
    body = request.get_json(silent=True)
    print("BODY:", body)
    if body is None:
        return jsonify({'msg': 'Debes enviar información en el body'}), 400
    if 'name' not in body:
        return jsonify({'msg': 'el campo name es obligatorio'}), 400
    if 'email' not in body:
        return jsonify({'msg': 'el campo email es obligatorio'}), 400
    if 'password' not in body:
        return jsonify({'msg': 'el campo password es obligatorio'}), 400
    if 'is_active' not in body:
        return jsonify({'msg': 'el campo password es obligatorio'}), 400


    new_user = User (

        name=body ['name'],
        email=body ['email'],
        password=body ['password'],
        is_active=body ['is_active']
    )
    db.session.add(new_user)
    db.session.commit()
    
    return  jsonify ({'msg' :' Usuario creado', 'data' : new_user.serialize () }),201
    


@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'msg': f' El usuario con ide {user_id} no existe'}), 404

    favorites_characters_serialized = []
    for favorite_character in user.favorite_character:
        print(favorite_character.character.serialize())
        favorites_characters_serialized.append(
            favorite_character.character.serialize())
        
    favorites_planets_serialized = []
    for favorite_planet in user.favorite_planet:
        print(favorite_planet.planet.serialize())
        favorites_planets_serialized.append(
            favorite_planet.planet.serialize())

    return jsonify({'msg': 'Estos son tus favoritos',
                    'favorite_characters': favorites_characters_serialized, 'favorite_planets': favorites_planets_serialized}), 200


@app.route('/characters', methods=['GET'])
def get_characters():
    characters = Character.query.all()
    print(characters)
    characters_serialized = []
    for character in characters:
        characters_serialized.append(character.serialize())
    print(characters_serialized)
    return jsonify({'data': characters_serialized})


@app.route('/characters/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character = Character.query.get(character_id)

    if character is None:
        return jsonify({"msg": "Character no encontrado"}), 404

    return jsonify({"data": character.serialize()}), 200


@app.route('/character', methods=['POST'])
def add_character():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'Debes enviar información en el body'}), 400
    if 'name' not in body:
        return jsonify({'msg': 'el campo name es obligatorio'}), 400
    if 'height' not in body:
        return jsonify({'msg': 'el campo height es obligatorio'}), 400
    if 'weight' not in body:
        return jsonify({'msg': 'el campo weight es obligatorio'}), 400

    new_character = Character()
    new_character.name = body['name']
    new_character.height = body['height']
    new_character.weight = body['weight']
    db.session.add(new_character)
    db.session.commit()
    return jsonify({'msg': 'Usuario agregado exitosamente'}), 201


@app.route('/favorite/character/<int:character_id>/user/<int:user_id>', methods=['POST'])
def add_favoritecharacter(character_id, user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'msg': 'User no encontrado'}), 404

    character = Character.query.get(character_id)
    if character is None:
        return jsonify({'msg': 'Character no encontrado'}), 404

    new_fav = FavoriteCharacter(user_id=user_id, character_id=character_id)
    db.session.add(new_fav)
    db.session.commit()

    return jsonify({
        "msg": "Favorito agregado",
        "data": {
            "id": new_fav.id,
            "user_id": new_fav.user_id,
            "character_id": new_fav.character_id
        }

    }), 201


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    print(planets)
    planets_serialized = []
    for planet in planets:
        planets_serialized.append(planet.serialize())
    print(planets_serialized)
    return jsonify({'data': planets_serialized})


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)

    if planet is None:
        return jsonify({"msg": "Planet no encontrado"}), 404

    return jsonify({"data": planet.serialize()}), 200


@app.route('/planet', methods=['POST'])
def add_planet():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'Debes enviar información en el body'}), 400
    if 'name' not in body:
        return jsonify({'msg': 'el campo name es obligatorio'}), 400
    if 'density' not in body:
        return jsonify({'msg': 'el campo density es obligatorio'}), 400

    new_planet = Planet()
    new_planet.name = body['name']
    new_planet.density = body['density']
    db.session.add(new_planet)
    db.session.commit()
    return jsonify({'msg': 'Planeta agregado exitosamente'}), 201


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)


@app.route('/favorite/planet/<int:planet_id>/user/<int:user_id>', methods=['POST'])
def add_favoriteplanet(planet_id, user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'msg': 'User no encontrado'}), 404

    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({'msg': 'Planet no encontrado'}), 404

    new_fav = FavoritePlanet(user_id=user_id, planet_id=planet_id)
    db.session.add(new_fav)
    db.session.commit()

    return jsonify({
        "msg": "Favorito agregado",
        "data": {
            "id": new_fav.id,
            "user_id": new_fav.user_id,
            "planet_id": new_fav.planet_id
        }

    }), 201



@app.route('/favorite/planet/<int:planet_id>/user/<int:user_id>', methods=['DELETE'])
def delete_favoriteplanet(planet_id, user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'msg': 'User no encontrado'}), 404

    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({'msg': 'Planet no encontrado'}), 404
    
    fav = FavoritePlanet.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if fav is None:
        return jsonify ({'msg': 'Ese favorito no existe'}), 404

    db.session.delete(fav)
    db.session.commit()

    return jsonify({
        "msg": "Favorito eliminado",
        "data": {
            "id": fav.id,
            "user_id": fav.user_id,
            "planet_id": fav.planet_id
        }

    }), 200



@app.route('/favorite/character/<int:character_id>/user/<int:user_id>', methods=['DELETE'])
def delete_favoritecharacter(character_id, user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'msg': 'User no encontrado'}), 404

    character = Character.query.get(character_id)
    if character is None:
        return jsonify({'msg': 'Personaje no encontrado'}), 404
    
    fav = FavoriteCharacter.query.filter_by(user_id=user_id, character_id= character_id).first()
    if fav is None:
        return jsonify ({'msg': 'Ese favorito no existe'}), 404

    db.session.delete(fav)
    db.session.commit()

    return jsonify({
        "msg": "Favorito eliminado",
        "data": {
            "id": fav.id,
            "user_id": fav.user_id,
            "character_id": fav.character_id
        }

    }), 200