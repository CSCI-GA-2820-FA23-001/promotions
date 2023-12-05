"""
My Service

Describe what your service does here
"""
from datetime import datetime
from flask import jsonify, request, abort
from flask_restx import Resource, fields, reqparse, inputs
from service.common import status  # HTTP Status Codes
from service.models import Promotion

# Import Flask application
from . import app, api


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="OK"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    # return (
    #     # "Reminder: return some useful information in json format about the service here",
    #     jsonify(
    #         name="Promotion REST API Service",
    #         version="1.0",
    #     ),
    #     status.HTTP_200_OK,
    # )
    return app.send_static_file("index.html")


# Define the model so that the docs reflect what can be sent
create_model = api.model(
    "Promotion",
    {
        "name": fields.String(required=True, description="The name of the Promotion"),
        "description": fields.String(description="The description of the Promotion"),
        "products_type": fields.String(
            required=True, description="The products type of the Promotion"
        ),
        "promotion_code": fields.String(
            description="The promotion code of the Promotion"
        ),
        "require_code": fields.Boolean(
            required=True, description="Is the code required for Promotion?"
        ),
        "start_date": fields.Date(
            required=True, description="The day the Promotion start"
        ),
        "end_date": fields.Date(required=True, description="The day the Promotion end"),
        "is_active": fields.Boolean(
            required=True, description="Is the Promotion active?"
        ),
    },
)

promotion_model = api.inherit(
    "PromotionModel",
    create_model,
    {
        "_id": fields.String(
            readOnly=True,
            description="The unique id assigned internally by service",
        ),
    },
)

# query string arguments
promotion_args = reqparse.RequestParser()
promotion_args.add_argument(
    "name", type=str, location="args", required=False, help="List Promotions by name"
)
promotion_args.add_argument(
    "products_type",
    type=str,
    location="args",
    required=False,
    help="List Promotion by products type",
)
# promotion_args.add_argument(
#     "require_code",
#     type=inputs.boolean,
#     location="args",
#     required=False,
#     help="List promotions by require code",
# )
# promotion_args.add_argument(
#     "start_date",
#     type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
#     location="args",
#     required=False,
#     help="List Promotion by start date",
# )
# promotion_args.add_argument(
#     "end_date",
#     type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
#     location="args",
#     required=False,
#     help="List Promotion by end date",
# )
# promotion_args.add_argument(
#     "date",
#     type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
#     location="args",
#     required=False,
#     help="List Promotion by date",
# )


