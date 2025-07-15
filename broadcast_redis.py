import redis
import random

r = redis.Redis(host="localhost", port=6379)

stream = "controller"
group = f"group_uuid"
consumer = "subscriber_uuid"

try:
    r.xgroup_create(stream, group, id="0", mkstream=True)
except redis.exceptions.ResponseError as e:
    if "BUSYGROUP" not in str(e):
        raise

r.xadd(stream, {"value": "broadcast"})
