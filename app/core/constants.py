VITAL_CODES = {
    "blood_pressure_systolic": {
        "code": "8480-6",
        "display": "Systolic blood pressure",
        "unit": "mm[Hg]"
    },
    "blood_pressure_diastolic": {
        "code": "8462-4",
        "display": "Diastolic blood pressure",
        "unit": "mm[Hg]"
    },
    "heart_rate": {
        "code": "8867-4",
        "display": "Heart rate",
        "unit": "/min"
    },
    "body_temperature": {
        "code": "8310-5",
        "display": "Body temperature",
        "unit": "Cel"
    },
    "respiratory_rate": {
        "code": "9279-1",
        "display": "Respiratory rate",
        "unit": "/min"
    },
    "oxygen_saturation": {
        "code": "2708-6",
        "display": "Oxygen saturation",
        "unit": "%"
    },
    "body_weight": {
        "code": "29463-7",
        "display": "Body weight",
        "unit": "kg"
    },
    "body_height": {
        "code": "8302-2",
        "display": "Body height",
        "unit": "cm"
    },
    "bmi": {
        "code": "39156-5",
        "display": "Body mass index",
        "unit": "kg/m2"
    }
}

METHODS = {
    "automatic": "702869007",  # Automatic blood pressure reading
    "manual": "37931006",      # Manual blood pressure reading
    "auscultation": "113011001", # Auscultation
    "calculated": "703858009",  # Calculated
}

VALUE_RANGES = {
    "blood_pressure_systolic": (90, 180),
    "blood_pressure_diastolic": (60, 120),
    "heart_rate": (60, 100),
    "body_temperature": (36.0, 38.0),
    "respiratory_rate": (12, 20),
    "oxygen_saturation": (94, 100),
    "body_weight": (45.0, 120.0),
    "body_height": (150.0, 190.0),
    "bmi": (18.5, 35.0)
}