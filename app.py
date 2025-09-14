# from flask import Flask, request, jsonify
# from flask_pymongo import PyMongo
# from flask_bcrypt import Bcrypt
# from flask_jwt_extended import (
#     JWTManager, create_access_token, jwt_required,
#     get_jwt_identity, get_jwt, unset_jwt_cookies
# )
# from flask_cors import CORS
# from werkzeug.utils import secure_filename
# import datetime, os


# app = Flask(__name__)


# app.config["MONGO_URI"] = "mongodb+srv://railmatrixsih_db_user:CSiHNEUKIInSVvv2@railmatrix.kaguhoo.mongodb.net/railmatrix?retryWrites=true&w=majority"
# app.config["JWT_SECRET_KEY"] = "super-secret"  
# app.config["UPLOAD_FOLDER"] = "uploads"


# mongo = PyMongo(app)
# bcrypt = Bcrypt(app)
# jwt = JWTManager(app)
# CORS(app)


# os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# jwt_blacklist = set()
# user_created = False


# @jwt.token_in_blocklist_loader
# def check_if_token_revoked(jwt_header, jwt_payload):
#     jti = jwt_payload["jti"]
#     return jti in jwt_blacklist


# @app.route("/", methods=["GET"])
# def home():
#     return "RailMatrix API is running."


# @app.route('/favicon.ico')
# def favicon():
#     return '', 204


# # Create default user on first request (alternative to before_first_request)
# @app.before_request
# def create_default_user():
#     global user_created
#     if not user_created:
#         if not mongo.db.users.find_one({"email": "inspector@rail.com"}):
#             hashed_pwd = bcrypt.generate_password_hash("rail123").decode("utf-8")
#             user = {
#                 "name": "Railway Inspector",
#                 "email": "inspector@rail.com",
#                 "password": hashed_pwd,
#                 "role": "inspector"
#             }
#             mongo.db.users.insert_one(user)
#             print("Default user created: inspector@rail.com / rail123")
#         user_created = True


# @app.route("/login", methods=["POST"])
# def login():
#     data = request.get_json()
#     if not data or not all(k in data for k in ("email", "password")):
#         return jsonify({"msg": "Email and password required"}), 400
    
#     user = mongo.db.users.find_one({"email": data["email"]})
#     if user and bcrypt.check_password_hash(user["password"], data["password"]):
#         access_token = create_access_token(identity=str(user["_id"]))
#         return jsonify({
#             "access_token": access_token, 
#             "user_id": str(user["_id"]), 
#             "name": user["name"]
#         }), 200
#     return jsonify({"msg": "Invalid email or password"}), 401


# @app.route("/logout", methods=["POST"])
# @jwt_required()
# def logout():
#     jti = get_jwt()["jti"]
#     jwt_blacklist.add(jti)
#     return jsonify({"msg": "Successfully logged out"}), 200


# @app.route("/defect/upload", methods=["POST"])
# @jwt_required()
# def defect_upload():
#     if 'image' not in request.files:
#         return jsonify({"msg": "No image uploaded"}), 400
    
#     image = request.files['image']
#     if image.filename == '':
#         return jsonify({"msg": "No image selected"}), 400
    
#     fitting_type = request.form.get("fitting_type")
#     location = request.form.get("location")
#     remarks = request.form.get("remarks", "")
    
#     if not fitting_type or not location:
#         return jsonify({"msg": "fitting_type and location are required"}), 400
    
#     # Save image with timestamp
#     timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S_")
#     filename = secure_filename(timestamp + image.filename)
#     filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
#     image.save(filepath)
    
#     # AI classification result (replace with actual AI model)
#     classification = "Defect_Detected"
#     confidence = 0.87
    
#     # Save to database
#     record = {
#         "user_id": get_jwt_identity(),
#         "filename": filename,
#         "fitting_type": fitting_type,
#         "location": location,
#         "remarks": remarks,
#         "classification": classification,
#         "confidence": confidence,
#         "timestamp": datetime.datetime.utcnow()
#     }
#     result = mongo.db.defect_logs.insert_one(record)
    
