from __future__ import annotations

from sqlalchemy.orm import Session

from app.datasets.linker import SyntheticCustomerLinker
from app.datasets.types import (
    CanonicalBatch,
    CanonicalCustomerRecord,
    CanonicalLoanRecord,
    CanonicalProductRecord,
    CanonicalTransactionRecord,
    NormalizedRow,
)
from app.datasets.utils import (
    build_customer_id,
    clean_text,
    income_category,
    to_float,
    to_int,
)


class DatasetMapper:
    """Maps normalized public datasets into the canonical financial schema."""

    def __init__(self, session: Session) -> None:
        self.linker = SyntheticCustomerLinker(session)

    def map(self, dataset_name: str, rows: list[NormalizedRow]) -> CanonicalBatch:
        if dataset_name == "bank_customer_churn":
            return self._map_bank_churn(rows)
        if dataset_name == "credit_card_customers":
            return self._map_credit_card_customers(rows)
        if dataset_name == "loan_prediction":
            return self._map_loan_prediction(rows)
        if dataset_name == "paysim_transactions":
            return self._map_paysim(rows)
        msg = f"Unsupported dataset: {dataset_name}"
        raise ValueError(msg)

    def _map_bank_churn(self, rows: list[NormalizedRow]) -> CanonicalBatch:
        customers: list[CanonicalCustomerRecord] = []
        products: list[CanonicalProductRecord] = []

        for index, row in enumerate(rows):
            source_id = clean_text(row.get("customer_id")) or str(index)
            customer_id = build_customer_id("bank_customer_churn", source_id)
            salary = to_float(row.get("estimated_salary"))
            balance = to_float(row.get("balance"))
            products_count = to_int(row.get("num_of_products")) or 0

            customers.append(
                CanonicalCustomerRecord(
                    customer_id=customer_id,
                    full_name=clean_text(row.get("surname")),
                    gender=clean_text(row.get("gender")),
                    age=to_int(row.get("age")),
                    geography=clean_text(row.get("geography")),
                    education=None,
                    marital_status=None,
                    income_category=income_category(salary),
                    estimated_income=salary,
                    credit_score=to_int(row.get("credit_score")),
                    savings_balance=balance,
                    tenure_months=(to_int(row.get("tenure")) or 0) * 12,
                    source_dataset="bank_customer_churn",
                    source_record_id=source_id,
                    external_references={"customer_id": source_id},
                )
            )

            if to_int(row.get("has_cr_card")) == 1:
                products.append(
                    CanonicalProductRecord(
                        customer_id=customer_id,
                        product_type="Credit Card",
                        status="active",
                        credit_limit=None,
                        revolving_balance=None,
                        revenue=0.0,
                        source_dataset="bank_customer_churn",
                        source_record_id=f"{source_id}:credit_card",
                    )
                )

            for product_index in range(max(products_count - 1, 0)):
                products.append(
                    CanonicalProductRecord(
                        customer_id=customer_id,
                        product_type="Banking Product",
                        status="active",
                        credit_limit=None,
                        revolving_balance=None,
                        revenue=0.0,
                        source_dataset="bank_customer_churn",
                        source_record_id=f"{source_id}:product:{product_index}",
                    )
                )

        return CanonicalBatch(customers=customers, products=products)

    def _map_credit_card_customers(self, rows: list[NormalizedRow]) -> CanonicalBatch:
        customers: list[CanonicalCustomerRecord] = []
        products: list[CanonicalProductRecord] = []

        for index, row in enumerate(rows):
            source_id = clean_text(row.get("clientnum")) or str(index)
            customer_id = build_customer_id("credit_card_customers", source_id)
            credit_limit = to_float(row.get("credit_limit"))
            revolving_balance = to_float(row.get("total_revolving_bal"))
            revenue = (to_float(row.get("total_trans_amt")) or 0.0) * 0.015
            card_category = clean_text(row.get("card_category")) or "Credit"

            customers.append(
                CanonicalCustomerRecord(
                    customer_id=customer_id,
                    full_name=None,
                    gender=clean_text(row.get("gender")),
                    age=to_int(row.get("customer_age")),
                    geography=None,
                    education=clean_text(row.get("education_level")),
                    marital_status=clean_text(row.get("marital_status")),
                    income_category=clean_text(row.get("income_category")),
                    estimated_income=self._income_midpoint(row.get("income_category")),
                    credit_score=None,
                    savings_balance=None,
                    tenure_months=to_int(row.get("months_on_book")),
                    source_dataset="credit_card_customers",
                    source_record_id=source_id,
                    external_references={"clientnum": source_id},
                )
            )
            products.append(
                CanonicalProductRecord(
                    customer_id=customer_id,
                    product_type=f"{card_category} Card",
                    status=(
                        "active"
                        if row.get("attrition_flag") == "Existing Customer"
                        else "inactive"
                    ),
                    credit_limit=credit_limit,
                    revolving_balance=revolving_balance,
                    revenue=round(revenue, 2),
                    source_dataset="credit_card_customers",
                    source_record_id=f"{source_id}:card",
                )
            )

        return CanonicalBatch(customers=customers, products=products)

    def _map_loan_prediction(self, rows: list[NormalizedRow]) -> CanonicalBatch:
        customers: list[CanonicalCustomerRecord] = []
        loans: list[CanonicalLoanRecord] = []

        for index, row in enumerate(rows):
            source_id = clean_text(row.get("loan_id")) or str(index)
            customer_id = self.linker.link("loan_prediction", source_id)
            income = (to_float(row.get("applicant_income")) or 0.0) + (
                to_float(row.get("coapplicant_income")) or 0.0
            )
            loan_amount = (to_float(row.get("loan_amount")) or 0.0) * 1000

            customers.append(
                CanonicalCustomerRecord(
                    customer_id=customer_id,
                    full_name=None,
                    gender=clean_text(row.get("gender")),
                    age=None,
                    geography=clean_text(row.get("property_area")),
                    education=clean_text(row.get("education")),
                    marital_status=clean_text(row.get("married")),
                    income_category=income_category(income),
                    estimated_income=income,
                    credit_score=None,
                    savings_balance=None,
                    tenure_months=None,
                    source_dataset="loan_prediction",
                    source_record_id=source_id,
                    external_references={"loan_id": source_id},
                )
            )
            loans.append(
                CanonicalLoanRecord(
                    customer_id=customer_id,
                    loan_type="Home Loan",
                    amount=loan_amount,
                    term_months=to_int(row.get("loan_amount_term")),
                    status="approved" if row.get("loan_status") == "Y" else "rejected",
                    credit_history=to_float(row.get("credit_history")),
                    property_area=clean_text(row.get("property_area")),
                    source_dataset="loan_prediction",
                    source_record_id=source_id,
                )
            )

        return CanonicalBatch(customers=customers, loans=loans)

    def _map_paysim(self, rows: list[NormalizedRow]) -> CanonicalBatch:
        transactions: list[CanonicalTransactionRecord] = []

        for index, row in enumerate(rows):
            origin = clean_text(row.get("name_orig")) or f"origin-{index}"
            destination = clean_text(row.get("name_dest"))
            transaction_type = clean_text(row.get("type")) or "UNKNOWN"
            amount = to_float(row.get("amount")) or 0.0
            customer_id = self.linker.link("paysim_transactions", origin)

            transactions.append(
                CanonicalTransactionRecord(
                    customer_id=customer_id,
                    step=to_int(row.get("step")),
                    transaction_type=transaction_type,
                    category=self._transaction_category(transaction_type),
                    direction=self._transaction_direction(transaction_type),
                    amount=amount,
                    description=f"PaySim {transaction_type.title()} transaction",
                    counterparty=destination,
                    is_fraud=to_int(row.get("is_fraud")) or 0,
                    source_dataset="paysim_transactions",
                    source_record_id=f"{origin}:{index}:{transaction_type}:{amount}",
                )
            )

        return CanonicalBatch(transactions=transactions)

    def _income_midpoint(self, category: str | None) -> float | None:
        normalized = clean_text(category)
        if normalized is None or normalized == "Unknown":
            return None
        mapping = {
            "Less than $40K": 30000.0,
            "$40K - $60K": 50000.0,
            "$60K - $80K": 70000.0,
            "$80K - $120K": 100000.0,
            "$120K +": 150000.0,
        }
        return mapping.get(normalized)

    def _transaction_category(self, transaction_type: str) -> str:
        categories = {
            "PAYMENT": "Payments",
            "TRANSFER": "Transfers",
            "CASH_OUT": "Cash Withdrawal",
            "CASH_IN": "Cash Deposit",
            "DEBIT": "Debit",
        }
        return categories.get(transaction_type.upper(), "Other")

    def _transaction_direction(self, transaction_type: str) -> str:
        if transaction_type.upper() == "CASH_IN":
            return "credit"
        return "debit"
