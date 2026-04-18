from typing import List

PHASE_TITLES = [
    "Foundation Building","Core Skill Development","Applied Practice",
    "Intermediate Mastery","Advanced Topics","Project Building",
    "Portfolio & Branding","Interview Preparation","Mock Interviews",
    "Job Applications","Networking","Offer Negotiation",
]

DOMAIN_RESOURCES = {
    "technical":  ["Official documentation","LeetCode","GitHub","YouTube tutorials","CS50 edX"],
    "marketing":  ["Google Skillshop","HubSpot Academy","Coursera Marketing","Ahrefs Blog","GrowthHackers"],
    "finance":    ["CFI Institute","Investopedia","Bloomberg Markets","Mergers & Inquisitions","CFA Institute"],
    "healthcare": ["PubMed","MedScape","UpToDate","CITI Program","WHO Publications"],
    "design":     ["Figma Community","NNGroup","Behance","Dribbble","ADPList Mentors"],
    "legal":      ["SCC Online","Indian Kanoon","Bar & Bench","Manupatra","WIPO Academy"],
    "hr":         ["SHRM.org","LinkedIn Learning HR","Darwinbox Academy","HR Katha","Wharton People Analytics"],
    "sales":      ["Salesforce Trailhead","HubSpot Sales Academy","Gong.io Blog","LinkedIn Sales Navigator"],
    "operations": ["APICS","Coursera Supply Chain","Six Sigma Council","MIT OpenCourseWare Ops"],
    "consulting": ["Case in Point (book)","Victor Cheng LOMS","Preplounge.com","McKinsey Insights","BCG Henderson Institute"],
    "education":  ["Coursera","ATD.org","EdSurge","Teaching Channel","eLearning Industry"],
}

def generate_roadmap(field_key: str, domain: str, level: str, missing_skills: List[str]) -> List[dict]:
    resources = DOMAIN_RESOURCES.get(domain, DOMAIN_RESOURCES["technical"])
    skills_per_week = 2 if level in ("fresher","junior") else 1
    chunks = [missing_skills[i:i+skills_per_week] for i in range(0, min(len(missing_skills), 24), skills_per_week)]

    # Pad to 12 weeks minimum
    while len(chunks) < 12:
        chunks.append([])

    plan = []
    for i, chunk in enumerate(chunks[:12]):
        w = i + 1
        title = PHASE_TITLES[i % len(PHASE_TITLES)]
        tasks = []
        if chunk:
            tasks += [f"Study and practice: {sk}" for sk in chunk]
            tasks += ["Complete 2 hands-on exercises","Document learning in personal notes"]
        else:
            tasks = [
                "Review and consolidate skills from previous weeks",
                "Work on a real project applying learnt skills",
                "Seek feedback from a mentor or peer",
            ]
        plan.append({
            "week": w, "title": title, "tasks": tasks,
            "skills": chunk,
            "resources": resources[:3],
        })
    return plan
