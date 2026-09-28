from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Protocol

import boto3

from app.config import settings


class ObjectStorage(Protocol):
    async def put(self, key: str, data: bytes, *, content_type: str | None = None) -> None: ...
    async def get(self, key: str) -> bytes: ...
    async def delete(self, key: str) -> None: ...


def _safe_key(key: str) -> str:
    path = PurePosixPath(key)
    if path.is_absolute() or ".." in path.parts or key.strip() == "":
        raise ValueError("invalid storage key")
    return str(path)


class LocalFilesystemStorage:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        safe = _safe_key(key)
        target = (self.root / safe).resolve()
        if self.root not in target.parents and target != self.root:
            raise ValueError("storage key escapes root")
        return target

    async def put(self, key: str, data: bytes, *, content_type: str | None = None) -> None:
        del content_type
        target = self._path(key)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    async def get(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    async def delete(self, key: str) -> None:
        path = self._path(key)
        if path.exists():
            path.unlink()


class S3ObjectStorage:
    def __init__(
        self,
        *,
        bucket: str,
        endpoint_url: str | None = None,
        region_name: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
    ) -> None:
        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            region_name=region_name,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    async def put(self, key: str, data: bytes, *, content_type: str | None = None) -> None:
        params = {"Bucket": self.bucket, "Key": _safe_key(key), "Body": data}
        if content_type:
            params["ContentType"] = content_type
        self.client.put_object(**params)

    async def get(self, key: str) -> bytes:
        response = self.client.get_object(Bucket=self.bucket, Key=_safe_key(key))
        return response["Body"].read()

    async def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=_safe_key(key))


def build_object_storage() -> ObjectStorage:
    if settings.storage_backend == "local":
        return LocalFilesystemStorage(settings.storage_local_path)
    if settings.storage_backend == "s3":
        if not settings.s3_bucket:
            raise RuntimeError("S3_BUCKET is required when STORAGE_BACKEND=s3")
        return S3ObjectStorage(
            bucket=settings.s3_bucket,
            endpoint_url=settings.s3_endpoint,
            region_name=settings.s3_region,
            access_key=settings.s3_access_key,
            secret_key=settings.s3_secret_key,
        )
    raise RuntimeError(f"Unsupported STORAGE_BACKEND={settings.storage_backend!r}")
