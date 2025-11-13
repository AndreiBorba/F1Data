from flask import Flask, request, jsonify

from metrics.general import PositionChanges, Live, Events, WorldC
from utils.zapi import ZApiService
import os, logging

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

test_number = os.getenv("ZAPI_TEST_NUMBER")

app = Flask(__name__)

@app.route("/f1data", methods=["POST"])
def f1data():
    webhook_data = request.json

    if not webhook_data:
        logger.warning("No data received in webhook")
        return jsonify({"status": "no data"}), 400
    
    from_phone = webhook_data.get("phone")
    message = webhook_data.get("text", {}).get("message")
    
    logger.info(f"received message from {from_phone}")

    match message:
        case "/top5":
            logger.info("processing command: /top5")
            send_top5_data(from_phone)
        
        case "/corridas":
            logger.info("processing command: /corridas")
            send_remaining_events(from_phone)
        
        case "/winmax":
            logger.info("processing command: /winmax")
            send_if_verstappen_can_win(from_phone)
        
        case _:
            return jsonify({"status": "command not found"}), 400
    
    return jsonify({"status": "success"}), 200


def send_top5_data(phone_number):
    ZApiService.send_message(message_group=phone_number, message=Live.top_5_live())


def send_remaining_events(phone_number):
    ZApiService.send_message(message_group=phone_number, message=Events.get_remaining_events())


def send_if_verstappen_can_win(phone_number):
    ZApiService.send_message(message_group=phone_number, message=WorldC.driver_chances_of_winning(driver_code="VER"))


if __name__ == "__main__":
    app.run(port=5000, debug=True)
