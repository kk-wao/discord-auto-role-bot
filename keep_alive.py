from flask import Flask, Response
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return Response("Bot is alive", status=200)

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
