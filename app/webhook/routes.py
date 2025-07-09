from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os
from app.extensions import mongo

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

events_collection = mongo.db.events

@webhook.route('/events', methods=["GET"])
def get_events():
    events = list(events_collection.find({}, {"_id": 0}))
    return jsonify(events)


@webhook.route('/receiver', methods=["POST"])
def receiver():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')
    sender = data.get("sender", {}).get("login", "unknown")
    timestamp = datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")

    record = {}

    if event_type == "push":
        branch = data["ref"].split("/")[-1]
        record = {
            "type": "push",
            "author": sender,
            "to_branch": branch,
            "timestamp": timestamp
        }

    elif event_type == "pull_request":
        pr = data["pull_request"]
        if data["action"] == "opened":
            record = {
                "type": "pull_request",
                "author": sender,
                "from_branch": pr["head"]["ref"],
                "to_branch": pr["base"]["ref"],
                "timestamp": timestamp
            }
        elif data["action"] == "closed" and pr["merged"]:
            record = {
                "type": "merge",
                "author": sender,
                "from_branch": pr["head"]["ref"],
                "to_branch": pr["base"]["ref"],
                "timestamp": timestamp
            }

    if record:
        events_collection.insert_one(record)
        return jsonify({"status": "success", "data": record}), 200

    return jsonify({"status": "ignored"}), 204
