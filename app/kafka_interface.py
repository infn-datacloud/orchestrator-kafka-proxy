# Copyright (c) Istituto Nazionale di Fisica Nucleare (INFN). 2019-2025
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import string
import random
import json
from kafka import KafkaConsumer, KafkaProducer  # type: ignore

bootstrap_servers = None

BOOTSTRAP_MSG_ERR: str = "Bootstrap_servers is not set"
SYSLOG_TS_FORMAT = "%Y-%m-%dT%H:%M:%S%z"  # YYYY-MM-DDTHH:MM:SS+ZZ:ZZ


def set_bootstrap_servers(b_servers):
    global bootstrap_servers
    bootstrap_servers = b_servers


# Write message in kafka topic
def write_msg_to_kafka(data, topic):
    global bootstrap_servers
    if bootstrap_servers is None:
        print(BOOTSTRAP_MSG_ERR)
        return

    producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                             value_serializer=lambda x: json.dumps(x, sort_keys=True).encode('utf-8'))
    if isinstance(data, list):
        for msg in data:
            producer.send(topic, msg)
    else:
        producer.send(topic, data)
    producer.flush()
    producer.close()


def collect_all_msgs_from_topics(*topics):
    global bootstrap_servers
    if bootstrap_servers is None:
        print(BOOTSTRAP_MSG_ERR)
        return

    group_id = ''.join(random.choices(string.ascii_uppercase +
                                      string.ascii_lowercase +
                                      string.digits, k=64))
    group_base = '-'.join(topics)
    consumer = KafkaConsumer(
        *topics,
        bootstrap_servers=bootstrap_servers,
        group_id=f'{group_base}-{group_id}',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        max_partition_fetch_bytes=100_000_000,
        fetch_max_bytes=50_000_000,
        consumer_timeout_ms=10000
    )

    collected_msgs = {topic: list() for topic in topics}
    for message in consumer:
        topic = str(message.topic)
        collected_msgs[topic].append(message)
    return collected_msgs


def collect_all_msgs_from_topic(topic):
    global bootstrap_servers
    if bootstrap_servers is None:
        print(BOOTSTRAP_MSG_ERR)
        return

    group_id = ''.join(random.choices(string.ascii_uppercase +
                                      string.ascii_lowercase +
                                      string.digits, k=64))
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=f'{topic}-{group_id}',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        max_partition_fetch_bytes=100_000_000,
        fetch_max_bytes=50_000_000,
        consumer_timeout_ms=10000
    )

    collected_msgs = list()
    for message in consumer:
        collected_msgs.append(message)
    return collected_msgs


def get_topics_consumer_obj(*topics, deser_format='str'):
    global bootstrap_servers
    if bootstrap_servers is None:
        print(BOOTSTRAP_MSG_ERR)
        return

    def derserializer(deser_format):
        def decode_str_func(x):
            return x.decode('utf-8')

        def decode_json_func(x):
            return json.loads(x.decode('utf-8'))

        if deser_format == 'json':
            return decode_json_func
        elif deser_format == 'str':
            return decode_str_func
        else:
            return decode_str_func

    deser_func = derserializer(deser_format)
    group_base = '-'.join(topics)
    group_id = ''.join(random.choices(string.ascii_uppercase +
                                      string.ascii_lowercase +
                                      string.digits, k=64))
    consumer = KafkaConsumer(
        *topics,
        bootstrap_servers=bootstrap_servers,
        group_id=f'{group_base}-{group_id}',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=deser_func
    )

    return consumer


def get_topic_consumer_obj(topic, deser_format='str'):
    global bootstrap_servers
    if bootstrap_servers is None:
        print(BOOTSTRAP_MSG_ERR)
        return

    def derserializer(deser_format):
        def decode_str_func(x):
            return x.decode('utf-8')

        def decode_json_func(x):
            return json.loads(x.decode('utf-8'))

        if deser_format == 'json':
            return decode_json_func
        elif deser_format == 'str':
            return decode_str_func
        else:
            return decode_str_func

    deser_func = derserializer(deser_format)
    group_id = ''.join(random.choices(string.ascii_uppercase +
                                      string.ascii_lowercase +
                                      string.digits, k=64))
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=f'{topic}-{group_id}',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=deser_func
    )

    return consumer


def get_consumer_obj_Str(*topics):
    global bootstrap_servers
    if bootstrap_servers is None:
        print(BOOTSTRAP_MSG_ERR)
        return

    group_base = '-'.join(topics)
    group_id = ''.join(random.choices(string.ascii_uppercase +
                                      string.ascii_lowercase +
                                      string.digits, k=64))
    consumer = KafkaConsumer(
        *topics,
        bootstrap_servers=bootstrap_servers,
        group_id=f'{group_base}-{group_id}',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda x: x.decode('utf-8')
    )

    return consumer
