from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.canonical import Transaction
from app.models.intelligence import TransactionInsight
from app.nlp.behaviour.indicators import LifestyleIndicatorExtractor
from app.nlp.classification.rules import TransactionClassifier
from app.nlp.entities.extractor import EntityExtractor
from app.nlp.preprocessing.text import TransactionTextPreprocessor
from app.nlp.sentiment.rules import SentimentAnalyzer

NLP_PROCESSING_VERSION = "nlp_rules_v1"


@dataclass(frozen=True)
class TransactionInsightResult:
    transaction: Transaction
    insight: TransactionInsight
    classification_reason: str


class TransactionIntelligencePipeline:
    """Runs deterministic transaction NLP and persists insights."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.preprocessor = TransactionTextPreprocessor()
        self.classifier = TransactionClassifier()
        self.entities = EntityExtractor()
        self.sentiment = SentimentAnalyzer()
        self.indicators = LifestyleIndicatorExtractor()

    def process_transaction(
        self,
        transaction: Transaction,
    ) -> TransactionInsightResult:
        started = perf_counter()
        cleaned = self.preprocessor.clean(transaction.description)
        normalized = self.preprocessor.normalize(cleaned)
        classification = self.classifier.classify(transaction, normalized)
        extracted_entities = self.entities.extract(transaction, normalized)
        sentiment = self.sentiment.analyze(
            transaction,
            normalized,
            classification.category,
        )
        lifestyle = self.indicators.extract(transaction, classification.category)
        keywords = self.preprocessor.keywords(
            cleaned,
            transaction.transaction_type,
            transaction.category,
            classification.category,
        )
        processing_time_ms = round((perf_counter() - started) * 1000, 3)
        existing = self.session.scalar(
            select(TransactionInsight).where(
                TransactionInsight.transaction_id == transaction.id
            )
        )
        payload: dict[str, Any] = {
            "transaction_id": transaction.id,
            "customer_id": transaction.customer_id,
            "raw_description": transaction.description,
            "cleaned_description": cleaned,
            "normalized_description": normalized,
            "keywords": keywords,
            "entities": {
                **extracted_entities,
                "classification_reason": classification.reason,
            },
            "category": classification.category,
            "sentiment_label": sentiment.label,
            "sentiment_score": sentiment.score,
            "lifestyle_indicators": lifestyle,
            "processing_version": NLP_PROCESSING_VERSION,
            "processing_time_ms": processing_time_ms,
        }
        if existing is None:
            insight = TransactionInsight(**payload)
            self.session.add(insight)
        else:
            insight = existing
            for key, value in payload.items():
                setattr(insight, key, value)
        self.session.flush()
        return TransactionInsightResult(
            transaction=transaction,
            insight=insight,
            classification_reason=classification.reason,
        )

    def process_customer(self, customer_id: str) -> list[TransactionInsightResult]:
        transactions = list(
            self.session.scalars(
                select(Transaction)
                .where(Transaction.customer_id == customer_id)
                .order_by(Transaction.id)
            )
        )
        results = [
            self.process_transaction(transaction) for transaction in transactions
        ]
        self.session.commit()
        return results

    def process_all(self) -> int:
        transactions = list(
            self.session.scalars(select(Transaction).order_by(Transaction.id))
        )
        for transaction in transactions:
            self.process_transaction(transaction)
        self.session.commit()
        return len(transactions)
