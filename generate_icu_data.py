import pandas as pd
import numpy as np

def simulate_icu_data(num_samples=1000):
    np.random.seed(42)

    weight = np.random.normal(70, 15, num_samples).clip(40, 150)  # kg
    height = np.random.normal(170, 10, num_samples).clip(140, 200)  # cm
    bmi = weight / ((height / 100) ** 2)

    data = {
        'Weight': weight,
        'Height': height,
        'BMI': bmi,
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

    # Target with improved formula incorporating weight and BMI effects
    df['TV_recommendation'] = (
        df['TV_previous'] +
        (100 - df['SpO2']) * 1.5 +
        (7.4 - df['pH']) * 100 +
        (df['PaCO2'] - 40) * 2 +
        (df['Weight'] - 70) * 0.5 +       # weight effect
        (22 - df['BMI']) * 5 +            # BMI effect, assuming 22 ideal
        np.random.normal(0, 10, num_samples)
    ).clip(300, 600)

    df.to_csv("icu_simulated_data.csv", index=False)
    print("✅ Simulated ICU data saved to icu_simulated_data.csv")

if __name__ == "__main__":
    simulate_icu_data()
