from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity, get_jwt, unset_jwt_cookies
)
from flask_cors import CORS
from werkzeug.utils import secure_filename
import datetime, os

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb+srv://railmatrixsih_db_user:CSiHNEUKIInSVvv2@railmatrix.kaguhoo.mongodb.net/railmatrix?retryWrites=true&w=majority"
app.config["JWT_SECRET_KEY"] = "super-secret"  
app.config["UPLOAD_FOLDER"] = "uploads"

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app)  # Enable CORS

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

jwt_blacklist = set()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in jwt_blacklist

@app.route("/", methods=["GET"])
def home():
    return "RailMatrix API is running."

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not all(k in data for k in ("name", "email", "password", "role")):
        return jsonify({"msg": "Incomplete registration data"}), 400
    if mongo.db.users.find_one({"email": data["email"]}):
        return jsonify({"msg": "User already exists"}), 409
    hashed_pwd = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    user = {
        "name": data["name"],
        "email": data["email"],
        "password": hashed_pwd,
        "role": data["role"]
    }
    mongo.db.users.insert_one(user)
    return jsonify({"msg": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not all(k in data for k in ("email", "password")):
        return jsonify({"msg": "Incomplete login data"}), 400
    user = mongo.db.users.find_one({"email": data["email"]})
    if user and bcrypt.check_password_hash(user["password"], data["password"]):
        access_token = create_access_token(identity=str(user["_id"]))
        return jsonify(access_token=access_token)
    return jsonify({"msg": "Invalid credentials"}), 401

@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    jwt_blacklist.add(jti)
    response = jsonify({"msg": "Logout successful"})
    unset_jwt_cookies(response)
    return response

@app.route("/defect/upload", methods=["POST"])
@jwt_required()
def defect_upload():
    if 'image' not in request.files:
        return jsonify({"msg": "No image part"}), 400
    image = request.files['image']
    fitting_type = request.form.get("fitting_type")
    location = request.form.get("location")
    remarks = request.form.get("remarks", "")
    if not all([image, fitting_type, location]):
        return jsonify({"msg": "Missing required form data"}), 400
    filename = secure_filename(image.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image.save(filepath)
    classification = "Defect_Class"  # Replace with AI model result when ready
    record = {
        "user_id": get_jwt_identity(),
        "filename": filename,
        "fitting_type": fitting_type,
        "location": location,
        "remarks": remarks,
        "classification": classification,
        "timestamp": datetime.datetime.utcnow()
    }
    result = mongo.db.defect_logs.insert_one(record)
    return jsonify({"result": classification, "record_id": str(result.inserted_id)}), 201

if __name__ == "__main__":
    app.run(debug=True)
