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

import json
import os
import time
from threading import Thread
from flask import Flask
from logging.config import dictConfig
from werkzeug.middleware.proxy_fix import ProxyFix
import app.kafka_interface as ki
import app.ranking_processor as rp
from app.ranking_service import cpr_bp


def create_app():

    app = Flask(__name__, instance_relative_config=True)
    app.wsgi_app = ProxyFix(app.wsgi_app)

    # read configuration file
    if os.environ.get("TESTING", "").lower() == "true":
        app.config.from_file("../tests/resources/config.json", json.load)
    else:
        app.config.from_file("config.json", json.load)
        app.config.from_prefixed_env()


    app.register_blueprint(cpr_bp, url_prefix=app.config['ROOT_PATH'])

    # Log configuration
    configure_logging(app)

    app.logger.info("orchestrator-kafka-proxy is starting up")

    # Kafka parameteres
    ranking_topic = os.environ.get(app.config['KAFKA_RANKING_TOPIC'],
                                   app.config['KAFKA_RANKING_TOPIC_DEFAULT'])
    bootstrap_servers = os.environ.get(app.config['KAFKA_BOOTSTRAP_SERVERS'],
                                       app.config['KAFKA_BOOTSTRAP_SERVERS_DEFAULT']).split(',')
    messages_lifespan = app.config['MESSAGES_LIFESPAN'] if app.config['MESSAGES_LIFESPAN'] else 5

    # set kafka server parameters
    ki.set_bootstrap_servers(bootstrap_servers)

    app.thread_dict = {
        'pupulate_ranking_data': Thread(target=rp.pupulate_ranking_data, daemon=True,
                                        args=(ranking_topic, app.logger), name='pupulate_ranking_data'),
        'clean_ranking_data': Thread(target=rp.clean_ranking_data, daemon=True,
                                     args=(messages_lifespan, app.logger), name='clean_ranking_data'),
    }

    #start worker threads
    for t in app.thread_dict.values():
        if not t.is_alive():
            t.start()
            time.sleep(1)

    return app

# write test data in topic
# populate_kafka.write_test_data(ranking_topic)

# Import historical messages from kafka topics
# start_time = time()

# collected_msgs = ki.collect_all_msgs_from_topic(ranking_topic)
# for message in collected_msgs:
#    rp.ranking_data[message.value['uuid']] = message
# logger.info(f"Loaded {len(rp.ranking_data)} messages at startup.")


# @app.on_event("startup")
# async def startup_event():
#    # start threads
#    global thread_dict
#    for t in thread_dict.values():
#        t.start()
#        time.sleep(0.1)


def validate_log_level(log_level):
    """
    Validates that the provided log level is a valid choice.

    Parameters:
    - log_level (str): The log level to validate.

    Raises:
    - ValueError: If the log level is not one of ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'].
    """
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level not in valid_log_levels:
        raise ValueError(f"Invalid log level: {log_level}. Valid log levels are {valid_log_levels}")


def configure_logging(app):
    """
    Configures logging for a Flask application based on the provided app configuration.

    This function sets up a logging configuration using the provided log level from the app's configuration.
    It configures a stream handler with a custom formatter for the 'app' logger and the root logger.

    Parameters:
    - app (Flask): The Flask application instance.
    """
    level = app.config.get("LOG_LEVEL")
    validate_log_level(level)

    if level == "DEBUG":
        msg_format = (
            "%(asctime)s - %(levelname)s - %(message)s [%(funcName)s() in %(pathname)s:%(lineno)s]"
        )
    else:
        msg_format = "%(asctime)s - %(levelname)s - %(message)s"

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "stream_handler": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "custom_formatter",
            },
        },
        "formatters": {
            "custom_formatter": {
                "format": msg_format,
            },
        },
        "loggers": {
            "app": {
                "handlers": ["stream_handler"],
                "level": level,
                "propagate": False,  # Do not propagate messages to the root logger
            },
            "root": {
                "handlers": [],
                "level": level,
            },
        },
        "root": {
            "handlers": ["stream_handler"],
            "level": level,
        },
    }
    dictConfig(logging_config)