######################################################################
#  PATH: /promotions/{id}
######################################################################
@api.route("/promotions/<promotion_id>")
@api.param("promotion_id", "The promotion identifier")
class PromotionResource(Resource):
    """
    PromotionResource class

    Allows the manipulation of a single Promotion
    GET /promotion{id} - Returns a promotion with the id
    PUT /promotion{id} - Update a promotion with the id
    DELETE /promotion{id} -  Deletes a promotion with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A PROMOTION
    # ------------------------------------------------------------------
    @api.doc("get_promotions")
    @api.response(404, "Promotion not found")
    @api.marshal_with(promotion_model)
    def get(self, promotion_id):
        """
        Retrieve a single promotion

        This endpoint will return a promotion based on it's id
        """
        app.logger.info("Request to Retrieve a promotion with id [%s]", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Promotion with id '{promotion_id}' was not found.",
            )
        return promotion.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING PROMOTION
    # ------------------------------------------------------------------
    @api.doc("update_promotions")
    @api.response(404, "Promotion not found")
    @api.response(400, "The posted Promotion data was not valid")
    @api.expect(promotion_model)
    @api.marshal_with(promotion_model)
    def put(self, promotion_id):
        """
        Update a Promotion

        This endpoint will update a Promotion based the body that is posted
        """
        app.logger.info("Request to Update a promotion with id [%s]", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Promotion with id '{promotion_id}' was not found.",
            )
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        promotion.deserialize(data)
        promotion.id = promotion_id
        promotion.update()
        return promotion.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A PROMOTION
    # ------------------------------------------------------------------
    @api.doc("delete_promotions")
    @api.response(204, "Promotion deleted")
    def delete(self, promotion_id):
        """
        Delete a Promotion

        This endpoint will delete a Promotion based the id specified in the path
        """
        app.logger.info("Request to Delete a promotion with id [%s]", promotion_id)
        promotion = Promotion.find(promotion_id)
        if promotion:
            promotion.delete()
            app.logger.info("Promotion with id [%s] was deleted", promotion_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /promotions
######################################################################
@api.route("/promotions", strict_slashes=False)
class PromotionCollection(Resource):
    """Handles all interactions with collections of Promotions"""

    # ------------------------------------------------------------------
    # LIST ALL PROMOTIONS
    # ------------------------------------------------------------------
    @api.doc("list_promotions")
    @api.expect(promotion_args, validate=True)
    @api.marshal_list_with(promotion_model)
    def get(self):
        """Returns all of the Promotions"""
        app.logger.info("Request to list Promotions...")
        promotions = []
        args = promotion_args.parse_args()

        if args["name"]:
            app.logger.info("Filtering by name: %s", args["name"])
            promotions = list(Promotion.find_by_name(args["name"]))
        elif args["products_type"]:
            app.logger.info("Filtering by products_type: %s", args["products_type"])
            promotions = list(Promotion.find_by_products_type(args["products_type"]))
        # elif args["require_code"]:
        #     app.logger.info("Filtering by require_code: %s", args["require_code"])
        #     promotions = Promotion.find_by_require_code(args["require_code"])
        # elif args["start_date"]:
        #     app.logger.info("Filtering by start_date: %s", args["start_date"])
        #     promotions = Promotion.find_by_start_date(args["start_date"])
        # elif args["end_date"]:
        #     app.logger.info("Filtering by end_date: %s", args["end_date"])
        #     promotions = Promotion.find_by_end_date(args["end_date"])
        # elif args["date"]:
        #     app.logger.info("Filtering by date: %s", args["date"])
        #     promotions = Promotion.find_by_date(args["date"])
        else:
            app.logger.info("Returning unfiltered list.")
            promotions = Promotion.all()

        app.logger.info("[%s] Promotions returned", len(promotions))
        results = [promotion.serialize() for promotion in promotions]
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW PROMOTION
    # ------------------------------------------------------------------
    @api.doc("create_promotions")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_model)
    @api.marshal_with(promotion_model, code=201)
    def post(self):
        """
        Creates a promotion
        This endpoint will create a promotion based the data in the body that is posted
        """
        app.logger.info("Request to Create a promotion")
        promotion = Promotion()
        app.logger.debug("Payload = %s", api.payload)
        promotion.deserialize(api.payload)
        promotion.create()
        app.logger.info("Promotion with new id [%s] created!", promotion.id)
        location_url = api.url_for(
            PromotionResource, promotion_id=promotion.id, _external=True
        )
        return (
            promotion.serialize(),
            status.HTTP_201_CREATED,
            {"Location": location_url},
        )


######################################################################
#  PATH: /promotions/{id}/activate
######################################################################
@api.route("/promotions/<promotion_id>/activate")
@api.param("promotion_id", "The promotion identifier")
class ActivateResource(Resource):
    """Activate actions on a Promotion"""

    @api.doc("activate_promotions")
    @api.response(404, "Promotion not found")
    @api.response(409, "The promotion is not available for activate")
    def put(self, promotion_id):
        """
        Activate a Promotion

        This endpoint will activate a promotion
        """
        app.logger.info("Request to activate a promotion")
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Promotion with id [{promotion_id}] was not found.",
            )

        promotion.activate()
        app.logger.info("Promotion with id [%s] activated.", promotion.id)
        return promotion.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /promotions/{id}/deactivate
######################################################################
@api.route("/promotions/<promotion_id>/deactivate")
@api.param("promotion_id", "The promotion identifier")
class DeactivateResource(Resource):
    """Deactivate actions on a Promotion"""

    @api.doc("deactivate_promotions")
    @api.response(404, "Promotion not found")
    @api.response(409, "The promotion is not available for deactivate")
    def put(self, promotion_id):
        """
        Deactivate a Promotion

        This endpoint will deactivate a promotion
        """
        app.logger.info("Request to deactivate a promotion")
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Promotion with id [{promotion_id}] was not found.",
            )

        promotion.deactivate()
        app.logger.info("Promotion with id [%s] deactivated.", promotion.id)
        return promotion.serialize(), status.HTTP_200_OK


# ######################################################################
# # CREATE A NEW PROMOTION
# ######################################################################
# @app.route("/promotions", methods=["POST"])
# def create_promotions():
#     """
#     Creates a promotions
#     This endpoint will create a promotions based the data in the body that is posted
#     """
#     app.logger.info("Request to create a promotions")

