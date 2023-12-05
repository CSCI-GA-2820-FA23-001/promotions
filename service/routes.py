"""
My Service

Describe what your service does here
"""
from flask import jsonify, abort
from flask_restx import Resource, fields, reqparse
from service.common import status  # HTTP Status Codes
from service.models import Promotion

# Import Flask application
from . import app, api


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health():
    """Let them know our heart is still beating"""
    return jsonify({"status": "OK"}), status.HTTP_200_OK


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
