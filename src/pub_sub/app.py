from fastapi import FastAPI
from pub_sub_client import *

app = FastAPI()

pub_sub_client = PubSubClient()

@app.get("/status")
def status():
    return "Ok"

@app.post("/publish")
def publish(channel_name: str, data):
    return pub_sub_client.publish(channel_name, data)

@app.post("/subscribe")
def subscribe(channel_name: str):
    return "To be implemented"

@app.get("/channel_status/{channel_name}")
def channel_status(channel_name: str):
    return "To be implemented"

@app.get("/test")
def test():
    publish("my_channel", "test data")
    # after this, add something for trying to read this

    # pub_sub_client.subscribe("my_channel")
    messages = pub_sub_client.get_messages(1, "my_channel", 0)

    return messages
