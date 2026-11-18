"""Curated, verified learning resource catalog & curriculum templates for SkillGap AI.

All URLs below are canonical, verified public URLs from trusted educational platforms:
Official Documentation, freeCodeCamp, Coursera, edX, Kaggle, and official YouTube channels.
"""

from typing import Any, Dict, List

TRUSTED_RESOURCE_DOMAINS = (
    "docs.python.org",
    "www.freecodecamp.org",
    "www.coursera.org",
    "www.edx.org",
    "www.kaggle.com",
    "www.youtube.com",
    "www.postgresql.org",
    "pandas.pydata.org",
    "numpy.org",
    "scikit-learn.org",
    "spacy.io",
    "www.nltk.org",
    "huggingface.co",
    "www.tensorflow.org",
    "pytorch.org",
    "react.dev",
    "developer.mozilla.org",
    "www.typescriptlang.org",
    "nodejs.org",
    "fastapi.tiangolo.com",
    "docs.pydantic.dev",
    "restfulapi.net",
    "docs.docker.com",
    "kubernetes.io",
    "docs.aws.amazon.com",
    "aws.amazon.com",
    "learn.microsoft.com",
    "developer.hashicorp.com",
    "ubuntu.com",
    "git-scm.com",
    "docs.github.com",
    "support.microsoft.com",
    "www.tableau.com",
    "spark.apache.org",
    "dev.java",
    "en.cppreference.com",
    "owasp.org",
    "go.dev",
)

