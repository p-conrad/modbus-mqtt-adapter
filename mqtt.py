"""
This module contains all the functions for setting up the MQTT client,
particulary the callbacks for the async client.
"""
import logging
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    """Callback when the MQTT server acknowledges our connect request."""
    # pylint: disable=unused-argument
    if rc == 0:
        logging.info("Successfully connected to MQTT broker %s", userdata["target"])
    else:
        logging.error(
            "Connection to MQTT broker %s failed (reason: %s)",
            userdata["target"],
            mqtt.error_string(rc),
        )


def on_connect_fail(client, userdata):
    """Callback when the initial connection to the MQTT server fails."""
    logging.error(
        "Connection to MQTT broker %s failed",
        userdata["target"],
    )
    client.on_connect_fail = None


def on_disconnect(client, userdata, rc):
    """Callback when the connection to the MQTT server is lost."""
    # pylint: disable=unused-argument
    if rc == 0:
        logging.info(
            "Successfully disconnected from MQTT broker %s", userdata["target"]
        )
    else:
        logging.error(
            "Connection to MQTT broker %s lost (reason: %s)",
            userdata["target"],
            mqtt.error_string(rc),
        )


def on_publish(client, userdata, mid):
    """Callback when a message has been successfully published."""
    # pylint: disable=unused-argument
    logging.debug("Message with id %s published successfully", mid)


def create_mqtt_client(args):
    """Creates the MQTT client from all given command line arguments."""
    client = mqtt.Client(f"MQTT-{args.device}", userdata={"target": args.target})
    if args.username:
        client.username_pw_set(args.username, args.password)
    client.on_connect = on_connect
    client.on_connect_fail = on_connect_fail
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    return client
