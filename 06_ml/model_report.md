\# Week 5 — Machine Learning Model Report



\## 1. Objective



The objective of this week's machine learning work is to build a baseline

binary classification model that predicts whether an eligible customer

will make at least one completed purchase during the defined future

prediction window.



The project label is named `repeat\_purchase`.



The formal target definition is:



\- `repeat\_purchase = 1` if the customer has at least one completed

&#x20; transaction during the future prediction window.

\- `repeat\_purchase = 0` otherwise.



Although the project label is called `repeat\_purchase`, the target is

formally defined by future completed-purchase behavior.



\---



\## 2. Prediction Setup



\### Historical cutoff



2026-05-24 00:00:00



\### Prediction window



2026-05-24 00:00:00 < transaction\_date <= 2026-08-22 00:00:00



\### Eligible customers



Customers whose signup date was on or before the historical cutoff.



\### Dataset size



84 eligible customers.



\### Target distribution



| Target | Count | Percentage |

|---|---:|---:|

| 0 — No future purchase | 51 | 60.71% |

| 1 — Future purchase | 33 | 39.29% |



The prediction target is therefore binary classification.



\---



\## 3. Leakage Prevention



The feature dataset was constructed so that predictive features only use

information available on or before the historical cutoff.



Future transactions are used only to construct the target.



The following types of future information were excluded from the feature

set:



\- Future completed purchases

\- Future transaction revenue

\- Future transaction status

\- Future orders

\- Future events

\- Future purchase counts

\- Any feature calculated using the complete dataset rather than the

&#x20; historical cutoff



The feature engineering process therefore follows a temporal prediction

setup:



Historical data → Features



Future data → Target



This separation is essential because using future information as a

predictive feature would cause target leakage.



\---



\## 4. Feature Engineering



The final feature dataset contains:



\- 84 customers

\- 24 columns

\- 21 predictive features

\- 1 target column

\- Customer identifiers and audit-related fields



\### Customer features



\- `country`

\- `status`

\- `customer\_tenure\_days`



\### Historical transaction features



\- `completed\_order\_count`

\- `completed\_revenue`

\- `average\_order\_value`

\- `last\_purchase\_date`

\- `days\_since\_last\_purchase`

\- `has\_previous\_purchase`

\- `total\_transaction\_count`

\- `failed\_transaction\_count`

\- `refunded\_transaction\_count`

\- `unique\_products\_purchased`

\- `unique\_categories\_purchased`



\### Historical event features



\- `total\_event\_count`

\- `product\_view\_count`

\- `add\_to\_cart\_count`

\- `checkout\_started\_count`

\- `search\_count`

\- `login\_count`

\- `purchase\_count`

\- `remove\_from\_cart\_count`



\### Target



\- `repeat\_purchase`



`customer\_id` was retained in the feature dataset for identification and

audit purposes but was excluded from model training.



`last\_purchase\_date` was also excluded from model training because it is a

raw date field. The derived `days\_since\_last\_purchase` feature was used

instead.



\---



\## 5. Missing Values



Missing values occurred only in:



\- `last\_purchase\_date`

\- `days\_since\_last\_purchase`



There were 10 customers without a previous completed purchase.



For these customers, the missing recency value is meaningful rather than

an accidental data error: there was no historical completed purchase from

which to calculate purchase recency.



The model therefore handles missing numerical values using median

imputation inside the preprocessing pipeline.



\---



\## 6. Logistic Regression Baseline



The first model was logistic regression.



\### Preprocessing



Numerical features:



\- Median imputation

\- StandardScaler



Categorical features:



\- Most-frequent imputation

\- One-hot encoding

\- `handle\_unknown="ignore"`



The preprocessing and model were combined into a single scikit-learn

Pipeline.



\### Model configuration



```python

LogisticRegression(

&#x20;   max\_iter=2000,

&#x20;   random\_state=42

)

