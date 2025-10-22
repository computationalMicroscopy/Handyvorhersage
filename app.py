#%%writefile app.py
import streamlit as st
import random
from collections import Counter

# Eingangsknoten definieren
alter = {"2539":0.05, "4054":0.7,"5567":0.25} #Eingabe der Wahrscheinlichkeiten für Alterintervalle (2539 ->25 Jahre bis 39 Jahre)
einkommen = {"viel":0.7,"wenig":0.3}

kaufentscheidung = {
    ("2539","viel"):{"Apple":0.85,"Android":0.15}, # Slightly less extreme for high income young
    ("2539","wenig"):{"Apple":0.3,"Android":0.7}, # More likely to choose Android with low income
    ("4054","viel"):{"Apple":0.7,"Android":0.3}, # Still leaning Apple with high income, but less so than younger group
    ("4054","wenig"):{"Apple":0.2,"Android":0.8}, # Strong preference for Android with low income in this age group
    ("5567","viel"):{"Apple":0.9,"Android":0.1}, # High income older users still strongly prefer Apple
    ("5567","wenig"):{"Apple":0.1,"Android":0.9} # Very strong preference for Android with low income older users
}

def sampleAlter(alter_probs):
  r = random.random()
  if (r < alter_probs['2539']):
    return "2539"
  if (r < alter_probs['2539'] + alter_probs['4054']):
    return "4054"
  else:
    return "5567"

def sampleEinkommen(einkommen_probs):
  r = random.random()
  if(r < einkommen_probs['viel']):
    return "viel"
  else:
    return "wenig"

def sampleKaufentscheidung(alter, einkommen, kaufentscheidung_probs):
  sample = []
  r = random.random()
  sample.append(alter)
  sample.append(einkommen)
  if (r < kaufentscheidung_probs[(alter, einkommen)]['Apple']):
    sample.append("Apple")
    return sample
  else:
    sample.append("Android")
    return sample


def forwardsampling(noSamples, alter_probs, einkommen_probs, kaufentscheidung_probs):
  sampleset = [] # Initialize sampleset within the function to avoid global variable issues in Streamlit
  for i in range(noSamples):
    alter_sample = sampleAlter(alter_probs)
    einkommen_sample = sampleEinkommen(einkommen_probs)
    sampleset.append(sampleKaufentscheidung(alter_sample, einkommen_sample, kaufentscheidung_probs))
  return sampleset

# Streamlit App Interface

st.set_page_config(layout="wide", page_title="Bayessches Netzwerk Kaufentscheidung") # Use wide layout and set page title

st.title("📱 Bayessches Netzwerk für Kaufentscheidungen")

st.markdown("""
Diese interaktive App simuliert ein bayessches Netzwerk, um Kaufentscheidungen (Apple oder Android) basierend auf Alter und Einkommen vorherzusagen.
Verwenden Sie die Seitenleiste, um die Wahrscheinlichkeitsverteilungen für Alter und Einkommen sowie die Anzahl der Stichproben für die Simulation anzupassen.
Klicken Sie auf "Simulation starten", um die vorhergesagten Kaufwahrscheinlichkeiten zu sehen.
""")

st.sidebar.header("Eingabe der Wahrscheinlichkeitsverteilungen")

st.sidebar.subheader("🎂 Alter")
col1, col2, col3 = st.sidebar.columns(3)
with col1:
    age_2539 = st.slider("25-39 Jahre", 0.0, 1.0, 0.05, 0.01, key='age_2539')
with col2:
    age_4054 = st.slider("40-54 Jahre", 0.0, 1.0, 0.7, 0.01, key='age_4054')
with col3:
    age_5567 = st.slider("55-67 Jahre", 0.0, 1.0, 0.25, 0.01, key='age_5567')


