# -----------------------------
# Quantity Class
# -----------------------------
class Quantity:
    def __init__(self, name, value, unit):
        # Always store names in lowercase for consistent lookups
        self.name = name.lower()
        self.value = value
        self.unit = unit

    def __repr__(self):
        return f"{self.name.capitalize()}: {self.value} {self.unit}"


# -----------------------------
# Formula Class
# -----------------------------
class Formula:
    def __init__(self, name, inputs, output, expression, formula_text):
        self.name = name
        # Normalize all formula inputs and outputs to lowercase
        self.inputs = [i.lower() for i in inputs]
        self.output = output.lower()
        self.expression = expression
        self.formula_text = formula_text  # NEW ATTRIBUTE

    def can_compute(self, given_inputs):
        return all(inp in given_inputs for inp in self.inputs)

    def compute(self, values):
        return self.expression(*[values[inp] for inp in self.inputs])


# -----------------------------
# Unit Converter Class
# -----------------------------
class UnitConverter:
    @staticmethod
    def convert(quantity, value):
        conversions = {}
        # Ensure the quantity check is lowercase
        q = quantity.lower()

        if q == "speed":
            conversions["m/s"] = value
            conversions["km/h"] = value * 3.6
        elif q == "area":
            conversions["mm^2"] = value * 1E+6
            conversions["cm^2"] = value * 1E+4
            conversions["m^2"] = value
        elif q == "distance":
            conversions["m"] = value
            conversions["km"] = value / 1000
            conversions["cm"] = value * 100
        elif q == "time":
            conversions["s"] = value
            conversions["min"] = value / 60
            conversions["hr"] = value / 3600
        elif q == "pressure":
            conversions["Pa"] = value
            conversions["kPa"] = value / 1000
        elif q == "force" or q == "weight":
            conversions["N"] = value
        elif q == "acceleration":
            conversions["m/(s^2)"] = value

        return conversions


# -----------------------------
# Physics Calculator Class
# -----------------------------
class PhysicsCalculator:
    def __init__(self):
        self.quantities = {}
        self.formulas = self._load_formulas()

    def _load_formulas(self):
        # Standardized all strings to lowercase for logic matching
        return [
            Formula("Speed", ["distance", "time"], "speed", lambda d, t: d / t, "speed = distance / time"),
            Formula("Distance", ["speed", "time"], "distance", lambda s, t: s * t, "distance = speed × time"),
            Formula("Time", ["distance", "speed"], "time", lambda d, s: d / s, "time = distance / speed"),
            Formula("Density", ["mass", "volume"], "density", lambda m, v: m / v, "density = mass / volume"),
            Formula("Mass from Density", ["density", "volume"], "mass", lambda d, v: d * v, "mass = density × volume"),
            Formula("Volume", ["density", "mass"], "volume", lambda d, m: m / d, "volume = mass / density"),
            Formula("Pressure", ["force", "area"], "pressure", lambda f, a: f / a, "pressure = force / area"),
            Formula("Force from Pressure", ["pressure", "area"], "force", lambda p, a: p * a, "force = pressure × area"),
            Formula("Area", ["force", "pressure"], "area", lambda f, p: f / p, "area = force / pressure"),
            Formula("Work", ["force", "distance"], "work", lambda f, d: f * d, "work = force × distance"),
            Formula("Power", ["work", "time"], "power", lambda w, t: w / t, "power = work / time"),
            Formula("Force from Newton's 2nd Law", ["mass", "acceleration"], "force", lambda m, a: m * a, "force = mass × acceleration"),
            Formula("Mass from Force", ["force", "acceleration"], "mass", lambda f, a: f / a, "mass = force / acceleration"),
            Formula("Acceleration", ["mass", "force"], "acceleration", lambda m, f: f / m, "acceleration = force / mass"),
            Formula("Weight", ["mass", "gravity"], "weight", lambda m, g: m * g, "weight = mass × gravity"),
            Formula("Mass from Weight", ["weight", "gravity"], "mass", lambda w, g: w / g, "mass = weight / gravity"),
            Formula("Gravity", ["mass", "weight"], "gravity", lambda m, w: w / m, "gravity = weight / mass"),
        ]

    def add_quantity(self, name, value, unit):
        self.quantities[name.lower()] = value

    def suggest_computable(self):
        suggestions = []
        for formula in self.formulas:
            if formula.can_compute(self.quantities):
                if formula.output not in suggestions:
                    suggestions.append(formula.output)
        return suggestions

    # NEW METHOD
    def suggest_computable_with_formulas(self):
        results = []
        for formula in self.formulas:
            if formula.can_compute(self.quantities):
                results.append(formula)
        return results

    def compute(self, target):
        target = target.lower()
        for formula in self.formulas:
            if formula.output == target and formula.can_compute(self.quantities):
                return formula.compute(self.quantities)
        return None    



import streamlit as st

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f7f9fc;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
<style>

body, .stApp {
    color: inherit;
}

input, textarea {
    border-radius: 8px !important;
}

.stButton > button {
    border-radius: 8px;
    border: 1px solid rgba(128,128,128,0.4);
    padding: 0.5rem 1rem;
}

.stButton > button:hover {
    border-color: rgba(128,128,128,0.7);
}

</style>
""", unsafe_allow_html=True)

# Page settings
st.set_page_config(page_title="Little Calc Lab", layout="centered")

# Keep calculator persistent
if "calc" not in st.session_state:
    st.session_state.calc = PhysicsCalculator()

calc = st.session_state.calc

# ---------------- UI ----------------

st.title("Little Calc Lab")
st.caption("Physics Numerical Solver - Class 7 & 8")

# =========================
# 1. Enter Given Data
# =========================

st.subheader("Enter Given Data")

col1, col2, col3 = st.columns(3)

with col1:
    name = st.text_input("Quantity name")

with col2:
    value = st.number_input("Value")

with col3:
    unit = st.text_input("Unit")

if st.button("Add Data"):
    if name:
        calc.add_quantity(name, value, unit)
        st.success(f"Added {name}")
    else:
        st.warning("Enter quantity name")

# =========================
# 2. Show Computable Quantities
# =========================

st.subheader("Show Computable Quantities")

if st.button("Show Computable"):
    sug = calc.suggest_computable()

    if sug:
        st.write(", ".join(sug))

        # show formulas like your main()
        formulas = calc.suggest_computable_with_formulas()
        for formula in formulas:
            st.write(f"{formula.output.capitalize()} → {formula.formula_text}")
    else:
        st.write("None")

# =========================
# 3. Calculate
# =========================

st.subheader("Calculate")

target = st.text_input("Which quantity to compute?")

if st.button("Compute"):
    res = calc.compute(target)

    if res is not None:
        st.success(f"Result: {res}")

        convs = UnitConverter.convert(target, res)

        for u, v in convs.items():
            st.write(f"{v:.4f} {u}")

        if target.lower() == "acceleration":
            st.write("Unit is m/(s²)")
    else:
        st.warning("Missing data for that calculation.")
