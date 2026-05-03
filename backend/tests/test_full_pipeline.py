"""
Comprehensive Resume Pipeline Test — 6 diverse fields (tech + non-tech).
Tests: text extraction → section detection → ATS scoring → field detection

Run: cd backend && python tests/test_full_pipeline.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
from app.services.parser import clean_text
from app.services.ats_scorer import compute_ats_score

# ── 6 Test Resumes (raw text, simulating PDF extraction) ─────────────────────
RESUMES = {

    # 1. Data Analyst (Tech) — user's own field
    "data_analyst": """
ARUN SINGH
arunsingh225166@gmail.com  +91 8882443665  github.com/arunsingh225  linkedin.com/in/arun-singh22

PROFESSIONAL SUMMARY
Motivated Computer Science undergraduate (B.Tech, expected 2027) aspiring to build a career in
Data Analysis. Possess foundational knowledge of Excel, SQL, Python, data cleaning, data
preprocessing, data wrangling, exploratory data analysis (EDA), and basic machine learning.
Hands-on experience through academic and self-driven projects involving loan prediction,
customer segmentation, and resume data analysis using Pandas, NumPy, Matplotlib, and Seaborn.

TECHNICAL SKILLS
Languages: Python, Java, HTML, CSS, SQL
Machine Learning & Data Science: Scikit-learn, PyTorch, NumPy, Pandas, Matplotlib, Seaborn
Tools & Platforms: Git, GitHub, Jupyter
Data Structures & Algorithms: Java

PROJECTS
AI Resume Analyzer (SaaS) | AI Application  2026
Stack: React, Vite, Tailwind CSS, FastAPI, Python, REST API, Vercel
• Designed and deployed a full-stack ATS Resume Analyzer SaaS product
• Built custom ATS scoring engine with 53+ career field detection
• Integrated Gemini AI API for AI-powered resume improvement suggestions

Loan Prediction System | ML Project  2025
Stack: Python, Scikit-learn, Pandas, NumPy, Matplotlib
• Developed ML model with 87% accuracy for loan default prediction
• Performed EDA, feature engineering and model evaluation

Customer Segmentation | Data Science  2025
Stack: Python, K-Means, Pandas, Seaborn
• Applied K-Means clustering on 10,000+ customer records
• Visualized segments using Matplotlib and Seaborn

EDUCATION
B.Tech Computer Science | XYZ University  2023-2027  CGPA: 7.8

CERTIFICATIONS
• Oracle Cloud Infrastructure 2025 Certified AI Professional
• Google Data Analytics Certificate
• SQL for Data Analysis - Coursera

ACHIEVEMENTS
• EY Techathon 2025 – Qualified Round 1
• LeetCode – 27 problems solved
• Built AI Resume Analyzer SaaS serving real users
""",

    # 2. Software Engineer (Tech)
    "software_engineer": """
PRIYA SHARMA
priya.sharma@gmail.com  +91 9876543210  linkedin.com/in/priyasharma  github.com/priyasharma

PROFESSIONAL SUMMARY
Software Engineer with 3 years of experience building scalable backend systems. Proficient in
Java, Spring Boot, microservices, and REST APIs. Experienced in agile development, code reviews,
and system design.

WORK EXPERIENCE
Software Engineer | Infosys, Bangalore  2022 - Present
• Developed REST APIs for payment processing module using Spring Boot, handling 50k+ daily transactions
• Reduced API response time by 40% through Redis caching and query optimization
• Led migration of monolithic application to microservices architecture
• Mentored 3 junior developers and conducted code reviews

Backend Developer Intern | TCS, Pune  2021 - 2022
• Built CRUD APIs using Java Spring MVC and MySQL
• Wrote unit tests achieving 85% code coverage using JUnit and Mockito

TECHNICAL SKILLS
Languages: Java, Python, SQL
Frameworks: Spring Boot, Spring MVC, Hibernate
Databases: MySQL, PostgreSQL, Redis, MongoDB
Tools: Git, Docker, Jenkins, Jira, Maven

EDUCATION
B.E. Computer Engineering | Pune University  2018-2022  CGPA: 8.5

