from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.datasets.utils import build_customer_id, stable_hash
from app.models.canonical import Customer


class SyntheticCustomerLinker:
    """Creates deterministic joins across unrelated public datasets."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def anchor_customer_ids(self) -> list[str]:
        return list(
            self.session.scalars(
                select(Customer.customer_id).order_by(Customer.customer_id)
            )
        )

    def link(self, namespace: str, source_record_id: str) -> str:
        anchors = self.anchor_customer_ids()
        if not anchors:
            return build_customer_id(namespace, source_record_id)
        index = int(stable_hash(f"{namespace}|{source_record_id}", 12), 16) % len(
            anchors
        )
        return anchors[index]