# Ensure age probabilities sum to 1
total_age_prob = age_2539 + age_4054 + age_5567
if not (0.99 <= total_age_prob <= 1.01): # Allow for small floating point errors
    st.sidebar.warning(f"Die Alterswahrscheinlichkeiten ergeben zusammen nicht 1.0 (Aktuelle Summe: {total_age_prob:.2f}). Bitte anpassen.")
    # Normalize probabilities if they don't sum to 1
    if total_age_prob != 0:
        age_2539 /= total_age_prob
        age_4054 /= total_age_prob
        age_5567 /= total_age_prob
        st.sidebar.info(f"Wahrscheinlichkeiten normalisiert: 25-39={age_2539:.2f}, 40-54={age_4054:.2f}, 55-67={age_5567:.2f}")


st.sidebar.subheader("💰 Einkommen")
col4, col5 = st.sidebar.columns(2)
with col4:
    income_viel = st.slider("Hohes Einkommen", 0.0, 1.0, 0.7, 0.01, key='income_viel')
with col5:
    income_wenig = st.slider("Niedriges Einkommen", 0.0, 1.0, 0.3, 0.01, key='income_wenig')

# Ensure income probabilities sum to 1
total_income_prob = income_viel + income_wenig
if not (0.99 <= total_income_prob <= 1.01): # Allow for small floating point errors
    st.sidebar.warning(f"Die Einkommenswahrscheinlichkeiten ergeben zusammen nicht 1.0 (Aktuelle Summe: {total_income_prob:.2f}). Bitte anpassen.")
    # Normalize probabilities if they don't sum to 1
    if total_income_prob != 0:
        income_viel /= total_income_prob
        income_wenig /= total_income_prob
        st.sidebar.info(f"Wahrscheinlichkeiten normalisiert: Hohes Einkommen={income_viel:.2f}, Niedriges Einkommen={income_wenig:.2f}")


# Update the probability dictionaries with user input
alter_probs = {"2539": age_2539, "4054": age_4054, "5567": age_5567}
einkommen_probs = {"viel": income_viel, "wenig": income_wenig}

st.sidebar.subheader("📊 Simulationseinstellungen")
num_samples = st.sidebar.number_input("Anzahl der Stichproben", min_value=100, max_value=100000, value=1000, step=100)

# Run simulation and display results
if st.sidebar.button("Simulation starten"):
    st.subheader("✅ Simulationsergebnisse")
    sampleset = forwardsampling(num_samples, alter_probs, einkommen_probs, kaufentscheidung)

    # Count occurrences of purchase decisions
    purchase_counts = Counter(sample[2] for sample in sampleset)

    st.write("### Verteilung der Kaufentscheidungen:")
    col_apple, col_android = st.columns(2)
    with col_apple:
        st.info(f"🍎 Apple: {purchase_counts.get('Apple', 0)} Stichproben ({purchase_counts.get('Apple', 0)/num_samples:.2%})")
    with col_android:
        st.success(f"🤖 Android: {purchase_counts.get('Android', 0)} Stichproben ({purchase_counts.get('Android', 0)/num_samples:.2%})")


    st.write("### Detaillierte Verteilung nach Alter und Einkommen:")
    # Count occurrences of each combination in sampleset
    distribution = Counter(tuple(item) for item in sampleset)

    # Display the distribution in a more organized way
    age_groups = ["2539", "4054", "5567"]
    income_groups = ["viel", "wenig"]
    purchase_decisions = ["Apple", "Android"]

    for age_group in age_groups:
        st.write(f"#### Altersgruppe: {age_group}")
        for income_group in income_groups:
            st.write(f"**Einkommen:** {income_group}")
            col_detail_apple, col_detail_android = st.columns(2)
            for decision in purchase_decisions:
                key = (age_group, income_group, decision)
                count = distribution.get(key, 0)
                probability = count / num_samples
                if decision == "Apple":
                    with col_detail_apple:
                         st.info(f"🍎 {decision}: {count} Stichproben ({probability:.2%})")
                else:
                    with col_detail_android:
                        st.success(f"🤖 {decision}: {count} Stichproben ({probability:.2%})")
