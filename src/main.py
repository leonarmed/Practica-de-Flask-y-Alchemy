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
from models import db, User, Contacts
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

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

# @app.route('/contact', methods=['POST'])
# def create_contact():
#     """
#     Create new contacts
#     """
#     body = request.json
#     new_contact = Contacts()
#     new_contact.name = body["name"]
#     new_contact.email = body["email"]
#     new_contact.phone = body["phone"]
#     new_contact.active = body["active"]
    
#     db.session.add(new_contact)
#     db.session.commit()

#     print(new_contact)
#     print(body)
#     return "Hello", 201

# @app.route("/contact", methods=['POST'])
# def create():
#     body = request.json
#     print(body)
#     new_contact = Contacts.create(body["name"], body["email"], body["phone"], body["active"])
#     if new_contact["success"] and isinstance(new_contact, Contacts):
#         saved = Contacts.save_and_commit(new_contact)
#         if not saved:
#             return jsonify({
#                 "message":"Error interno de la App",
#             }), 500
#         return jsonify([]), 201
    
#     return jsonify({
#         "message":"No se pudo crear"
#     }), 500

@app.route("/contact", methods=["GET", "POST"])
def get_contact():
    if request.method == "GET":
        contact_list = Contacts.query.all()
        print(contact_list)
        contacts_dict = list(map(lambda contact: contact.serialize(), contact_list))
        print(contacts_dict)
        return jsonify({
            "success": True,
            "contacts": contacts_dict
        }), 200
    if request.method == "POST":
        """ 
        Crea una instancia y la almacena en la base de datos. En caso ocurra un error en el proceso, se returna el error correspondiente
        """
        body = request.json
        new_contact = Contacts.create(body) #Creamos la instancia ejecutando el método de clase creado en models

        if not isinstance(new_contact, Contacts): #Si no es una instancia de Contact, quiere decir que ocurrió un error
            print(new_contact)
            return jsonify({
                "message": new_contact["message"]
            }), new_contact["status"]

        contact = Contacts.query.filter_by(email=new_contact.email).one_or_none()  #Obtenemos el contacto para acceder al id, el cual es generado luego de que la instancia se guarda en la base de datos.
        return jsonify({
            "sucess": True,
            "contact": contact.serialize()
        }), 201

@app.route("/getcontact/<int:id>")
def get_contact_by_id(id):
    try:
        contact = Contacts.query.get(id)
        if contact is None:
            return jsonify({
                "success": False,
                "message": "Contact does not exist"
            }), 404
        return jsonify({
            "success": True,
            "contact": contact.serialize()
        }), 200
        print(contact)
    except Exception as error:
        return jsonify({
            "success": False,
            "message": "Error del servidor"
        }), 500

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
