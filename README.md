# orchestrator-kafka-proxy

The
[Orchestrator-Kafka-Proxy](https://github.com/infn-datacloud/orchestrator-kafka-proxy) is
a standalone REST WEB Service designed to interface the new AI-Ranker to the legacy 
Java orchestrator replacing the Cloud Provider Ranker service

The [INDIGO PaaS Orchestrator](https://github.com/infn-datacloud/orchestrator)
interacts with this service in order to obtain the rank of two or more cloud
services depending on processing performed by AI-Ranker.

The aim of this micro component is to fully decouple the ranking logic
from the Orchestrator's business logic.

The Orchestrator-Kafka-Proxy can be installed on any machine which is
reachable from the Orchestrator via TCP connection (including the
machine running the Orchestrator itself) and also able to reach the 
Kafka server that collect the AI-Ranker results. 

In the INDIGO PaaS Orchestrator configuration the CPR service must be configured as "v2"

########## Cloud Provider Ranker Configuration ##########   
cpr.url=https://my.cloud.infn.it/cpr  
cpr.serviceVersion=v2
  
# API

The provided APIs are:

POST /rank  

# /rank  
Returns the ranking of the services selected for the current deployment as provided from AI-Ranker

The payload the client must send in a POST HTTP request is the Deployment ID.

The Ranking JSON response format is the one returned from the new AI-Ranker service.

Response example:

[  
"ranked-providers",  
0,  
0,  
1743767995696,  
0,  
null,  
{  
"ranked_providers":[  
{  
"bandwidth_in":10.0,  
"bandwidth_out":10.0,  
"classification":-1,  
"exact_flavors":1.0,  
"floating_ips_quota":100.0,  
"floating_ips_requ":1.0,  
"floating_ips_usage":82.0,  
"gpus_requ":0.0,  
"n_instances_quota":500.0,  
"n_instances_requ":2.0,  
"n_instances_usage":115.0,  
"n_volumes_quota":500.0,  
"n_volumes_requ":0.0,  
"n_volumes_usage":43.0,  
"overbooking_cpu":1.0,  
"overbooking_ram":1.0,  
"provider_name":"CLOUD-INFN-CATANIA",  
"ram_gb_quota":8000.0,  
"ram_gb_requ":8.0,  
"ram_gb_usage":654.0,  
"region_name":"INFN-CT",  
"regression":-1,  
"resource_exactness":0.5,  
"storage_gb_quota":10000.0,  
"storage_gb_requ":0.0,
"storage_gb_usage":2566.0,  
"test_failure_perc_1d":0.0,  
"test_failure_perc_30d":0.0,  
"test_failure_perc_7d":0.0,  
"vcpus_quota":1000.0,  
"vcpus_requ":4.0,  
"vcpus_usage":327.0  
}  
],  
"uuid":"11efe247-bea1-933a-8c8c-0242e34b7d6d"  
},  
[  
],  
null,  
-1,  
875,  
-1  
]

This new data format is interpreted correctly in the Orchestrator when the "v2" version of the CPR has been specified.
