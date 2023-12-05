"""
TestPromotion API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from urllib.parse import quote_plus
from datetime import datetime
from datetime import date
from service import app
from service.models import db, Promotion, init_db
from service.common import status  # HTTP Status Codes
from tests.factories import PromotionFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/api/promotions"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestPromotionServer(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        self.client = app.test_client()
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    # helper method to create promotion
    def _create_promotions(self, count):
        """Factory method to create promotions in bulk"""
        promotions = []
        for _ in range(count):
            test_promotion = PromotionFactory()
            response = self.client.post(BASE_URL, json=test_promotion.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test promotion",
            )
            new_promotion = response.get_json()
            test_promotion.id = new_promotion["_id"]
            promotions.append(test_promotion)
        return promotions

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(b"Promotion REST API Service", resp.data)

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["message"], "OK")

    ######################################################################
    # CREATE A NEW PROMOTION
    ######################################################################

    def test_create_promotion(self):
        """It should Create a new Promotion"""
        test_promotion = PromotionFactory()
        logging.debug("Test promotion: %s", test_promotion.serialize())

        # POST -- create
        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_promotion = response.get_json()
        self.assertEqual(new_promotion["name"], test_promotion.name)
        self.assertEqual(new_promotion["description"], test_promotion.description)
        self.assertEqual(new_promotion["products_type"], test_promotion.products_type)
        self.assertEqual(new_promotion["promotion_code"], test_promotion.promotion_code)
        self.assertEqual(new_promotion["require_code"], test_promotion.require_code)
        self.assertEqual(
            date.fromisoformat(new_promotion["start_date"]), test_promotion.start_date
        )
        self.assertEqual(
            date.fromisoformat(new_promotion["end_date"]), test_promotion.end_date
        )

        # Check that the location header was correct -- GET URL
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_promotion = response.get_json()
        self.assertEqual(new_promotion["name"], test_promotion.name)
        self.assertEqual(new_promotion["description"], test_promotion.description)
        self.assertEqual(new_promotion["products_type"], test_promotion.products_type)
        self.assertEqual(new_promotion["promotion_code"], test_promotion.promotion_code)
        self.assertEqual(new_promotion["require_code"], test_promotion.require_code)
        self.assertEqual(
            date.fromisoformat(new_promotion["start_date"]), test_promotion.start_date
        )
        self.assertEqual(
            date.fromisoformat(new_promotion["end_date"]), test_promotion.end_date
        )

    def test_create_promotion_with_missing_data(self):
        """It should not Create a new Promotion with missing data"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_promotion_with_wrong_data(self):
        """It should not Create a new Promotion with wrong data"""
        test_promotion = PromotionFactory()
        logging.debug("Test promotion: %s", test_promotion.serialize())

        # POST -- create
        response = self.client.post(
            BASE_URL,
            data={
                "name": test_promotion.name,
                "description": test_promotion.description,
                "products_type": test_promotion.products_type,
                "promotion_code": test_promotion.promotion_code,
                "require_code": test_promotion.require_code,
                "start_date": test_promotion.start_date,
                "end_date": test_promotion.end_date,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_promotion_no_content_type(self):
        """It should not Create a Promotion with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_promotion_with_missing_name(self):
        """It should not Create a new Promotion with missing name"""
        test_promotion = PromotionFactory()
        test_promotion.name = None
        logging.debug("Test promotion: %s", test_promotion.serialize())
        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_promotion_with_missing_products_type(self):
        """It should not Create a new Promotion with missing products type"""
        test_promotion = PromotionFactory()
        test_promotion.products_type = None
        logging.debug("Test promotion: %s", test_promotion.serialize())
        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_promotion_with_wrong_promotion_code(self):
        """It should not Create a new Promotion with wrong promotion code"""
        test_promotion = PromotionFactory()
        test_promotion.require_code = False
        test_promotion.promotion_code = "6604876475937"
        logging.debug("Test promotion: %s", test_promotion.serialize())
        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_promotion_with_wrong_start_and_end_date(self):
        """It should not Create a new Promotion with wrong start and end date"""
        test_promotion = PromotionFactory()
        test_promotion.start_date = date(2023, 10, 10)
        test_promotion.end_date = date(2023, 9, 10)
        logging.debug("Test promotion: %s", test_promotion.serialize())
        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    ######################################################################
    # LIST ALL PROMOTIONS
    ######################################################################
    def test_list_promotions(self):
        """It should list all promotion"""
        self._create_promotions(5)
        response = self.client.get(f"{BASE_URL}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_list_promotions_by_name(self):
        """It should Filter promotions by name"""
        promotions = self._create_promotions(10)
        test_name = promotions[0].name
        name_promotions = [
            promotion for promotion in promotions if promotion.name == test_name
        ]
        response = self.client.get(
            BASE_URL, query_string=f"name={quote_plus(test_name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(name_promotions))
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion["name"], test_name)

    def test_list_promotions_by_products_type(self):
        """It should Filter promotions by products type"""
        promotions = self._create_promotions(10)
        test_products_type = promotions[0].products_type
        products_type_promotions = [
            promotion
            for promotion in promotions
            if promotion.products_type == test_products_type
        ]
        response = self.client.get(
            BASE_URL,
            query_string=f"products_type={quote_plus(test_products_type)}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(products_type_promotions))
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion["products_type"], test_products_type)

    # def test_list_promotions_by_date(self):
    #     """It should filter promotions by date"""
    #     promotions = self._create_promotions(10)
    #     test_date = promotions[0].start_date
    #     date_promotions = [
    #         promotion
    #         for promotion in promotions
    #         if promotion.start_date <= test_date and promotion.end_date >= test_date
    #     ]

    #     response = self.client.get(
    #         BASE_URL,
    #         query_string=f"start_date={quote_plus(test_date)}",
    #     )

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     data = response.get_json()
    #     self.assertEqual(len(data), len(date_promotions))

    # # check the data just to be sure
    # for promotion in data:
    #     self.assertGreaterEqual(promotion["start_date"], test_date)

    # def test_list_promotions_by_require_code(self):
    #     """It should Filter promotions by require_code"""
    #     promotions = self._create_promotions(10)
    #     test_require_code = promotions[0].require_code
    #     require_code_promotions = [
    #         promotion
    #         for promotion in promotions
    #         if promotion.require_code == test_require_code
    #     ]
    #     test_require_code_str = str(test_require_code).lower()
    #     response = self.client.get(
    #         BASE_URL, query_string=f"require_code={quote_plus(test_require_code_str)}"
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     data = response.get_json()
    #     self.assertEqual(len(data), len(require_code_promotions))
    #     # check the data just to be sure
    #     for promotion in data:
    #         self.assertEqual(promotion["require_code"], test_require_code)

    # def test_list_promotions_by_valid_start_date(self):
    #     """It should filter promotions by valid start date"""
    #     promotions = self._create_promotions(20)
    #     start_date = "2023-01-01"

    #     test_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

    #     start_date_filter_promotions = [
    #         promotion
    #         for promotion in promotions
    #         if promotion.start_date >= test_start_date
    #     ]

    #     response = self.client.get(
    #         "/promotions",
    #         query_string=f"start_date={quote_plus(start_date)}",
    #     )

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     data = response.get_json()
    #     self.assertEqual(len(data), len(start_date_filter_promotions))

    #     # check the data just to be sure
    #     for promotion in data:
    #         self.assertGreaterEqual(promotion["start_date"], start_date)

    # def test_list_promotions_by_invalid_start_date(self):
    #     """It should filter promotions by invalid start date"""

    #     self._create_promotions(20)
    #     start_date = "invalid_start_date_format"

    #     response = self.client.get(
    #         "/promotions",
    #         query_string=f"start_date={quote_plus(start_date)}",
    #     )

    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    #     # Check if the response contains an appropriate error message
    #     error_message = response.get_json()["message"]
    #     self.assertIn("Invalid start_date format", error_message)

    # def test_list_promotions_by_valid_end_date(self):
    #     """It should filter promotions by valid end date"""
    #     promotions = self._create_promotions(20)
    #     end_date = "2024-01-01"

    #     test_end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    # end_date_filter_promotions = [
    #     promotion for promotion in promotions if promotion.end_date <= test_end_date
    # ]

    # response = self.client.get(
    #     "/promotions",
    #     query_string=f"end_date={quote_plus(end_date)}",
    # )

    # self.assertEqual(response.status_code, status.HTTP_200_OK)
    # data = response.get_json()
    # self.assertEqual(len(data), len(end_date_filter_promotions))

    # # check the data just to be sure
    # for promotion in data:
    #     self.assertLessEqual(promotion["end_date"], end_date)

    # def test_list_promotions_by_invalid_end_date(self):
    #     """It should filter promotions by invalid end date"""

    #     self._create_promotions(20)
    #     end_date = "invalid_end_date_format"

    #     response = self.client.get(
    #         "/promotions",
    #         query_string=f"end_date={quote_plus(end_date)}",
    #     )

    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    #     # Check if the response contains an appropriate error message
    #     error_message = response.get_json()["message"]
    # self.assertIn("Invalid end_date format", error_message)

    # def test_list_promotions_by_discounted_products_list(self):
    #     """It should Filter promotions by discounted_products_list"""

    #     promotions = self._create_promotions(10)
    #     test_discounted_products_list = [promotions[0].id, promotions[1].id]

    #     product_ids_query = ",".join(map(str, test_discounted_products_list))

    #     response = self.client.get(
    #         BASE_URL,
    #         query_string=f"discounted_products={quote_plus(product_ids_query)}",
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     data = response.get_json()

    #     self.assertEqual(len(data), len(test_discounted_products_list))

    #     returned_promotion_ids = [promo["id"] for promo in data]

    #     # Check if the IDs in the response match the IDs in the test list
    #     for promo_id in test_discounted_products_list:
    #         self.assertIn(promo_id, returned_promotion_ids)

    ######################################################################
    # READ A NEW PROMOTION
    ######################################################################
    def test_read_promotion(self):
        """It should Get a single promotion"""
        # get the id of a promotion
        test_promotion = self._create_promotions(1)[0]
        if test_promotion.id is not None:
            response = self.client.get(f"{BASE_URL}/{test_promotion.id}")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.get_json()
            self.assertEqual(data["name"], test_promotion.name)

    def test_read_promotion_not_found(self):
        """It should not Get a promotion thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn(
            "was not found", data["message"]
        )  # message contains a message related to an error or status information from the server.

    ######################################################################
    # DELETE A PROMOTION
    ######################################################################
    def test_delete_promotion(self):
        """It should delete a single promotion by its id"""
        test_promotion = self._create_promotions(1)[0]
        if test_promotion.id is not None:
            response = self.client.delete(f"{BASE_URL}/{test_promotion.id}")
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.assertEqual(len(response.data), 0)
            # make sure they are deleted
            response = self.client.get(f"{BASE_URL}/{test_promotion.id}")
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_and_list_promotions(self):
        """It should create three promotion and delete one"""
        test_promotion = self._create_promotions(3)[0]
        if test_promotion.id is not None:
            # list before deletion
            response_list_before = self.client.get(f"{BASE_URL}")
            self.assertEqual(response_list_before.status_code, status.HTTP_200_OK)
            data = response_list_before.get_json()
            self.assertEqual(len(data), 3)
            # delete
            response = self.client.delete(f"{BASE_URL}/{test_promotion.id}")
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.assertEqual(len(response.data), 0)
            # list after deletion
            response_list_after = self.client.get(f"{BASE_URL}")
            self.assertEqual(response_list_after.status_code, status.HTTP_200_OK)
            data = response_list_after.get_json()
            self.assertEqual(len(data), 2)
            # make sure they are deleted
            response = self.client.get(f"{BASE_URL}/{test_promotion.id}")
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    # UPDATE EXISTING PROMOTION
    ######################################################################
    def test_update_promotion(self):
        """It should Update an existing Promotion"""
        # Create a promotion to update
        test_promotion = PromotionFactory()
        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Update the promotion
        new_promotion = response.get_json()
        promotion_id = new_promotion["_id"]
        if promotion_id is not None:
            logging.debug(new_promotion)
            new_promotion["promotion_code"] = "UPDATED123"
            response = self.client.put(f"{BASE_URL}/{promotion_id}", json=new_promotion)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            updated_promotion = response.get_json()
            self.assertEqual(updated_promotion["promotion_code"], "UPDATED123")

    def test_update_nonexistent_promotion(self):
        """It should return a 404 Not Found when updating a non-existent promotion"""
        # Attempt to update a promotion with a non-existent ID
        non_existent_promotion_id = 9999  # Assuming this ID does not exist

        new_promotion_data = {
            "name": "Updated Promotion",
            "description": "Updated description",
            "products_type": "Updated Type",
            "promotion_code": "UPDATED123",
            "require_code": True,
            "start_date": "2023-10-01",
            "end_date": "2023-10-31",
        }

        response = self.client.put(
            f"{BASE_URL}/{non_existent_promotion_id}", json=new_promotion_data
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Check if the response contains an appropriate error message
        error_message = response.get_json()["message"]
        self.assertIn("was not found", error_message)

    ######################################################################
    # ACTIVE A PROMOTION
    ######################################################################
    def test_activate_promotion(self):
        """It should Activate an existing Promotion"""
        # Create a promotion to activate
        test_promotion = self._create_promotions(1)[0]
        if test_promotion.id is not None:
            # Activate the promotion using PUT request
            response = self.client.put(f"{BASE_URL}/{test_promotion.id}/activate")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Get the promotion and check if it is active
            response = self.client.get(f"{BASE_URL}/{test_promotion.id}")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.get_json()
            self.assertTrue(data["is_active"])

    def test_activate_promotion_not_found(self):
        """It should return a 404 Not Found when activating a non-existent promotion"""
        non_existent_promotion_id = (
            9999  # Assuming this ID does not exist in the test database
        )
        response = self.client.put(f"/promotions/{non_existent_promotion_id}/activate")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    ######################################################################
    # DEACTIVE A PROMOTION
    ######################################################################
    def test_deactivate_promotion(self):
        """It should Deactivate an existing Promotion"""
        # Create and activate a promotion
        test_promotion = self._create_promotions(1)[0]
        if test_promotion.id is not None:
            self.client.put(f"{BASE_URL}/{test_promotion.id}/activate")

            # Deactivate the promotion using PUT request
            response = self.client.put(f"{BASE_URL}/{test_promotion.id}/deactivate")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Get the promotion and check if it is inactive
            response = self.client.get(f"{BASE_URL}/{test_promotion.id}")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.get_json()
            self.assertFalse(data["is_active"])

        # promotions = self._create_promotions(5)
        # promotion_count = self._create_promotions()
        # test_promotion = promotions[0]
        # resp = self.app.delete(f"{BASE_URL}/{test_promotion.id}")
        # self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        # self.assertEqual(len(resp.data), 0)
        # # make sure they are deleted
        # resp = self.app.get(f"{BASE_URL}/{test_promotion.id}")
        # self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        # new_count = self._create_promotions()
        # self.assertEqual(new_count, promotion_count - 1)

    def test_deactivate_promotion_not_found(self):
        """It should return a 404 Not Found when activating a non-existent promotion"""
        non_existent_promotion_id = (
            9999  # Assuming this ID does not exist in the test database
        )
        response = self.client.put(
            f"/promotions/{non_existent_promotion_id}/deactivate"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])
