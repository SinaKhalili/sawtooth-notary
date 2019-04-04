#! /usr/bin/env python3

'''Sample Sawtooth event client

   To run, start the validator then type the following on the command line:
       ./events_client.py

   For more information, see
   https://sawtooth.hyperledger.org/docs/core/releases/latest/app_developers_guide/event_subscriptions.html
'''

import sys
import traceback
import zmq
from sawtooth_sdk.messaging.stream import Stream
from sawtooth_sdk.protobuf import events_pb2
from sawtooth_sdk.protobuf import client_event_pb2
from sawtooth_sdk.protobuf.validator_pb2 import Message

# hard-coded for simplicity (otherwise get the URL from the args in main):
# For localhost access:
#DEFAULT_VALIDATOR_URL = 'tcp://localhost:4004'
# For Docker access:
DEFAULT_VALIDATOR_URL = 'tcp://validator:4004'
# Calculated from the 1st 6 characters of SHA-512("notary"):
NOTARY_TP_ADDRESS_PREFIX = '58504b'


def listen_to_events(delta_filters=None):
    '''Listen to notary state-delta events.'''

    # Subscribe to events
    block_commit_subscription = events_pb2.EventSubscription(
        event_type="sawtooth/block-commit")
    state_delta_subscription = events_pb2.EventSubscription(
        event_type="sawtooth/state-delta", filters=delta_filters)
    sale_subscription = events_pb2.EventSubscription(
        event_type="notary/sale")
    request = client_event_pb2.ClientEventsSubscribeRequest(
        subscriptions=[block_commit_subscription, state_delta_subscription, 
        sale_subscription])

    # Send the subscription request
    stream = Stream(DEFAULT_VALIDATOR_URL)
    msg = stream.send(message_type=Message.CLIENT_EVENTS_SUBSCRIBE_REQUEST,
                      content=request.SerializeToString()).result()
    assert msg.message_type == Message.CLIENT_EVENTS_SUBSCRIBE_RESPONSE

    # Parse the subscription response
    response = client_event_pb2.ClientEventsSubscribeResponse()
    response.ParseFromString(msg.content)
    assert response.status == \
           client_event_pb2.ClientEventsSubscribeResponse.OK

    # Listen for events in an infinite loop
    print("Listening to events.")
    while True:
        msg = stream.receive().result()
        assert msg.message_type == Message.CLIENT_EVENTS

        # Parse the response
        event_list = events_pb2.EventList()
        event_list.ParseFromString(msg.content)
        print("Received the following events: ----------")
        for event in event_list.events:
            print(event)

    # Unsubscribe from events
    request = client_event_pb2.ClientEventsUnsubscribeRequest()
    msg = stream.send(Message.CLIENT_EVENTS_UNSUBSCRIBE_REQUEST,
                      request.SerializeToString()).result()
    assert msg.message_type == Message.CLIENT_EVENTS_UNSUBSCRIBE_RESPONSE

    # Parse the unsubscribe response
    response = client_event_pb2.ClientEventsUnsubscribeResponse()
    response.ParseFromString(msg.content)
    assert response.status == \
           client_event_pb2.ClientEventsUnsubscribeResponse.OK


def main():
    '''Entry point function for the client CLI.'''

    subscription = EventSubscription(
        event_type="sawtooth/state-delta",
        filters=[
            EventFilter(
                key="address",
                match_string=
                NOTARY_TP_ADDRESS_PREFIX + ".*",
                filter_type=EventFilter.REGEX_ANY
            )
        ]
    )


#   subscription = EventSubscription(
#     event_type="sawtooth/state-delta",
#     filters=[
#         # Filter to only addresses in the "xo" namespace using a regex
#         EventFilter(
#             key="address",
#             match_string="5b7349.*",
#             filter_type=EventFilter.REGEX_ANY)
#     ])
    filters = [events_pb2.EventFilter(key="address",
                                      match_string=
                                      NOTARY_TP_ADDRESS_PREFIX + ".*",
                                      filter_type=events_pb2.
                                      EventFilter.REGEX_ANY)]

    try:
        # To listen to all events, pass delta_filters=None :
        #listen_to_events(delta_filters=None)
        listen_to_events(delta_filters=filters)
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
