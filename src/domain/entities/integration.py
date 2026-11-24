from dataclasses import dataclass


@dataclass(frozen=True)
class Integration:
    """
    Represents an SFTP integration configuration.

    An integration defines the connection information required to access
    a remote SFTP server. Credentials are stored in AWS Secrets Manager
    and referenced by the secret_name field.
    """

    name: str

    secret_name: str

    enabled: bool

    description: str | None = None