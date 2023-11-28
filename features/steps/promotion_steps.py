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


import os
import requests
import json
from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_404_NOT_FOUND = 404

# Base URL for the RESTful service
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


@given("the following promotions")
def step_impl(context):
    context.base_url = BASE_URL
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
        context.resp = requests.post(context.base_url + "/promotions", json=promotion)
        assert context.resp.status_code == HTTP_201_CREATED


@when('I visit the "Home Page"')
def step_impl(context):
    context.resp = requests.get(context.base_url)
    assert context.resp.status_code == HTTP_200_OK


@then('I should see "{message}"')
def step_impl(context, message):
    assert message in str(context.resp.text)


@then('I should not see "{message}"')
def step_impl(context, message):
    assert message not in str(context.resp.text)
