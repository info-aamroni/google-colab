import http.client
import json
from urllib.parse import urlencode, urlparse
from typing import Optional, Dict, Any


class HttpClientService:
    def __init__(self, base_url: str):
        self.api_url = base_url.rstrip('/')  # Ensures no trailing slash in base URL
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.method = 'GET'
        self.params = None

    # Add request method
    def add_method(self, method: str):
        self.method = method.upper()
        return self

    # Add request header
    def add_header(self, headers: Optional[Dict[str, str]] = None):
        self.headers.update(headers or {})
        return self

    # Add request params
    def add_params(self, params: Optional[Dict[str, Any]] = None):
        self.params = params
        return self

    # Get the response
    def response(self, endpoint: str):
        # Parse the base URL
        parsed_url = urlparse(self.api_url)
        connection = http.client.HTTPSConnection(parsed_url.netloc) if parsed_url.scheme == "https" else http.client.HTTPConnection(parsed_url.netloc)
        path = f"{parsed_url.path}/{endpoint.lstrip('/')}"

        # Add query params if provided
        if self.params and self.method == "GET":
            path += f"?{urlencode(self.params)}"

        try:
            # Convert the body for POST/PUT/PATCH requests
            body = None
            if self.method in ["POST", "PUT", "PATCH"] and self.params and self.headers.get("Content-Type") == "application/json":
                body = json.dumps(self.params).encode('utf-8')

            # Make the request
            connection.request(self.method, path, body=body, headers=self.headers)
            response = connection.getresponse()
            data = response.read()

            # Handle response
            if 200 <= response.status < 300:
                return json.loads(data) if data else None
            elif response.status == 404:
                raise Exception(f"Resource not found at {path}")
            else:
                raise Exception(f"HTTP error occurred: {response.status} - {response.reason}")

        except json.JSONDecodeError:
            raise Exception("Failed to decode the response as JSON.")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {str(e)}")
        finally:
            connection.close()
