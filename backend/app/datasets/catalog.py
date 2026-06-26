from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetDefinition:
    name: str
    display_name: str
    source: str
    filename: str
    version: str
    required_columns: tuple[str, ...]
    sample_rows: int | None = None


DATASET_CATALOG: tuple[DatasetDefinition, ...] = (
    DatasetDefinition(
        name="bank_customer_churn",
        display_name="Bank Customer Churn",
        source="https://raw.githubusercontent.com/selva86/datasets/master/Churn_Modelling.csv",
        filename="bank_customer_churn.csv",
        version="public-github-selva86-2026-06",
        required_columns=(
            "CustomerId",
            "CreditScore",
            "Geography",
            "Gender",
            "Age",
            "Tenure",
            "Balance",
            "NumOfProducts",
            "HasCrCard",
            "IsActiveMember",
            "EstimatedSalary",
        ),
    ),
    DatasetDefinition(
        name="loan_prediction",
        display_name="Loan Prediction",
        source=(
            "https://raw.githubusercontent.com/shrikant-temburwar/"
            "Loan-Prediction-Dataset/master/train.csv"
        ),
        filename="loan_prediction.csv",
        version="public-github-shrikant-temburwar-2026-06",
        required_columns=(
            "Loan_ID",
            "Gender",
            "Married",
            "Education",
            "ApplicantIncome",
            "LoanAmount",
            "Loan_Amount_Term",
            "Credit_History",
            "Property_Area",
            "Loan_Status",
        ),
    ),
    DatasetDefinition(
        name="credit_card_customers",
        display_name="Credit Card Customers",
        source=(
            "https://raw.githubusercontent.com/amoghkori/"
            "Credit-Card-Customer-Churn/main/BankChurners.csv"
        ),
        filename="credit_card_customers.csv",
        version="public-github-amoghkori-2026-06",
        required_columns=(
            "CLIENTNUM",
            "Attrition_Flag",
            "Customer_Age",
            "Gender",
            "Income_Category",
            "Card_Category",
            "Months_on_book",
            "Credit_Limit",
            "Total_Revolving_Bal",
            "Total_Trans_Amt",
            "Total_Trans_Ct",
        ),
        sample_rows=3000,
    ),
    DatasetDefinition(
        name="paysim_transactions",
        display_name="PaySim Transactions Sample",
        source="https://huggingface.co/datasets/theman10/paysim/resolve/main/paysim.csv",
        filename="paysim_transactions_sample.csv",
        version="public-huggingface-theman10-sample-2026-06",
        required_columns=(
            "step",
            "type",
            "amount",
            "nameOrig",
            "oldbalanceOrg",
            "newbalanceOrig",
            "nameDest",
            "oldbalanceDest",
            "newbalanceDest",
            "isFraud",
        ),
        sample_rows=2500,
    ),
)


def get_dataset_definition(name: str) -> DatasetDefinition:
    for definition in DATASET_CATALOG:
        if definition.name == name:
            return definition
    msg = f"Unknown dataset: {name}"
    raise ValueError(msg)
