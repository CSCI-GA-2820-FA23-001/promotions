"""
Models for Promotion

All of the models are stored in this module
"""
import logging

# from enum import Enum
from datetime import date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_


logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


# Function to initialize the database
def init_db(app):
    """Initializes the SQLAlchemy app"""
    Promotion.init_db(app)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Promotion(db.Model):
    """
    Class that represents a Promotion
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    description = db.Column(db.String(63))
    products_type = db.Column(db.String(63), nullable=False)
    promotion_code = db.Column(db.String(63))
    require_code = db.Column(db.Boolean(), nullable=False, default=False)
    start_date = db.Column(db.Date(), nullable=False, default=date.today())
    end_date = db.Column(db.Date(), nullable=False, default=date.today())

    def __repr__(self):
        return f"<Promotion {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Promotion to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        if not self.require_code and self.promotion_code:
            raise DataValidationError(
                "Creates called with promotion_code and require_code=False"
            )
        if self.start_date > self.end_date:
            raise DataValidationError("Creates called with start_date > end_date")
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Promotion to the database
        """
        logger.info("Saving %s", self.name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """Removes a Promotion from the data store"""
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """Serializes a Promotion into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "products_type": self.products_type,
            "promotion_code": self.promotion_code,
            "require_code": self.require_code,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
        }

    def deserialize(self, data):
        """
        Deserializes a Promotion from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.description = data["description"]
            self.products_type = data["products_type"]
            self.promotion_code = data["promotion_code"]
            if isinstance(data["require_code"], bool):
                self.require_code = data["require_code"]
            else:
                raise DataValidationError(
                    "Invalid type for boolean [require_code]: "
                    + str(type(data["require_code"]))
                )
            self.start_date = date.fromisoformat(data["start_date"])
            self.end_date = date.fromisoformat(data["end_date"])

        except KeyError as error:
            raise DataValidationError(
                "Invalid Promotion: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Promotion: body of request contained bad or no data - "
                "Error message: " + str(error)
            ) from error
        return self

    @classmethod
    def init_db(cls, app):
        """Initializes the database session"""
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """Returns all of the Promotion in the database"""
        logger.info("Processing all Promotion")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Promotion by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Promotion with the given name

        Args:DataValidationError
            name (string): the name of the Promotion you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_products_type(cls, products_type):
        """Returns all Promotion with the given products_type

        Args:DataValidationError
            name (string): the products_type of the Promotion you want to match
        """
        logger.info("Processing products_type query for %s ...", products_type)
        return cls.query.filter(cls.products_type == products_type)

    @classmethod
    def find_by_date(cls, date_temp):
        """Returns all Promotion with the given date (current day)

        Args:DataValidationError
            name (string): the products_type of the Promotion you want to match
        """
        logger.info("Processing products_type query for %s ...", date_temp)
        # return cls.query.filter(
        #     cls.start_date <= date_temp and cls.end_date >= date_temp
        # )

        return cls.query.filter(
            and_(cls.start_date <= date_temp, cls.end_date >= date_temp)
        )
