from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(filename='sms_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

@app.route('/', methods=['GET', 'POST'])
def root():
    return "App is running", 200

@app.route('/sms', methods=['POST'])
def receive_sms():
    # Get the message and sender from the Twilio request
    print(request.form)  # Debug incoming data
    return "<Response><Message>Message received</Message></Response>", 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)