CERTIFICATIONS
• AWS Certified Developer Associate
• Oracle Java SE 11 Professional

ACHIEVEMENTS
• Best Employee Award Q3 2023 at Infosys
• Reduced deployment time by 60% via CI/CD pipeline setup
• Open source contributor — 15 PRs merged
""",

    # 3. Digital Marketing (Non-tech)
    "digital_marketing": """
SNEHA GUPTA
sneha.gupta@gmail.com  +91 9988776655  linkedin.com/in/sneha-gupta

PROFESSIONAL SUMMARY
Results-driven Digital Marketing Specialist with 4 years of experience in SEO, SEM, content
marketing, and social media strategy. Proven track record of increasing organic traffic by 200%
and managing ₹50L+ monthly ad budgets across Google Ads and Meta.

WORK EXPERIENCE
Digital Marketing Manager | Startup XYZ, Delhi  2022 - Present
• Grew organic search traffic by 200% in 12 months through technical SEO and content strategy
• Managed ₹50L monthly Google Ads and Meta Ads budget with 3.2x ROAS
• Led team of 4 content writers and 2 SEO analysts
• Launched email marketing campaigns with 45% open rate (industry avg: 21%)

SEO Analyst | ABC Agency, Delhi  2020 - 2022
• Performed on-page and off-page SEO for 15+ client websites
• Improved client website rankings from page 4 to page 1 for 30+ keywords
• Created keyword research reports and monthly analytics dashboards using Google Analytics

SKILLS
SEO/SEM, Google Analytics, Google Ads, Meta Ads Manager, HubSpot, Mailchimp,
Ahrefs, SEMrush, Content Strategy, Copywriting, WordPress, Canva, Power BI

EDUCATION
BBA Marketing | Delhi University  2017-2020  CGPA: 7.6

CERTIFICATIONS
• Google Ads Certified (Search, Display, Video)
• HubSpot Content Marketing Certified
• Meta Blueprint Certified

ACHIEVEMENTS
• Increased company leads by 180% in FY2023-24
• Speaker at DigiMarCon India 2023
""",

    # 4. HR Recruiter (Non-tech)
    "hr_recruiter": """
RAHUL MEHRA
rahul.mehra@gmail.com  +91 8877665544  linkedin.com/in/rahulmehra

PROFESSIONAL SUMMARY
Experienced HR Recruiter with 5 years of expertise in full-cycle recruitment, talent acquisition,
and employer branding. Specialized in tech and non-tech hiring across startups and MNCs.
Placed 300+ candidates and reduced time-to-hire by 35%.

WORK EXPERIENCE
Senior HR Recruiter | Tech Corp India, Mumbai  2021 - Present
• Managed end-to-end recruitment for 50+ positions across engineering, product, and sales
• Reduced average time-to-hire from 45 days to 29 days through process optimization
• Implemented ATS (Workday) and trained team of 6 HR executives
• Conducted salary benchmarking and created compensation bands for 200+ roles

HR Recruiter | Talent Solutions, Noida  2019 - 2021
• Sourced and screened 1000+ candidates per quarter via LinkedIn, Naukri, and job boards
• Conducted behavioral interviews and assessments for mid-senior roles
• Managed candidate experience and achieved 4.5/5 candidate NPS score

SKILLS
Full-Cycle Recruitment, ATS (Workday, Greenhouse), LinkedIn Recruiter,
Behavioral Interviewing, Salary Negotiation, Employer Branding,
HR Analytics, Onboarding, Diversity Hiring, Naukri, Indeed

EDUCATION
MBA Human Resources | Symbiosis International University  2017-2019  CGPA: 8.1
BBA | Amity University  2014-2017

CERTIFICATIONS
• SHRM-CP Certified
• LinkedIn Recruiting Certification

ACHIEVEMENTS
• Placed 300+ candidates with 92% retention rate
• Built college recruitment program partnering with 10 top engineering colleges
• Employee of the Quarter - Q2 2023
""",

    # 5. Finance Analyst (Non-tech)
    "finance_analyst": """
ANJALI VERMA
anjali.verma@gmail.com  +91 7766554433  linkedin.com/in/anjaliverma

