# User Interaction Description

**Application:** Heating Systems Conversational Assistant
**Knowledge base:** Data Science for Residential Energy Systems (6K-line guide, 20 chapters)
**Users:** Engineers, data scientists, energy consultants, students exploring the residential heating domain
**Languages:** English and German (user chooses, agent responds in kind)

---

## How It Works

The user opens a Streamlit chat interface. The agent greets them and explains what it can help with. The user types (or speaks, if voice is enabled) a question in English or German. The agent classifies the intent, routes to the appropriate tool or retrieval pipeline, and responds with a grounded answer citing the source section.

Three interaction modes emerge naturally from the knowledge base:

1. **Ask** — Knowledge questions answered via RAG over the guide
2. **Calculate** — Deterministic calculations using domain tools
3. **Explore** — Guided navigation through related topics

The agent handles multi-turn conversations: follow-up questions, clarifications, topic shifts, and language switches mid-conversation.

---

## Interaction 1: Domain Knowledge Question (English)

A data scientist exploring heating systems for the first time.

```
User: What is a Heizkennlinie and why does it matter for ML?

Agent: A Heizkennlinie (heating curve) defines the relationship between outdoor
       temperature and the flow temperature (Vorlauftemperatur) supplied to a
       heating system. It has two key parameters:

       - **Slope (Neigung):** How steeply the flow temperature rises as outdoor
         temperature drops. Steeper slopes suit poorly insulated buildings.
       - **Parallel shift (Parallelverschiebung):** Shifts the entire curve up
         or down, adjusting the base comfort level.

       For ML, the heating curve is both a target and a feature:
       - **As a target:** Optimizing slope and shift per building reduces energy
         waste (Chapter 9: Control & Optimization).
       - **As a feature:** Deviations between actual flow temperature and the
         curve prediction signal anomalies or misconfiguration
         (Chapter 8: Anomaly Detection).

       Sources: Chapter 3 (Key Control Variables), Chapter 9 (Control &
       Optimization Algorithms)

User: How would I detect if the curve is misconfigured?

Agent: Two approaches from the guide:

       1. **Statistical:** Compare measured flow temperatures against the curve's
          expected output for each outdoor temperature reading. Persistent positive
          deviations (actual > expected) suggest the curve is set too high, wasting
          energy. Use z-score or IQR on the residuals (Chapter 8).

       2. **ML-based:** Train an Isolation Forest on (outdoor_temp, flow_temp,
          return_temp) tuples from a known-good period. New data points flagged
          as outliers may indicate curve drift or manual override
          (Chapter 8: Anomaly Detection).

       A practical signal: if the return temperature (Rücklauftemperatur) is
       consistently too high, the Spreizung (temperature spread) is too narrow,
       which often points to an overaggressive heating curve.

       Sources: Chapter 3 (Key Control Variables), Chapter 8 (Anomaly Detection)
```

---

## Interaction 2: Deterministic Calculation (German)

An energy engineer checking heating curve parameters for a building retrofit.

