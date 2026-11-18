"""Canonical technical & soft skill taxonomy with synonym normalization and ambiguity rules."""

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass(frozen=True)
class SkillDefinition:
    canonical: str
    category: str
    aliases: List[str] = field(default_factory=list)
    ambiguous_aliases: Set[str] = field(default_factory=set)
    context_keywords: Set[str] = field(default_factory=set)
    negative_patterns: List[str] = field(default_factory=list)


TECHNICAL_SKILL_DEFINITIONS: List[SkillDefinition] = [
    # --- Programming ---
    SkillDefinition(
        canonical="Python",
        category="Programming",
        aliases=["Python", "Python3", "Python 3"],
        context_keywords={"django", "fastapi", "flask", "pandas", "numpy", "pytest", "script", "backend", "data"},
    ),
    SkillDefinition(
        canonical="Java",
        category="Programming",
        aliases=["Java", "Java SE", "Java EE", "Spring Boot"],
        ambiguous_aliases={"Java"},
        context_keywords={"spring", "jvm", "maven", "gradle", "backend", "oop", "android", "programming", "languages", "jdk"},
        negative_patterns=[r"\bjava\s+coffee\b", r"\bjavascript\b"],
    ),
    SkillDefinition(
        canonical="C++",
        category="Programming",
        aliases=["C++", "CPP", "C plus plus"],
        ambiguous_aliases={"CPP"},
        context_keywords={"stl", "cmake", "c", "algorithms", "systems", "embedded", "programming", "languages"},
    ),
    SkillDefinition(
        canonical="JavaScript",
        category="Programming",
        aliases=["JavaScript", "JS", "ES6", "ECMAScript"],
        ambiguous_aliases={"JS"},
        context_keywords={"react", "node", "frontend", "web", "html", "css", "typescript", "dom", "programming", "skills"},
    ),
    SkillDefinition(
        canonical="TypeScript",
        category="Programming",
        aliases=["TypeScript", "TS"],
        ambiguous_aliases={"TS"},
        context_keywords={"react", "javascript", "node", "angular", "next.js", "frontend", "typed", "skills"},
    ),
    SkillDefinition(
        canonical="Go",
        category="Programming",
        aliases=["Golang", "Go"],
        ambiguous_aliases={"Go"},
        context_keywords={"golang", "microservices", "goroutines", "gin", "backend", "docker", "kubernetes", "programming"},
        negative_patterns=[
            r"\bgo\s+(?:to|above|beyond|through|into|back|forward|with|from|on|out|up|down)\b",
            r"\bto\s+go\b",
        ],
    ),
    SkillDefinition(
        canonical="C#",
        category="Programming",
        aliases=["C#", "CSharp", "C-Sharp"],
        context_keywords={".net", "dotnet", "asp.net", "unity", "backend", "programming"},
    ),
    SkillDefinition(
        canonical="R",
        category="Programming",
        aliases=["R Programming", "RStudio", "R"],
        ambiguous_aliases={"R"},
        context_keywords={"rstudio", "ggplot", "tidyverse", "statistics", "data", "python", "sql", "sas", "analytics"},
    ),

    # --- Data ---
    SkillDefinition(
        canonical="SQL",
        category="Data",
        aliases=["SQL", "MySQL", "PostgreSQL", "Postgres", "SQLite", "T-SQL", "PL/SQL", "NoSQL"],
        context_keywords={"database", "queries", "query", "relational", "etl", "schema", "data", "postgres", "mysql"},
    ),
    SkillDefinition(
        canonical="Excel",
        category="Data",
        aliases=["Microsoft Excel", "MS Excel", "Excel"],
        ambiguous_aliases={"Excel"},
        context_keywords={"vlookup", "pivot", "spreadsheets", "spreadsheet", "macros", "vba", "power bi", "tableau", "sql", "analytics", "data", "skills"},
        negative_patterns=[r"\bexcel(?:s|led|ling)?\s+(?:at|in|as)\b", r"\bstrive\s+to\s+excel\b"],
    ),
    SkillDefinition(
        canonical="Power BI",
        category="Data",
        aliases=["Power BI", "PowerBI", "Microsoft Power BI"],
        context_keywords={"dax", "dashboard", "dashboards", "bi", "tableau", "reporting", "analytics", "sql"},
    ),
    SkillDefinition(
        canonical="Tableau",
        category="Data",
        aliases=["Tableau", "Tableau Desktop", "Tableau Server"],
        context_keywords={"dashboard", "visualization", "bi", "power bi", "sql", "analytics", "data"},
    ),
    SkillDefinition(
        canonical="Pandas",
        category="Data",
        aliases=["Pandas"],
        context_keywords={"python", "numpy", "dataframe", "data", "cleaning", "analysis", "scikit-learn"},
    ),
    SkillDefinition(
        canonical="NumPy",
        category="Data",
        aliases=["NumPy", "Numpy"],
        context_keywords={"python", "pandas", "scipy", "arrays", "matrix", "machine learning", "data"},
    ),

    # --- AI/ML ---
    SkillDefinition(
        canonical="Machine Learning",
        category="AI/ML",
        aliases=["Machine Learning", "ML", "Scikit-learn", "Scikit Learn", "sklearn"],
        ambiguous_aliases={"ML"},
        context_keywords={"model", "models", "python", "ai", "deep learning", "nlp", "classification", "regression", "scikit", "tensorflow", "pytorch", "data", "training", "skills"},
        negative_patterns=[r"\b\d+\s*ml\b", r"\bmilliliter", r"\bml\s+of\b"],
    ),
    SkillDefinition(
        canonical="Deep Learning",
        category="AI/ML",
        aliases=["Deep Learning", "DL", "Neural Networks", "CNN", "RNN", "Transformers"],
        ambiguous_aliases={"DL"},
        context_keywords={"pytorch", "tensorflow", "keras", "neural", "cnn", "transformer", "machine learning", "gpu", "ai"},
    ),
    SkillDefinition(
        canonical="Natural Language Processing",
        category="AI/ML",
        aliases=["Natural Language Processing", "NLP", "spaCy", "NLTK", "Hugging Face", "Text Mining"],
        ambiguous_aliases={"NLP"},
        context_keywords={"spacy", "nltk", "transformers", "bert", "llm", "text", "tokenization", "machine learning", "ai", "python", "skills"},
    ),
    SkillDefinition(
        canonical="TensorFlow",
        category="AI/ML",
        aliases=["TensorFlow", "Tensorflow", "Keras", "TF"],
        ambiguous_aliases={"TF"},
        context_keywords={"keras", "pytorch", "deep learning", "machine learning", "neural", "python", "model"},
    ),
    SkillDefinition(
        canonical="PyTorch",
        category="AI/ML",
        aliases=["PyTorch", "Pytorch", "Torch"],
        ambiguous_aliases={"Torch"},
        context_keywords={"deep learning", "neural", "tensorflow", "python", "cuda", "transformers", "model"},
    ),

    # --- Web ---
    SkillDefinition(
        canonical="React",
        category="Web",
        aliases=["React", "React.js", "ReactJS"],
        ambiguous_aliases={"React"},
        context_keywords={"javascript", "typescript", "redux", "next.js", "vite", "frontend", "jsx", "hooks", "html", "css", "web", "ui", "tailwind", "node"},
        negative_patterns=[r"\breact(?:ed|ing|s)?\s+(?:to|quickly|positively|under|calmly|effectively)\b"],
    ),
    SkillDefinition(
        canonical="Node.js",
        category="Web",
        aliases=["Node.js", "NodeJS", "Node JS", "Express.js", "ExpressJS"],
        context_keywords={"javascript", "express", "npm", "backend", "api", "react", "typescript", "web"},
    ),
    SkillDefinition(
        canonical="HTML",
        category="Web",
        aliases=["HTML", "HTML5"],
        context_keywords={"css", "javascript", "web", "frontend", "react", "dom", "markup"},
    ),
    SkillDefinition(
        canonical="CSS",
        category="Web",
        aliases=["CSS", "CSS3", "Tailwind CSS", "TailwindCSS", "SASS", "SCSS"],
        context_keywords={"html", "javascript", "frontend", "responsive", "react", "ui", "web", "tailwind"},
    ),
    SkillDefinition(
        canonical="FastAPI",
        category="Web",
        aliases=["FastAPI", "Fast API"],
        context_keywords={"python", "pydantic", "uvicorn", "rest", "api", "sqlalchemy", "backend"},
    ),
    SkillDefinition(
        canonical="REST APIs",
        category="Web",
        aliases=["REST API", "REST APIs", "RESTful API", "RESTful APIs", "GraphQL"],
        context_keywords={"http", "json", "fastapi", "node", "backend", "microservices", "endpoint"},
    ),

    # --- Cloud ---
    SkillDefinition(
        canonical="AWS",
        category="Cloud",
        aliases=["AWS", "Amazon Web Services", "EC2", "S3", "AWS Lambda"],
        context_keywords={"cloud", "ec2", "s3", "lambda", "rds", "iam", "docker", "devops", "terraform", "deploy"},
    ),
    SkillDefinition(
        canonical="Azure",
        category="Cloud",
        aliases=["Azure", "Microsoft Azure", "Azure DevOps"],
        context_keywords={"cloud", "microsoft", "devops", "kubernetes", "docker", "aws", "ci/cd"},
    ),
    SkillDefinition(
        canonical="Docker",
        category="Cloud",
        aliases=["Docker", "Docker Compose", "Dockerfile", "Containerization"],
        context_keywords={"kubernetes", "container", "containers", "ci/cd", "devops", "aws", "deploy", "linux"},
    ),
    SkillDefinition(
        canonical="Kubernetes",
        category="Cloud",
        aliases=["Kubernetes", "K8s", "Helm"],
        ambiguous_aliases={"Helm"},
        context_keywords={"docker", "containers", "pods", "cloud", "aws", "azure", "devops", "ci/cd", "orchestration"},
    ),
    SkillDefinition(
        canonical="Git",
        category="Cloud",
        aliases=["Git", "GitHub", "GitLab", "GitHub Actions", "CI/CD"],
        context_keywords={"version control", "branch", "pull request", "pipeline", "devops", "docker", "code"},
    ),
    SkillDefinition(
        canonical="Terraform",
        category="Cloud",
        aliases=["Terraform", "Infrastructure as Code", "IaC", "CloudFormation"],
        context_keywords={"aws", "azure", "gcp", "cloud", "kubernetes", "docker", "devops", "infrastructure"},
    ),
    SkillDefinition(
        canonical="Linux",
        category="Cloud",
        aliases=["Linux", "Ubuntu", "Bash", "Shell Scripting"],
        context_keywords={"server", "docker", "cloud", "aws", "security", "networking", "devops", "cli"},
    ),
    SkillDefinition(
        canonical="Spark",
        category="Data",
        aliases=["Apache Spark", "PySpark", "Spark", "Airflow", "Apache Airflow", "ETL"],
        ambiguous_aliases={"Spark"},
        context_keywords={"data", "etl", "pipeline", "sql", "python", "hadoop", "warehouse", "big data", "airflow"},
    ),
    SkillDefinition(
        canonical="Cybersecurity",
        category="Security",
        aliases=["Cybersecurity", "Information Security", "InfoSec", "SOC", "Threat Analysis", "Vulnerability Assessment"],
        context_keywords={"siem", "security", "network", "firewall", "incident", "penetration", "splunk", "compliance"},
    ),
    SkillDefinition(
        canonical="SIEM",
        category="Security",
        aliases=["SIEM", "Splunk", "QRadar", "Microsoft Sentinel", "Incident Response"],
        context_keywords={"security", "soc", "logs", "alerts", "cybersecurity", "threat", "monitoring"},
    ),
    SkillDefinition(
        canonical="Network Security",
        category="Security",
        aliases=["Network Security", "Firewalls", "Wireshark", "IDS/IPS", "Penetration Testing", "OWASP"],
        context_keywords={"security", "tcp/ip", "firewall", "cybersecurity", "vulnerability", "nmap", "linux"},
    ),
    SkillDefinition(
        canonical="Business Analysis",
        category="Business",
        aliases=["Business Analysis", "Requirements Gathering", "BRD", "FRD", "Stakeholder Management", "JIRA", "KPI Reporting"],
        context_keywords={"requirements", "business", "stakeholders", "sql", "excel", "power bi", "tableau", "agile", "process"},
    ),
]


