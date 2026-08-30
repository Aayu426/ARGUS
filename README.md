# ARGUS 🔍

### AI-Powered Digital Forensics & Evidence Analysis Platform

ARGUS is an AI-powered digital forensics platform designed to help investigators preserve, verify, and analyze digital evidence through a unified forensic workflow.

It combines cryptographic evidence integrity, chain-of-custody tracking, NLP-based stylometry, social graph analysis, and AI-powered visual/deepfake analysis into a single platform.

---

## 🏆 Achievement

🥇 **1st Place — CDAC Hackathon, VIT VELLORE

ARGUS was developed as a team project and selected as the winning solution among **180+ participants**.

---

## 🚨 Problem

Digital investigations increasingly involve evidence from multiple sources such as images, documents, social connections, and digital identities.

Traditional forensic workflows can make it difficult to:

* Maintain reliable evidence integrity
* Track the complete chain of custody
* Detect manipulated or AI-generated media
* Analyze writing patterns and authorship
* Understand relationships between entities
* Combine different forensic signals into one investigation

ARGUS addresses these challenges through a centralized AI-assisted forensic workflow.

---

## 💡 Our Solution

ARGUS provides investigators with a unified environment where digital evidence can be:

**Collected → Verified → Analyzed → Correlated → Reported**

The platform combines conventional digital forensics with AI-assisted analysis while maintaining evidence integrity throughout the investigation.

---

## ⚡ Key Features

### 🔐 Evidence Integrity & Chain of Custody

* Cryptographic hashing for evidence verification
* Tamper-evident evidence handling
* Chain-of-custody tracking
* Evidence integrity verification

### 🧠 NLP Stylometry

* Writing-style analysis
* Stylometric feature extraction
* Authorship comparison
* Linguistic pattern analysis

### 🕸️ Social Graph Analysis

* Relationship and entity mapping
* Graph-based investigation
* Connection analysis between entities

### 🖼️ AI-Powered Visual Forensics

* Image analysis
* Error Level Analysis (ELA)
* Manipulation detection
* Deepfake detection capabilities

### 📊 Unified Investigation Workflow

ARGUS brings multiple forensic techniques together so investigators can analyze evidence from different dimensions instead of relying on isolated tools.

---

## 🏗️ System Workflow

```text
                    Digital Evidence
                           │
                           ▼
                  ┌─────────────────┐
                  │ Evidence Intake │
                  └────────┬────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │ Integrity & Custody     │
              │ Hashing + Verification  │
              └───────────┬────────────┘
                          │
          ┌───────────────┼────────────────┐
          ▼               ▼                ▼
      NLP Analysis    Graph Analysis   Visual Analysis
          │               │                │
          ▼               ▼                ▼
      Stylometry      Relationships    ELA / Deepfake
          │               │                │
          └───────────────┼────────────────┘
                          ▼
                 ┌─────────────────┐
                 │ Forensic Results│
                 └────────┬────────┘
                          ▼
                   Investigation
                       Report
```

---

## 🛠️ Technology Stack

**Backend**

* Python
* FastAPI
* Machine Learning / AI models
* NLP
* Computer Vision

**Frontend**

* Next.js
* React
* TypeScript

**Forensics & Security**

* Cryptographic hashing
* Chain of custody
* Evidence integrity verification
* Digital forensic analysis

**AI / Analysis**

* NLP stylometry
* Graph analysis
* Image forensics
* Deepfake detection

---

## 📁 Project Structure

```text
ARGUS/
│
├── argus_forensics/      # Python forensic backend
│   ├── core/
│   ├── graph/
│   ├── ingestion/
│   ├── integrity/
│   ├── nlp/
│   ├── vision/
│   └── main.py
│
├── argus-ui/             # Next.js frontend
│
├── tests/                # Testing
│
├── docs/                 # Project documentation
│
├── screenshots/          # Project screenshots
│
├── README.md
└── .gitignore
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Aayu426/ARGUS.git
cd ARGUS
```

### 2. Setup the backend

```bash
cd argus_forensics

python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Setup the frontend

Open another terminal:

```bash
cd argus-ui
npm install
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:3000
```

> Backend startup commands may vary depending on the configured entry point and environment.

---

## 📸 Screenshots

### ARGUS Dashboard

![ARGUS Dashboard](screenshots/dashboard.png)

### Evidence Analysis

![Evidence Analysis](screenshots/evidence-analysis.png)

### AI / Deepfake Analysis

![Deepfake Analysis](screenshots/deepfake-analysis.png)

### Chain of Custody

![Chain of Custody](screenshots/chain-of-custody.png)

---

## 🔮 Future Scope

* More advanced multimodal forensic models
* Improved deepfake and synthetic-media detection
* Automated forensic report generation
* Larger-scale graph-based investigations
* Additional evidence formats and forensic sources
* Deployment as a scalable investigation platform

---

## 👥 Team

ARGUS was developed collaboratively as a team project.

Contributors:

* **Aayush Pachchigar** — [GitHub](https://github.com/Aayu426)
* **Shlok** — [GitHub](https://github.com/shlokDS16)
* **[Add remaining team members]**

---

## 📌 Disclaimer

ARGUS is a research and hackathon project intended for digital-forensics experimentation and educational purposes. Results produced by automated analysis should be validated by qualified investigators before being used as evidence in real investigations.
