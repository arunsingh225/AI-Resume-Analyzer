"""
Field detector v3 — detects exact job role / sub-field.
Covers all roles requested:
  tech: Frontend, Backend, Full Stack, Java, Python, Web Dev, Data Analyst,
        Data Scientist, AI/ML, DevOps, Cloud, Cybersecurity, QA, Mobile, Product, BA
  non-tech: UI/UX, Product Designer, Digital Marketing, SEO, Content Writer,
            Social Media, HR Recruiter, TA, Sales, BDA, Finance Analyst,
            Accountant, Investment Banking, Operations, Customer Support,
            Management Trainee, General Fresher
"""
from collections import defaultdict
from typing import Tuple, Dict

FIELD_MAP: Dict[str, dict] = {

    # ═══════════════════════ TECH ═══════════════════════

    "frontend_developer": {
        "domain": "technical", "display": "Frontend Developer",
        "keywords": [
            "react", "vue", "angular", "nextjs", "nuxt", "svelte",
            "html5", "css3", "sass", "less", "tailwind", "bootstrap",
            "javascript", "typescript", "webpack", "vite", "rollup",
            "responsive design", "ui developer", "frontend engineer",
            "web ui", "spa", "pwa", "redux", "zustand", "recoil",
            "storybook", "jest", "cypress", "playwright frontend",
        ]
    },
    "backend_developer": {
        "domain": "technical", "display": "Backend Developer",
        "keywords": [
            "backend", "server-side", "api development", "rest api", "graphql",
            "node.js", "express", "fastapi", "django", "flask", "spring boot",
            "laravel", "ruby on rails", "gin", "fiber", "nestjs",
            "microservices", "grpc", "message queue", "rabbitmq",
            "database design", "orm", "prisma", "sqlalchemy", "hibernate",
            "backend engineer", "server engineer",
        ]
    },
    "fullstack_developer": {
        "domain": "technical", "display": "Full Stack Developer",
        "keywords": [
            "full stack", "fullstack", "mern", "mean", "mevn",
            "react node", "django react", "spring react", "next.js",
            "frontend backend", "end to end development",
            "full-stack engineer", "t-shaped developer",
        ]
    },
    "java_developer": {
        "domain": "technical", "display": "Java Developer",
        "keywords": [
            "java", "spring boot", "spring framework", "spring mvc",
            "hibernate", "jpa", "maven", "gradle", "junit",
            "java 8", "java 11", "java 17", "lambda", "streams",
            "microservices java", "jvm", "tomcat", "wildfly",
            "java developer", "j2ee", "enterprise java",
        ]
    },
    "python_developer": {
        "domain": "technical", "display": "Python Developer",
        "keywords": [
            "python", "django", "flask", "fastapi", "celery",
            "pandas", "numpy", "asyncio", "aiohttp", "pydantic",
            "sqlalchemy", "alembic", "pytest", "poetry",
            "python developer", "python engineer", "scripting",
            "automation python", "web scraping", "beautifulsoup",
        ]
    },
    "software_engineer": {
        "domain": "technical", "display": "Software Engineer",
        "keywords": [
            "software engineer", "software developer", "sde",
            "object oriented programming", "design patterns", "solid principles",
            "data structures", "algorithms", "system design", "oop",
            "c++", "c#", ".net", "golang", "rust", "scala", "kotlin",
            "code review", "technical documentation", "sdlc",
        ]
    },
    "data_analyst": {
        "domain": "technical", "display": "Data Analyst",
        "keywords": [
            "data analyst", "data analysis", "business intelligence",
            "sql", "excel", "power bi", "tableau", "looker",
            "pandas", "matplotlib", "seaborn", "data visualization",
            "statistical analysis", "reporting", "dashboard",
            "pivot tables", "vlookup", "google analytics",
            "ab testing", "data cleaning", "etl analyst",
        ]
    },
    "data_scientist": {
        "domain": "technical", "display": "Data Scientist",
        "keywords": [
            "data science", "machine learning", "statistical modeling",
            "scikit-learn", "xgboost", "lightgbm", "catboost",
            "feature engineering", "model training", "hyperparameter",
            "cross-validation", "regression", "classification", "clustering",
            "hypothesis testing", "bayesian", "time series forecasting",
            "data scientist", "applied scientist",
        ]
    },
    "ml_ai_engineer": {
        "domain": "technical", "display": "AI / ML Engineer",
        "keywords": [
            "machine learning engineer", "ml engineer", "ai engineer",
            "deep learning", "tensorflow", "pytorch", "keras",
            "neural network", "cnn", "rnn", "lstm", "transformer",
            "nlp", "natural language processing", "computer vision",
            "llm", "generative ai", "fine-tuning", "rag",
            "mlops", "mlflow", "kubeflow", "model deployment",
            "feature store", "embedding", "vector database",
        ]
    },
    "devops_engineer": {
        "domain": "technical", "display": "DevOps Engineer",
        "keywords": [
            "devops", "sre", "site reliability", "ci/cd",
            "jenkins", "github actions", "gitlab ci", "circleci",
            "docker", "kubernetes", "helm", "terraform", "ansible",
            "infrastructure as code", "iac", "monitoring",
            "prometheus", "grafana", "elk", "pagerduty",
            "devops engineer", "platform engineer", "release engineer",
        ]
    },
    "cloud_engineer": {
        "domain": "technical", "display": "Cloud Engineer",
        "keywords": [
            "cloud engineer", "cloud architect", "solutions architect",
            "aws", "azure", "gcp", "cloud native",
            "ec2", "s3", "lambda", "rds", "vpc", "iam",
            "azure devops", "arm templates", "bicep",
            "google cloud", "gke", "bigquery", "cloud functions",
            "multi-cloud", "cloud migration", "cloud cost optimization",
        ]
    },
    "cybersecurity": {
        "domain": "technical", "display": "Cybersecurity Analyst",
        "keywords": [
            "cybersecurity", "information security", "infosec",
            "penetration testing", "ethical hacking", "vapt",
            "soc analyst", "siem", "splunk", "qradar",
            "vulnerability assessment", "owasp", "nmap", "metasploit",
            "firewall", "ids", "ips", "zero trust", "cissp", "ceh", "oscp",
            "network security", "incident response", "threat intelligence",
            "security analyst", "cyber analyst",
        ]
    },
    "qa_engineer": {
        "domain": "technical", "display": "QA / Test Engineer",
        "keywords": [
            "qa engineer", "quality assurance", "software testing",
            "selenium", "cypress", "playwright", "appium",
            "manual testing", "automation testing", "test cases",
            "regression testing", "performance testing", "jmeter",
            "api testing", "postman", "rest assured",
            "bug reporting", "jira", "test plan", "test strategy",
            "qe", "sdet", "quality engineer",
        ]
    },
    "mobile_developer": {
        "domain": "technical", "display": "Mobile App Developer",
        "keywords": [
            "android developer", "ios developer", "mobile developer",
            "react native", "flutter", "dart",
            "kotlin", "swift", "objective-c",
            "android studio", "xcode", "play store", "app store",
            "push notifications", "firebase", "mobile ui",
            "jetpack compose", "swiftui", "mvvm mobile",
        ]
    },
    "product_manager": {
        "domain": "technical", "display": "Product Manager",
        "keywords": [
            "product manager", "product management", "product owner",
            "roadmap", "user stories", "backlog", "sprint planning",
            "product strategy", "go-to-market", "product analytics",
            "prd", "mrd", "okr", "kpi product",
            "agile product", "scrum", "stakeholder management",
            "a/b testing product", "product discovery", "user interviews",
        ]
    },
    "business_analyst": {
        "domain": "technical", "display": "Business Analyst",
        "keywords": [
            "business analyst", "ba", "requirements gathering",
            "business requirements document", "brd", "frd",
            "process mapping", "use cases", "user acceptance testing",
            "uat", "gap analysis", "as-is to-be", "workflow analysis",
            "stakeholder interviews", "data flow diagram", "dfd",
            "erp implementation", "sap ba", "salesforce ba",
        ]
    },
    "blockchain": {
        "domain": "technical", "display": "Blockchain Developer",
        "keywords": [
            "blockchain", "solidity", "ethereum", "web3", "smart contract",
            "defi", "nft", "polygon", "hyperledger", "truffle", "hardhat",
            "ipfs", "dao", "crypto", "dapp", "metamask",
        ]
    },
    "embedded_iot": {
        "domain": "technical", "display": "Embedded / IoT Engineer",
        "keywords": [
            "embedded systems", "iot", "arduino", "raspberry pi",
            "rtos", "firmware", "microcontroller", "arm cortex",
            "pcb design", "uart", "spi", "i2c", "mqtt", "modbus",
            "embedded c", "real-time systems", "fpga",
        ]
    },

    # ═══════════════════════ MARKETING ═══════════════════════

    "digital_marketing": {
        "domain": "marketing", "display": "Digital Marketing Specialist",
        "keywords": [
            "digital marketing", "performance marketing", "paid media",
            "google ads", "facebook ads", "instagram ads", "linkedin ads",
            "sem", "ppc", "cpc", "cpm", "roas", "ctr",
            "email marketing", "campaign management", "lead generation",
            "a/b testing", "conversion rate optimization", "cro",
            "marketing funnel", "attribution modeling",
        ]
    },
    "seo_specialist": {
        "domain": "marketing", "display": "SEO Specialist",
        "keywords": [
            "seo", "search engine optimization", "on-page seo", "off-page seo",
            "technical seo", "keyword research", "link building",
            "ahrefs", "semrush", "moz", "screaming frog",
            "google search console", "google analytics",
            "core web vitals", "page speed", "schema markup",
            "content optimization", "backlinks", "domain authority",
        ]
    },
    "content_writer": {
        "domain": "marketing", "display": "Content Writer",
        "keywords": [
            "content writing", "copywriting", "blog writing",
            "seo writing", "content strategy", "editorial",
            "ghostwriting", "white papers", "case studies",
            "content calendar", "wordpress", "content management",
            "proofreading", "editing", "technical writing",
            "email copywriting", "ad copy", "long-form content",
        ]
    },
    "social_media_manager": {
        "domain": "marketing", "display": "Social Media Manager",
        "keywords": [
            "social media", "social media management", "instagram",
            "facebook", "twitter", "linkedin management", "youtube",
            "tiktok", "reels", "content creation social",
            "community management", "influencer marketing",
            "social media analytics", "hootsuite", "buffer",
            "engagement rate", "follower growth", "brand voice",
        ]
    },
    "brand_marketing": {
        "domain": "marketing", "display": "Brand Manager",
        "keywords": [
            "brand management", "brand strategy", "brand identity",
            "market research", "consumer insights", "brand positioning",
            "fmcg", "advertising", "atl", "btl", "media planning",
            "brand equity", "nps", "brand awareness", "brand guidelines",
        ]
    },

    # ═══════════════════════ FINANCE ═══════════════════════

    "finance_analyst": {
        "domain": "finance", "display": "Finance Analyst",
        "keywords": [
            "financial analyst", "financial analysis", "fp&a",
            "financial modeling", "excel", "valuation", "dcf",
            "budgeting", "forecasting", "variance analysis",
            "p&l management", "financial reporting", "kpi",
            "power bi finance", "tableau finance", "erp finance",
        ]
    },
    "accountant": {
        "domain": "finance", "display": "Accountant / CA",
        "keywords": [
            "accounting", "accountant", "ca", "cpa", "cma",
            "gaap", "ifrs", "ind as", "tally", "sap fico",
            "gst", "tds", "tax", "audit", "accounts payable",
            "accounts receivable", "reconciliation", "bookkeeping",
            "balance sheet", "profit loss", "statutory audit",
            "internal audit", "tax filing", "itr",
        ]
    },
    "investment_banking": {
        "domain": "finance", "display": "Investment Banking Analyst",
        "keywords": [
            "investment banking", "m&a", "mergers acquisitions",
            "dcf", "lbo", "comparable company", "precedent transactions",
            "pitch book", "capital markets", "bloomberg",
            "ipo", "equity offering", "debt capital markets",
            "deal advisory", "financial due diligence",
            "investment banker", "ib analyst",
        ]
    },
    "risk_compliance": {
        "domain": "finance", "display": "Risk & Compliance Analyst",
        "keywords": [
            "risk management", "credit risk", "market risk", "operational risk",
            "basel iii", "var", "stress testing", "compliance",
            "aml", "kyc", "sebi", "rbi regulations", "fema",
            "regulatory reporting", "frm", "risk analyst",
        ]
    },
    "equity_research": {
        "domain": "finance", "display": "Equity Research Analyst",
        "keywords": [
            "equity research", "stock analysis", "cfa", "buy side", "sell side",
            "sector research", "investment thesis", "target price",
            "portfolio management", "asset management",
            "financial statements analysis", "bloomberg equity",
        ]
    },

    # ═══════════════════════ HEALTHCARE ═══════════════════════

    "clinical_medicine": {
        "domain": "healthcare", "display": "Clinical Doctor / Medical Officer",
        "keywords": [
            "mbbs", "md", "physician", "clinical", "diagnosis",
            "patient care", "surgery", "icu", "emergency medicine",
            "cardiology", "neurology", "oncology", "radiology",
            "internal medicine", "pediatrics", "obgyn",
        ]
    },
    "clinical_research": {
        "domain": "healthcare", "display": "Clinical Research Associate",
        "keywords": [
            "clinical trials", "gcp", "ich guidelines", "fda regulations",
            "pharmacovigilance", "adverse events", "cra", "irb",
            "protocol monitoring", "crf", "clinical data management",
            "medidata", "phase 1 2 3 4 trials",
        ]
    },
    "health_informatics": {
        "domain": "healthcare", "display": "Health Informatics Analyst",
        "keywords": [
            "health informatics", "ehr", "epic", "cerner", "hl7", "fhir",
            "hipaa", "healthcare analytics", "telemedicine", "health data",
            "clinical decision support", "icd-10", "snomed",
        ]
    },
    "nursing": {
        "domain": "healthcare", "display": "Registered Nurse",
        "keywords": [
            "nursing", "registered nurse", "rn", "bsc nursing", "gnm",
            "patient care", "vital signs", "medication administration",
            "icu nurse", "wound care", "iv therapy",
        ]
    },
    "pharmacy": {
        "domain": "healthcare", "display": "Pharmacist / Drug Regulatory",
        "keywords": [
            "pharmacy", "pharmacist", "drug regulatory", "cdsco",
            "pharmacokinetics", "drug formulation", "b.pharm", "m.pharm",
            "pharmaceutical", "gmp", "quality assurance pharma",
        ]
    },

    # ═══════════════════════ DESIGN ═══════════════════════

    "ui_ux_designer": {
        "domain": "design", "display": "UI/UX Designer",
        "keywords": [
            "ui design", "ux design", "user experience", "user interface",
            "figma", "adobe xd", "sketch", "wireframing", "prototyping",
            "user research", "usability testing", "design system",
            "interaction design", "information architecture",
            "accessibility wcag", "ui ux", "ux researcher",
        ]
    },
    "product_designer": {
        "domain": "design", "display": "Product Designer",
        "keywords": [
            "product design", "product designer", "design thinking",
            "end-to-end design", "design system", "figma product",
            "user journey", "persona", "design sprint",
            "b2b saas design", "mobile app design", "0 to 1 design",
        ]
    },
    "graphic_designer": {
        "domain": "design", "display": "Graphic Designer",
        "keywords": [
            "graphic design", "visual design", "photoshop",
            "illustrator", "indesign", "print design", "logo design",
            "typography", "color theory", "brand design",
            "packaging design", "publication design",
        ]
    },
    "motion_designer": {
        "domain": "design", "display": "Motion Designer",
        "keywords": [
            "motion design", "after effects", "motion graphics",
            "animation", "lottie", "premiere pro", "video editing",
            "3d animation", "cinema 4d", "blender", "kinetic typography",
        ]
    },

    # ═══════════════════════ LEGAL ═══════════════════════

    "corporate_law": {
        "domain": "legal", "display": "Corporate / M&A Lawyer",
        "keywords": [
            "corporate law", "m&a", "mergers acquisitions", "due diligence law",
            "shareholders agreement", "term sheet", "sebi regulations",
            "companies act", "corporate restructuring", "legal research corporate",
        ]
    },
    "litigation": {
        "domain": "legal", "display": "Litigation Lawyer",
        "keywords": [
            "litigation", "dispute resolution", "arbitration", "mediation",
            "civil litigation", "court appearances", "pleadings", "cpc", "crpc",
            "evidence act", "writ petition", "appellate", "nclt",
        ]
    },
    "ip_law": {
        "domain": "legal", "display": "IP / Technology Lawyer",
        "keywords": [
            "intellectual property", "patent", "trademark", "copyright",
            "ip litigation", "wipo", "technology transfer", "licensing",
            "trade secrets", "patent prosecution",
        ]
    },
    "data_privacy_law": {
        "domain": "legal", "display": "Data Privacy / Tech Law Specialist",
        "keywords": [
            "gdpr", "data privacy", "dpdp act", "data protection",
            "dpo", "privacy by design", "ccpa", "pdpa",
            "tech law", "fintech regulation", "cyber law",
        ]
    },

    # ═══════════════════════ HR ═══════════════════════

    "hr_recruiter": {
        "domain": "hr", "display": "HR Recruiter",
        "keywords": [
            "recruitment", "recruiter", "hr recruiter", "talent sourcing",
            "job posting", "screening", "shortlisting", "interview coordination",
            "offer management", "joining formalities", "ats recruiting",
            "naukri", "linkedin recruiting", "campus placement",
        ]
    },
    "talent_acquisition": {
        "domain": "hr", "display": "Talent Acquisition Specialist",
        "keywords": [
            "talent acquisition", "full cycle recruiting", "sourcing",
            "linkedin recruiter", "boolean search", "employer branding",
            "diversity hiring", "executive search", "headhunting",
            "hiring metrics", "time to fill", "cost per hire",
        ]
    },
    "hr_business_partner": {
        "domain": "hr", "display": "HR Business Partner",
        "keywords": [
            "hrbp", "hr business partner", "performance management",
            "employee relations", "org design", "succession planning",
            "workforce planning", "hr strategy", "okr hr", "change management",
        ]
    },
    "compensation_benefits": {
        "domain": "hr", "display": "Compensation & Benefits Specialist",
        "keywords": [
            "compensation", "benefits", "total rewards", "payroll",
            "salary benchmarking", "pay equity", "ctc", "pf", "esi",
            "grade bands", "esop", "aon hewitt", "mercer compensation",
        ]
    },
    "learning_development": {
        "domain": "hr", "display": "L&D Specialist",
        "keywords": [
            "learning and development", "l&d", "training",
            "instructional design", "lms", "e-learning",
            "onboarding program", "leadership development",
            "capability building", "tna", "training needs analysis",
        ]
    },

    # ═══════════════════════ SALES & OPS ═══════════════════════

    "sales_executive": {
        "domain": "sales", "display": "Sales Executive",
        "keywords": [
            "sales executive", "sales representative", "b2b sales",
            "inside sales", "field sales", "cold calling",
            "lead generation sales", "crm", "salesforce",
            "pipeline management", "quota", "revenue target",
            "deal closure", "negotiation", "account management",
        ]
    },
    "business_development": {
        "domain": "sales", "display": "Business Development Associate",
        "keywords": [
            "business development", "bda", "bde", "partnerships",
            "strategic alliances", "market expansion", "new business",
            "prospecting", "outreach", "sales pitch",
            "revenue growth", "b2b partnership",
        ]
    },
    "operations_executive": {
        "domain": "operations", "display": "Operations Executive",
        "keywords": [
            "operations", "operations executive", "process management",
            "supply chain", "logistics", "vendor management",
            "inventory", "procurement", "warehouse",
            "lean", "six sigma", "sop", "erp operations",
        ]
    },
    "customer_support": {
        "domain": "operations", "display": "Customer Support Executive",
        "keywords": [
            "customer support", "customer service", "helpdesk",
            "zendesk", "freshdesk", "ticketing system",
            "customer satisfaction", "csat", "nps",
            "inbound calls", "outbound calls", "bpo",
            "query resolution", "escalation", "sla",
        ]
    },
    "consulting": {
        "domain": "consulting", "display": "Management Consultant",
        "keywords": [
            "management consulting", "strategy consulting",
            "mckinsey", "bcg", "bain", "mbb",
            "case study", "structured problem solving",
            "mece", "hypothesis-driven", "digital transformation",
            "organizational restructuring", "due diligence consulting",
        ]
    },
    "management_trainee": {
        "domain": "general", "display": "Management Trainee",
        "keywords": [
            "management trainee", "mt program", "graduate trainee",
            "trainee program", "rotational program", "campus hire",
            "fresher management", "pgdm trainee", "mba trainee",
            "cross-functional", "leadership program",
        ]
    },
    "general_fresher": {
        "domain": "general", "display": "Fresh Graduate",
        "keywords": [
            "fresher", "fresh graduate", "entry level", "campus placement",
            "internship", "college project", "college student",
            "btech", "bca", "bsc", "bcom", "ba graduate",
            "looking for opportunity", "seeking first job",
            "no experience", "0 experience", "0-1 years",
        ]
    },
}


