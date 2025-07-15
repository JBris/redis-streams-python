import redis
import uuid

r = redis.Redis(host="localhost", port=6379)
exit_condition = False

stream = "temperature"
group = f"group_{str(uuid.uuid4())}"
consumer = "subscriber_uuid"

try:
    r.xgroup_create(stream, group, id="0", mkstream=True)
except redis.exceptions.ResponseError as e:
    if "BUSYGROUP" not in str(e):
        raise

print("Waiting...")

while not exit_condition:
    entries = r.xreadgroup(
        groupname=group,
        consumername=consumer,
        streams={stream: '>'},
        block=0
    )

    for _, msgs in entries:
        for msg_id, data in msgs:
            value = data[b'value'].decode()
            print(f"Received value: {value}")
            r.xack(stream, group, msg_id)

            if value == "exit":
                exit_condition = True
                break