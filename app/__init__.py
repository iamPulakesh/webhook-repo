from flask import Flask
from app.extensions import mongo
from app.webhook import webhook  # Import Blueprint from webhook package

# Creating our flask app
def create_app():

    app = Flask(__name__)

    # MongoDB config
    app.config["MONGO_URI"] = "mongodb://localhost:27017/webhook_db"
    mongo.init_app(app)

    with app.app_context():
        mongo.db.events.drop()
    
    # registering all the blueprints
    app.register_blueprint(webhook)
    
    return app