```
User: Berechne die Vorlauftemperatur für ein Gebäude Baujahr 1975,
      Außentemperatur -10°C, Heizkennlinie Neigung 1.8, Parallelverschiebung +2.

Agent: Berechnung der Vorlauftemperatur:

       Eingangsparameter:
       - Baujahr: 1975 (unsanierter Altbau, typisch Neigung 1.5-2.0)
       - Außentemperatur: -10°C
       - Neigung: 1.8
       - Parallelverschiebung: +2°C

       Ergebnis:
       - Vorlauftemperatur: 74.6°C
       - Rücklauftemperatur (geschätzt, Spreizung 15K): 59.6°C

       Hinweis: Eine Neigung von 1.8 ist plausibel für ein unsaniertes Gebäude
       von 1975. Nach einer Fassadendämmung (z.B. EnEV/GEG-Niveau) könnte die
       Neigung auf 1.0-1.2 reduziert werden, was die Vorlauftemperatur auf
       ca. 52°C senken würde, geeignet für Wärmepumpen-Betrieb.

       Quelle: Kapitel 3 (Heizkennlinie), DIN EN 12831

       [Tool: heating_curve_calculator]

User: Und wenn wir auf Wärmepumpe umstellen, welche Neigung wäre sinnvoll?

Agent: Für Wärmepumpen-Betrieb sind niedrige Vorlauftemperaturen entscheidend,
       da der COP (Coefficient of Performance) mit steigender Vorlauftemperatur
       sinkt.

       Empfehlung nach Sanierung auf GEG-Niveau:
       - Neigung: 0.8-1.2
       - Maximale Vorlauftemperatur: ≤55°C (Grenzwert für effiziente WP)

       Neuberechnung mit Neigung 1.0, Parallelverschiebung 0:
       - Vorlauftemperatur bei -10°C: 45.0°C
       - COP-Schätzung (Luft-Wasser-WP): ca. 2.8

       Voraussetzung: Hydraulischer Abgleich nach Verfahren B (raumweise
       Heizlastberechnung nach DIN EN 12831) und ggf. Heizkörpertausch.

       Quellen: Kapitel 2 (Heat Pumps), Kapitel 4 (Hydraulischer Abgleich),
       Kapitel 5 (Sektorkopplung)

       [Tool: heating_curve_calculator]
```

---

## Interaction 3: ML Architecture Guidance (English)

A data scientist designing a heat demand forecasting pipeline.

```
User: I need to build a heat demand forecasting model for a portfolio of 50
      buildings. Where do I start?

Agent: The guide covers this across several chapters. Here's a recommended path:

       **1. Data preparation (Chapter 6: Time Series Fundamentals)**
       - Resample sensor data to hourly intervals
       - Handle missing values (forward-fill for short gaps, interpolation for longer)
       - Feature engineering: lag features (t-1, t-24, t-168), rolling means,
         Fourier terms for seasonality, outdoor temperature forecasts

       **2. Model selection (Chapter 7: Forecasting Heat Demand)**
       - Start with gradient boosting (XGBoost/LightGBM), it handles mixed
         feature types and missing values well
       - For 50 buildings: train one model per building cluster, not one per
         building (Chapter 11: Clustering building portfolios)
       - Deep learning (LSTM) is worth trying if you have 2+ years of hourly data

       **3. Production (Chapter 14: MLOps Fundamentals)**
       - MLflow for experiment tracking across buildings
       - Monitor per-building prediction drift (a model that works in winter
         may degrade in shoulder seasons)

       Want me to go deeper on any of these steps?

User: How should I cluster the 50 buildings?

Agent: Chapter 11 recommends clustering by consumption pattern, not building
       metadata:

       **Features for clustering:**
       - Normalized daily load profiles (24-hour shape, not absolute values)
       - Heating degree-day sensitivity (slope of consumption vs. HDD regression)
       - Weekend/weekday ratio
       - Base load level (minimum consumption in summer)

       **Method:**
       - K-means or hierarchical clustering on the feature matrix
       - Use silhouette score to select k (typically 3-5 clusters for 50 buildings)
       - Interpret clusters: "high base load + flat profile" = likely commercial,
         "steep HDD sensitivity + low base" = likely residential, well-insulated

       This matches the approach in Chapter 19 (System Design: Energy management
       platform for large building portfolios).

       Sources: Chapter 11 (Unsupervised Learning), Chapter 19 (System Design)
```

---

## Interaction 4: Standard Lookup + Cross-Reference (Bilingual)

A consultant preparing a hydraulic balancing assessment.

