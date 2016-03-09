from flask import request
from flask_restful import Resource

class RankRoot(Resource):
    """ Return an example of a ranked document search"""
    def get(self):
        return [{"title": "Example 1",
                 "summary": "Find documents that contain the words 'electronic' and 'device'",
                 "links": [{
                            "href": request.base_url + "/electronic+device",
                            "rel": "item",
                            "title": "Top 10 documents that contain 'electronic' and 'device'",
                            "type": "application/json"
                            }]
                 },
                 {"title": "Example 2",
                  "summary": "Find documents that contain 'truck' or 'trucks'",
                  "links": [{
                             "href": request.base_url + "/trucks?field=lemma",
                             "rel": "item",
                             "title": "Top 10 documents that contain variants of 'truck'",
                             "type": "application/json"
                             }]
                 },
                 {"title": "Example 3",
                  "summary": "Find documents that contain words derived from 'category'",
                  "links": [{
                             "href": request.base_url + "/category?field=stem",
                             "rel": "item",
                             "title": "Top 10 documents that contain derivatives of 'category'",
                             "type": "application/json"
                             }]
                  }]
