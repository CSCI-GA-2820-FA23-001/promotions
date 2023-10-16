"""
TestPromotion API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from datetime import date
from service import app
from service.models import db, Promotion, init_db
from service.common import status  # HTTP Status Codes
from tests.factories import PromotionFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/promotions"


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
                "Could not create test pet",
            )
            new_promotion = response.get_json()
            test_promotion.id = new_promotion["id"]
            promotions.append(test_promotion)
        return promotions

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], "Promotion REST API Service")

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
    # READ A NEW PROMOTION
    ######################################################################
    def test_read_promotion(self):
        """It should Get a single promotion"""
        # get the id of a promotion
        test_promotion = self._create_promotions(1)[0]
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
    def test_delete_promotion_by_id(self):
        """It should delete a single promotion by its id"""
        test_promotion = self._create_promotions(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_promotion_by_name(self):
        """It should delete a single promotion by its name"""
        test_promotion = self._create_promotions(1)[0]
        response = self.client.delete(f"{BASE_URL}/name/{test_promotion.name}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
