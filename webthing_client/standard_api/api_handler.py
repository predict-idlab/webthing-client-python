import logging
import json
import inspect
from typing import Any, Callable, Tuple
from enum import Enum
import traceback
from abc import ABC

import requests


class ApiResponseStatus(Enum):
    SUCCESS = 'success'
    ERROR = 'error'
    OTHER = 'other'


class ApiRequestingException(Exception):
    """
    Exception used when error or other, allows readable chaining of multiple depth api calls.
    """

    def __init__(self, message, data):
        super().__init__(message)
        self.message = message
        self.data = data


class ApiBase(ABC):
    """
    Base Api functions.
    """

    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(__name__)

    def _json_dumps(self, obj: Any, indent: int = 2) -> str:
        return json.dumps(obj, indent=indent)

    def _json_loads(self, obj: str) -> Any:
        return json.loads(obj)

    @staticmethod
    def _get_status_code(status: ApiResponseStatus) -> int:
        if status == ApiResponseStatus.SUCCESS:
            return 200
        else:
            return 400

    @staticmethod
    def _get_status(status_code: int) -> ApiResponseStatus:
        if status_code == 200:
            return ApiResponseStatus.SUCCESS
        elif status_code == 400:
            return ApiResponseStatus.ERROR
        else:
            return ApiResponseStatus.OTHER

    @staticmethod
    def _request_set_default(request_body: dict) -> dict:
        request_body.setdefault('endpoint', '')
        request_body.setdefault('metadata', {})
        request_body.setdefault('data', None)
        return request_body


class ApiRequester(ApiBase):
    """
    Class that helps getting data from standard api interface.
    """

    def __init__(self,  base_api_endpoint: str,
                        default_metadata: dict = {},
                        before_request: Callable[[], None] = None,
                        after_request: Callable[[], None] = None,
                        headers: dict = {}):
        super().__init__()
        self._base_api_endpoint = base_api_endpoint.rstrip('/')
        self._default_metadata = default_metadata
        self._before_request = before_request
        self._after_request = after_request
        self._headers = headers
        self._headers.update({'Content-type': 'application/json', 'Accept': 'application/json'})

    def call(self, function_endpoint: str, data: Any = None, metadata: dict = {}) -> Any:
        """
        Calls the function endpoint and handle errors/exceptions. Payload should be a json serializable object.
        Exceptions are rethrown with extra information. Return data in 'data'.
        """
        endpoint = f"{self._base_api_endpoint}/{function_endpoint.lstrip('/')}"
        request_body = {
            'data': data,
            'metadata': {**self._default_metadata, **metadata},
            'endpoint': endpoint
        }
        request_body_serialized = self._json_dumps(request_body)

        self._logger.info(  f"--- Requesting an API call ---\n"
                            f"- Request endpoint: {endpoint}\n"
                            f"- Request payload:\n{request_body_serialized}\n")

        if self._before_request is not None:
            self._before_request()
        
        response = requests.post(endpoint, data=request_body_serialized, headers=self._headers)
        response_status = self._get_status(response.status_code)

        log_message = ( f"--- API response ---\n"
                        f"- Response status: {response.reason} ({response.status_code})\n"
                        f"- Response body:\n{response.text}\n")

        if self._after_request is not None:
            self._after_request()

        if response_status == ApiResponseStatus.SUCCESS:
            # Server answered the request succesfully
            self._logger.info(log_message)

            response_body = self._json_loads(response.text)
            return response_body['data']

        else:
            self._logger.error(log_message)

            data = {
                'response': {
                    'statusCode': response.status_code,
                    'headers': dict(response.headers),
                    'body': None
                },
                'request': {
                    'endpoint': endpoint,
                    'headers': dict(response.request.headers),
                    'body': request_body
                }
            }
            if response_status == ApiResponseStatus.ERROR:
                # Server could not answer the request succesfully
                data['response']['body'] = json.loads(response.text)
                raise ApiRequestingException(f"API calling error", data)

            else:
                # Server could not answer the request (most likely 500)
                data['response']['body'] = response.text
                raise ApiRequestingException(f"API calling failed", data)


class ApiResponder(ApiBase):
    """
    Class that helps returning data as standard api interface format.
    """

    def __init__(self,  process_metadata: Callable[[dict], None] = None,
                        before_processing: Callable[[], None] = None,
                        after_processing: Callable[[], None] = None):
        """
        Before processing should accept full json request body object and return one, 
        after processing should accept wrapped json response body object and return one.
        """
        super().__init__()
        self._process_metadata = process_metadata
        self._before_processing = before_processing
        self._after_processing = after_processing

    def _create_response(self, status: ApiResponseStatus, endpoint: str, message: str, data: Any) -> Tuple[dict, int]:
        """
        Returns wrapped response body.
        """
        response = {'status': status.value, 'endpoint': endpoint, 'message': message, 'data': data}
        return response

    def process(self, function: Callable[[Any], Any], request_body: dict) -> Tuple[dict, int]:
        """
        Process the payload with the given function and return the wrapped response and http response code.
        The return data from the function should be json serializable and errors in the function should cause an exception.
        """
        request_body = self._request_set_default(request_body)
        
        function_string = inspect.getsource(function).strip(' ')
        endpoint = request_body['endpoint']

        self._logger.info(  f"--- Responding to API call ---\n"
                            f"- Request function: {function_string}\n"
                            f"- Request body:\n{self._json_dumps(request_body)}\n")
                            
        try:
            if self._process_metadata is not None:
                self._process_metadata(request_body['metadata'])

            result = function(request_body['data'])

            response_status = ApiResponseStatus.SUCCESS
            response_body = self._create_response(response_status, endpoint, "Success", result,)

        except ApiRequestingException as e:
            # This component was calling a remote component via the api and it failed on the remote component
            # Allow more readable chaining of depth api calls, the response body of the deeper call is in the data of upper call
            data = {
                'request': {
                    'function': function_string,
                    'body': request_body
                },
                'remoteApiCall': e.data
            }

            response_status = ApiResponseStatus.ERROR
            response_body = self._create_response(response_status, endpoint, e.message, data)

        except Exception as e:
            # When any exception return back stacktrace and request body
            data = {
                'request': {
                    'function': function_string,
                    'body': request_body
                },
                'exception': {
                    'exception': str(e),
                    'traceback': traceback.format_exc()
                }
            }

            response_status = ApiResponseStatus.ERROR
            response_body = self._create_response(response_status, endpoint, f"Exception occured", data)

        log_message = ( f"--- API response ---\n"
                        f"- Response status: {response_status.value}\n"
                        f"- Response body:\n{self._json_dumps(response_body)}\n")

        if response_status == ApiResponseStatus.SUCCESS:
            self._logger.info(log_message)
        else:
            self._logger.error(log_message)

        return response_body, self._get_status_code(response_status)


class ApiForwarder(ApiBase):
    """
    Class that receives api responses and forwards them to another endpoint.
    """

    def __init__(self, base_api_endpoint: str, transform_metadata: Callable[[dict], dict] = None):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self._requester = ApiRequester(base_api_endpoint)
        self._responder = ApiResponder()
        self._transform_metadata = transform_metadata

    def forward_request(self, function_endpoint: str, request_body: Any) -> Tuple[dict, int]:
        request_body = self._request_set_default(request_body)

        def process_metadata_and_call(data):
            if self._transform_metadata is not None:
                request_body['metadata'] = self._transform_metadata(request_body['metadata'])
            return self._requester.call(function_endpoint, data, request_body['metadata'])

        func = process_metadata_and_call
        return self._responder.process(func, request_body)
