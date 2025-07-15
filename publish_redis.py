import redis
import time
import random

r = redis.Redis(host="localhost", port=6379)

stream = "controller"
group = f"group_uuid"
consumer = "subscriber_uuid"

exit_condition = False

try:
    r.xgroup_create(stream, group, id="0", mkstream=True)
except redis.exceptions.ResponseError as e:
    if "BUSYGROUP" not in str(e):
        raise

while not exit_condition:
    entries = r.xreadgroup(
        groupname=group,
        consumername=consumer,
        streams={stream: '>'},
        block=1,   
        count=1
    )

    for _, msgs in entries:
        for msg_id, data in msgs:
            value = data[b'value'].decode()
            print(f"Received controller value: {value}")
            r.xack(stream, group, msg_id)

            if value == "exit":
                exit_condition = True
                r.xadd("temperature", {"value": "exit"})
                r.xtrim(stream, maxlen=0)
                r.xtrim("temperature", maxlen=0)
                break
            elif value == "broadcast":
                r.xadd("temperature", {"value": "broadcast"})
    
    if not exit_condition:
        value = random.randint(0, 100)
        r.xadd("temperature", {"value": value})
        print(f"Published: {value}")

        time.sleep(5)