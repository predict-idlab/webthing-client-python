from typing import Tuple, Union
try:
    from flask_restx import Api
except ImportError:
    import werkzeug
    werkzeug.cached_property = werkzeug.utils.cached_property # type: ignore
    from flask_restx import Api
from flask_restx import fields, OrderedModel, Model


# Properties
api_request = None
api_response = None
api_error_response = None


# Base api marshalling
def register_api_base_models(api: Api) -> Tuple[Union[OrderedModel, Model], Union[OrderedModel, Model], Union[OrderedModel, Model]]:
    """
    Register standard api models for marshalling to the provided flask-restx Api.
    :return: Tuple of api_request, api_response, api_error_response.
    """
    global api_request
    global api_response
    global api_error_response

    api_request = api.model('ApiRequest', {
        'endpoint': fields.String(required=False),
        'metadata': fields.Raw(required=False, description='Metadata'),
        'data': fields.Raw(required=False, description='Payload')
    })

    api_response = api.model('ApiResponse', {
        'endpoint': fields.String(required=False),
        'status': fields.String(
            description="If 'success' results in 'data', if 'error' information in 'message' and 'data'",
            enum=['success', 'error'], required=True),
        'message': fields.String(required=True),
        'data': fields.Raw(required=True, description='Payload')
    })

    api_error_response = api.inherit('ApiErrorResponse', api_response, {
        'data': fields.Raw(description='(Nested) information about error')
    })

    return api_request, api_response, api_error_response
