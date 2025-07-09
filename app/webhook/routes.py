from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from app.extensions import mongo
from app.webhook import webhook
from flask import render_template
import pytz

@webhook.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# get all webhook events from mongoDB
@webhook.route('/events', methods=["GET"])
def get_events():
    events = list(mongo.db.events.find({}, {"_id": 0}))
    return jsonify(events)

#receive gitHub webhook event
@webhook.route('/receiver', methods=["POST"])
def receiver():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')
    sender = data.get("sender", {}).get("login", "unknown")
    utc_now = datetime.now(timezone.utc)
    ist_time = utc_now.astimezone(pytz.timezone("Asia/Kolkata")) #changing from UTC to IST
    timestamp = ist_time.strftime("%d %B %Y - %I:%M %p IST")

    record = {} # this will store the final data saved in mongoDB

    if event_type == "push":
        branch = data["ref"].split("/")[-1]
        request_id = data["after"]
        record = {
            "request_id": request_id,
            "type": "push",
            "author": sender,
            "to_branch": branch,
            "timestamp": timestamp
        }

    elif event_type == "pull_request":
        pr = data["pull_request"]
        request_id = str(pr["id"])
        if data["action"] == "opened":
            record = {
                "request_id": request_id,
                "type": "pull_request",
                "author": sender,
                "from_branch": pr["head"]["ref"],
                "to_branch": pr["base"]["ref"],
                "timestamp": timestamp
            }
        elif data["action"] == "closed" and pr["merged"]:
            record = {
                "request_id": request_id,
                "type": "merge",
                "author": sender,
                "from_branch": pr["head"]["ref"],
                "to_branch": pr["base"]["ref"],
                "timestamp": timestamp
            }
    # if a valid event was recorded insert it into DB
    if record:
        mongo.db.events.insert_one(record)
        return jsonify({"status": "success", "data": record}), 200

    return jsonify({"status": "ignored"}), 204
