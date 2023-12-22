from flask import Flask, jsonify, request, redirect, url_for, session
from pymongo import MongoClient
from cloudinary import config, utils
from flask_cors import CORS
from bson import ObjectId
from functools import wraps
from flask_bcrypt import Bcrypt

app = Flask(__name__)
CORS(app)
app.secret_key = 'mysecretkey123'

bcrypt = Bcrypt(app)


def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')


# Create a MongoClient object with your connection string
connection_string = 'mongodb+srv://cardio1697:Root123@cluster0.o1uhh6a.mongodb.net/Cardio_Test?tlsCAFile=cacert.pem'

# Connect to the database
mongo_client = MongoClient(connection_string)

database_name = 'Cardio_Test'
collection_name = 'cardio_collection'

users_collection_name = 'users_collection'

users_collection_schema = {
    "username": str,
    "password": str,
    "first_name": str,
    "last_name": str,
    "email": str,
}


def get_image_from_cloudinary(mongo_client, database_name, collection_name, user_id):
    """
    Retrieves the image URL from Cloudinary based on the given ID from MongoDB.

    Args:
        mongo_client: A MongoClient object connected to the MongoDB database.
        database_name: The name of the MongoDB database containing the collection.
        collection_name: The name of the MongoDB collection containing image data.
        user_id: The ID of the image to retrieve from Cloudinary.

    Returns:
        The Cloudinary URL for the image or None if not found.
    """

    config(cloud_name="dqg3wqmjq", api_key="249284327657225", api_secret="VAPnrcjWZoxdPZlBm9YoiXEKFZU")

    # Connect to the specified database and collection
    db = mongo_client[database_name]
    collection = db[collection_name]

    # Find the document with the matching ID in the collection
    document = collection.find_one({"id": user_id})

    # Check if the document exists and has a path attribute
    if document and "path" in document:
        # Extract the Cloudinary URL from the path attribute
        cloudinary_url = document["path"]

        # Use Cloudinary's URL generator to ensure secure delivery
        url_tuple = utils.cloudinary_url(cloudinary_url)

        # Extract the URL string from the tuple
        url_string = url_tuple[0]

        return url_string
    else:
        return None


@app.route("/image/<int:image_id>", methods=["GET"])
def get_image_url(image_id):
    """
    Endpoint to retrieve the Cloudinary URL for an image based on the image ID.

    Args:
        image_id: The ID of the image.

    Returns:
        JSON response containing the Cloudinary URL or an error message.
    """
    try:
        image_url = get_image_from_cloudinary(mongo_client, database_name, collection_name, image_id)

        if image_url:
            return jsonify({"image_url": image_url})
        else:
            return jsonify({"error": f"Image not found for ID {image_id}"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/userdata/<int:image_id>", methods=["GET"])
def get_user_data(image_id):
    try:
        # Connect to the specified database and collection
        db = mongo_client[database_name]
        collection = db[collection_name]

        # Find the document with the matching ID in the collection
        document = collection.find_one({"id": image_id})

        # Check if the document exists
        if not document:
            return jsonify({"error": f"User not found for ID {id}"}), 404

        # Convert ObjectId to string
        document['_id'] = str(document['_id'])

        return jsonify(document)

    except ValueError as ve:
        return jsonify({"error": f"Invalid user ID format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/user/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        # Check if user ID is provided
        if user_id is None:
            return jsonify({"error": "User ID is required"}), 400

        # Connect to the specified database and collection
        db = mongo_client[database_name]
        collection = db[collection_name]

        # Find the document with the matching ID in the collection
        document = collection.find_one({"id": user_id})

        # Check if the document exists
        if not document:
            return jsonify({"error": f"User not found for ID {user_id}"}), 404

        # Print received JSON data for debugging
        print("Received JSON data:", request.json)

        # Parse height and weight from request data
        new_height = int(request.json.get("height", 0))
        new_weight = float(request.json.get("weight", 0.0))

        # Print parsed height and weight
        print(f"Parsed height: {new_height}, weight: {new_weight}")

        # Update the document with the new height and weight
        collection.update_one({"id": user_id}, {"$set": {"height": new_height, "weight": new_weight}})

        return jsonify({"success": f"User {user_id} updated successfully"})

    except ValueError as ve:
        return jsonify({"error": f"Invalid user ID format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/user", methods=["POST"])
def insert_user():
    try:
        # Connect to the specified database and collection
        db = mongo_client[database_name]
        collection = db[collection_name]

        # Parse data from request JSON
        data = request.json
        new_user = {
            "id": data["id"],
            "age": data["age"],
            "gender": data["gender"],
            "height": data["height"],
            "weight": data["weight"],
            "ap_hi": data["ap_hi"],
            "ap_lo": data["ap_lo"],
            "cholesterol": data["cholesterol"],
            "gluc": data["gluc"],
            "smoke": data["smoke"],
            "alco": data["alco"],
            "active": data["active"],
            "cardio": data["cardio"],
            "url": data["url"],
            "qrcode_filename": data["qrcode_filename"],
        }

        # Insert the new user record
        result = collection.insert_one(new_user)

        # Print the inserted document ID
        print(f"Inserted user with ID: {result.inserted_id}")

        return jsonify({"success": "User inserted successfully", "user_id": str(result.inserted_id)}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/register", methods=["POST"])
def register_user():
    try:
        data = request.json
        hashed_password = hash_password(data["password"])

        new_user = {
            "username": data["username"],
            "password": hashed_password,
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "email": data["email"],
        }

        # Connect to the specified database and collection
        db = mongo_client[database_name]
        collection = db[users_collection_name]

        result = collection.insert_one(new_user)

        return jsonify({"success": "User registered successfully", "user_id": str(result.inserted_id)}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/login", methods=["POST"])
def login_user():
    try:
        db = mongo_client[database_name]
        collection = db[users_collection_name]
        data = request.json
        user = collection.find_one({"username": data["username"]})

        if user and bcrypt.check_password_hash(user["password"], data["password"]):
            session["user_id"] = str(user["_id"])
            return jsonify({"success": "Login successful", "user_id": session["user_id"]}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)

    return decorated_function


@app.route("/logout")
@login_required
def logout_user():
    session.pop("user_id", None)
    return jsonify({"success": "Logout successful"}), 200


@app.route("/edit/<int:user_id>", methods=["GET"])
def edit_user(user_id):
    return redirect(url_for('edit_user_page', user_id=user_id))


@app.route("/edit-page/<int:user_id>", methods=["GET"])
def edit_user_page(user_id):
    return f"Edit Page for User ID: {user_id}"


# Define a route for the root URL
@app.route("/")
def home():
    return "Welcome to the Cardio API!"


if __name__ == "__main__":
    # Run the Flask app
    app.run(host="0.0.0.0", port=5000)
    # app.run(host="127.0.0.1", port=5012)
