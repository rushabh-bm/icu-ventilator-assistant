from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
import os

app = FastAPI()

# Load model
model = joblib.load("tv_predictor_model.pkl")


class ICUInput(BaseModel):
    HeartRate: float
    SpO2: float
    RespiratoryRate: float
    pH: float
    PaO2: float
    PaCO2: float
    TV_previous: float
    PEEP_previous: float

@app.post("/predict_tv")
def predict_tv(data: ICUInput):
    input_data = np.array([
        data.HeartRate, data.SpO2, data.RespiratoryRate, data.pH,
        data.PaO2, data.PaCO2, data.TV_previous, data.PEEP_previous
    ]).reshape(1, -1)

    prediction = model.predict(input_data)[0]
    result = round(prediction, 2)

    # Logging to CSV
    log_data = {
        "HeartRate": data.HeartRate,
        "SpO2": data.SpO2,
        "RespiratoryRate": data.RespiratoryRate,
        "pH": data.pH,
        "PaO2": data.PaO2,
        "PaCO2": data.PaCO2,
        "TV_previous": data.TV_previous,
        "PEEP_previous": data.PEEP_previous,
        "Predicted_TV": result
    }
    df = pd.DataFrame([log_data])
    if not os.path.exists("icu_log.csv"):
        df.to_csv("icu_log.csv", index=False)
    else:
        df.to_csv("icu_log.csv", mode='a', index=False, header=False)

    return {"recommended_tidal_volume": result}
