from boto3.resources.base import ServiceResource

from src.infrastructure.aws.boto_session import BotoSession


class DynamoDbClient:

    def __init__(self):

        self._resource: ServiceResource = (
            BotoSession.session().resource("dynamodb")
        )

    @property
    def resource(self) -> ServiceResource:
        return self._resource