PROFESSIONAL SUMMARY
Chartered Accountant and Finance Analyst with 4 years of experience in financial modeling,
FP&A, equity research, and investment analysis. Expert in Excel, Power BI, and Bloomberg
Terminal. Experience across BFSI sector.

WORK EXPERIENCE
Finance Analyst | HDFC Bank, Mumbai  2021 - Present
• Built and maintained 25+ financial models for quarterly earnings forecasting
• Conducted DCF and comparable company analysis for equity research reports
• Prepared board-level financial dashboards in Power BI reducing reporting time by 50%
• Analysed loan portfolio worth ₹2000Cr for risk assessment and provisioning

Junior Finance Analyst | EY India, Pune  2020 - 2021
• Assisted in due diligence for M&A transactions worth ₹500Cr+
• Prepared financial statements and reconciliation reports for audit clients
• Built automated Excel macros reducing manual work by 30%

SKILLS
Financial Modeling, DCF Analysis, Excel (Advanced), Power BI, Bloomberg Terminal,
SQL, FP&A, Equity Research, Variance Analysis, IFRS/Ind AS, Tally, SAP

EDUCATION
Chartered Accountant (CA) | ICAI  2020
B.Com (Hons) | Shri Ram College of Commerce, Delhi  2014-2017  CGPA: 8.8

CERTIFICATIONS
• CFA Level 1 Passed
• Bloomberg Market Concepts Certified
• NISM Series VIII Equity Derivatives

ACHIEVEMENTS
• Topped CA Final Exam in first attempt (AIR 87)
• Saved ₹1.2Cr annually through process automation
""",

    # 6. DevOps Engineer (Tech)
    "devops_engineer": """
KARAN PATEL
karan.patel@gmail.com  +91 9900112233  github.com/karanpatel  linkedin.com/in/karanpatel

PROFESSIONAL SUMMARY
DevOps Engineer with 3 years of hands-on experience building CI/CD pipelines, managing cloud
infrastructure on AWS, and implementing containerized deployments using Docker and Kubernetes.
Passionate about reliability, automation, and infrastructure as code.

WORK EXPERIENCE
DevOps Engineer | Razorpay, Bangalore  2022 - Present
• Designed and maintained CI/CD pipelines using Jenkins and GitHub Actions for 40+ microservices
• Reduced deployment frequency from weekly to multiple-per-day releases (DORA metrics improved)
• Managed 200+ node Kubernetes cluster on AWS EKS handling 10M daily transactions
• Implemented Infrastructure as Code using Terraform, reducing provisioning time by 70%
• Set up centralized monitoring with Prometheus, Grafana, and ELK stack

Cloud Engineer | Wipro, Hyderabad  2021 - 2022
• Managed AWS infrastructure (EC2, S3, RDS, Lambda, VPC) for 5 client projects
• Automated server provisioning using Ansible playbooks
• Reduced cloud costs by 35% through resource right-sizing and spot instances

TECHNICAL SKILLS
CI/CD: Jenkins, GitHub Actions, GitLab CI, ArgoCD
Cloud: AWS (EKS, EC2, S3, RDS, Lambda, CloudFormation), GCP basics
Containers: Docker, Kubernetes, Helm
IaC: Terraform, Ansible, CloudFormation
Monitoring: Prometheus, Grafana, ELK Stack, Datadog
Scripting: Bash, Python

EDUCATION
B.Tech Computer Science | NIT Surat  2017-2021  CGPA: 7.9

CERTIFICATIONS
• AWS Certified DevOps Engineer – Professional
• Certified Kubernetes Administrator (CKA)
• HashiCorp Terraform Associate

