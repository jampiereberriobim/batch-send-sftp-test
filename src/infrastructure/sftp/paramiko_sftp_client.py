from io import StringIO
import posixpath

import paramiko

from src.domain.entities.sftp_credentials import SftpCredentials
from src.domain.exceptions import SftpConnectionError
from src.domain.ports.sftp_client import SftpClient
from src.shared.logger import logger


class ParamikoSftpClient(SftpClient):
    """Paramiko adapter using SSH private-key authentication."""

    def __init__(self) -> None:
        self._transport = None
        self._client = None

    @staticmethod
    def _load_private_key(
        key: str,
        passphrase: str | None = None,
    ):
        # Secrets Manager may store line breaks as escaped \\n sequences.
        normalized_key = (
            key.replace("\\r\\n", "\\n")
            .replace("\\n", "\n")
            .strip()
        )

        for key_cls in (
            paramiko.Ed25519Key,
            paramiko.RSAKey,
            paramiko.ECDSAKey,
        ):
            try:
                return key_cls.from_private_key(
                    StringIO(normalized_key + "\\n"),
                    password=passphrase,
                )
            except Exception:
                continue

        raise ValueError(
            "Unsupported or invalid SSH private key format. "
            "Expected an Ed25519, RSA, or ECDSA private key."
        )

    def connect(self, credentials: SftpCredentials) -> None:
        logger.info(
            "Connecting to SFTP %s:%s",
            credentials.host,
            credentials.port,
        )

        try:
            if not credentials.private_key:
                raise ValueError(
                    "SSH private key is required for SFTP authentication."
                )

            private_key = self._load_private_key(
                credentials.private_key,
                credentials.private_key_passphrase,
            )

            self._transport = paramiko.Transport(
                (credentials.host, credentials.port)
            )
            self._transport.connect(
                username=credentials.username,
                pkey=private_key,
            )
            logger.info("Authenticated to SFTP using SSH private key.")

            self._client = paramiko.SFTPClient.from_transport(
                self._transport
            )
            logger.info("SFTP connection established successfully.")
        except Exception as exc:
            self.disconnect()
            raise SftpConnectionError(
                f"Unable to connect to SFTP server: {exc}"
            ) from exc

    def disconnect(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
        if self._transport:
            self._transport.close()
            self._transport = None

    def _ensure_connection(self) -> None:
        if self._client is None:
            raise SftpConnectionError(
                "SFTP connection has not been established."
            )

    def _ensure_remote_directory(self, remote_path: str) -> None:
        self._ensure_connection()
        normalized = posixpath.normpath(remote_path or ".")
        if normalized in ("", "."):
            return

        current = "/" if normalized.startswith("/") else ""
        for part in normalized.strip("/").split("/"):
            if not part:
                continue
            current = posixpath.join(current, part) if current else part
            try:
                self._client.stat(current)
            except OSError:
                self._client.mkdir(current)

    def upload(
        self,
        file_stream,
        remote_path: str,
        filename: str,
    ) -> str:
        self._ensure_connection()
        self._ensure_remote_directory(remote_path)

        remote_file = posixpath.join(remote_path, filename)
        if hasattr(file_stream, "seek"):
            file_stream.seek(0)

        self._client.putfo(file_stream, remote_file)
        logger.info("Uploaded file to SFTP: %s", remote_file)
        return remote_file
