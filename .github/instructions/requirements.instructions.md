---
applyTo: "**"
---

# Project Context: Deutsche Bank "Signal Radar"

> **DEveloper Note:** This project is a real-time intelligence dashboard designed to replace manual media monitoring with proactive, automated risk detection.

## The Core Problem

Corporate Affairs teams currently rely on reactive, noisy keyword alerts, often missing "weak signals" (early indicators of reputational risk) until they become mainstream news headlines. They suffer from high noise-to-signal ratios and siloed intelligence between different teams (e.g., Regulatory vs. Public Comms).

## Functional Requirements (Solving the Problem)

The application must solve these specific pain points through code:

1.  **Noise Reduction (The "Anti-Alert" System)**

    - _Problem:_ Too many irrelevant alerts (stock tickers, generic press releases).
    - _Solution:_ Implement strict filtering using TF-IDF for topic _velocity_ (newness) rather than just raw frequency.

2.  **Weak Signal Detection**

    - _Problem:_ Critical risks often start small in niche sources (NGO PDFs, policy sub-pages).
    - _Solution:_ The ingestion engine must scrape deeply, not just widely. The scoring algorithm must heavily weight low-frequency terms if they appear in high-authority designated sources.

3.  **Persona-Based Context (Breaking Silos)**
    - _Problem:_ Different teams need different views of the same data pool.
    - _Solution:_ Implement a "Relevance Engine" that dynamically re-scores and re-ranks the unified data stream based on the active user profile (Regulatory, Comms, Strategy).

## Domain Glossary (For Variable Naming & Comments)

- **`Signal`**: A specific data point (article, tweet, report) that has passed initial noise filters.
- **`Velocity`**: The rate of change in a topic's mention frequency compared to its historical baseline (acceleration of interest).
- **`Weak Signal`**: A high-relevance, low-velocity topic that is just beginning to emerge.
- **`Persona`**: The active user view profile that determines scoring weights (e.g., `PERSONA_REGULATORY`, `PERSONA_COMMS`).
- **`Entity`**: A specific stakeholder detected by NER (Organization, Person, GPE).
