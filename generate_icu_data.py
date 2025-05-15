import pandas as pd
import numpy as np

def simulate_icu_data(num_samples=1000):
    np.random.seed(42)

    data = {
        'HeartRate': np.random.normal(85, 10, num_samples).clip(60, 130),
        'SpO2': np.random.normal(95, 2, num_samples).clip(85, 100),
        'RespiratoryRate': np.random.normal(20, 5, num_samples).clip(10, 40),
        'pH': np.random.normal(7.4, 0.05, num_samples).clip(7.2, 7.6),
        'PaO2': np.random.normal(80, 15, num_samples).clip(50, 200),
        'PaCO2': np.random.normal(40, 5, num_samples).clip(20, 70),
        'TV_previous': np.random.normal(450, 50, num_samples).clip(300, 600),
        'PEEP_previous': np.random.normal(5, 1, num_samples).clip(3, 10),
    }

    df = pd.DataFrame(data)

    # Simulated target: optimal TV based on some formula + noise
    df['TV_recommendation'] = (
        df['TV_previous'] +
        (100 - df['SpO2']) * 1.5 +
        (7.4 - df['pH']) * 100 +
        (df['PaCO2'] - 40) * 2 +
        np.random.normal(0, 10, num_samples)
    ).clip(300, 600)

    df.to_csv("icu_simulated_data.csv", index=False)
    print("✅ Simulated ICU data saved to icu_simulated_data.csv")

if __name__ == "__main__":
    simulate_icu_data()
