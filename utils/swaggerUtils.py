# utils.py (or a new file for custom utilities)

from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema

class CustomAutoSchema(SwaggerAutoSchema):
    def get_request_body(self, request_body=None):
        if request_body is not None:
            return request_body
        
        if self.method == 'POST':
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'currentUserId': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the current user'),
                },
                required=['currentUserId'],
            )

        return super().get_request_body(request_body)

    def get_responses(self):
        responses = super().get_responses()

        if self.method == 'POST':
            responses.update({
                200: openapi.Response(
                    description="A list of users that the current user is following.",
                    schema=openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
                                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                                # Add other fields returned by UserSerializer
                            }
                        )
                    )
                ),
                400: openapi.Response(description="Bad Request"),
                404: openapi.Response(description="Not Found"),
            })
        return responses
