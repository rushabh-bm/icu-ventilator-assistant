from typing import List

def get_ventilation_guidelines(condition: str) -> List[str]:
    # Normalize input (case insensitive, strip whitespace)
    cond = condition.strip().lower()

    guidelines = {
        "ards": [
            "Use low tidal volume ventilation (4–6 mL/kg predicted body weight) to reduce ventilator-induced lung injury.",
            "Maintain plateau pressure below 30 cmH₂O to avoid barotrauma.",
            "Apply PEEP according to ARDSNet table to optimize alveolar recruitment without overdistension.",
            "Consider prone positioning if PaO₂/FiO₂ < 150 for at least 12-16 hours per day."
        ],
        "copd": [
            "Use lower respiratory rate (10–14 breaths per minute) to allow longer expiratory time.",
            "Set I:E ratio ≥ 1:3 to prevent air trapping and auto-PEEP.",
            "Allow permissive hypercapnia to avoid high airway pressures, monitor for dynamic hyperinflation.",
            "Use bronchodilators and optimize sedation to facilitate ventilation."
        ],
        "restrictive": [
            "Use low tidal volumes (4–6 mL/kg) to prevent volutrauma.",
            "Increase respiratory rate (20–30 breaths per minute) to maintain minute ventilation.",
            "Closely monitor lung compliance and plateau pressures.",
            "Adjust PEEP cautiously based on oxygenation and lung mechanics."
        ],
        "head injury": [
            "Maintain PaCO₂ around 35 mmHg to optimize cerebral blood flow and reduce intracranial pressure (ICP).",
            "Avoid high PEEP as it can increase ICP.",
            "Prevent hypoxia and hypercapnia to protect brain tissue.",
            "Monitor neurological status and consider sedation to minimize agitation."
        ],
        "weaning": [
            "Ensure spontaneous respiratory rate is less than 35 breaths per minute.",
            "Maintain SpO₂ above 90% on less than 40% FiO₂.",
            "Rapid Shallow Breathing Index (RSBI) should be less than 105 breaths/min/L.",
            "Negative Inspiratory Force (NIF) should be more negative than -20 cmH₂O, indicating sufficient respiratory muscle strength.",
            "Perform spontaneous breathing trials and assess readiness frequently."
        ]
    }

    if cond == "list" or cond == "":
        return ["Supported conditions: " + ", ".join(sorted(guidelines.keys()))]

    return guidelines.get(cond, ["No specific ventilation guideline available. Please consult clinical protocols."])


