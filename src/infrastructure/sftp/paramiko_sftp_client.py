from fnmatch import fnmatch
from io import BytesIO
from stat import S_ISDIR
from datetime import datetime
import paramiko
from io import StringIO
from src.domain.entities.remote_file import RemoteFile
from src.domain.entities.sftp_credentials import SftpCredentials
from src.domain.ports.sftp_client import SftpClient
from src.domain.exceptions import SftpConnectionError
from src.shared.logger import logger

class ParamikoSftpClient(SftpClient):
    """
    Paramiko implementation of the SFTP client.
    """

    def __init__(self) -> None:

        self._transport = None
        self._client = None

    def _load_private_key(self, key: str, passphrase: str | None = None):

        for key_cls in (
            paramiko.Ed25519Key,
            paramiko.RSAKey,
            paramiko.ECDSAKey,
        ):
            try:
                return key_cls.from_private_key(
                    StringIO(key),
                    password=passphrase,
                )
            except Exception:
                continue

        raise ValueError("Unsupported private key format.")

    def connect(
        self,
        credentials: SftpCredentials,
    ) -> None:

        logger.info(
            "Connecting to SFTP %s:%s",
            credentials.host,
            credentials.port,
        )

        try:

            self._transport = paramiko.Transport(
                (credentials.host, credentials.port)
            )

            if credentials.private_key:

                private_key = self._load_private_key(
                    credentials.private_key,
                    credentials.private_key_passphrase,
                )

                self._transport.connect(
                    username=credentials.username,
                    pkey=private_key,
                )
                logger.info("Authenticating with private key.")

            else:

                self._transport.connect(
                    username=credentials.username,
                    password=credentials.password,
                )
                logger.info("Authenticating with password.")

            self._client = paramiko.SFTPClient.from_transport(
                self._transport
            )

            logger.info("SFTP connection established successfully.")

        except Exception as e:

            self.disconnect()

            raise SftpConnectionError(
                f"Unable to connect to SFTP server: {e}"
            ) from e

    def disconnect(self) -> None:
    
        if self._client:
            self._client.close()
            self._client = None
    
        if self._transport:
            self._transport.close()
            self._transport = None
            
    def _ensure_connection(self) -> None:
        """
        Ensures that the SFTP connection has been established.
        """

        if self._client is None:
            raise SftpConnectionError(
                "SFTP connection has not been established."
            )
            
    def list_files(
        self,
        remote_path: str,
        pattern: str,
        recursive: bool,
    ) -> list[RemoteFile]:

        files: list[RemoteFile] = []

        self._list_directory(
            remote_path,
            pattern,
            recursive,
            files,
        )
        logger.info(
            "Listing files from %s",
            remote_path,
        )
        return files

    def download(
        self,
        remote_file: RemoteFile,
    ) -> BytesIO:
        logger.info(
            "Downloading %s",
            remote_file.name,
        )    
        self._ensure_connection()
    
        stream = BytesIO()
    
        self._client.getfo(
            remote_file.path,
            stream,
        )
    
        stream.seek(0)
    
        return stream

    def _list_directory(
        self,
        directory: str,
        pattern: str,
        recursive: bool,
        files: list[RemoteFile],
    ) -> None:

        for item in self._client.listdir_attr(directory):

            path = f"{directory}/{item.filename}"

            if S_ISDIR(item.st_mode):

                if recursive:

                    self._list_directory(
                        path,
                        pattern,
                        recursive,
                        files,
                    )

                continue

            if not fnmatch(item.filename, pattern):
                continue

            files.append(
                RemoteFile(
                    name=item.filename,
                    path=path,
                    size=item.st_size,
                    modified_at=datetime.fromtimestamp(
                        item.st_mtime),
                )
            )