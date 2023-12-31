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
from datetime import date
from service import app
from service.models import db, Promotion, init_db
from service.common import status  # HTTP Status Codes
from tests.factories import PromotionFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/api/promotions"
CONTENT_TYPE_JSON = "application/json"


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
        self.app = app.test_client()
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
            response = self.app.post(
                BASE_URL,
                json=test_promotion.serialize(),
                content_type=CONTENT_TYPE_JSON,
            )
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
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(b"Promotion REST API Service", resp.data)

    def test_health(self):
        """It should be healthy"""
        response = self.app.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], "OK")

    ######################################################################
    # CREATE A NEW PROMOTION
    ######################################################################

    def test_create_promotion(self):
        """It should Create a new Promotion"""
        test_promotion = PromotionFactory()
        logging.debug("Test promotion: %s", test_promotion.serialize())

        # POST -- create
        response = self.app.post(BASE_URL, json=test_promotion.serialize())
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
        response = self.app.get(location)
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
        response = self.app.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_promotion_with_wrong_data(self):
        """It should not Create a new Promotion with wrong data"""
        test_promotion = PromotionFactory()
        logging.debug("Test promotion: %s", test_promotion.serialize())

        # POST -- create
        response = self.app.post(
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
        response = self.app.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_promotion_with_missing_name(self):
        """It should not Create a new Promotion with missing name"""
        test_promotion = PromotionFactory()
        test_promotion.name = None
        logging.debug("Test promotion: %s", test_promotion.serialize())
        response = self.app.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_promotion_with_missing_products_type(self):
        """It should not Create a new Promotion with missing products type"""
        test_promotion = PromotionFactory()
        test_promotion.products_type = None
        logging.debug("Test promotion: %s", test_promotion.serialize())
        response = self.app.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_promotion_with_wrong_promotion_code(self):
        """It should not Create a new Promotion with wrong promotion code"""
        test_promotion = PromotionFactory()
        test_promotion.require_code = False
        test_promotion.promotion_code = "6604876475937"
        logging.debug("Test promotion: %s", test_promotion.serialize())
        response = self.app.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_promotion_with_wrong_start_and_end_date(self):
        """It should not Create a new Promotion with wrong start and end date"""
        test_promotion = PromotionFactory()
        test_promotion.start_date = date(2023, 10, 10)
        test_promotion.end_date = date(2023, 9, 10)
        logging.debug("Test promotion: %s", test_promotion.serialize())
        response = self.app.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    ######################################################################
    # LIST ALL PROMOTIONS
    ######################################################################
    def test_list_promotions(self):
        """It should list all promotion"""
        self._create_promotions(5)
        response = self.app.get(f"{BASE_URL}")
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
        response = self.app.get(BASE_URL, query_string=f"name={quote_plus(test_name)}")
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
        response = self.app.get(
            BASE_URL,
            query_string=f"products_type={quote_plus(test_products_type)}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(products_type_promotions))
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion["products_type"], test_products_type)

    ######################################################################
    # READ A NEW PROMOTION
    ######################################################################
    def test_read_promotion(self):
        """It should Get a single promotion"""
        # get the id of a promotion
        test_promotion = self._create_promotions(1)[0]
        response = self.app.get(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_promotion.name)

    def test_read_promotion_not_found(self):
        """It should not Get a promotion thats not found"""
        response = self.app.get(f"{BASE_URL}/0")
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
        response = self.app.delete(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.app.get(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_and_list_promotions(self):
        """It should create three promotion and delete one"""
        test_promotion = self._create_promotions(3)[0]
        # list before deletion
        response_list_before = self.app.get(f"{BASE_URL}")
        self.assertEqual(response_list_before.status_code, status.HTTP_200_OK)
        data = response_list_before.get_json()
        self.assertEqual(len(data), 3)
        # delete
        response = self.app.delete(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # list after deletion
        response_list_after = self.app.get(f"{BASE_URL}")
        self.assertEqual(response_list_after.status_code, status.HTTP_200_OK)
        data = response_list_after.get_json()
        self.assertEqual(len(data), 2)
        # make sure they are deleted
        response = self.app.get(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    # UPDATE EXISTING PROMOTION
    ######################################################################
    def test_update_promotion(self):
        """It should Update an existing Promotion"""
        # Create a promotion to update
        test_promotion = PromotionFactory()
        response = self.app.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Update the promotion
        new_promotion = response.get_json()
        promotion_id = new_promotion["_id"]
        if promotion_id is not None:
            logging.debug(new_promotion)
            new_promotion["promotion_code"] = "UPDATED123"
            response = self.app.put(f"{BASE_URL}/{promotion_id}", json=new_promotion)

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

        response = self.app.put(
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
        # if test_promotion.id is not None:
        # Activate the promotion using PUT request
        response = self.app.put(f"{BASE_URL}/{test_promotion.id}/activate")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Get the promotion and check if it is active
        response = self.app.get(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(data["is_active"])

    def test_activate_promotion_not_found(self):
        """It should return a 404 Not Found when activating a non-existent promotion"""
        non_existent_promotion_id = (
            9999  # Assuming this ID does not exist in the test database
        )
        response = self.app.put(f"/promotions/{non_existent_promotion_id}/activate")
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
            self.app.put(f"{BASE_URL}/{test_promotion.id}/activate")

            # Deactivate the promotion using PUT request
            response = self.app.put(f"{BASE_URL}/{test_promotion.id}/deactivate")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Get the promotion and check if it is inactive
            response = self.app.get(f"{BASE_URL}/{test_promotion.id}")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.get_json()
            self.assertFalse(data["is_active"])

    def test_deactivate_promotion_not_found(self):
        """It should return a 404 Not Found when activating a non-existent promotion"""
        non_existent_promotion_id = (
            9999  # Assuming this ID does not exist in the test database
        )
        response = self.app.put(f"/promotions/{non_existent_promotion_id}/deactivate")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])