SKILL_CURRICULUM_CATALOG: Dict[str, Dict[str, Any]] = {
    "Python": {
        "category": "Programming",
        "objectives": [
            "Write clean, modular Python using functions, OOP, virtual environments, and type hints.",
            "Handle files, JSON/CSV datasets, error handling, and automated unit tests with pytest.",
        ],
        "exercises": [
            "Implement a CLI data parser using pathlib, dataclasses, and exception handling.",
            "Write 10 unit tests covering edge cases with pytest fixtures.",
        ],
        "mini_project": "Build a modular Python log analyzer & CSV summary reporter with pytest coverage.",
        "checkpoint": "Pass a timed Python refactoring & debugging exercise with 100% pytest pass rate.",
        "resources": [
            {"title": "Official Python 3 Tutorial", "source": "Official Documentation", "url": "https://docs.python.org/3/tutorial/"},
            {"title": "Scientific Computing with Python", "source": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/"},
            {"title": "Kaggle Learn: Python", "source": "Kaggle", "url": "https://www.kaggle.com/learn/python"},
        ],
    },
    "SQL": {
        "category": "Data",
        "objectives": [
            "Master SELECT, JOINs, GROUP BY, CTEs, and window functions for analytical querying.",
            "Design normalized relational schemas with primary/foreign keys and B-tree indexes.",
        ],
        "exercises": [
            "Write multi-table JOIN and window-function queries (RANK, LAG, running totals) on sample order tables.",
            "Analyze slow queries with EXPLAIN ANALYZE and add appropriate composite indexes.",
        ],
        "mini_project": "Design and query a PostgreSQL student career & job analytics database with 15 KPI queries.",
        "checkpoint": "Solve 8 SQL analytical query challenges covering CTEs, aggregations, and schema indexing.",
        "resources": [
            {"title": "PostgreSQL Official Tutorial", "source": "Official Documentation", "url": "https://www.postgresql.org/docs/current/tutorial.html"},
            {"title": "Intro to SQL", "source": "Kaggle", "url": "https://www.kaggle.com/learn/intro-to-sql"},
            {"title": "Relational Database Certification", "source": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/relational-database/"},
        ],
    },
    "Pandas": {
        "category": "Data",
        "objectives": [
            "Clean messy real-world datasets: handle missing values, duplicates, types, and merges.",
            "Perform vectorized aggregations, groupby pipelines, and time-series resampling.",
        ],
        "exercises": [
            "Clean a multi-file CSV dataset with nulls, malformed dates, and inconsistent categories.",
            "Build a chained groupby + pivot summary pipeline exporting clean Parquet/CSV outputs.",
        ],
        "mini_project": "Create an automated job-market salary & skill demand ETL notebook in Pandas.",
        "checkpoint": "Reproduce a clean end-to-end exploratory data analysis report without Python for-loops.",
        "resources": [
            {"title": "Pandas Getting Started Guides", "source": "Official Documentation", "url": "https://pandas.pydata.org/docs/getting_started/index.html"},
            {"title": "Kaggle Learn: Pandas", "source": "Kaggle", "url": "https://www.kaggle.com/learn/pandas"},
        ],
    },
    "NumPy": {
        "category": "Data",
        "objectives": [
            "Use N-dimensional arrays, broadcasting, masking, and linear algebra primitives efficiently.",
            "Implement cosine similarity, normalization, and statistical summaries using vectorized NumPy.",
        ],
        "exercises": [
            "Compute pairwise cosine similarity matrices across 1,000 vectors using NumPy broadcasting.",
            "Benchmark vectorized NumPy operations against pure Python loops.",
        ],
        "mini_project": "Build a fast NumPy vector similarity search helper for skill embeddings.",
        "checkpoint": "Implement matrix normalization and dot-product ranking from scratch in NumPy.",
        "resources": [
            {"title": "NumPy Quickstart Tutorial", "source": "Official Documentation", "url": "https://numpy.org/doc/stable/user/quickstart.html"},
            {"title": "freeCodeCamp Data Analysis with Python", "source": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/data-analysis-with-python/"},
        ],
    },
    "Machine Learning": {
        "category": "AI/ML",
        "objectives": [
            "Understand supervised vs. unsupervised learning, bias-variance tradeoff, and cross-validation.",
            "Build leak-free Scikit-learn pipelines with feature preprocessing and rigorous metric evaluation.",
        ],
        "exercises": [
            "Train and compare Logistic Regression, LinearSVC, and Random Forest on a stratified split.",
            "Inspect precision, recall, F1-score, ROC-AUC, and confusion matrices to diagnose errors.",
        ],
        "mini_project": "Build and evaluate a multi-class tabular/text classification pipeline in Scikit-learn.",
        "checkpoint": "Explain train/test leakage prevention and interpret a multi-class confusion matrix.",
        "resources": [
            {"title": "Scikit-learn Official User Guide", "source": "Official Documentation", "url": "https://scikit-learn.org/stable/user_guide.html"},
            {"title": "Intro to Machine Learning", "source": "Kaggle", "url": "https://www.kaggle.com/learn/intro-to-machine-learning"},
            {"title": "Machine Learning Specialization", "source": "Coursera", "url": "https://www.coursera.org/specializations/machine-learning-introduction"},
        ],
    },
    "Deep Learning": {
        "category": "AI/ML",
        "objectives": [
            "Understand neural network layers, backpropagation, regularization, and optimization.",
            "Fine-tune pretrained architectures and monitor training vs. validation loss curves.",
        ],
        "exercises": [
            "Implement a multi-layer perceptron with dropout and early stopping on a benchmark dataset.",
            "Diagnose overfitting vs. underfitting using learning rate schedules and weight decay.",
        ],
        "mini_project": "Train and evaluate a neural classifier with reproducible checkpoints and validation metrics.",
        "checkpoint": "Explain gradient descent, batch normalization, and overfitting mitigation clearly.",
        "resources": [
            {"title": "Intro to Deep Learning", "source": "Kaggle", "url": "https://www.kaggle.com/learn/intro-to-deep-learning"},
            {"title": "Deep Learning Specialization", "source": "Coursera", "url": "https://www.coursera.org/specializations/deep-learning"},
            {"title": "3Blue1Brown Neural Networks Series", "source": "YouTube", "url": "https://www.youtube.com/@3blue1brown"},
        ],
    },
    "Natural Language Processing": {
        "category": "AI/ML",
        "objectives": [
            "Build tokenization, lemmatization, NER, TF-IDF, and sentence-embedding NLP workflows.",
            "Evaluate entity extraction precision/recall and prevent false-positive keyword matches.",
        ],
        "exercises": [
            "Build a spaCy + NLTK preprocessing pipeline extracting entities and clean sentences.",
            "Compute semantic similarity between documents using Sentence Transformers embeddings.",
        ],
        "mini_project": "Create a semantic document search & taxonomy tagging tool with evidence snippets.",
        "checkpoint": "Demonstrate accurate synonym normalization and semantic similarity threshold tuning.",
        "resources": [
            {"title": "spaCy 101 Official Guide", "source": "Official Documentation", "url": "https://spacy.io/usage/spacy-101"},
            {"title": "Hugging Face NLP Course", "source": "Official Documentation", "url": "https://huggingface.co/learn/nlp-course/chapter1/1"},
            {"title": "NLTK Book Online", "source": "Official Documentation", "url": "https://www.nltk.org/book/"},
        ],
    },
    "TensorFlow": {
        "category": "AI/ML",
        "objectives": [
            "Build, compile, train, and export Keras/TensorFlow neural models using tf.data pipelines.",
            "Apply transfer learning and save models in SavedModel/Keras formats for inference.",
        ],
        "exercises": [
            "Construct a tf.data input pipeline with batching and prefetching.",
            "Train a text or tabular Keras Sequential/Functional model with EarlyStopping callbacks.",
        ],
        "mini_project": "Build and export a TensorFlow text classifier served behind a Python inference function.",
        "checkpoint": "Train, serialize, reload, and verify identical inference outputs in TensorFlow.",
        "resources": [
            {"title": "TensorFlow Official Tutorials", "source": "Official Documentation", "url": "https://www.tensorflow.org/tutorials"},
            {"title": "DeepLearning.AI TensorFlow Developer", "source": "Coursera", "url": "https://www.coursera.org/professional-certificates/tensorflow-in-practice"},
        ],
    },
    "PyTorch": {
        "category": "AI/ML",
        "objectives": [
            "Master PyTorch tensors, autograd, Dataset/DataLoader, and custom nn.Module training loops.",
            "Save and load model state_dicts and run deterministic eval-mode inference.",
        ],
        "exercises": [
            "Write a clean PyTorch training and validation loop with AdamW and CrossEntropyLoss.",
            "Fine-tune a pretrained transformer encoder on a classification benchmark.",
        ],
        "mini_project": "Implement a PyTorch multi-class text classifier with validation F1 tracking.",
        "checkpoint": "Build a custom nn.Module and verify tensor shapes, gradients, and checkpoint loading.",
        "resources": [
            {"title": "PyTorch Official Tutorials", "source": "Official Documentation", "url": "https://pytorch.org/tutorials/"},
            {"title": "freeCodeCamp PyTorch Tutorials", "source": "freeCodeCamp", "url": "https://www.freecodecamp.org/news/tag/pytorch/"},
        ],
    },
    "React": {
        "category": "Web",
        "objectives": [
            "Build modular React components using hooks (useState, useEffect, useMemo, useCallback), Context, and Router.",
            "Integrate REST APIs with loading, error, and empty states cleanly.",
        ],
        "exercises": [
            "Build a filterable, searchable card dashboard backed by async Axios API state.",
            "Implement accessible forms with client-side validation and optimistic UI updates.",
        ],
        "mini_project": "Create a responsive multi-page React + Tailwind SaaS dashboard with live API persistence.",
        "checkpoint": "Pass a component architecture review covering state lifting, code splitting, and zero console errors.",
        "resources": [
            {"title": "React Official Learn Docs", "source": "Official Documentation", "url": "https://react.dev/learn"},
            {"title": "Front End Development Libraries", "source": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/front-end-development-libraries/"},
        ],
    },
    "JavaScript": {
        "category": "Programming",
        "objectives": [
            "Master ES6+ syntax, closures, promises, async/await, array methods, and modules.",
            "Debug browser runtime state, network requests, and DOM/event lifecycles effectively.",
        ],
        "exercises": [
            "Solve 15 ES6 data transformation & async Promise.all exercises.",
            "Build a debounced search utility and localStorage persistence helper.",
        ],
        "mini_project": "Build an interactive browser-based API explorer with fetch/Axios error handling.",
        "checkpoint": "Explain event loop execution order, closures, and async error propagation.",
        "resources": [
            {"title": "MDN JavaScript Guide", "source": "Official Documentation", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"},
            {"title": "JavaScript Algorithms & Data Structures", "source": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures-v8/"},
        ],
    },
    "TypeScript": {
        "category": "Programming",
        "objectives": [
            "Design strict interfaces, union types, generics, and typed API client contracts.",
            "Eliminate null/undefined runtime bugs using TypeScript strict mode.",
        ],
        "exercises": [
            "Convert a JavaScript Axios service layer and React component tree to strict TypeScript.",
            "Write generic utility types for paginated API responses.",
        ],
        "mini_project": "Build a type-safe task tracker frontend with strict TypeScript and Zod/schema validation.",
        "checkpoint": "Compile a multi-module React + TypeScript project with zero `any` escapes.",
        "resources": [
            {"title": "TypeScript Official Handbook", "source": "Official Documentation", "url": "https://www.typescriptlang.org/docs/handbook/intro.html"},
            {"title": "freeCodeCamp YouTube Channel", "source": "YouTube", "url": "https://www.youtube.com/@freecodecamp"},
        ],
    },
    "HTML": {
        "category": "Web",
        "objectives": [
            "Author semantic HTML5 landmarks, accessible forms, and SEO-friendly document structure.",
        ],
        "exercises": [
            "Audit and refactor a multi-section page using semantic header, nav, main, article, and ARIA labels.",
        ],
        "mini_project": "Build a WCAG-accessible landing page and signup form.",
        "checkpoint": "Verify full keyboard navigation and zero semantic accessibility violations.",
        "resources": [
            {"title": "MDN Learn Web Development", "source": "Official Documentation", "url": "https://developer.mozilla.org/en-US/docs/Learn"},
            {"title": "Responsive Web Design Certification", "source": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/"},
        ],
    },
    "CSS": {
        "category": "Web",
        "objectives": [
            "Master Flexbox, CSS Grid, responsive breakpoints, design tokens, and Tailwind CSS utility architecture.",
        ],
        "exercises": [
            "Build a responsive 12-column SaaS layout that adapts cleanly from 375px mobile to 1440px desktop.",
        ],
        "mini_project": "Create a reusable SaaS UI card & sidebar component library in CSS/Tailwind.",
        "checkpoint": "Verify zero horizontal overflow across mobile, tablet, and desktop viewports.",
        "resources": [
            {"title": "MDN Learn CSS", "source": "Official Documentation", "url": "https://developer.mozilla.org/en-US/docs/Learn"},
            {"title": "Responsive Web Design", "source": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/"},
        ],
    },
    "Node.js": {
        "category": "Web",
        "objectives": [
            "Build asynchronous REST services, Express middleware, input validation, and environment config in Node.js.",
        ],
        "exercises": [
            "Implement a Node.js REST API with JWT authentication, error middleware, and structured logging.",
        ],
        "mini_project": "Build a Node.js + Express job bookmarking microservice with automated API tests.",
        "checkpoint": "Demonstrate non-blocking async I/O handling and clean REST status code design.",
        "resources": [
            {"title": "Node.js Official Learn Guides", "source": "Official Documentation", "url": "https://nodejs.org/en/learn/getting-started/introduction-to-nodejs"},
            {"title": "Back End Development and APIs", "source": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/back-end-development-and-apis/"},
        ],
    },
    "FastAPI": {
        "category": "Web",
        "objectives": [
            "Design modular FastAPI routers, Pydantic v2 schemas, dependency injection, and SQLAlchemy persistence.",
            "Secure endpoints with JWT Bearer auth, CORS configuration, and TestClient integration tests.",
        ],
        "exercises": [
            "Build CRUD routes with Pydantic validation, dependency-injected DB sessions, and proper HTTP status codes.",
            "Write pytest + TestClient tests verifying auth protection and validation errors.",
        ],
        "mini_project": "Build a containerized FastAPI microservice with Alembic migrations and OpenAPI docs.",
        "checkpoint": "Achieve 100% passing API integration tests covering happy paths and 401/404/422 errors.",
        "resources": [
            {"title": "FastAPI Official Tutorial", "source": "Official Documentation", "url": "https://fastapi.tiangolo.com/tutorial/"},
            {"title": "Pydantic V2 Official Docs", "source": "Official Documentation", "url": "https://docs.pydantic.dev/latest/"},
        ],
    },
    "REST APIs": {
        "category": "Web",
        "objectives": [
            "Design consistent resource URIs, HTTP verbs, idempotent PATCH/PUT semantics, pagination, and auth headers.",
        ],
        "exercises": [
            "Design an OpenAPI 3 specification covering pagination, filtering, and standard error schemas.",
        ],
        "mini_project": "Document and test a full REST API contract using OpenAPI Swagger UI and httpx.",
        "checkpoint": "Audit an API for proper 200/201/400/401/404/409/422 status code usage.",
        "resources": [
            {"title": "MDN HTTP & REST Overview", "source": "Official Documentation", "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP"},
            {"title": "RESTful API Design Guide", "source": "Official Documentation", "url": "https://restfulapi.net/"},
        ],
    },
    "Docker": {
        "category": "Cloud",
        "objectives": [
            "Author lean multi-stage Dockerfiles, .dockerignore files, and multi-service Docker Compose stacks.",
            "Debug container networking, healthchecks, volumes, and environment variable injection.",
        ],
        "exercises": [
            "Containerize a FastAPI backend and React frontend with healthchecks and shared Compose bridge network.",
            "Optimize Docker layer caching to cut rebuild times by >50%.",
        ],
        "mini_project": "Orchestrate a 3-tier React + FastAPI + PostgreSQL app locally with Docker Compose.",
        "checkpoint": "Bring up a clean full-stack environment from scratch using `docker compose up --build`.",
        "resources": [
            {"title": "Docker Official Get Started", "source": "Official Documentation", "url": "https://docs.docker.com/get-started/"},
            {"title": "TechWorld with Nana (Docker & DevOps)", "source": "YouTube", "url": "https://www.youtube.com/@TechWorldwithNana"},
        ],
    },
    "Kubernetes": {
        "category": "Cloud",
        "objectives": [
            "Understand Pods, Deployments, Services, ConfigMaps, Secrets, and readiness/liveness probes.",
            "Manage rolling updates, horizontal scaling, and cluster troubleshooting via kubectl.",
        ],
        "exercises": [
            "Write Deployment and Service YAML manifests for a containerized web API with health probes.",
            "Perform a zero-downtime rolling update and rollback in a local cluster.",
        ],
        "mini_project": "Deploy a 2-service containerized web app to a local Kubernetes cluster with ConfigMaps.",
        "checkpoint": "Diagnose a failing Pod using kubectl describe and logs.",
        "resources": [
            {"title": "Kubernetes Official Tutorials", "source": "Official Documentation", "url": "https://kubernetes.io/docs/tutorials/"},
            {"title": "Introduction to Kubernetes (Linux Foundation)", "source": "edX", "url": "https://www.edx.org/learn/kubernetes/the-linux-foundation-introduction-to-kubernetes"},
        ],
    },
    "AWS": {
        "category": "Cloud",
        "objectives": [
            "Configure core AWS building blocks: IAM least privilege, S3, EC2, RDS PostgreSQL, and CloudWatch.",
            "Deploy containerized APIs securely without hardcoding cloud credentials.",
        ],
        "exercises": [
            "Design an IAM role policy following least-privilege principles for an S3-backed backend.",
            "Map a 3-tier VPC architecture with public load balancer and private RDS subnet.",
        ],
        "mini_project": "Architect and document a production AWS deployment blueprint for a FastAPI + PostgreSQL app.",
        "checkpoint": "Pass a cloud architecture review covering IAM security, backups, and cost estimates.",
        "resources": [
            {"title": "AWS Official Documentation", "source": "Official Documentation", "url": "https://docs.aws.amazon.com/"},
            {"title": "AWS Training and Certification", "source": "Official Documentation", "url": "https://aws.amazon.com/training/"},
        ],
    },
    "Azure": {
        "category": "Cloud",
        "objectives": [
            "Deploy web apps, managed PostgreSQL, container instances, and RBAC policies on Microsoft Azure.",
        ],
        "exercises": [
            "Configure Azure App Service environment variables and managed identity access.",
        ],
        "mini_project": "Design an Azure Container Apps + Azure Database for PostgreSQL deployment guide.",
        "checkpoint": "Verify RBAC role assignments and CI/CD deployment workflow on Azure.",
        "resources": [
            {"title": "Microsoft Learn: Azure Docs", "source": "Official Documentation", "url": "https://learn.microsoft.com/en-us/azure/"},
            {"title": "Microsoft Azure Training Paths", "source": "Official Documentation", "url": "https://learn.microsoft.com/en-us/training/azure/"},
        ],
    },
    "Terraform": {
        "category": "Cloud",
        "objectives": [
            "Provision reproducible cloud infrastructure using HCL modules, state management, variables, and outputs.",
        ],
        "exercises": [
            "Write a modular Terraform configuration declaring VPC, storage, and managed database resources.",
        ],
        "mini_project": "Create a reusable Terraform IaC starter kit with `terraform fmt`, `validate`, and `plan`.",
        "checkpoint": "Explain remote state locking and drift detection in Terraform.",
        "resources": [
            {"title": "HashiCorp Terraform Tutorials", "source": "Official Documentation", "url": "https://developer.hashicorp.com/terraform/tutorials"},
        ],
    },
    "Linux": {
        "category": "Cloud",
        "objectives": [
            "Navigate Linux filesystems, permissions, systemd services, networking diagnostics, and Bash scripting.",
        ],
        "exercises": [
            "Write a Bash health-check and log rotation script using grep, awk, and curl.",
        ],
        "mini_project": "Automate local server environment diagnostics and backup checks via Bash.",
        "checkpoint": "Troubleshoot file permissions, open ports, and process signals cleanly from CLI.",
        "resources": [
            {"title": "Ubuntu Official Tutorials", "source": "Official Documentation", "url": "https://ubuntu.com/tutorials"},
            {"title": "Introduction to Linux (Linux Foundation)", "source": "edX", "url": "https://www.edx.org/learn/linux/the-linux-foundation-introduction-to-linux"},
        ],
    },
    "Git": {
        "category": "Cloud",
        "objectives": [
            "Use feature branching, interactive rebase/merge, pull request reviews, and GitHub Actions CI pipelines.",
        ],
        "exercises": [
            "Configure a GitHub Actions workflow running automated pytest and Vite builds on every PR.",
        ],
        "mini_project": "Set up a complete CI pipeline with branch protection and automated test reporting.",
        "checkpoint": "Resolve a realistic merge conflict cleanly without losing commit history.",
        "resources": [
            {"title": "Git Official Documentation", "source": "Official Documentation", "url": "https://git-scm.com/doc"},
            {"title": "GitHub Get Started Docs", "source": "Official Documentation", "url": "https://docs.github.com/en/get-started"},
        ],
    },
    "Excel": {
        "category": "Data",
        "objectives": [
            "Master XLOOKUP/INDEX-MATCH, Pivot Tables, Power Query, conditional formatting, and KPI modeling.",
        ],
        "exercises": [
            "Build a dynamic monthly revenue & variance tracker using Pivot Tables and slicers.",
        ],
        "mini_project": "Create an executive financial/KPI workbook with automated summary dashboards.",
        "checkpoint": "Clean a 5,000-row raw export and generate an error-free Pivot summary in 30 minutes.",
        "resources": [
            {"title": "Microsoft Excel Official Help & Learning", "source": "Official Documentation", "url": "https://support.microsoft.com/en-us/excel"},
            {"title": "Excel Skills on Coursera", "source": "Coursera", "url": "https://www.coursera.org/learn/excel-essentials"},
        ],
    },
    "Power BI": {
        "category": "Data",
        "objectives": [
            "Model star schemas, write DAX measures, and build interactive drill-down business dashboards.",
        ],
        "exercises": [
            "Build a star-schema data model with YoY growth and moving-average DAX measures.",
        ],
        "mini_project": "Publish an interactive multi-page sales & operations Power BI dashboard.",
        "checkpoint": "Explain star schema relationships and row-level filter context in DAX.",
        "resources": [
            {"title": "Microsoft Learn: Power BI Training", "source": "Official Documentation", "url": "https://learn.microsoft.com/en-us/training/powerplatform/power-bi"},
        ],
    },
    "Tableau": {
        "category": "Data",
        "objectives": [
            "Design clear analytical dashboards using calculated fields, LOD expressions, filters, and story points.",
        ],
        "exercises": [
            "Build a cohort retention heatmap and KPI overview dashboard in Tableau.",
        ],
        "mini_project": "Create a public Tableau portfolio workbook analyzing open industry employment trends.",
        "checkpoint": "Implement fixed LOD expressions and interactive cross-sheet filter actions.",
        "resources": [
            {"title": "Tableau Official Free Training", "source": "Official Documentation", "url": "https://www.tableau.com/learn/training"},
        ],
    },
    "Spark": {
        "category": "Data",
        "objectives": [
            "Process large-scale datasets using PySpark DataFrames, partitioning, joins, and ETL job orchestration.",
        ],
        "exercises": [
            "Write a PySpark batch transformation reading CSV/JSON into partitioned Parquet tables.",
        ],
        "mini_project": "Build an automated PySpark data ingestion and aggregation ETL pipeline.",
        "checkpoint": "Explain Spark lazy evaluation, shuffles, and partition tuning.",
        "resources": [
            {"title": "Apache Spark Official Quick Start", "source": "Official Documentation", "url": "https://spark.apache.org/docs/latest/quick-start.html"},
        ],
    },
    "Java": {
        "category": "Programming",
        "objectives": [
            "Master modern Java OOP, Collections, Streams, exception handling, and Spring Boot backend APIs.",
        ],
        "exercises": [
            "Build a multi-layered Java REST service with JUnit 5 unit tests and Maven/Gradle.",
        ],
        "mini_project": "Create a Spring Boot REST API with relational persistence and integration tests.",
        "checkpoint": "Write clean Java Streams transformations and pass a JUnit 5 service test suite.",
        "resources": [
            {"title": "Dev.java Official Learning Portal", "source": "Official Documentation", "url": "https://dev.java/learn/"},
        ],
    },
    "C++": {
        "category": "Programming",
        "objectives": [
            "Master modern C++ memory management (RAII, smart pointers), STL containers, and algorithmic performance.",
        ],
        "exercises": [
            "Implement core data structures and benchmark STL containers with CMake.",
        ],
        "mini_project": "Build a fast C++ text indexing & search utility with unit tests.",
        "checkpoint": "Demonstrate leak-free RAII resource handling and optimal algorithm complexity.",
        "resources": [
            {"title": "cppreference Official Reference", "source": "Official Documentation", "url": "https://en.cppreference.com/w/"},
        ],
    },
    "Cybersecurity": {
        "category": "Security",
        "objectives": [
            "Master threat modeling, OWASP Top 10 web vulnerabilities, IAM hardening, and incident triage.",
        ],
        "exercises": [
            "Audit a sample web API against the OWASP Top 10 checklist and document remediations.",
        ],
        "mini_project": "Write a security posture assessment & hardening playbook for a 3-tier web app.",
        "checkpoint": "Identify and remediate injection, broken access control, and credential exposure risks.",
        "resources": [
            {"title": "OWASP Top Ten Project", "source": "Official Documentation", "url": "https://owasp.org/www-project-top-ten/"},
            {"title": "Google Cybersecurity Certificate", "source": "Coursera", "url": "https://www.coursera.org/professional-certificates/google-cybersecurity"},
            {"title": "edX Cybersecurity Courses", "source": "edX", "url": "https://www.edx.org/learn/cybersecurity"},
        ],
    },
    "SIEM": {
        "category": "Security",
        "objectives": [
            "Ingest security logs, write correlation detection rules, and triage SOC alerts methodically.",
        ],
        "exercises": [
            "Author 5 log-correlation queries detecting brute-force logins and anomalous privilege escalation.",
        ],
        "mini_project": "Build a simulated SOC alert triage playbook with severity classification and escalation steps.",
        "checkpoint": "Complete a structured incident log analysis identifying root cause and containment steps.",
        "resources": [
            {"title": "Google Cybersecurity Certificate (SIEM Modules)", "source": "Coursera", "url": "https://www.coursera.org/professional-certificates/google-cybersecurity"},
            {"title": "OWASP Security Logging Cheat Sheet", "source": "Official Documentation", "url": "https://owasp.org/www-project-top-ten/"},
        ],
    },
    "Network Security": {
        "category": "Security",
        "objectives": [
            "Understand TCP/IP, TLS/HTTPS, firewalls, segmentation, and packet capture inspection.",
        ],
        "exercises": [
            "Analyze HTTP/TLS handshake behavior and design firewall ingress/egress rules for a cloud VPC.",
        ],
        "mini_project": "Create a network segmentation and firewall hardening diagram with verification rules.",
        "checkpoint": "Explain defense-in-depth, TLS certificate verification, and common network attack vectors.",
        "resources": [
            {"title": "edX Cybersecurity & Networking", "source": "edX", "url": "https://www.edx.org/learn/cybersecurity"},
            {"title": "OWASP Top Ten Reference", "source": "Official Documentation", "url": "https://owasp.org/www-project-top-ten/"},
        ],
    },
    "Business Analysis": {
        "category": "Business",
        "objectives": [
            "Elicit stakeholder requirements, author clear BRD/FRD documents, map processes, and define KPIs.",
        ],
        "exercises": [
            "Write a structured Business Requirements Document (BRD) with acceptance criteria and user stories.",
        ],
        "mini_project": "Produce an end-to-end process improvement case study with ROI projections and KPI dashboard mockup.",
        "checkpoint": "Present prioritized backlog trade-offs tied directly to measurable business goals.",
        "resources": [
            {"title": "Business Analysis on Coursera", "source": "Coursera", "url": "https://www.coursera.org/learn/business-analysis"},
            {"title": "Business Analysis Courses on edX", "source": "edX", "url": "https://www.edx.org/learn/business-analysis"},
        ],
    },
}


def get_skill_curriculum(skill_name: str) -> Dict[str, Any]:
    """Return curated curriculum & verified resources for a skill (with safe generic fallback)."""
    for key, val in SKILL_CURRICULUM_CATALOG.items():
        if key.lower() == skill_name.strip().lower():
            return {"skill_name": key, **val}

    clean = skill_name.strip() or "Core Engineering"
    return {
        "skill_name": clean,
        "category": "General",
        "objectives": [
            f"Build foundational theoretical and hands-on fluency in {clean}.",
            f"Apply {clean} within an end-to-end portfolio project relevant to your target role.",
        ],
        "exercises": [
            f"Complete guided practical labs covering core {clean} patterns and best practices.",
            f"Document key trade-offs and troubleshooting notes while practicing {clean}.",
        ],
        "mini_project": f"Build a focused portfolio mini-project demonstrating real-world {clean} usage.",
        "checkpoint": f"Pass a self-assessment code/architecture review verifying {clean} proficiency.",
        "resources": [
            {"title": "freeCodeCamp Curriculum", "source": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/"},
            {"title": "Coursera Guided Catalog", "source": "Coursera", "url": "https://www.coursera.org/"},
            {"title": "edX Open Courses", "source": "edX", "url": "https://www.edx.org/"},
        ],
    }


def is_trusted_resource_url(url: str) -> bool:
    """Ensure every recommended resource URL belongs to a verified trusted educational domain."""
    if not url or not url.startswith("https://"):
        return False
    without_scheme = url[len("https://"):]
    host = without_scheme.split("/", 1)[0].lower()
    return any(host == d or host.endswith("." + d) for d in TRUSTED_RESOURCE_DOMAINS)
