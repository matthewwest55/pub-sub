# This is a wrapper class for changing the pub/sub service easily
from redis_pub_sub import *
import redis
import json
import re

class PubSubClient():
    client:redis.Redis = None
#    sub_client:redis.Redis = None

    def __init__(self):
        # Hate that I'm making this something that is hard-coded, but have to do it
        # self.client = get_redis_client('34.170.74.225', 6379, 0)
        self.client = get_redis_client('REDIS-REPLACE-ME', 6379, 0)

    def publish(self, channel: str, message: str):
        pattern = re.compile("[0-9]*-[0-9]*")
        id_added = redis_publish(self.client, channel, message).decode('ascii')
        if pattern.match(id_added):
            return "Added"
        else:
            return "Error"


    async def batch_publish(self, channel:str, data):
        for metadata in data:
            self.publish(channel, "POST " + str(metadata.guid) + " " + json.dumps(metadata.data))

#    def subscribe(self, channel):
#        self.sub_client = self.client.pubsub()
#        self.sub_client.subscribe(channel)

    def get_messages(self, count, channel_key, index:int):
        #message_count = 0
        #messages = []
        #while message_count < count:
        messages = self.client.xread(count=count, streams={channel_key:index})
        #   if message:
        #       messages.append(message)
        #       message_count += 1

        return messages
