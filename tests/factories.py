# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
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

"""
Test Factory to make fake objects for testing
"""
from datetime import date

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate
from service.models import Promotion


class PromotionFactory(factory.Factory):
    """Creates fake Promotion"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Promotion

    id = factory.Sequence(lambda n: n)
    name = FuzzyChoice(
        choices=[
            "First time Shopper Discount",
            "Limited Time Offers",
            "Buy One, Get One Free",
            "Clearance Sales",
            "Member-Only Discounts",
        ]
    )
    description = FuzzyChoice(
        choices=[
            "Offer a special discount for first-time customers",
            "Create urgency with time limited promotions",
            "Introduce buy-one-get-one promotions",
            "clearance section to clear out excess inventory",
            "Provide exclusive discounts for members",
        ]
    )
    products_type = FuzzyChoice(
        choices=["all_types", "Electronics", "clothing", "Toys", "all_types"]
    )

    require_code = FuzzyChoice(choices=[True, False])

    @factory.lazy_attribute
    def promotion_code(self):
        """
        Generate a promotion code if require_code is True.

        Returns:
            str: The generated promotion code if require_code is True, else None.
        """
        if self.require_code:
            temp = factory.Faker("pystr")
            return f"{temp}"
        return None

    start_date = FuzzyDate(date(2008, 1, 1))

    @factory.lazy_attribute
    def end_date(self):
        """
        Generate an end date based on the start date.

        Returns:
          datetime: An end date generated after the start date.
        """
        date_s = self.start_date
        return FuzzyDate(date_s).fuzz()
