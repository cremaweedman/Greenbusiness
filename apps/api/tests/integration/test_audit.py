import pytest
from sqlalchemy import select

from app.audit import append_audit_event
from app.db.models import AuditEvent
from app.db.session import SessionLocal


@pytest.mark.asyncio
async def test_audit_event_persists():
    async with SessionLocal() as session:
        event = await append_audit_event(
            session,
            event_type="foundation.integration_test",
            actor_type="system",
            request_id="integration-test",
            payload={"ok": True},
        )
        await session.commit()
        event_id = event.id

    async with SessionLocal() as session:
        stored = await session.scalar(select(AuditEvent).where(AuditEvent.id == event_id))
        assert stored is not None
        assert stored.event_type == "foundation.integration_test"
        assert stored.payload == {"ok": True}
