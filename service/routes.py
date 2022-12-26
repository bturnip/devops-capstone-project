"""
Account Service

This microservice handles the lifecycle of Accounts
"""
# pylint: disable=unused-import
from flask import jsonify, request, make_response, abort, url_for   # noqa; F401
from service.models import Account
from service.common import status  # HTTP Status Codes
from . import app  # Import Flask application


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Account REST API Service",
            version="1.0",
            # paths=url_for("list_accounts", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A NEW ACCOUNT
######################################################################
@app.route("/accounts", methods=["POST"])
def create_accounts():
    """
    Creates an Account
    This endpoint will create an Account based the data in the body that is posted
    """
    app.logger.info("Request to create an Account")
    check_content_type("application/json")
    account = Account()
    account.deserialize(request.get_json())
    account.create()
    message = account.serialize()
    # Uncomment once get_accounts has been implemented
    # location_url = url_for("get_accounts", account_id=account.id, _external=True)
    location_url = "/"  # Remove once get_accounts has been implemented
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


######################################################################
# LIST ALL ACCOUNTS
######################################################################
@app.route("/accounts", methods=["GET"])
def list_accounts():
    """ Return a list of all accounts """
    app.logger.info("Returning all records")
    acct_list = []
    for x in Account.all():
        acct_list.append(x.serialize())

    records_returned = len(acct_list)
    app.logger.info(f"Total number of records returned: [{records_returned}]")
    message = acct_list

    request_status = status.HTTP_200_OK

    return make_response(jsonify(message), request_status, {"Location": "/"})


######################################################################
# READ AN ACCOUNT
######################################################################
@app.route("/accounts/<acct_id>", methods=["GET"])
def read_account(acct_id):
    """
    Finds and returns an account by input id
    Returns status HTTP-404 if account not found, HTTP-200 otherwise
    """
    app.logger.info(f"Account info request: acct_id:[{acct_id}]")
    account = Account.find(acct_id)

    if account is None:
        message = f"No account found with id: [{acct_id}]"
        request_status = status.HTTP_404_NOT_FOUND
    else:
        message = account.serialize()
        request_status = status.HTTP_200_OK

    return make_response(jsonify(message), request_status, {"Location": "/"})


######################################################################
# UPDATE AN EXISTING ACCOUNT
######################################################################
@app.route("/accounts/<acct_id>", methods=["PUT"])
def upate_account(acct_id):
    """
    Updates an account with given input id
    Returns status HTTP-404 if account not found, HTTP-200 otherwise
    PUT Method implies full record must be included in request
    """
    app.logger.info(f"Updating Account request: acct_id:[{acct_id}]")
    account = Account.find(acct_id)

    if account is None:
        message = f"No account found with id: [{acct_id}]"
        request_status = status.HTTP_404_NOT_FOUND
        abort(request_status, message)
    else:
        # call the deserialize() method on the account passing in request.get_json()
        # call account.update() to update the account with the new data
        account.deserialize(request.get_json())
        account.update()

        # refetch new account details and return
        message = account.serialize()
        request_status = status.HTTP_200_OK

    return make_response(jsonify(message), request_status, {"Location": "/"})


######################################################################
# DELETE AN ACCOUNT
######################################################################
@app.route("/accounts/<acct_id>", methods=["DELETE"])
def delete_account(acct_id):
    """
    Finds and deletes an account with given input id
    Returns status HTTP-204 after deleting or if account not found
    """
    app.logger.info(f"Deleting Account request: acct_id:[{acct_id}]")
    account = Account.find(acct_id)

    if account is None:
        message = f"Account id [{acct_id}] not found, nothing to do."
        app.logger.info(message)
    else:
        message = f"Account id [{acct_id}] deleted"
        account.delete()

    request_status = status.HTTP_204_NO_CONTENT
    return make_response(jsonify(message), request_status, {"Location": "/"})


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
