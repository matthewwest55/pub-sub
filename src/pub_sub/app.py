from fastapi import FastAPI
from pub_sub_client import *
import threading
import asyncio
import time

app = FastAPI()

pub_sub_client = PubSubClient()

# This is where we will maintain pointers to all the workers
agg_mds_subscription_pool = dict[str, threading.Thread]()

class SubscriptionListeningThread(threading.Thread):
    def __init__(self, ip_address, hostname, channel_name, service_endpoint):
        super(SubscriptionListeningThread, self).__init__()
        self.ip_address = ip_address
        self.hostname = hostname
        self.channel_name = channel_name
        self.service_endpoint = service_endpoint
        self.stay_alive = True

    def run(self):
        # Might not need this while loop, for the record
        # while self.stay_alive:
        asyncio.run(self.subscribe_to_commons(self.ip_address, self.hostname, self.channel_name))

    async def subscribe_to_commons(self, ip_address:str, hostname:str, channel_name:str):
        # TO-DO: Add a timeout to this so it dies after a while (need to also make joining automatic when publishing)
        # Setup connection to Redis
        # Gonna hard-code one ip address for now, will fix with config later
        # pubsub_client = PubSubClient()
        redis_client = redis.Redis(host=ip_address, port=6379, db=0, password="temporary_password")
        channel = channel_name

        # 2. Make redis spin
        # pubsub_client.subscribe(channel)
        print(f"Subscribed to {channel}. Waiting for messages...")
        last_index = 0
        while self.stay_alive:
            # print("trying to get message now")
            # message = redis_client.xrange(channel, last_index, "+", 1)
            message = redis_client.xread(streams={channel: last_index}, count=1000)
            # print("got message")

            # print(f"message: {message}")
            
            # Check if there are any new entries. If not, wait and check again
            if len(message) == 0:
                time.sleep(1)
                continue

            print("Last: " + str(last_index))

            # This is where we send the data to the provided service_endpoint

            # time_index = message[0][0].decode('utf-8')
            # print(f"Got {time_index} entry")
            # read_data = message[0][1]
            # ms_time_index = time_index.split("-")[0]

            # increment last_index (is this okay? can I assume unique timestamps...)
            # last_index = str(int(ms_time_index) + 1) + "-0"
            last_index = message[0][1][-1][0]

            # just need to save all the data now to a timestoreDB

@app.get("/status")
def status():
    return "Ok"

@app.post("/publish")
def publish(channel_name: str, data):
    return pub_sub_client.publish(channel_name, data)

@app.post("/subscribe")
# service_endpoint is where the data that is colelcted will be returned to
def subscribe(ip_address:str, hostname:str, channel_name:str, service_endpoint:str):
    # TO-DO: Add override option
    # Here we need to spin up a process and then return that that was a success, returning the name of the thread so we can check its status
    # if hostname not in agg_mds_subscription_pool or (hostname in agg_mds_subscription_pool and override):
    if hostname not in agg_mds_subscription_pool:
    # Will this lead to memory leaks if I don't close threads properly?
    # new_thread = threading.Thread(target=asyncio.run, args=(subscribe_to_commons(ip_address, hostname, channel_name),))
        new_thread = SubscriptionListeningThread(ip_address=ip_address, hostname=hostname, channel_name=channel_name, service_endpoint=service_endpoint)
        if hostname in agg_mds_subscription_pool:
            dying_process = agg_mds_subscription_pool[hostname]
            dying_process.stay_alive = False
            del agg_mds_subscription_pool[hostname]
            dying_process.join()
        agg_mds_subscription_pool[hostname] = new_thread
        new_thread.start()
        # need to do error checking here I think
        return "Subscribed"    
    return "Not Subscribed"

@app.get("/subscription_status/{hostname}")
def subscription_status(hostname: str):
    print(len(agg_mds_subscription_pool))
    print(agg_mds_subscription_pool)
    if hostname in agg_mds_subscription_pool:
        if agg_mds_subscription_pool[hostname].is_alive():
            return "Found - Working"
        else:
            return "Found - In Error"
    else:
        return "Not Found"

# @app.get("/test")
# def test():
#     publish("my_channel", "test data")
#     # after this, add something for trying to read this

#     # pub_sub_client.subscribe("my_channel")
#     messages = pub_sub_client.get_messages(1, "my_channel", 0)

#     return messages
