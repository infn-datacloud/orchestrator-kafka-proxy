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

from flask import (
    abort,
    Blueprint,
    request,
)
from flask import current_app as app
import app.ranking_processor as rp


cpr_bp = Blueprint(
    "cpr_bp", __name__
)


@cpr_bp.route("/")
def root():
    return "orchestrator-kafka-proxy"


@cpr_bp.route("/rank", methods=['POST'])
def get_deployment_rank():
    uuid = str(request.data)
    uuid = "11f0095a-3795-8e38-b314-0242e34b7d6d"
    ranking_data = rp.get_ranking_data(uuid)
    if ranking_data:
        return ranking_data
    abort(404)
