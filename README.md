# AI-Assisted Support Triage & Insights

A small customer-support operations project built with Python, Streamlit, SQLite, and an optional OpenAI API integration.

The goal is to demonstrate a realistic support workflow rather than a fully autonomous chatbot. A support agent can submit a ticket, review its classification and escalation recommendation, see a relevant knowledge-base article, and view aggregate issue patterns in a dashboard.

## Features

- Ticket intake with customer plan context
- Rule-based ticket classification that works without external APIs
- Optional model-assisted classification through the OpenAI Responses API
- Priority and human-escalation recommendations
- Knowledge-base matching
- Draft support responses
- SQLite ticket history
- Dashboard for recurring issue categories, priorities, and escalation rate
- Synthetic seed data for demonstration

## Tech stack

- Python
- Streamlit
- SQLite
- pandas
- OpenAI API (optional)

## Project structure

```text
ai-support-triage/
├── app.py
├── analytics.py
├── classifier.py
├── database.py
├── knowledge_base.py
├── requirements.txt
├── .env.example
├── .gitignore
├── data/
│   ├── tickets.csv
│   └── knowledge_base.json
└── tests/
    ├── test_classifier.py
    └── test_knowledge_base.py
```

## Run locally

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the app:

```bash
streamlit run app.py
```

The app works immediately with the local rule-based classifier.

## Optional OpenAI integration

Copy the example environment file:

```bash
cp .env.example .env
```

Then add your API key and a model available to your OpenAI API account:

```text
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=your_model_here
```

Do not commit `.env` or an API key to GitHub.

If either environment variable is missing, the project automatically falls back to the local classifier.

## Run tests

```bash
pytest
```

## Portfolio talking points

This project is intentionally scoped around support operations:

- deciding what can be handled automatically vs. escalated to a person
- identifying recurring ticket patterns
- connecting tickets to self-service documentation
- keeping AI recommendations reviewable rather than fully autonomous

## Future improvements

- semantic knowledge-base search with embeddings
- ticket similarity scoring
- response-quality evaluation
- weekly trend comparisons
- agent feedback buttons
- issue clustering
- Zendesk-style ticket import/export
- authentication and role-based views
