import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib

# Load data
df = pd.read_csv("icu_simulated_data.csv")

X = df.drop("TV_recommendation", axis=1)
y = df["TV_recommendation"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save model
joblib.dump(model, "tv_predictor_model.pkl")
print("✅ Model trained and saved as tv_predictor_model.pkl")
