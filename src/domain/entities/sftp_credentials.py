from dataclasses import dataclass
from typing import Optional


@dataclass
class SftpCredentials:

    host: str

    port: int

    username: str

    password: Optional[str] = None

    private_key: Optional[str] = None

    private_key_passphrase: Optional[str] = None