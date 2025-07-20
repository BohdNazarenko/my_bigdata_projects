import asyncio
import logging
import os

from contextlib import asynccontextmanager
from typing import Optional, List
from botocore.exceptions import ClientError
from pathlib import Path
from dotenv import load_dotenv
from aiobotocore.session import get_session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("s3_client.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("S3")

load_dotenv()

CONFIG = {
    "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
    "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
    "region_name": os.getenv("AWS_REGION"),
    "container": os.getenv("BUCKET_NAME"),
}


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


class S3Storage:

    def __init__(self, *, aws_access_key_id: str, aws_secret_access_key: str, region_name: str, container: str):
        if not all([aws_access_key_id, aws_secret_access_key, region_name, container]):
            raise ValueError("Missing required configuration parameters")

        self._auth = {
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "region_name": region_name,
            "verify": False,
        }

        self._bucket = container
        self._session = get_session()


    @asynccontextmanager
    async def _connect(self):
        async with self._session.create_client("s3", **self._auth) as connection:
            yield connection


    async def send_file(self, local_source: str, target_name: Optional[str] = None) -> None:
        file_ref = Path(local_source)

        if target_name is None:
            target_name = file_ref.name
            logger.warning(f"Target name is none")

        try:
            async with self._connect() as remote:
                with file_ref.open("rb") as binary_data:
                    await remote.put_object(
                        Bucket=self._bucket,
                        Key=target_name,
                        Body=binary_data
                    )
                logger.info(f"Send {target_name} to s3 storage")
        except ClientError as error:
            logger.info(f"Failed to send {target_name}: {error}")


    async def fetch_file(self, remote_name: str, local_target: Optional[str] = None):
        try:
            async with self._connect() as remote:
                response = await remote.get_object(Bucket=self._bucket, Key=remote_name)
                body = await response["Body"].read()

                if local_target is None:
                    local_target = Path(remote_name).name
                    logger.info(f"Local target not specified, using: {local_target}")

                with open(local_target, "wb") as out:
                    out.write(body)
                logger.info(f"Retrieved: {remote_name}")

        except ClientError as error:
            logger.error(f"Could not retrieve {remote_name}: {error}")


    async def remove_file(self, remote_name: str):
        try:
            async with self._connect() as remote:
                await remote.delete_object(Bucket=self._bucket, Key=remote_name)
                logger.info(f"Removed: {remote_name}")

        except ClientError as error:
            logger.error(f"Failed to remove {remote_name}: {error}")




    #prefix - everything that is in the directory
    async def list_files(self, prefix: str = "") -> List[str]:

        keys: List[str] = []
        try:
            async with self._connect() as remote:
                paginator = remote.get_paginator("list_objects_v2")

                async for page in paginator.paginate(
                        Bucket=self._bucket,
                        Prefix=prefix
                ):
                    keys.extend(obj["Key"] for obj in page.get("Contents", []))
        #catch exception
        except ClientError as err:
            code = err.response["Error"]["Code"]
            if code in ("AccessDenied", "AllAccessDisabled"):
                logger.warning(
                    "No permission to list objects in bucket %s (prefix %s): %s",
                    self._bucket,
                    prefix or "(root)",
                    code,
                )
                return []
            raise

        return keys


    async def file_exists(self, *, prefix: str = "", file_name: str) -> bool:

        key = f"{prefix.rstrip('/') + '/' if prefix else ''}{file_name}"

        async with self._connect() as remote:
            try:
                await remote.head_object(Bucket=self._bucket, Key=key)
                return True
            except ClientError as err:
                if err.response["Error"]["Code"] == "404":
                    return False
                raise


    async def get_bucket_size(self) -> int:
        total_size = 0

        try:
            async with self._connect() as remote:
                paginator = remote.get_paginator("list_objects_v2")
                async for page in paginator.paginate(Bucket=self._bucket):
                    contents = page.get("Contents", [])
                    logger.info(f"Found {len(contents)} objects in page")

                    for obj in contents:
                        logger.info(f"Object {obj['Key']} - Size: {obj['Size']} bytes")
                        total_size += obj["Size"]

            logger.info(f"Total size calculated: {total_size} bytes")
            return total_size

        except ClientError as e:
            logger.error(f"Error calculating bucket size: {e}")
            return 0



async def demo():
    storage = S3Storage(
        aws_access_key_id=CONFIG["aws_access_key_id"],
        aws_secret_access_key=CONFIG["aws_secret_access_key"],
        region_name=CONFIG["region_name"],
        container=CONFIG["container"]
    )

    await storage.send_file("./Readme.md")

    all_keys = await storage.list_files("images/")
    print(all_keys)

    is_file = await storage.file_exists(file_name="Readme.md")
    print(is_file)


if __name__ == "__main__":
    asyncio.run(demo())
