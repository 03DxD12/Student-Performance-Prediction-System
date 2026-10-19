import pickle

import pandas as pd
from sklearn.linear_model import LogisticRegression


df = pd.read_csv("student_data.csv")

X = df[["study_hours", "attendance", "previous_grade"]]
y = df["result"]

model = LogisticRegression()
model.fit(X, y)

pickle.dump(model, open("model.pkl", "wb"))
