# Training Pipeline

## Risk Prediction

Pipeline:

1. Load latest feature snapshots
2. Build typed feature matrix
3. Generate deterministic risk labels
4. Train/test split
5. Median imputation
6. Standard scaling
7. Random Forest training
8. Evaluation
9. Artifact persistence
10. Model registry registration

Evaluation stores:

- Accuracy
- Precision
- Recall
- F1
- Classification report
- Confusion matrix
- ROC AUC when valid
- Feature importance
- Training time

## Segmentation

Pipeline:

1. Load latest feature snapshots
2. Build typed feature matrix
3. Median imputation
4. Standard scaling
5. KMeans clustering
6. Cluster evaluation
7. Business-label assignment
8. Artifact persistence
9. Model registry registration

Business labels:

- Premium
- High Value
- Budget
- Young Investors
- Loan Focused

Raw cluster numbers are internal and are not exposed to the UI.
