from flask import Flask, request, jsonify

from metrics.general import PositionChanges, Live, Events, WorldC
from utils.zapi import ZApiService
import fastf1
import os

from dotenv import load_dotenv

load_dotenv()

test_number = os.getenv("ZAPI_PREMIUM_TEST_NUMBER")

app = Flask(__name__)

@app.route("/f1data", methods=["POST"])
def f1data():
    webhook_data = request.json

    if not webhook_data:
        return jsonify({"status": "no data"}), 400
    
    from_phone = webhook_data.get("phone")
    message = webhook_data.get("text", {}).get("message")

    match message:
        case "/top5":
            send_top5_data(from_phone)
        
        case "/corridas":
            send_remaining_events(from_phone)
        
        case "/winmax":
            send_if_max_can_win(from_phone)
        
        case _:
            return jsonify({"status": "no data"}), 400
    
    return jsonify({"status": "success"}), 200


def send_top5_data(phone_number):
    live_data = Live.top_5_live()
    if live_data:
        ZApiService.send_message(message_group=phone_number, message=live_data)
    pass


def send_remaining_events(phone_number):
    next_events = Events.get_remaining_events()
    if next_events:
        ZApiService.send_message(message_group=phone_number, message=next_events)
    pass


def send_if_max_can_win(phone_number):
    max_chances = WorldC.calculate_if_max_can_win()
    if max_chances:
        ZApiService.send_message(message_group=phone_number, message=max_chances)
    pass


if __name__ == "__main__":
    app.run(port=5000, debug=True)
