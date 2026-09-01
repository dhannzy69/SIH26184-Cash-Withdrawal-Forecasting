SIH26184 Synthetic Prototype Dataset
====================================

This dataset is SYNTHETIC and intended only for a hackathon prototype/demo.
It is NOT real banking, cybercrime, ATM, police, or I4C data.

Files
-----
cases.csv         : cybercrime complaint/case records
accounts.csv      : victim and synthetic mule-account records
transactions.csv  : synthetic account-to-account fund transfers
locations.csv     : synthetic/demo ATM location clusters
withdrawals.csv   : historical outcome labels (where a cash-out occurred)

Recommended modelling formulation
----------------------------------
Create case-location examples at a prediction time T. Only information
available at or before T should be used as model features. The eventual
withdrawal location/time in withdrawals.csv should be used only to create
the target label for training/evaluation.

Important limitation
--------------------
Because the data is synthetic, model performance on this dataset does not
establish real-world predictive accuracy. Use it to demonstrate the
architecture, feature engineering, model training, ranking, evaluation,
and dashboard workflow.