def detect_field(text: str) -> Tuple[str, str, float, Dict[str, float]]:
    """
    Returns (subfield_key, domain, confidence, all_scores)
    Uses weighted keyword frequency: multi-word phrases score higher.
    """
    tl = text.lower()
    scores: Dict[str, float] = defaultdict(float)

    for key, meta in FIELD_MAP.items():
        weight = 0.0
        for kw in meta["keywords"]:
            cnt = tl.count(kw.lower())
            if cnt > 0:
                # multi-word phrases weighted higher; repeated mentions slightly boosted
                kw_weight = (len(kw.split()) ** 1.3) * (1 + 0.25 * (cnt - 1))
                weight += kw_weight
        # normalise by sqrt of keyword count to avoid list-length bias
        scores[key] = round(weight / max(len(meta["keywords"]) ** 0.5, 1), 4)

    if not any(v > 0 for v in scores.values()):
        return "general_fresher", "general", 0.4, dict(scores)

    best = max(scores, key=lambda k: scores[k])
    total = sum(scores.values()) or 1
    confidence = round(scores[best] / total, 4)
    domain = FIELD_MAP[best]["domain"]
    return best, domain, confidence, dict(scores)


def get_display_name(subfield_key: str) -> str:
    entry = FIELD_MAP.get(subfield_key)
    return entry["display"] if entry else subfield_key.replace("_", " ").title()


def get_domain(subfield_key: str) -> str:
    entry = FIELD_MAP.get(subfield_key)
    return entry["domain"] if entry else "general"
