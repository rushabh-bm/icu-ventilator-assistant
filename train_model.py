
import joblib
import shap
import matplotlib.pyplot as plt
import os


import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
# Load updated data
df = pd.read_csv("icu_simulated_data.csv")

X = df.drop(columns=["TV_recommendation"])
y = df["TV_recommendation"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f" MAE: {mae:.2f} ml")
print(f" R2 Score: {r2:.2f}")

joblib.dump(model, "tv_predictor_model.pkl")
print(" Model saved as tv_predictor_model.pkl")

# SHAP explainability
explainer = shap.Explainer(model.predict, X_train)
shap_values = explainer(X_test[:100])

shap.summary_plot(shap_values, X_test[:100], show=False)
plt.savefig("shap_summary_plot.png")
print(" SHAP summary plot saved as shap_summary_plot.png")
