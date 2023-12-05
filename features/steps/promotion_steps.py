######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Promotion Steps

Steps file for promotions.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""

import requests
from behave import given

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_404_NOT_FOUND = 404


@given("the following promotions")
def step_impl(context):
    """Delete all Promotions and load new ones"""

    # List all of the promotions and delete them one by one
    rest_endpoint = f"{context.base_url}/api/promotions"
    context.resp = requests.get(rest_endpoint)
    assert context.resp.status_code == HTTP_200_OK
    for promotion in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{promotion['_id']}")
        assert context.resp.status_code == HTTP_204_NO_CONTENT

    for row in context.table:
        promotion = {
            "name": row["name"],
            "description": row["description"],
            "products_type": row["products_type"],
            "promotion_code": row["promotion_code"],
            "require_code": row["require_code"] == "true",
            "start_date": row["start_date"],
            "end_date": row["end_date"],
            "is_active": row["is_active"] == "true",
        }
        context.resp = requests.post(rest_endpoint, json=promotion)
        assert context.resp.status_code == HTTP_201_CREATED
