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
from flask import current_app as app
import app.kafka_interface as ki
import sqlite3
import time
from threading import Event

db_connection = 'file:ranking_database?mode=memory&cache=shared'


def check_database():
    conn = sqlite3.connect(db_connection, timeout=5)
    conn.execute('CREATE TABLE IF NOT EXISTS ranking_data (uuid TEXT, ts INTEGER, rank TEXT);')
    conn.commit()
    conn.close()


# Process kafka queue and populate local cache
def pupulate_ranking_data(topic, logger):
    logger.info("pupulate_ranking_data thread is starting up")
    check_database()
    consumer = ki.get_topic_consumer_obj(topic, deser_format='json')
    conn = None
    while True:
        try:
            for message in consumer:
                uuid = message.value['uuid']
                ts = message.timestamp
                rank = json.dumps(message.value["ranked_providers"])
                conn = sqlite3.connect(db_connection, timeout=5)
                conn.execute("INSERT INTO ranking_data VALUES (?, ?, ?);", [uuid, ts, rank])
                conn.commit()
                conn.close()
                logger.info(f"Loaded {uuid} ranking data.")
            Event.wait(1)
        except BaseException as e:
            logger.error('{!r}; error loading ranking data'.format(e))
        finally:
            if conn:
                conn.close()


# get element from local cache
def get_ranking_data(uuid):
    delay = int(app.config['QUERY_TIMEOUT'])
    app.logger.info(f"Requested ranking for deployment id:{uuid}")
    check_database()
    ranking_data = None
    while delay > 0:
        conn = sqlite3.connect(db_connection, timeout=5)
        cur = conn.cursor()
        cur.execute('SELECT rank FROM ranking_data WHERE uuid=?;', [uuid])
        ranking_data = cur.fetchone()[0]
        conn.close()
        if ranking_data:
            return json.loads(ranking_data)
        time.sleep(1)
        delay = delay - 1
    return ranking_data


# Clean local cache
def clean_ranking_data(lifespan, logger):
    logger.info("clean_ranking_data thread is starting up")
    # initial delay
    Event().wait(15)
    while True:
        check_time = time.time() - float(lifespan) * 86400
        conn = sqlite3.connect(db_connection, timeout=5)
        cur = conn.cursor()
        cur.execute("DELETE FROM ranking_data WHERE ranking_data.ts < ?;", [check_time])
        removed = cur.rowcount
        logger.info(f"Removed {removed} messages from ranking data.")
        conn.commit()
        conn.close()
        Event().wait(86400)