SOFT_SKILL_DEFINITIONS: List[SkillDefinition] = [
    SkillDefinition(
        canonical="Communication",
        category="Soft Skills",
        aliases=["Communication", "Technical Writing", "Stakeholder Communication", "Presentation Skills", "Public Speaking"],
        context_keywords={"team", "stakeholders", "presented", "documentation", "clients", "cross-functional"},
    ),
    SkillDefinition(
        canonical="Leadership",
        category="Soft Skills",
        aliases=["Leadership", "Team Lead", "Led a team", "Mentoring", "Mentored"],
        context_keywords={"team", "led", "managed", "mentored", "guided", "coordinated", "project"},
    ),
    SkillDefinition(
        canonical="Teamwork & Collaboration",
        category="Soft Skills",
        aliases=["Teamwork", "Collaboration", "Cross-functional", "Collaborated"],
        context_keywords={"team", "engineers", "designers", "agile", "scrum", "stakeholders", "product"},
    ),
    SkillDefinition(
        canonical="Problem Solving",
        category="Soft Skills",
        aliases=["Problem Solving", "Problem-Solving", "Troubleshooting", "Analytical Thinking"],
        context_keywords={"debugged", "resolved", "root cause", "optimized", "complex", "analysis"},
    ),
    SkillDefinition(
        canonical="Agile & Scrum",
        category="Soft Skills",
        aliases=["Agile", "Scrum", "Kanban", "Sprint Planning"],
        context_keywords={"sprints", "jira", "standups", "retrospective", "product", "delivery"},
    ),
    SkillDefinition(
        canonical="Project Management",
        category="Soft Skills",
        aliases=["Project Management", "Time Management", "Prioritization", "Roadmap Planning"],
        context_keywords={"delivered", "deadlines", "milestones", "scope", "planning", "coordination"},
    ),
]


def build_synonym_lookup() -> Dict[str, str]:
    """Return lowercase alias -> canonical skill name map."""
    lookup: Dict[str, str] = {}
    for definition in TECHNICAL_SKILL_DEFINITIONS + SOFT_SKILL_DEFINITIONS:
        lookup[definition.canonical.lower()] = definition.canonical
        for alias in definition.aliases:
            lookup[alias.lower()] = definition.canonical
    return lookup


SYNONYM_MAP: Dict[str, str] = build_synonym_lookup()
