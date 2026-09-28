import pytest

from app.storage import LocalFilesystemStorage


@pytest.mark.asyncio
async def test_local_storage_round_trip(tmp_path):
    storage = LocalFilesystemStorage(tmp_path)
    await storage.put("test/asset.bin", b"greenbusiness")
    assert await storage.get("test/asset.bin") == b"greenbusiness"
    await storage.delete("test/asset.bin")
    with pytest.raises(FileNotFoundError):
        await storage.get("test/asset.bin")


@pytest.mark.asyncio
async def test_local_storage_rejects_path_traversal(tmp_path):
    storage = LocalFilesystemStorage(tmp_path)
    with pytest.raises(ValueError):
        await storage.put("../escape.bin", b"nope")
