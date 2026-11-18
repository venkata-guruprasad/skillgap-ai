-- =============================================================================
-- SkillGap AI – Seed Data (Initial Skills & Career Roles)
-- =============================================================================

INSERT INTO skills (name, category, description) VALUES
    ('Python', 'Programming', 'General-purpose programming language widely used in backend, data science, and AI.'),
    ('JavaScript', 'Programming', 'Core scripting language for interactive web development.'),
    ('SQL', 'Database', 'Structured Query Language for managing relational databases.'),
    ('React', 'Frontend', 'Component-based JavaScript library for building user interfaces.'),
    ('Tailwind CSS', 'Frontend', 'Utility-first CSS framework for rapid UI styling.'),
    ('FastAPI', 'Backend', 'Modern high-performance Python web framework for building APIs.'),
    ('PostgreSQL', 'Database', 'Advanced open-source relational database management system.'),
    ('Docker', 'Cloud & DevOps', 'Containerization platform for packaging and running applications.'),
    ('Git', 'Tools', 'Distributed version control system for tracking source code changes.'),
    ('Machine Learning', 'Data & AI', 'Design and training of statistical models that learn from data.'),
    ('Scikit-learn', 'Data & AI', 'Python library for classical machine learning algorithms.'),
    ('Natural Language Processing', 'Data & AI', 'Techniques for processing and analyzing human language text.'),
    ('REST APIs', 'Backend', 'Architectural style for designing networked web services.'),
    ('Data Visualization', 'Data & AI', 'Communicating analytical findings through visual charts and dashboards.'),
    ('CI/CD', 'Cloud & DevOps', 'Automated pipelines for continuous integration and continuous delivery.')
ON CONFLICT (name) DO NOTHING;

INSERT INTO career_roles (title, category, description, avg_salary_usd, demand_level) VALUES
    (
        'Full-Stack Developer',
        'Software Engineering',
        'Builds and maintains both client-side web interfaces and server-side APIs and databases.',
        115000,
        'High'
    ),
    (
        'Backend Engineer',
        'Software Engineering',
        'Designs scalable server-side architectures, APIs, and database systems.',
        125000,
        'High'
    ),
    (
        'Data Scientist',
        'Data & AI',
        'Extracts actionable insights from structured and unstructured data using statistics and ML.',
        130000,
        'High'
    ),
    (
        'Machine Learning Engineer',
        'Data & AI',
        'Develops, deploys, and monitors production machine learning and NLP systems.',
        145000,
        'Very High'
    ),
    (
        'Frontend Developer',
        'Software Engineering',
        'Creates responsive, accessible, and high-performance web applications.',
        108000,
        'High'
    )
ON CONFLICT (title) DO NOTHING;

-- Map foundational skills to career roles
INSERT INTO career_role_skills (career_role_id, skill_id, importance_weight, is_required)
SELECT cr.id, s.id, v.weight, v.req
FROM (VALUES
    ('Full-Stack Developer', 'JavaScript', 1.00, TRUE),
    ('Full-Stack Developer', 'React', 1.00, TRUE),
    ('Full-Stack Developer', 'Python', 0.90, TRUE),
    ('Full-Stack Developer', 'FastAPI', 0.85, TRUE),
    ('Full-Stack Developer', 'PostgreSQL', 0.85, TRUE),
    ('Full-Stack Developer', 'REST APIs', 0.90, TRUE),
    ('Full-Stack Developer', 'Docker', 0.70, FALSE),
    ('Full-Stack Developer', 'Git', 0.85, TRUE),

    ('Backend Engineer', 'Python', 1.00, TRUE),
    ('Backend Engineer', 'FastAPI', 0.95, TRUE),
    ('Backend Engineer', 'PostgreSQL', 1.00, TRUE),
    ('Backend Engineer', 'SQL', 0.95, TRUE),
    ('Backend Engineer', 'REST APIs', 1.00, TRUE),
    ('Backend Engineer', 'Docker', 0.85, TRUE),
    ('Backend Engineer', 'CI/CD', 0.75, FALSE),

    ('Data Scientist', 'Python', 1.00, TRUE),
    ('Data Scientist', 'SQL', 0.90, TRUE),
    ('Data Scientist', 'Machine Learning', 1.00, TRUE),
    ('Data Scientist', 'Scikit-learn', 0.95, TRUE),
    ('Data Scientist', 'Data Visualization', 0.85, TRUE),

    ('Machine Learning Engineer', 'Python', 1.00, TRUE),
    ('Machine Learning Engineer', 'Machine Learning', 1.00, TRUE),
    ('Machine Learning Engineer', 'Scikit-learn', 0.90, TRUE),
    ('Machine Learning Engineer', 'Natural Language Processing', 0.90, TRUE),
    ('Machine Learning Engineer', 'FastAPI', 0.80, FALSE),
    ('Machine Learning Engineer', 'Docker', 0.85, TRUE),

    ('Frontend Developer', 'JavaScript', 1.00, TRUE),
    ('Frontend Developer', 'React', 1.00, TRUE),
    ('Frontend Developer', 'Tailwind CSS', 0.85, TRUE),
    ('Frontend Developer', 'REST APIs', 0.80, TRUE),
    ('Frontend Developer', 'Git', 0.85, TRUE)
) AS v(role_title, skill_name, weight, req)
JOIN career_roles cr ON cr.title = v.role_title
JOIN skills s ON s.name = v.skill_name
ON CONFLICT (career_role_id, skill_id) DO NOTHING;