#     return jsonify({
#         "result": classification,
#         "confidence": confidence,
#         "record_id": str(result.inserted_id),
#         "msg": "Defect uploaded successfully"
#     }), 201


# # RETRIEVAL ENDPOINTS
# @app.route("/defects", methods=["GET"])
# @jwt_required()
# def get_defects():
#     user_id = get_jwt_identity()
#     defects = list(mongo.db.defect_logs.find({"user_id": user_id}).sort("timestamp", -1))
    
#     for defect in defects:
#         defect["_id"] = str(defect["_id"])
#         defect["timestamp"] = defect["timestamp"].isoformat()
    
#     return jsonify({
#         "defects": defects,
#         "count": len(defects)
#     }), 200


# @app.route("/defects/<record_id>", methods=["GET"])
# @jwt_required()
# def get_defect_details(record_id):
#     user_id = get_jwt_identity()
#     try:
#         from bson import ObjectId
#         defect = mongo.db.defect_logs.find_one({"_id": ObjectId(record_id), "user_id": user_id})
#         if not defect:
#             return jsonify({"msg": "Defect not found"}), 404
        
#         defect["_id"] = str(defect["_id"])
#         defect["timestamp"] = defect["timestamp"].isoformat()
#         return jsonify({"defect": defect}), 200
#     except:
#         return jsonify({"msg": "Invalid record ID"}), 400


# @app.route("/stats", methods=["GET"])
# @jwt_required()
# def get_stats():
#     user_id = get_jwt_identity()
    
#     total = mongo.db.defect_logs.count_documents({"user_id": user_id})
    
#     # Group by fitting type
#     type_stats = list(mongo.db.defect_logs.aggregate([
#         {"$match": {"user_id": user_id}},
#         {"$group": {"_id": "$fitting_type", "count": {"$sum": 1}}}
#     ]))
    
#     # Group by location
#     location_stats = list(mongo.db.defect_logs.aggregate([
#         {"$match": {"user_id": user_id}},
#         {"$group": {"_id": "$location", "count": {"$sum": 1}}}
#     ]))
    
#     return jsonify({
#         "total_defects": total,
#         "by_type": type_stats,
#         "by_location": location_stats
#     }), 200


# if __name__ == "__main__":
#     app.run(debug=True)

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
import hashlib
import hmac



app = Flask(__name__)



app.config["MONGO_URI"] = "mongodb+srv://railmatrixsih_db_user:CSiHNEUKIInSVvv2@railmatrix.kaguhoo.mongodb.net/railmatrix?retryWrites=true&w=majority"
app.config["JWT_SECRET_KEY"] = "super-secret"  
app.config["UPLOAD_FOLDER"] = "uploads"



mongo = PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app)



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
        return jsonify(access_token=access_token, user_id=str(user["_id"]), name=user["name"])
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
    
    # Save with timestamp
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S_")
    filename = secure_filename(timestamp + image.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image.save(filepath)
    
    classification = "Defect_Detected"  # Replace with AI model result when ready
    confidence = 0.87
    
    record = {
        "user_id": get_jwt_identity(),
        "filename": filename,
        "fitting_type": fitting_type,
        "location": location,
        "remarks": remarks,
        "classification": classification,
        "confidence": confidence,
        "timestamp": datetime.datetime.utcnow()
    }
    result = mongo.db.defect_logs.insert_one(record)
    return jsonify({
        "result": classification, 
        "confidence": confidence,
        "record_id": str(result.inserted_id)
    }), 201



# RETRIEVAL ENDPOINTS
@app.route("/defects", methods=["GET"])
@jwt_required()
def get_all_defects():
    user_id = get_jwt_identity()
    defects = list(mongo.db.defect_logs.find({"user_id": user_id}).sort("timestamp", -1))
    
    for defect in defects:
        defect["_id"] = str(defect["_id"])
        defect["timestamp"] = defect["timestamp"].isoformat()
    
    return jsonify({"defects": defects, "count": len(defects)}), 200



@app.route("/defects/<record_id>", methods=["GET"])
@jwt_required()
def get_defect_by_id(record_id):
    user_id = get_jwt_identity()
    try:
        from bson import ObjectId
        defect = mongo.db.defect_logs.find_one({"_id": ObjectId(record_id), "user_id": user_id})
        if not defect:
            return jsonify({"msg": "Defect record not found"}), 404
        
        defect["_id"] = str(defect["_id"])
        defect["timestamp"] = defect["timestamp"].isoformat()
        return jsonify({"defect": defect}), 200
    except:
        return jsonify({"msg": "Invalid record ID"}), 400



@app.route("/stats", methods=["GET"])
@jwt_required()
def get_user_stats():
    user_id = get_jwt_identity()
    
    total_defects = mongo.db.defect_logs.count_documents({"user_id": user_id})
    
    # Count by fitting type
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$fitting_type", "count": {"$sum": 1}}}
    ]
    type_stats = list(mongo.db.defect_logs.aggregate(pipeline))
    
    # Count by location
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$location", "count": {"$sum": 1}}}
    ]
    location_stats = list(mongo.db.defect_logs.aggregate(pipeline))
    
    return jsonify({
        "total_defects": total_defects,
        "by_type": type_stats,
        "by_location": location_stats
    }), 200



