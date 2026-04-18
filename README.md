# 🚀 Opportunity Copilot 

**Opportunity Copilot** is a high-performance, AI-driven dashboard designed to automate the discovery and ranking of academic and professional opportunities. Built specifically for students in the **Artificial Intelligence** department, it uses Large Language Models (LLMs) to scan messy inbox data, extract key metadata, and rank opportunities based on a deterministic scoring engine.

---

## 🛠️ Tech Stack

- **UI Framework:** [Flet](https://flet.dev/) (Flutter-based UI for Python)
- **AI Core:** [Groq API](https://groq.com/) (Llama-3.1-8b-instant)
- **Data Modeling:** [Pydantic](https://docs.pydantic.dev/) (Strict type validation)
- **Package Manager:** [uv](https://github.com/astral-sh/uv) (Extremely fast Python networking)
- **OS Environment:** Arch Linux (Hyprland WM)

---

## ✨ Key Features

- **Agentic Extraction:** Uses an LLM to identify if an email is a genuine opportunity or just noise (e.g., cafeteria updates or club meetings).
- **Deterministic Scoring:** Ranks opportunities by matching them against your real-time student profile (Major, GPA, Skills, and Interests).
- **Hard Eligibility Filtering:** Automatically filters out opportunities if you don't meet the strict CGPA requirements.
- **Modern Dashboard:** A sleek, dark-themed Material Design 3 interface with smooth scrolling and hardware acceleration.

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have the following installed on your system:
- Python 3.12+ (Stable recommended)
- `unzip` (Required for Flet's Flutter engine initialization)
- A Groq API Key

### 2. Installation
Clone the repository and install dependencies using `uv`:
```bash
uv venv
source .venv/bin/activate
uv pip install flet groq pydantic python-dotenv
```

### 3. Environment Setup
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_gsk_key_here
```

### 4. Running the App
Execute the dashboard directly from your terminal:
```bash
python app.py
```

## 🧠 How It Works



1. **Classification:** The AI reads the raw text and determines if the intent is an *Opportunity*.
2. **Extraction:** It pulls out `deadline`, `min_cgpa`, `required_skills`, and `contact_info`.
3. **Scoring:** The system compares the extraction to the values in the **Student Profile** sidebar to generate a % Match.
4. **Display:** Only qualified, high-value opportunities are rendered as interactive cards in the dashboard.

## 👨‍💻 Author

* **Rana Muhammad Afnan**
* **Muhammad Saim Khan**
* **Hassan Faisal** 






