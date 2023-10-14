"""
Test cases for YourResourceModel Model

"""
import os
import logging
import unittest
from datetime import date
from service.models import Promotion, DataValidationError, db
from service import app
from tests.factories import PromotionFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  P R O M O T I O N   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestPromotionModel(unittest.TestCase):
    """Test Cases for Promotion Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Promotion.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_Promotion(self):
        """It should Create a Promotion and assert that it exists"""
        promotion = Promotion(
            name="First time Shopper Discount",
            description="Offer a special discount for first-time customers",
            products_type="all_types",
            promotion_code="6604876475937",
            require_code=True,
            start_date=date(2023, 9, 10),
            end_date=date(2023, 10, 10),
        )

        self.assertEqual(
            str(promotion), "<Promotion First time Shopper Discount id=[None]>"
        )
        self.assertTrue(promotion is not None)
        self.assertEqual(promotion.id, None)
        self.assertEqual(promotion.name, "First time Shopper Discount")
        self.assertEqual(
            promotion.description, "Offer a special discount for first-time customers"
        )
        self.assertEqual(promotion.products_type, "all_types")
        self.assertEqual(promotion.promotion_code, "6604876475937")
        self.assertEqual(promotion.require_code, True)
        self.assertEqual(promotion.start_date, date(2023, 9, 10))
        self.assertEqual(promotion.end_date, date(2023, 10, 10))

    def test_add_a_promotion(self):
        """It should Create a promotion and add it to the database"""
        promotions = Promotion.all()
        self.assertEqual(promotions, [])
        promotion = Promotion(
            name="First time Shopper Discount",
            description="Offer a special discount for first-time customers",
            products_type="all_types",
            promotion_code="6604876475937",
            require_code=True,
            start_date=date(2023, 9, 10),
            end_date=date(2023, 10, 10),
        )
        self.assertTrue(promotion is not None)
        self.assertEqual(promotion.id, None)
        promotion.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(promotion.id)
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 1)

    def test_read_a_promotion(self):
        """It should Read a promotion"""
        promotion = PromotionFactory()
        logging.debug(promotion)
        promotion.id = None
        promotion.create()
        logging.debug(promotion)
        self.assertIsNotNone(promotion.id)

        # Fetch it back
        found_promotion = promotion.find(promotion.id)
        self.assertEqual(found_promotion.id, promotion.id)
        self.assertEqual(found_promotion.name, promotion.name)
        self.assertEqual(found_promotion.description, promotion.description)
        self.assertEqual(found_promotion.products_type, promotion.products_type)
        self.assertEqual(found_promotion.promotion_code, promotion.promotion_code)
        self.assertEqual(found_promotion.require_code, promotion.require_code)
        self.assertEqual(found_promotion.start_date, promotion.start_date)
        self.assertEqual(found_promotion.end_date, promotion.end_date)

    def test_update_a_promotion(self):
        """It should Update a promotion"""
        promotion = PromotionFactory()
        logging.debug(promotion)
        promotion.id = None
        promotion.create()
        logging.debug(promotion)
        self.assertIsNotNone(promotion.id)
        original_id = promotion.id
        # Change it an save it
        promotion.name = "Member-Only Discounts"
        promotion.update()
        self.assertEqual(promotion.id, original_id)
        self.assertEqual(promotion.name, "Member-Only Discounts")
        # Fetch it back
        found_promotion = promotion.find(original_id)  # the id hasn't changed
        self.assertEqual(found_promotion.name, promotion.name)

    def test_update_no_id(self):
        """It should not Update a promotion with no id"""
        promotion = PromotionFactory()
        logging.debug(promotion)
        promotion.id = None
        self.assertRaises(DataValidationError, promotion.update)

    def test_delete_a_promotion(self):
        """It should Delete a promotion"""
        promotion = PromotionFactory()
        promotion.create()
        self.assertIsNotNone(promotion.id)
        self.assertEqual(len(promotion.all()), 1)
        promotion.delete()
        self.assertEqual(len(promotion.all()), 0)

    def test_list_all_promotion(self):
        """It should List all promotion in the database"""
        promotions = Promotion.all()
        self.assertEqual(promotions, [])

        # Create 5 promotions
        for _ in range(5):
            promotion = PromotionFactory()
            promotion.create()

        # See if we get back 5 promotions
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 5)

    def test_serialize_a_promotion(self):
        """It should serialize a promotion"""

        promotion = PromotionFactory()
        data = promotion.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], promotion.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], promotion.name)
        self.assertIn("description", data)
        self.assertEqual(data["description"], promotion.description)
        self.assertIn("products_type", data)
        self.assertEqual(data["products_type"], promotion.products_type)
        self.assertIn("promotion_code", data)
        self.assertEqual(data["promotion_code"], promotion.promotion_code)
        self.assertIn("require_code", data)
        self.assertEqual(data["require_code"], promotion.require_code)
        self.assertIn("start_date", data)
        self.assertEqual(date.fromisoformat(data["start_date"]), promotion.start_date)
        self.assertIn("end_date", data)
        self.assertEqual(date.fromisoformat(data["end_date"]), promotion.end_date)

    def test_deserialize_a_promotion(self):
        """It should de-serialize a promotion"""
        data = PromotionFactory().serialize()
        promotion = Promotion()
        promotion.deserialize(data)

        self.assertNotEqual(promotion, None)
        self.assertEqual(promotion.id, None)
        self.assertEqual(promotion.name, data["name"])
        self.assertEqual(promotion.description, data["description"])
        self.assertEqual(promotion.products_type, data["products_type"])
        self.assertEqual(promotion.promotion_code, data["promotion_code"])
        self.assertEqual(promotion.require_code, data["require_code"])
        self.assertEqual(promotion.start_date, date.fromisoformat(data["start_date"]))
        self.assertEqual(promotion.end_date, date.fromisoformat(data["end_date"]))

    def test_deserialize_missing_data(self):
        """It should not deserialize a promotion with missing data"""
        data = {"id": 1, "require_code": False}
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, data)

    def test_deserialize_bad_require_code(self):
        """It should not deserialize a bad require_code attribute"""
        data = PromotionFactory().serialize()
        data["require_code"] = "true"
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, data)

    def test_find_promotion(self):
        """It should Find a promotion by id"""
        promotions = PromotionFactory.create_batch(5)
        for promotion in promotions:
            promotion.create()
        logging.debug(promotions)

        # make sure they got saved
        self.assertEqual(len(Promotion.all()), 5)

        # find the 2nd pet in the list
        promotion = Promotion.find(promotions[1].id)
        self.assertIsNot(promotion, None)
        self.assertEqual(promotion.id, promotions[1].id)
        self.assertEqual(promotion.name, promotions[1].name)
        self.assertEqual(promotion.description, promotions[1].description)
        self.assertEqual(promotion.products_type, promotions[1].products_type)
        self.assertEqual(promotion.promotion_code, promotions[1].promotion_code)
        self.assertEqual(promotion.require_code, promotions[1].require_code)
        self.assertEqual(promotion.start_date, promotions[1].start_date)
        self.assertEqual(promotion.end_date, promotions[1].end_date)

    def test_find_by_name(self):
        """It should Find a promotion by Name"""
        promotions = PromotionFactory.create_batch(5)
        for promotion in promotions:
            promotion.create()
        logging.debug(promotions)

        name = promotions[1].name
        count = len([promotion for promotion in promotions if promotion.name == name])

        found = Promotion.find_by_name(name)
        self.assertEqual(found.count(), count)
        for promotion in found:
            self.assertEqual(promotion.name, name)
