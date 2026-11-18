"""Dataset preparation module for the 12-role ML Career Prediction Engine.

IMPORTANT TRANSPARENCY NOTE:
This module builds a clearly labeled SYNTHETIC training/evaluation dataset derived from
curated role blueprints (required skills, preferred skills, experience, education, and
role descriptions). All records carry `is_synthetic=True`. Evaluation metrics on this
dataset measure classifier behavior on synthetic profiles, NOT real-world hiring outcomes.
"""

import csv
import json
from pathlib import Path
import random
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[4]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
DATASET_CSV_PATH = PROCESSED_DATA_DIR / "career_training_dataset.csv"
CATALOG_JSON_PATH = PROCESSED_DATA_DIR / "career_role_catalog.json"

DATASET_PROVENANCE = "synthetic_skillgap_career_dataset_v1"

# Curated catalog of all 12 supported career roles
CAREER_ROLE_CATALOG: List[Dict[str, Any]] = [
    {
        "title": "Data Analyst",
        "category": "Data & Analytics",
        "interest_tags": ["data", "analytics", "business", "visualization"],
        "avg_salary": "$78,000 - $98,000",
        "demand_level": "High",
        "required_skills": [
            {"name": "SQL", "category": "Data", "weight": 1.5},
            {"name": "Excel", "category": "Data", "weight": 1.3},
            {"name": "Power BI", "category": "Data", "weight": 1.3},
            {"name": "Tableau", "category": "Data", "weight": 1.2},
            {"name": "Python", "category": "Programming", "weight": 1.2},
            {"name": "Pandas", "category": "Data", "weight": 1.2},
        ],
        "preferred_skills": [
            {"name": "NumPy", "category": "Data", "weight": 0.7},
            {"name": "Business Analysis", "category": "Business", "weight": 0.7},
            {"name": "Git", "category": "Cloud", "weight": 0.6},
        ],
        "typical_experience": [
            "1-2 years analyzing KPI funnels, building executive BI dashboards, and writing SQL queries.",
            "Analytics internship focused on Excel reporting, Tableau visualizations, and Pandas cleaning.",
            "Junior analyst experience delivering revenue trend reports and automated Power BI scorecards.",
        ],
        "typical_education": [
            "Bachelor of Science in Data Analytics",
            "Bachelor of Science in Statistics",
            "Bachelor of Arts in Economics",
            "Bachelor of Science in Computer Science",
        ],
        "project_templates": [
            "Built interactive Power BI and Tableau dashboards backed by SQL queries for retail KPI tracking.",
            "Automated weekly Excel and Python Pandas cohort retention analysis reports.",
            "Created customer segmentation and funnel conversion visualizations using SQL and Tableau.",
        ],
        "role_description": (
            "Analyzes structured business and product datasets using SQL, Excel, Power BI, "
            "Tableau, Python, and Pandas to deliver dashboards and operational insights."
        ),
    },
    {
        "title": "Data Scientist",
        "category": "Data & AI",
        "interest_tags": ["data", "ai", "ml", "analytics", "research"],
        "avg_salary": "$115,000 - $142,000",
        "demand_level": "Very High",
        "required_skills": [
            {"name": "Python", "category": "Programming", "weight": 1.5},
            {"name": "SQL", "category": "Data", "weight": 1.3},
            {"name": "Pandas", "category": "Data", "weight": 1.3},
            {"name": "NumPy", "category": "Data", "weight": 1.2},
            {"name": "Machine Learning", "category": "AI/ML", "weight": 1.5},
            {"name": "Natural Language Processing", "category": "AI/ML", "weight": 1.2},
        ],
        "preferred_skills": [
            {"name": "TensorFlow", "category": "AI/ML", "weight": 0.8},
            {"name": "PyTorch", "category": "AI/ML", "weight": 0.8},
            {"name": "Tableau", "category": "Data", "weight": 0.6},
            {"name": "AWS", "category": "Cloud", "weight": 0.6},
        ],
        "typical_experience": [
            "2+ years building predictive Machine Learning models, A/B experiments, and SQL feature tables.",
            "Data Science internship developing statistical forecasting and NLP classification pipelines in Python.",
            "Applied modeling experience with Pandas, NumPy, Scikit-learn, and experimentation metrics.",
        ],
        "typical_education": [
            "Master of Science in Data Science",
            "Bachelor of Science in Statistics and Computer Science",
            "Master of Science in Applied Mathematics",
        ],
        "project_templates": [
            "Developed customer churn prediction models using Python, Pandas, NumPy, and Scikit-learn.",
            "Built NLP sentiment classification and statistical A/B experimentation framework over SQL tables.",
            "Engineered feature selection and predictive regression pipelines evaluated with cross-validation.",
        ],
        "role_description": (
            "Applies statistics, Python, SQL, Pandas, NumPy, Machine Learning, and NLP to "
            "extract predictive insights, run experiments, and solve complex analytical problems."
        ),
    },
    {
        "title": "Machine Learning Engineer",
        "category": "Data & AI",
        "interest_tags": ["ai", "ml", "engineering", "cloud"],
        "avg_salary": "$135,000 - $168,000",
        "demand_level": "Very High",
        "required_skills": [
            {"name": "Python", "category": "Programming", "weight": 1.5},
            {"name": "Machine Learning", "category": "AI/ML", "weight": 1.5},
            {"name": "Deep Learning", "category": "AI/ML", "weight": 1.4},
            {"name": "PyTorch", "category": "AI/ML", "weight": 1.4},
            {"name": "TensorFlow", "category": "AI/ML", "weight": 1.2},
            {"name": "Docker", "category": "Cloud", "weight": 1.2},
            {"name": "AWS", "category": "Cloud", "weight": 1.1},
        ],
        "preferred_skills": [
            {"name": "Natural Language Processing", "category": "AI/ML", "weight": 0.8},
            {"name": "Kubernetes", "category": "Cloud", "weight": 0.8},
            {"name": "FastAPI", "category": "Web", "weight": 0.7},
            {"name": "C++", "category": "Programming", "weight": 0.6},
        ],
        "typical_experience": [
            "2-3 years training Deep Learning models in PyTorch/TensorFlow and serving via Docker on AWS.",
            "ML Engineering experience optimizing GPU inference pipelines, MLOps tracking, and Kubernetes scaling.",
            "Built production ML training workflows and model registries with Python and Docker.",
        ],
        "typical_education": [
            "Master of Science in Machine Learning",
            "Bachelor of Science in Computer Science",
            "Master of Science in Artificial Intelligence",
        ],
        "project_templates": [
            "Trained and quantized PyTorch neural networks served via Dockerized inference endpoints on AWS.",
            "Built distributed TensorFlow Deep Learning training pipeline orchestrated with Kubernetes.",
            "Engineered low-latency ML feature serving and automated model evaluation CI/CD workflows.",
        ],
        "role_description": (
            "Trains, optimizes, containerizes, and deploys production Machine Learning and "
            "Deep Learning systems using Python, PyTorch, TensorFlow, Docker, and AWS."
        ),
    },
    {
        "title": "Python Developer",
        "category": "Software Engineering",
        "interest_tags": ["backend", "programming", "software", "apis"],
        "avg_salary": "$95,000 - $122,000",
        "demand_level": "High",
        "required_skills": [
            {"name": "Python", "category": "Programming", "weight": 1.5},
            {"name": "FastAPI", "category": "Web", "weight": 1.4},
            {"name": "SQL", "category": "Data", "weight": 1.3},
            {"name": "REST APIs", "category": "Web", "weight": 1.3},
            {"name": "Git", "category": "Cloud", "weight": 1.1},
            {"name": "Docker", "category": "Cloud", "weight": 1.1},
        ],
        "preferred_skills": [
            {"name": "AWS", "category": "Cloud", "weight": 0.7},
            {"name": "Linux", "category": "Cloud", "weight": 0.7},
            {"name": "Pandas", "category": "Data", "weight": 0.6},
        ],
        "typical_experience": [
            "1-3 years writing clean Python backend services, automation scripts, and FastAPI REST APIs.",
            "Python developer internship focusing on SQLAlchemy ORM, pytest test suites, and Docker.",
            "Built data processing scripts, asynchronous Python workers, and RESTful microservices.",
        ],
        "typical_education": [
            "Bachelor of Science in Computer Science",
            "Bachelor of Technology in Software Engineering",
            "Bachelor of Science in Information Technology",
        ],
        "project_templates": [
            "Developed modular FastAPI REST APIs in Python with SQLAlchemy, PostgreSQL, and pytest coverage.",
            "Automated document ingestion and scheduled Python CLI tools packaged in Docker containers.",
            "Engineered async Python service integrations with GitHub Actions CI/CD testing.",
        ],
        "role_description": (
            "Builds maintainable Python applications, FastAPI services, automation utilities, "
            "and SQL-backed REST APIs with Docker and Git."
        ),
    },
    {
        "title": "Full Stack Developer",
        "category": "Software Engineering",
        "interest_tags": ["web", "fullstack", "frontend", "backend", "software"],
        "avg_salary": "$105,000 - $135,000",
        "demand_level": "Very High",
        "required_skills": [
            {"name": "JavaScript", "category": "Programming", "weight": 1.5},
            {"name": "React", "category": "Web", "weight": 1.5},
            {"name": "HTML", "category": "Web", "weight": 1.1},
            {"name": "CSS", "category": "Web", "weight": 1.1},
            {"name": "Node.js", "category": "Web", "weight": 1.3},
            {"name": "SQL", "category": "Data", "weight": 1.2},
            {"name": "REST APIs", "category": "Web", "weight": 1.3},
            {"name": "Git", "category": "Cloud", "weight": 1.0},
        ],
        "preferred_skills": [
            {"name": "TypeScript", "category": "Programming", "weight": 0.8},
            {"name": "Python", "category": "Programming", "weight": 0.8},
            {"name": "FastAPI", "category": "Web", "weight": 0.7},
            {"name": "Docker", "category": "Cloud", "weight": 0.7},
        ],
        "typical_experience": [
            "1-3 years building responsive React frontends integrated with Node.js/FastAPI REST APIs and SQL.",
            "Full Stack engineering internship delivering end-to-end SaaS features across UI, backend, and DB.",
            "Shipped web applications with JavaScript, React, HTML, CSS, Node.js, and Docker deployments.",
        ],
        "typical_education": [
            "Bachelor of Science in Computer Science",
            "Bachelor of Engineering in Software Engineering",
            "Full Stack Web Development Degree / Bootcamp",
        ],
        "project_templates": [
            "Built a SaaS web platform using React, Tailwind CSS, Node.js/FastAPI REST APIs, and PostgreSQL.",
            "Developed an end-to-end e-commerce portal with JavaScript, React, SQL schemas, and JWT auth.",
            "Shipped a real-time collaborative task tracker using React, Node.js, HTML/CSS, and Docker.",
        ],
        "role_description": (
            "Develops complete web applications across React/JavaScript/HTML/CSS frontends, "
            "Node.js or Python FastAPI REST APIs, and SQL databases."
        ),
    },
    {
        "title": "Backend Developer",
        "category": "Software Engineering",
        "interest_tags": ["backend", "apis", "databases", "software", "cloud"],
        "avg_salary": "$118,000 - $148,000",
        "demand_level": "High",
        "required_skills": [
            {"name": "Python", "category": "Programming", "weight": 1.4},
            {"name": "Java", "category": "Programming", "weight": 1.3},
            {"name": "SQL", "category": "Data", "weight": 1.5},
            {"name": "REST APIs", "category": "Web", "weight": 1.5},
            {"name": "FastAPI", "category": "Web", "weight": 1.2},
            {"name": "Docker", "category": "Cloud", "weight": 1.3},
            {"name": "AWS", "category": "Cloud", "weight": 1.2},
        ],
        "preferred_skills": [
            {"name": "Node.js", "category": "Web", "weight": 0.7},
            {"name": "Kubernetes", "category": "Cloud", "weight": 0.8},
            {"name": "Go", "category": "Programming", "weight": 0.7},
            {"name": "Linux", "category": "Cloud", "weight": 0.7},
        ],
        "typical_experience": [
            "2-4 years designing scalable REST APIs, microservices, database indexing, and Docker deployments.",
            "Backend engineering experience with Java Spring Boot, Python FastAPI, PostgreSQL, and AWS.",
            "Architected authentication middleware, caching layers, and high-throughput SQL backends.",
        ],
        "typical_education": [
            "Bachelor of Science in Computer Science",
            "Master of Science in Software Engineering",
            "Bachelor of Engineering in Computer Engineering",
        ],
        "project_templates": [
            "Architected high-throughput REST API microservices using Java/Python, SQL indexing, and Docker.",
            "Designed multi-tenant FastAPI backend with JWT security, connection pooling, and AWS deployment.",
            "Built distributed order processing backend with relational transactions and automated migrations.",
        ],
        "role_description": (
            "Architects server-side APIs, relational SQL databases, authentication systems, "
            "and containerized cloud services using Python, Java, FastAPI, Docker, and AWS."
        ),
    },
    {
        "title": "Frontend Developer",
        "category": "Software Engineering",
        "interest_tags": ["frontend", "web", "ui", "design"],
        "avg_salary": "$100,000 - $128,000",
        "demand_level": "High",
        "required_skills": [
            {"name": "JavaScript", "category": "Programming", "weight": 1.5},
            {"name": "React", "category": "Web", "weight": 1.5},
            {"name": "HTML", "category": "Web", "weight": 1.4},
            {"name": "CSS", "category": "Web", "weight": 1.4},
            {"name": "TypeScript", "category": "Programming", "weight": 1.3},
            {"name": "Git", "category": "Cloud", "weight": 1.0},
        ],
        "preferred_skills": [
            {"name": "REST APIs", "category": "Web", "weight": 0.8},
            {"name": "Node.js", "category": "Web", "weight": 0.6},
        ],
        "typical_experience": [
            "1-3 years crafting accessible, responsive React & TypeScript component libraries and web apps.",
            "Frontend engineering internship implementing pixel-accurate Tailwind CSS designs and REST integrations.",
            "Optimized Core Web Vitals, code splitting, and state management in modern JavaScript SPAs.",
        ],
        "typical_education": [
            "Bachelor of Science in Computer Science",
            "Bachelor of Science in Human-Computer Interaction",
            "Bachelor of Arts in Digital Media & Web Development",
        ],
        "project_templates": [
            "Built a responsive SaaS analytics interface using React, TypeScript, HTML5, and Tailwind CSS.",
            "Created an accessible component design system with React hooks, CSS grid, and keyboard navigation.",
            "Developed an interactive portfolio and dashboard consuming REST APIs with Vite code splitting.",
        ],
        "role_description": (
            "Creates responsive, accessible, high-performance user interfaces using React, "
            "JavaScript, TypeScript, HTML, CSS, and modern frontend build tools."
        ),
    },
    {
        "title": "AI Engineer",
        "category": "Data & AI",
        "interest_tags": ["ai", "ml", "nlp", "apis", "engineering"],
        "avg_salary": "$140,000 - $175,000",
        "demand_level": "Very High",
        "required_skills": [
            {"name": "Python", "category": "Programming", "weight": 1.5},
            {"name": "Machine Learning", "category": "AI/ML", "weight": 1.4},
            {"name": "Natural Language Processing", "category": "AI/ML", "weight": 1.5},
            {"name": "Deep Learning", "category": "AI/ML", "weight": 1.3},
            {"name": "PyTorch", "category": "AI/ML", "weight": 1.3},
            {"name": "FastAPI", "category": "Web", "weight": 1.3},
            {"name": "Docker", "category": "Cloud", "weight": 1.1},
        ],
        "preferred_skills": [
            {"name": "TensorFlow", "category": "AI/ML", "weight": 0.7},
            {"name": "AWS", "category": "Cloud", "weight": 0.8},
            {"name": "REST APIs", "category": "Web", "weight": 0.8},
            {"name": "React", "category": "Web", "weight": 0.6},
        ],
        "typical_experience": [
            "2+ years building applied NLP, semantic search, LLM workflows, and FastAPI inference APIs.",
            "AI Engineering experience integrating Sentence Transformers, spaCy, and PyTorch into web products.",
            "Developed RAG pipelines, embedding retrieval services, and containerized AI backends.",
        ],
        "typical_education": [
            "Master of Science in Artificial Intelligence",
            "Bachelor of Science in Computer Science",
            "Master of Science in Computational Linguistics / NLP",
        ],
        "project_templates": [
            "Engineered a semantic search and NLP resume analyzer using Python, PyTorch, spaCy, and FastAPI.",
            "Built an LLM document Q&A assistant with embedding vectors served via Dockerized REST APIs.",
            "Developed multi-stage NLP entity extraction and recommendation APIs integrated with React.",
        ],
        "role_description": (
            "Integrates NLP, Deep Learning, semantic embeddings, and Machine Learning models "
            "into production AI applications using Python, PyTorch, FastAPI, and Docker."
        ),
    },
    {
        "title": "Business Analyst",
        "category": "Business & Strategy",
        "interest_tags": ["business", "analytics", "data", "strategy"],
        "avg_salary": "$82,000 - $108,000",
        "demand_level": "High",
        "required_skills": [
            {"name": "Business Analysis", "category": "Business", "weight": 1.5},
            {"name": "Excel", "category": "Data", "weight": 1.4},
            {"name": "SQL", "category": "Data", "weight": 1.3},
            {"name": "Power BI", "category": "Data", "weight": 1.3},
            {"name": "Tableau", "category": "Data", "weight": 1.2},
        ],
        "preferred_skills": [
            {"name": "Python", "category": "Programming", "weight": 0.7},
            {"name": "Pandas", "category": "Data", "weight": 0.6},
        ],
        "typical_experience": [
            "2+ years gathering BRD/FRD requirements, mapping business processes, and leading stakeholder workshops.",
            "Business Analyst experience translating operational KPIs into Power BI dashboards and JIRA user stories.",
            "Conducted ROI modeling in Excel, SQL root-cause analysis, and Agile sprint prioritization.",
        ],
        "typical_education": [
            "Bachelor of Business Administration (BBA)",
            "Master of Business Administration (MBA)",
            "Bachelor of Science in Management Information Systems",
        ],
        "project_templates": [
            "Authored BRD/FRD requirements and JIRA backlogs for an enterprise CRM workflow modernization.",
            "Built executive KPI reporting scorecards in Power BI, Tableau, and Excel backed by SQL queries.",
            "Performed cost-benefit process gap analysis and presented quarterly roadmap recommendations.",
        ],
        "role_description": (
            "Bridges business stakeholders and engineering teams through requirements gathering, "
            "KPI modeling, Excel, SQL, Power BI, Tableau, and process optimization."
        ),
    },
    {
        "title": "Data Engineer",
        "category": "Data & Analytics",
        "interest_tags": ["data", "engineering", "cloud", "databases"],
        "avg_salary": "$122,000 - $152,000",
        "demand_level": "Very High",
        "required_skills": [
            {"name": "Python", "category": "Programming", "weight": 1.5},
            {"name": "SQL", "category": "Data", "weight": 1.5},
            {"name": "Spark", "category": "Data", "weight": 1.5},
            {"name": "Pandas", "category": "Data", "weight": 1.2},
            {"name": "AWS", "category": "Cloud", "weight": 1.3},
            {"name": "Docker", "category": "Cloud", "weight": 1.2},
        ],
        "preferred_skills": [
            {"name": "Azure", "category": "Cloud", "weight": 0.8},
            {"name": "Kubernetes", "category": "Cloud", "weight": 0.8},
            {"name": "NumPy", "category": "Data", "weight": 0.6},
            {"name": "Java", "category": "Programming", "weight": 0.6},
        ],
        "typical_experience": [
            "2-4 years building automated ETL/ELT batch and streaming pipelines with PySpark, Airflow, and SQL.",
            "Data Engineering experience designing cloud data warehouses on AWS/Azure with Docker.",
            "Maintained petabyte-scale data ingestion, schema validation, and Python orchestration jobs.",
        ],
        "typical_education": [
            "Bachelor of Science in Computer Science",
            "Master of Science in Data Engineering",
            "Bachelor of Technology in Information Systems",
        ],
        "project_templates": [
            "Built automated ETL data lake pipelines using Apache Spark, Airflow, Python, and SQL on AWS.",
            "Engineered containerized data ingestion and schema quality checks with Docker and PostgreSQL.",
            "Optimized warehouse partitioning and PySpark batch transformations reducing runtime by 45%.",
        ],
        "role_description": (
            "Designs and operates reliable ETL pipelines, data warehouses, and cloud data "
            "infrastructure using Python, SQL, Spark/Airflow, Pandas, AWS, and Docker."
        ),
    },
    {
        "title": "Cloud Engineer",
        "category": "Cloud & Infrastructure",
        "interest_tags": ["cloud", "devops", "infrastructure", "engineering"],
        "avg_salary": "$125,000 - $155,000",
        "demand_level": "Very High",
        "required_skills": [
            {"name": "AWS", "category": "Cloud", "weight": 1.5},
            {"name": "Azure", "category": "Cloud", "weight": 1.3},
            {"name": "Docker", "category": "Cloud", "weight": 1.5},
            {"name": "Kubernetes", "category": "Cloud", "weight": 1.5},
            {"name": "Terraform", "category": "Cloud", "weight": 1.4},
            {"name": "Linux", "category": "Cloud", "weight": 1.3},
            {"name": "Git", "category": "Cloud", "weight": 1.1},
        ],
        "preferred_skills": [
            {"name": "Python", "category": "Programming", "weight": 0.8},
            {"name": "Network Security", "category": "Security", "weight": 0.7},
        ],
        "typical_experience": [
            "2-4 years provisioning multi-region AWS and Azure infrastructure using Terraform and Kubernetes.",
            "Cloud/DevOps experience managing Docker clusters, Linux servers, and GitHub Actions CI/CD.",
            "Automated cloud networking, IAM policies, observability, and zero-downtime K8s rollouts.",
        ],
        "typical_education": [
            "Bachelor of Science in Computer Science",
            "Bachelor of Science in Cloud Computing / Systems Engineering",
            "Bachelor of Technology in Network Engineering",
        ],
        "project_templates": [
            "Provisioned HA Kubernetes clusters on AWS and Azure using modular Terraform IaC templates.",
            "Automated multi-stage Docker CI/CD pipelines and Linux monitoring stacks with GitHub Actions.",
            "Migrated monolithic workloads into fault-tolerant containerized cloud services on AWS.",
        ],
        "role_description": (
            "Architects, automates, and secures scalable cloud infrastructure using AWS, "
            "Azure, Docker, Kubernetes, Terraform, Linux, and CI/CD pipelines."
        ),
    },
    {
        "title": "Cybersecurity Analyst",
        "category": "Security",
        "interest_tags": ["security", "cybersecurity", "cloud", "networking"],
        "avg_salary": "$102,000 - $136,000",
        "demand_level": "Very High",
        "required_skills": [
            {"name": "Cybersecurity", "category": "Security", "weight": 1.5},
            {"name": "SIEM", "category": "Security", "weight": 1.5},
            {"name": "Network Security", "category": "Security", "weight": 1.5},
            {"name": "Linux", "category": "Cloud", "weight": 1.3},
            {"name": "Python", "category": "Programming", "weight": 1.1},
        ],
        "preferred_skills": [
            {"name": "AWS", "category": "Cloud", "weight": 0.8},
            {"name": "SQL", "category": "Data", "weight": 0.7},
            {"name": "Docker", "category": "Cloud", "weight": 0.6},
        ],
        "typical_experience": [
            "1-3 years in SOC monitoring, Splunk SIEM triage, firewall analysis, and incident response.",
            "Cybersecurity internship performing vulnerability assessments, Wireshark packet inspection, and OWASP audits.",
            "Hardened Linux endpoints, investigated security alerts, and authored threat detection rules.",
        ],
        "typical_education": [
            "Bachelor of Science in Cybersecurity",
            "Bachelor of Science in Information Security",
            "Bachelor of Science in Computer Science",
        ],
        "project_templates": [
            "Configured Splunk SIEM correlation alerts and automated Python log enrichment for SOC triage.",
            "Executed OWASP web vulnerability scans and Wireshark network traffic analysis on Linux labs.",
            "Built an automated firewall rule auditing and incident response playbook for cloud hosts.",
        ],
        "role_description": (
            "Protects enterprise systems and networks through SIEM monitoring, threat detection, "
            "vulnerability assessment, Network Security, Linux hardening, and Python scripting."
        ),
    },
]