# NEW QR CODE RETRIEVAL ENDPOINT
@app.route("/qr/retrieve", methods=["POST"])
@jwt_required()
def retrieve_qr_details():
    """
    Retrieve QR code details using UID and HMAC for verification
    Expected payload: {"uid": "unique_id", "hmac": "hash_value"}
    """
    try:
        data = request.get_json()
        
        if not data or 'uid' not in data or 'hmac' not in data:
            return jsonify({"error": "UID and HMAC are required"}), 400
        
        uid = data['uid']
        provided_hmac = data['hmac']
        
        # Find QR record by UID
        qr_record = mongo.db.qr_codes.find_one({"uid": uid})
        
        if not qr_record:
            return jsonify({"error": "QR code not found"}), 404
        
        # Verify HMAC (using a secret key for HMAC verification)
        secret_key = "your-hmac-secret-key-change-in-production"
        expected_hmac = hmac.new(
            secret_key.encode(), 
            uid.encode(), 
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(provided_hmac, expected_hmac):
            return jsonify({"error": "Invalid HMAC - Authentication failed"}), 401
        
        # Convert ObjectId to string for JSON response
        qr_record["_id"] = str(qr_record["_id"])
        if "user_id" in qr_record:
            qr_record["user_id"] = str(qr_record["user_id"])
        
        # Return QR details
        return jsonify({
            "status": "success",
            "qr_details": {
                "uid": qr_record["uid"],
                "location": qr_record.get("location", "N/A"),
                "fitting_type": qr_record.get("fitting_type", "N/A"),
                "installation_date": qr_record.get("installation_date"),
                "last_inspection": qr_record.get("last_inspection"),
                "status": qr_record.get("status", "active"),
                "metadata": qr_record.get("metadata", {}),
                "created_at": qr_record.get("created_at"),
                "updated_at": qr_record.get("updated_at")
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# BONUS: Create QR Code endpoint (for testing purposes)
@app.route("/qr/create", methods=["POST"])
@jwt_required()
def create_qr_code():
    """
    Create a new QR code record for testing
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Generate unique UID
        uid = data.get("uid") or f"QR_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Generate HMAC
        secret_key = "your-hmac-secret-key-change-in-production"
        hmac_value = hmac.new(
            secret_key.encode(), 
            uid.encode(), 
            hashlib.sha256
        ).hexdigest()
        
        # Create QR record
        from bson import ObjectId
        qr_data = {
            "uid": uid,
            "hmac": hmac_value,
            "location": data.get("location", "Default Location"),
            "fitting_type": data.get("fitting_type", "elastic_clip"),
            "installation_date": data.get("installation_date", datetime.datetime.utcnow().isoformat()),
            "last_inspection": None,
            "status": "active",
            "metadata": data.get("metadata", {}),
            "created_by": ObjectId(current_user_id),
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow()
        }
        
        result = mongo.db.qr_codes.insert_one(qr_data)
        
        return jsonify({
            "message": "QR code created successfully",
            "qr_id": str(result.inserted_id),
            "uid": uid,
            "hmac": hmac_value
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True)
