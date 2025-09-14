from pymongo import MongoClient
from flask_bcrypt import Bcrypt

# Connect to MongoDB
client = MongoClient("mongodb+srv://railmatrixsih_db_user:CSiHNEUKIInSVvv2@railmatrix.kaguhoo.mongodb.net/railmatrix?retryWrites=true&w=majority")
db = client.railmatrix

# Initialize bcrypt
bcrypt = Bcrypt()

# Create test user
test_user = {
    "name": "Test Inspector",
    "email": "test@railmatrix.com",
    "password": bcrypt.generate_password_hash("test123").decode("utf-8"),
    "role": "inspector"
}

# Insert user
result = db.users.insert_one(test_user)
print(f"Test user created successfully!")
print(f"User ID: {result.inserted_id}")
print(f"Login credentials:")
print(f"Email: test@railmatrix.com")
print(f"Password: test123")
