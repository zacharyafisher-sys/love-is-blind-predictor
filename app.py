from flask import Flask, render_template, request, jsonify
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

app = Flask(__name__)

FEATURE_NAMES = [
    'p1_age', 'p1_emotional', 'p1_communication', 'p1_commitment',
    'p2_age', 'p2_emotional', 'p2_communication', 'p2_commitment',
    'physical_attraction', 'shared_values', 'conflict_frequency',
    'conflict_resolution', 'family_approval', 'emotional_connection',
    'lifestyle_compat', 'altar_pressure', 'age_diff'
]

FEATURE_LABELS = {
    'p1_emotional': "Person 1's emotional maturity",
    'p2_emotional': "Person 2's emotional maturity",
    'p1_communication': "Person 1's communication",
    'p2_communication': "Person 2's communication",
    'p1_commitment': "Person 1's commitment readiness",
    'p2_commitment': "Person 2's commitment readiness",
    'physical_attraction': "Physical attraction after reveal",
    'shared_values': "Shared values & life goals",
    'conflict_frequency': "Conflict frequency",
    'conflict_resolution': "Conflict resolution ability",
    'family_approval': "Family & friends approval",
    'emotional_connection': "Depth of emotional connection",
    'lifestyle_compat': "Lifestyle compatibility",
    'altar_pressure': "Doubt/pressure at the altar",
    'age_diff': "Age difference",
}


def generate_training_data(n_samples=3000):
    np.random.seed(42)

    p1_age = np.random.uniform(22, 45, n_samples)
    p2_age = np.random.uniform(22, 45, n_samples)
    p1_emotional = np.random.uniform(1, 5, n_samples)
    p2_emotional = np.random.uniform(1, 5, n_samples)
    p1_communication = np.random.uniform(1, 5, n_samples)
    p2_communication = np.random.uniform(1, 5, n_samples)
    p1_commitment = np.random.uniform(1, 5, n_samples)
    p2_commitment = np.random.uniform(1, 5, n_samples)
    physical_attraction = np.random.uniform(1, 5, n_samples)
    shared_values = np.random.uniform(1, 5, n_samples)
    conflict_frequency = np.random.uniform(1, 5, n_samples)
    conflict_resolution = np.random.uniform(1, 5, n_samples)
    family_approval = np.random.uniform(1, 5, n_samples)
    emotional_connection = np.random.uniform(1, 5, n_samples)
    lifestyle_compat = np.random.uniform(1, 5, n_samples)
    altar_pressure = np.random.uniform(1, 5, n_samples)
    age_diff = np.abs(p1_age - p2_age)

    # Weighted score reflecting Love Is Blind dynamics
    score = (
        0.13 * p1_emotional
        + 0.13 * p2_emotional
        + 0.10 * p1_communication
        + 0.10 * p2_communication
        + 0.07 * p1_commitment
        + 0.07 * p2_commitment
        + 0.09 * physical_attraction
        + 0.11 * shared_values
        + 0.10 * conflict_resolution
        + 0.09 * family_approval
        + 0.11 * emotional_connection
        + 0.07 * lifestyle_compat
        - 0.10 * conflict_frequency
        - 0.12 * altar_pressure
        - 0.015 * age_diff
        - 2.8  # bias keeps ~35% married rate (realistic for show)
    )

    score += np.random.normal(0, 0.35, n_samples)
    prob = 1 / (1 + np.exp(-score))
    y = (np.random.random(n_samples) < prob).astype(int)

    X = np.column_stack([
        p1_age, p1_emotional, p1_communication, p1_commitment,
        p2_age, p2_emotional, p2_communication, p2_commitment,
        physical_attraction, shared_values, conflict_frequency,
        conflict_resolution, family_approval, emotional_connection,
        lifestyle_compat, altar_pressure, age_diff
    ])

    return X, y


def train_model():
    X, y = generate_training_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model = GradientBoostingClassifier(
        n_estimators=300, max_depth=4, learning_rate=0.08,
        subsample=0.8, random_state=42
    )
    model.fit(X_train_s, y_train)
    acc = model.score(X_test_s, y_test)
    print(f"Model accuracy: {acc:.1%}  |  Marriage rate: {y.mean():.1%}")
    return model, scaler


print("Training Love Is Blind prediction model...")
model, scaler = train_model()