# Cross-role realistic noise skills to prevent trivial memorization in synthetic samples
NOISE_SKILLS_POOL = [
    "Git", "SQL", "Python", "Docker", "Linux", "Excel", "REST APIs", "AWS", "HTML", "CSS",
    "Pandas", "JavaScript", "FastAPI", "Azure", "Machine Learning", "React", "Tableau",
]

# Shared, role-agnostic phrasing patterns so train/test never leak via role-exclusive sentences
SHARED_ACTION_VERBS = [
    "built", "developed", "implemented", "engineered", "maintained", "delivered",
    "designed", "optimized", "automated", "supported", "contributed to", "deployed",
]
SHARED_CONTEXTS = [
    "production workflows", "team deliverables", "internal platforms", "enterprise initiatives",
    "customer-facing features", "analytics initiatives", "scalable applications", "capstone projects",
]
SHARED_EXPERIENCE_LEVELS = [
    "recent graduate with academic project work",
    "1 year of internship and junior technical experience",
    "2 years of hands-on industry experience",
    "3 years of cross-functional engineering experience",
    "4 years of applied technical delivery experience",
]


def build_synthetic_career_dataset(
    samples_per_role: int = 50,
    seed: int = 42,
    save_to_disk: bool = True,
) -> List[Dict[str, Any]]:
    """Build a clearly labeled, template-leak-free synthetic dataset across all 12 career roles."""
    rng = random.Random(seed)
    rows: List[Dict[str, Any]] = []
    sample_idx = 1

    # Map adjacent roles for realistic cross-domain skill overlap
    role_by_cat: Dict[str, List[Dict[str, Any]]] = {}
    for r in CAREER_ROLE_CATALOG:
        role_by_cat.setdefault(r["category"], []).append(r)

    for role in CAREER_ROLE_CATALOG:
        req_names = [s["name"] for s in role["required_skills"]]
        pref_names = [s["name"] for s in role["preferred_skills"]]
        sibling_roles = [r for r in role_by_cat.get(role["category"], []) if r["title"] != role["title"]]

        for _ in range(samples_per_role):
            # Sample realistic partial subset of required skills (50% to 100%)
            min_req = max(2, int(len(req_names) * 0.5))
            k_req = rng.randint(min_req, len(req_names))
            chosen_req = rng.sample(req_names, k=k_req)

            k_pref = rng.randint(0, len(pref_names)) if pref_names else 0
            chosen_pref = rng.sample(pref_names, k=k_pref)

            # Inject realistic cross-role overlap (skills from sibling roles or common pool)
            overlap_pool = list(NOISE_SKILLS_POOL)
            if sibling_roles and rng.random() < 0.65:
                sib = rng.choice(sibling_roles)
                overlap_pool.extend(s["name"] for s in sib["required_skills"])

            extra_pool = list(dict.fromkeys(s for s in overlap_pool if s not in chosen_req and s not in chosen_pref))
            chosen_noise = rng.sample(extra_pool, k=rng.randint(1, min(3, len(extra_pool))))

            all_skills = list(dict.fromkeys(chosen_req + chosen_pref + chosen_noise))
            rng.shuffle(all_skills)

            # Compose unique, role-agnostic experience & project sentences (no repeated role-exclusive strings)
            exp_skills = rng.sample(all_skills, k=min(3, len(all_skills)))
            proj_skills = rng.sample(all_skills, k=min(3, len(all_skills)))
            experience = (
                f"{rng.choice(SHARED_EXPERIENCE_LEVELS)}; "
                f"{rng.choice(SHARED_ACTION_VERBS)} {rng.choice(SHARED_CONTEXTS)} "
                f"using {', '.join(exp_skills)}."
            )
            project = (
                f"{rng.choice(SHARED_ACTION_VERBS).capitalize()} a solution for "
                f"{rng.choice(SHARED_CONTEXTS)} leveraging {', '.join(proj_skills)}."
            )
            education = rng.choice(role["typical_education"])

            profile_text = (
                f"Skills: {', '.join(all_skills)}. "
                f"Education: {education}. "
                f"Experience: {experience} "
                f"Project: {project}"
            )

            rows.append(
                {
                    "sample_id": f"syn_{sample_idx:04d}",
                    "career_role": role["title"],
                    "required_skills": ", ".join(chosen_req),
                    "preferred_skills": ", ".join(chosen_pref),
                    "experience": experience,
                    "education": education,
                    "projects": project,
                    "role_description": role["role_description"],
                    "profile_text": profile_text,
                    "is_synthetic": True,
                }
            )
            sample_idx += 1

    if save_to_disk:
        PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        fieldnames = list(rows[0].keys())
        with DATASET_CSV_PATH.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        with CATALOG_JSON_PATH.open("w", encoding="utf-8") as fh:
            json.dump(
                {
                    "provenance": DATASET_PROVENANCE,
                    "is_synthetic": True,
                    "role_count": len(CAREER_ROLE_CATALOG),
                    "roles": CAREER_ROLE_CATALOG,
                },
                fh,
                indent=2,
            )

    return rows
