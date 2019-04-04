import zmq 
# Setup a connection to the validator
from sawtooth_sdk.messaging.stream import Stream
from sawtooth_sdk.protobuf import events_pb2
from sawtooth_sdk.protobuf import client_event_pb2
from sawtooth_sdk.protobuf.validator_pb2 import Message

# context.add_event(
#     event_type="notary/sale",
#     attributes=[("sale-added", stringdata)])

subscription = events_pb2.EventSubscription(
    event_type="sawtooth/state-delta",
    filters=[
        # Filter to only addresses in the "notary" namespace using a regex
        events_pb2.EventFilter(
            key="address",
            match_string="58504b.*",
            filter_type=events_pb2.EventFilter.REGEX_ANY)
    ])





ctx = zmq.Context()






socket = ctx.socket(zmq.DEALER)
socket.connect(url)

# Construct the request
request = ClientEventsSubscribeRequest(
    subscriptions=[subscription]).SerializeToString()

# Construct the message wrapper
correlation_id = "123"  # This must be unique for all in-process requests
msg = Message(
    correlation_id=correlation_id,
    message_type=CLIENT_EVENTS_SUBSCRIBE_REQUEST,
    content=request)

# Send the request
socket.send_multipart([msg.SerializeToString()])

# Receive the response
resp = socket.recv_multipart()[-1]

# Parse the message wrapper
msg = Message()
msg.ParseFromString(resp)

# Validate the response type
if msg.message_type != CLIENT_EVENTS_SUBSCRIBE_RESPONSE:
    print("Unexpected message type")
    return

# Parse the response
response = ClientEventsSubscribeResponse()
response.ParseFromString(msg.content)

# Validate the response status
if response.status != ClientEventsSubscribeResponse.OK:
  print("Subscription failed: {}".format(response.response_message))
  return

while True:
  resp = socket.recv_multipart()[-1]

  # Parse the message wrapper
  msg = Message()
  msg.ParseFromString(resp)

  # Validate the response type
  if msg.message_type != CLIENT_EVENTS:
      print("Unexpected message type")
      return

  # Parse the response
  events = EventList()
  events.ParseFromString(msg.content)

  for event in events:
    print(event)

if __name__ == '__main__':
    print("hi")
