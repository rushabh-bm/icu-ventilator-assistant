def get_ventilation_guidelines(condition):
    guidelines = {
        "ARDS": [
            "Use low tidal volume ventilation (4–6 mL/kg PBW)",
            "Maintain plateau pressure <30 cmH₂O",
            "Apply PEEP per ARDSNet table"
        ],
        "COPD": [
            "Lower respiratory rate (10–14 bpm)",
            "Use I:E ratio of 1:3 or greater",
            "Allow permissive hypercapnia, monitor for auto-PEEP"
        ],
        "Restrictive": [
            "Tidal volume: 4–6 mL/kg",
            "Higher RR: 20–30 bpm",
            "Monitor lung compliance closely"
        ],
        "Head Injury": [
            "Keep PaCO₂ around 35 mmHg",
            "Avoid high PEEP; control ICP",
            "Prevent hypoxia and hypercapnia"
        ],
        "Weaning": [
            "Spontaneous RR < 35",
            "SpO₂ > 90% on <40% FiO₂",
            "RSBI < 105",
            "Negative Inspiratory Force < -20 cmH₂O"
        ]
    }
    return guidelines.get(condition, ["No guideline available."])
