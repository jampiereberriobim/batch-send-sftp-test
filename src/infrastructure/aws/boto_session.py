import boto3
from boto3.session import Session


class BotoSession:

    @staticmethod
    def session() -> Session:
        """
        Creates a boto3 session.

        Returns
        -------
        Session
            AWS boto3 session.
        """
        return boto3.Session()