```
User: What's the difference between Verfahren A and Verfahren B for
      hydraulischer Abgleich?

Agent: Both are methods for hydraulic balancing defined in VdW/ZVSHK guidelines:

       **Verfahren A (simplified):**
       - Estimates heat load per room using building age, insulation class,
         and room area
       - No room-by-room calculation
       - Faster, cheaper, less precise
       - Sufficient for GEG compliance in existing buildings

       **Verfahren B (detailed):**
       - Full room-by-room heat load calculation per DIN EN 12831
       - Considers: wall U-values, window areas, orientation, ventilation losses
       - Required for new construction and heat pump installations
       - Produces exact volume flow rates per radiator

       For data-driven assessment of whether a building needs rebalancing,
       Chapter 4 describes using return temperature spreads across radiator
       circuits as a proxy: high variance in Spreizung across rooms signals
       poor balancing.

       Sources: Chapter 4 (Hydraulischer Abgleich), DIN EN 12831

User: Gibt es dazu ein Feature-Engineering-Beispiel?

Agent: Ja, aus Kapitel 4 und 6 kombiniert:

       **Features zur Erkennung von Abgleich-Bedarf:**
       - Spreizung pro Heizkreis (Vorlauf - Rücklauf), Varianz über alle Kreise
       - Rücklauftemperatur-Differenz zum Sollwert pro Raum
       - Ventilstellung (wenn elektronische Thermostate vorhanden): Dauerlauf
         bei 100% = unterversorgt, Dauerlauf bei 0% = überversorgt
       - Raumtemperatur-Abweichung vom Sollwert, zeitlich gewichtet

       Diese Features lassen sich mit einem Isolation Forest (Kapitel 8)
       kombinieren, um Räume zu identifizieren, die am stärksten von einem
       Abgleich profitieren würden.

       Quellen: Kapitel 4 (Hydraulischer Abgleich), Kapitel 6 (Feature
       Engineering), Kapitel 8 (Anomaly Detection)
```

---

## Interaction 5: Guided Exploration (English)

A user who doesn't know what to ask yet.

```
User: I'm new to energy data science. What should I learn first?

Agent: Welcome! The guide is structured as a learning path. Here's what I
       recommend based on your background:

       **If you're a data scientist new to energy:**
       Start with Chapter 1-3 (thermodynamic principles, heating system types,
       control variables). The key concept to internalize: heating systems are
       physically constrained, so ML models need to respect domain boundaries
       (e.g., flow temperature can't drop below return temperature).

       **If you're an engineer new to ML:**
       Start with Chapter 6 (time series fundamentals) and Chapter 10
       (supervised learning applications). These connect engineering concepts
       you already know to ML formulations.

       **If you want to build something quickly:**
       Jump to Chapter 18 (case study walkthroughs) for end-to-end examples,
       then backtrack to the theory chapters as needed.

       Which background fits you best? I can tailor my guidance.

User: Data scientist, but I've worked with time series before.

Agent: Then you can skip the generic time series intro in Chapter 6 and focus
       on what's domain-specific:

       1. **Chapter 1-3** (1 hour): Get the physical vocabulary. Key terms:
          Heizkennlinie, Vorlauf/Rücklauf, Spreizung, Brennwert vs. Heizwert.
          You'll see these in every dataset.

       2. **Chapter 8** (30 min): Anomaly detection in heating systems. This is
          where your time series skills apply directly, but the anomalies are
          domain-specific (legionella risk, cycling behavior, return temperature
          violations).

       3. **Chapter 5** (30 min): Sector coupling. This is the frontier,
          optimizing PV + heat pump + battery is a multi-objective problem
          that's actively researched.

       Want me to start explaining any of these?
```

---

## Conversation Patterns

| Pattern | Example | Agent Behavior |
|---------|---------|---------------|
| Language switch | User starts English, switches to German | Agent follows, responds in the new language |
| Follow-up question | "Tell me more about that" | Agent uses conversation state to resolve "that" |
| Calculation + explanation | "Calculate X and explain why" | Tool call first, then RAG-grounded explanation |
| Out of scope | "What's the weather in Berlin?" | Polite deflection: "I specialize in residential heating systems and energy data science. For weather data, I can explain how to integrate weather APIs into heating models (Chapter 7)." |
| Ambiguous query | "Tell me about DIN" | Clarification: "The guide references several DIN standards. Are you asking about DIN EN 12831 (heat load calculation), DIN 4108 (thermal insulation), or another standard?" |
| Correction | "No, I meant Verfahren B" | Agent acknowledges, re-routes without repeating the full previous answer |