def get_confidence_label(prob):
    if prob > 0.80 or prob < 0.20:
        return "Very High"
    elif prob > 0.65 or prob < 0.35:
        return "High"
    elif prob > 0.55 or prob < 0.45:
        return "Moderate"
    else:
        return "Low (it's a close call!)"


def get_insights(data, prob):
    insights = []

    em_avg = (float(data['p1_emotional']) + float(data['p2_emotional'])) / 2
    comm_avg = (float(data['p1_communication']) + float(data['p2_communication'])) / 2
    commit_avg = (float(data['p1_commitment']) + float(data['p2_commitment'])) / 2

    if em_avg >= 4.0:
        insights.append(("strength", "Both partners show strong emotional maturity — a Love Is Blind essential."))
    elif em_avg < 2.5:
        insights.append(("warning", "Emotional maturity gaps may lead to avoidance and unresolved tension."))

    if comm_avg >= 4.0:
        insights.append(("strength", "Exceptional communication built in the pods — their foundation is solid."))
    elif comm_avg < 2.5:
        insights.append(("warning", "Poor communication could collapse the relationship before the altar."))

    if float(data['physical_attraction']) >= 4.0:
        insights.append(("strength", "Strong physical chemistry after the reveal keeps the spark alive."))
    elif float(data['physical_attraction']) < 2.5:
        insights.append(("warning", "Lack of physical attraction after the reveal is a serious hurdle."))

    if float(data['shared_values']) >= 4.0:
        insights.append(("strength", "Deep alignment on values and life goals builds a lasting bond."))
    elif float(data['shared_values']) < 2.5:
        insights.append(("warning", "Mismatched life goals are a common dealbreaker in this experiment."))

    if float(data['family_approval']) >= 4.0:
        insights.append(("strength", "Family and friends are on board — external support matters."))
    elif float(data['family_approval']) < 2.5:
        insights.append(("warning", "Family opposition has derailed many Love Is Blind couples."))

    if float(data['altar_pressure']) >= 4.0:
        insights.append(("warning", "High doubt at the altar often ends in a painful 'I don't.'"))

    if float(data['conflict_frequency']) >= 4.0:
        insights.append(("warning", "Frequent arguing without resolution is a red flag for longevity."))
    elif float(data['conflict_resolution']) >= 4.0 and float(data['conflict_frequency']) >= 3.0:
        insights.append(("strength", "They argue but know how to come back together — healthy conflict."))

    if commit_avg >= 4.0:
        insights.append(("strength", "Both are truly ready to commit — no cold feet here."))

    return insights[:5]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    try:
        p1_age = float(data['p1_age'])
        p1_emotional = float(data['p1_emotional'])
        p1_communication = float(data['p1_communication'])
        p1_commitment = float(data['p1_commitment'])

        p2_age = float(data['p2_age'])
        p2_emotional = float(data['p2_emotional'])
        p2_communication = float(data['p2_communication'])
        p2_commitment = float(data['p2_commitment'])

        physical_attraction = float(data['physical_attraction'])
        shared_values = float(data['shared_values'])
        conflict_frequency = float(data['conflict_frequency'])
        conflict_resolution = float(data['conflict_resolution'])
        family_approval = float(data['family_approval'])
        emotional_connection = float(data['emotional_connection'])
        lifestyle_compat = float(data['lifestyle_compat'])
        altar_pressure = float(data['altar_pressure'])

        age_diff = abs(p1_age - p2_age)

        features = np.array([[
            p1_age, p1_emotional, p1_communication, p1_commitment,
            p2_age, p2_emotional, p2_communication, p2_commitment,
            physical_attraction, shared_values, conflict_frequency,
            conflict_resolution, family_approval, emotional_connection,
            lifestyle_compat, altar_pressure, age_diff
        ]])

        features_scaled = scaler.transform(features)
        prediction = int(model.predict(features_scaled)[0])
        proba = model.predict_proba(features_scaled)[0]
        marriage_prob = float(proba[1])

        return jsonify({
            'prediction': prediction == 1,
            'marriage_probability': round(marriage_prob * 100, 1),
            'confidence': get_confidence_label(marriage_prob),
            'insights': get_insights(data, marriage_prob),
        })

    except (KeyError, ValueError) as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