#     check_content_type("application/json")
#     promotion = Promotion()
#     promotion.deserialize(request.get_json())

#     promotion.create()
#     message = promotion.serialize()

#     location_url = url_for("read_promotions", promotion_id=promotion.id, _external=True)

#     app.logger.info("promotion with ID [%s] created.", promotion.id)
#     return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
# ######################################################################
# # READ A PROMOTION
# ######################################################################
# @app.route("/promotions/<int:promotion_id>", methods=["GET"])
# def read_promotions(promotion_id):
#     """
#     Retrieve a single promotion

#     This endpoint will return a promotion based on it's id
#     """
#     app.logger.info("Request for promotion with id: %s", promotion_id)
#     promotion = Promotion.find(promotion_id)
#     if not promotion:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"promotion with id '{promotion_id}' was not found.",
#         )

#     app.logger.info("Returning promotion: %s", promotion.name)
#     return jsonify(promotion.serialize()), status.HTTP_200_OK
# ######################################################################
# # LIST ALL PROMOTIONS
# ######################################################################
# @app.route("/promotions", methods=["GET"])
# def list_promotions():  # noqa: C901
#     """Returns all of the Promotions"""
#     app.logger.info("Request for promotion list")

#     name = request.args.get("name")

#     products_type = request.args.get("products_type")

#     require_code = request.args.get("require_code")

#     start_date_filter = request.args.get("start_date")
#     end_date_filter = request.args.get("end_date")

#     discounted_products_list = request.args.get("discounted_products")

#     promotions = Promotion.all()

#     # Filter by product name if specified
#     if name:
#         promotions = [promotion for promotion in promotions if promotion.name == name]

#     # Filter by product type if specified
#     if products_type:
#         promotions = [
#             promo for promo in promotions if promo.products_type == products_type
#         ]

#     # Filter by require_code if specified
#     if require_code:
#         require_code_bool = require_code.lower() == "true"
#         promotions = [
#             promotion
#             for promotion in promotions
#             if promotion.require_code == require_code_bool
#         ]

#     # Filter by start date if specified
#     if start_date_filter:
#         try:
#             start_date = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
#             promotions = [
#                 promo for promo in promotions if promo.start_date >= start_date
#             ]
#         except ValueError:
#             app.logger.info("Invalid start_date format: {start_date_filter}")
#             abort(
#                 status.HTTP_400_BAD_REQUEST,
#                 f"Invalid start_date format: {start_date_filter}",
#             )

#     # Filter by end date if specified
#     if end_date_filter:
#         try:
#             end_date = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
#             promotions = [promo for promo in promotions if promo.end_date <= end_date]
#         except ValueError:
#             app.logger.info("Invalid end_date format: {end_date_filter}")
#             abort(
#                 status.HTTP_400_BAD_REQUEST,
#                 f"Invalid end_date format: {end_date_filter}",
#             )