ACHIEVEMENTS
• Achieved 99.98% platform uptime for Razorpay's payment systems
• Reduced mean time to recovery (MTTR) by 60% through chaos engineering
• Presented at KubeCon India 2023
""",
}


from app.services.field_detector import detect_field
from app.services.skill_analyzer import analyze_skills
from app.services.parser import extract_years_experience
from app.constants import determine_level

def run_test(field_name: str, resume_text: str) -> dict:
    """Run a resume through the full pipeline and return results."""
    # Step 1: Clean text (same as parser.py)
    cleaned = clean_text(resume_text)

    # Step 2: Meta
    years = extract_years_experience(cleaned)
    level = determine_level(years)

    # Step 3: Detect field
    field_key, domain, confidence, _ = detect_field(cleaned)

    # Step 4: Skills
    skills = analyze_skills(cleaned, field_key)
    found = skills["found"]

    # Step 5: Score
    result = compute_ats_score(cleaned, field_key, domain, years, found)

    # Formatting structure of result correctly
    sections_found = [s["name"] for s in result.get("section_details", []) if s.get("present")]
    sections_missing = [s["name"] for s in result.get("section_details", []) if not s.get("present")]

    return {
        "field_name": field_name,
        "detected_field": field_key,
        "detected_subfield": field_key,
        "ats_score": result.get("total"),
        "grade": result.get("grade"),
        "experience_level": level,
        "sections_found": sections_found,
        "sections_missing": sections_missing,
        "keyword_score": result.get("keyword_score"),
        "formatting_score": result.get("formatting_score"),
        "section_score": result.get("section_score"),
        "keyword_hits": result.get("keywords_found", [])[:8],
    }


if __name__ == "__main__":
    print("=" * 70)
    print("  AI Resume Analyzer — Full Pipeline Test (6 Fields)")
    print("=" * 70)

    all_results = []
    issues = []

    for field_name, resume_text in RESUMES.items():
        print(f"\n{'─'*50}")
        print(f"  Testing: {field_name.upper()}")
        print(f"{'─'*50}")

        try:
            r = run_test(field_name, resume_text)
            all_results.append(r)

            print(f"  ✅ Detected Field   : {r['detected_field']} / {r['detected_subfield']}")
            print(f"  ✅ ATS Score        : {r['ats_score']} ({r['grade']})")
            print(f"  ✅ Experience Level : {r['experience_level']}")
            print(f"  ✅ Sections Found   : {', '.join(r['sections_found']) or 'NONE'}")
            print(f"  ❌ Sections Missing : {', '.join(r['sections_missing']) or 'none'}")
            print(f"  📊 Keyword Score    : {r['keyword_score']}")
            print(f"  📊 Formatting Score : {r['formatting_score']}")
            print(f"  📊 Keyword Hits     : {r['keyword_hits']}")

            # ── Detect issues ──
            if r['ats_score'] is None or r['ats_score'] < 20:
                issues.append(f"[{field_name}] ATS score too low or None: {r['ats_score']}")
            if not r['detected_field'] or r['detected_field'] == 'general':
                issues.append(f"[{field_name}] Field not detected correctly: got '{r['detected_field']}'")
            if 'Professional Summary' in r['sections_missing'] or 'Summary' in r['sections_missing']:
                issues.append(f"[{field_name}] Professional Summary not detected!")
            if 'Skills' in r['sections_missing'] or 'Technical Skills' in r['sections_missing']:
                issues.append(f"[{field_name}] Skills section not detected!")
            if r['ats_score'] and r['ats_score'] > 0 and r['keyword_score'] == 0:
                issues.append(f"[{field_name}] Zero keyword score — keyword list may be empty!")

        except Exception as e:
            import traceback
            issues.append(f"[{field_name}] EXCEPTION: {e}")
            print(f"  💥 EXCEPTION: {e}")
            traceback.print_exc()

    # ── Summary ──
    print(f"\n{'=' * 70}")
    print(f"  SUMMARY")
    print(f"{'=' * 70}")
    scores = [r['ats_score'] for r in all_results if r['ats_score'] is not None]
    print(f"  Tests run    : {len(all_results)}/6")
    print(f"  Avg ATS score: {sum(scores)/len(scores):.1f}" if scores else "  No scores computed")
    print(f"  Score range  : {min(scores)} – {max(scores)}" if scores else "")

    if issues:
        print(f"\n  ⚠️  ISSUES FOUND ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    else:
        print("\n  ✅ ALL TESTS PASSED — No issues found!")

    print(f"\n{'=' * 70}\n")
