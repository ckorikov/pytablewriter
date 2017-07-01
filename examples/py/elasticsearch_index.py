#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import datetime
import json

from elasticsearch import Elasticsearch

import pytablewriter as ptw


es = Elasticsearch(hosts="localhost:9200")

writer = ptw.ElasticsearchWriter()
writer.stream = es
writer.index_name = "es writer example"
writer.header_list = [
    "str", "byte", "short", "int", "long", "float", "date", "bool", "ip",
]
writer.value_matrix = [
    [
        "abc", 100, 10000, 2000000000, 200000000000, 0.1,
        datetime.datetime(2017, 1, 2, 3, 4, 5), True, "127.0.0.1",
    ],
    [
        "def", -10, -1000, -200000000, -20000000000, 100.1,
        datetime.datetime(2017, 6, 5, 4, 5, 2), False, "::1",
    ],
]

# delete existing index ---
es.indices.delete(index=writer.index_name, ignore=404)

# create an index and put data ---
writer.write_table()

# display the result ---
es.indices.refresh(index=writer.index_name)

print("----- mappings -----")
response = es.indices.get_mapping(index=writer.index_name, doc_type="table")
print("{}\n".format(json.dumps(response, indent=4)))

print("----- documents -----")
response = es.search(
    index=writer.index_name,
    doc_type="table",
    body={
        "query": {"match_all": {}}
    }
)
for hit in response["hits"]["hits"]:
    print(json.dumps(hit["_source"], indent=4))