#     # filter by discounted_products
#     if discounted_products_list:
#         discounted_products_intlist = list(
#             map(int, discounted_products_list.split(","))
#         )

#         promotions = [
#             promotion
#             for promotion in promotions
#             if promotion.id in discounted_products_intlist
#         ]

#     results = [promotion.serialize() for promotion in promotions]
#     app.logger.info("Returning %d promotions", len(promotions))
#     return jsonify(results), status.HTTP_200_OK
# ######################################################################
# # DELETE A PROMOTION
# ######################################################################
# @app.route("/promotions/<int:promotion_id>", methods=["DELETE"])
# def delete_promotions(promotion_id):
#     """
#     Delete a Promotion by ID

#     This endpoint will delete a Promotion based on the id specified in the path
#     """
#     app.logger.info("Request for delete promotion with id: %s", promotion_id)
#     promotion = Promotion.find(promotion_id)
#     if promotion:
#         promotion.delete()

#     app.logger.info("Promotion with ID [%s] delete complete.", promotion_id)
#     return "", status.HTTP_204_NO_CONTENT
# ######################################################################
# # UPDATE A PROMOTION
# ######################################################################
# @app.route("/promotions/<int:promotion_id>", methods=["PUT"])
# def update_promotions(promotion_id):
#     """
#     Update a promotion

#     This endpoint will update a promotion based on the data in the body that is posted
#     """
#     app.logger.info("Request to update promotion with id: %s", promotion_id)
#     check_content_type("application/json")

#     promotion = Promotion.find(promotion_id)
#     if not promotion:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Promotion with id '{promotion_id}' was not found.",
#         )

#     # Deserialize the JSON data from the request and update the promotion object
#     promotion_data = request.get_json()
#     promotion.deserialize(promotion_data)
#     promotion.update()

#     app.logger.info("Promotion with ID [%s] updated.", promotion.id)

#     return jsonify(promotion.serialize()), status.HTTP_200_OK

# ######################################################################
# # ACTIVE A PROMOTION
# ######################################################################
# @app.route("/promotions/<int:promotion_id>/activate", methods=["PUT"])
# def activate_promotion(promotion_id):
#     """
#     Activate a promotion

#     This endpoint will set a promotion's is_active to True based on the id specified in the path
#     """

#     app.logger.info("Request to activate promotion with id: %s", promotion_id)
#     promotion = Promotion.find(promotion_id)
#     if not promotion:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Promotion with id '{promotion_id}' was not found.",
#         )

#     promotion.activate()
#     app.logger.info("Promotion with ID [%s] activated.", promotion_id)

#     return jsonify(promotion.serialize()), status.HTTP_200_OK

# ######################################################################
# # DEACTIVE A PROMOTION
# ######################################################################
# @app.route("/promotions/<int:promotion_id>/deactivate", methods=["PUT"])
# def deactivate_promotion(promotion_id):
#     """
#     Deactivate a promotion

#     This endpoint will set a promotion's is_active to False based on the id specified in the path
#     """
#     app.logger.info("Request to deactivate promotion with id: %s", promotion_id)
#     promotion = Promotion.find(promotion_id)
#     if not promotion:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Promotion with id '{promotion_id}' was not found.",
#         )

#     promotion.deactivate()
#     app.logger.info("Promotion with ID [%s] deactivated.", promotion_id)

#     return jsonify(promotion.serialize()), status.HTTP_200_OK


# ######################################################################
# #  U T I L I T Y   F U N C T I O N S
# ######################################################################
# def check_content_type(content_type):
#     """Checks that the media type is correct"""
#     if "Content-Type" not in request.headers:
#         app.logger.error("No Content-Type specified.")
#         abort(
#             status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
#             f"Content-Type must be {content_type}",
#         )

#     if request.headers["Content-Type"] == content_type:
#         return

#     app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
#     abort(
#         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
#         f"Content-Type must be {content_type}",
#     )
