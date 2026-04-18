import json, os
from typing import List

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

COURSES = {
    "python":              [{"course_name":"Python for Everybody Specialization","platform":"Coursera","url":"https://www.coursera.org/specializations/python","duration":"8 months","level":"Beginner","rating":4.8}],
    "machine learning":    [{"course_name":"Machine Learning Specialization","platform":"Coursera (Andrew Ng)","url":"https://www.coursera.org/specializations/machine-learning-introduction","duration":"3 months","level":"Intermediate","rating":4.9}],
    "deep learning":       [{"course_name":"Deep Learning Specialization","platform":"Coursera (DeepLearning.AI)","url":"https://www.coursera.org/specializations/deep-learning","duration":"4 months","level":"Advanced","rating":4.9}],
    "tensorflow":          [{"course_name":"TensorFlow Developer Certificate","platform":"Coursera","url":"https://www.coursera.org/professional-certificates/tensorflow-in-practice","duration":"4 months","level":"Intermediate","rating":4.7}],
    "pytorch":             [{"course_name":"PyTorch for Deep Learning","platform":"Udemy","url":"https://www.udemy.com/course/pytorch-for-deep-learning-in-python-bootcamp/","duration":"17 hours","level":"Intermediate","rating":4.6}],
    "docker":              [{"course_name":"Docker and Kubernetes: The Complete Guide","platform":"Udemy","url":"https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/","duration":"22 hours","level":"Intermediate","rating":4.7}],
    "kubernetes":          [{"course_name":"Certified Kubernetes Administrator (CKA)","platform":"Udemy","url":"https://www.udemy.com/course/certified-kubernetes-administrator-with-practice-tests/","duration":"18 hours","level":"Advanced","rating":4.8}],
    "aws":                 [{"course_name":"AWS Certified Solutions Architect – Associate","platform":"Udemy (Stephane Maarek)","url":"https://www.udemy.com/course/aws-certified-solutions-architect-associate-saa-c03/","duration":"27 hours","level":"Intermediate","rating":4.7}],
    "azure":               [{"course_name":"Microsoft Azure Fundamentals AZ-900","platform":"Microsoft Learn","url":"https://learn.microsoft.com/en-us/training/paths/microsoft-azure-fundamentals-describe-cloud-concepts/","duration":"8 hours","level":"Beginner","rating":4.7}],
    "react":               [{"course_name":"React – The Complete Guide","platform":"Udemy (Maximilian)","url":"https://www.udemy.com/course/react-the-complete-guide-incl-redux/","duration":"49 hours","level":"Beginner","rating":4.7}],
    "typescript":          [{"course_name":"Understanding TypeScript","platform":"Udemy","url":"https://www.udemy.com/course/understanding-typescript/","duration":"15 hours","level":"Beginner","rating":4.6}],
    "next.js":             [{"course_name":"Next.js & React – The Complete Guide","platform":"Udemy","url":"https://www.udemy.com/course/nextjs-react-the-complete-guide/","duration":"25 hours","level":"Intermediate","rating":4.7}],
    "sql":                 [{"course_name":"The Complete SQL Bootcamp","platform":"Udemy","url":"https://www.udemy.com/course/the-complete-sql-bootcamp/","duration":"9 hours","level":"Beginner","rating":4.7}],
    "system design":       [{"course_name":"Grokking the System Design Interview","platform":"Educative","url":"https://www.educative.io/courses/grokking-the-system-design-interview","duration":"Self-paced","level":"Advanced","rating":4.8}],
    "terraform":           [{"course_name":"HashiCorp Certified Terraform Associate","platform":"Udemy","url":"https://www.udemy.com/course/terraform-beginner-to-advanced/","duration":"12 hours","level":"Intermediate","rating":4.7}],
    "kafka":               [{"course_name":"Apache Kafka Series – Complete Guide","platform":"Udemy","url":"https://www.udemy.com/course/apache-kafka/","duration":"13 hours","level":"Intermediate","rating":4.7}],
    "redis":               [{"course_name":"Redis: The Complete Developer's Guide","platform":"Udemy","url":"https://www.udemy.com/course/redis-the-complete-developers-guide-p/","duration":"17 hours","level":"Intermediate","rating":4.7}],
    "graphql":             [{"course_name":"Modern GraphQL with Node.js","platform":"Udemy","url":"https://www.udemy.com/course/graphql-bootcamp/","duration":"13 hours","level":"Intermediate","rating":4.5}],
    "seo":                 [{"course_name":"SEO Specialization","platform":"Coursera (UC Davis)","url":"https://www.coursera.org/specializations/seo","duration":"4 months","level":"Beginner","rating":4.6}],
    "google analytics":    [{"course_name":"GA4 Certification","platform":"Google Skillshop","url":"https://skillshop.exceedlms.com/student/path/508845","duration":"6 hours","level":"Beginner","rating":4.7}],
    "google ads":          [{"course_name":"Google Ads Certification","platform":"Google Skillshop","url":"https://skillshop.exceedlms.com/student/catalog/list?category_ids=2-google-ads","duration":"Self-paced","level":"Beginner","rating":4.7}],
    "facebook ads":        [{"course_name":"Meta Social Media Marketing Professional Certificate","platform":"Coursera (Meta)","url":"https://www.coursera.org/professional-certificates/facebook-social-media-marketing","duration":"5 months","level":"Beginner","rating":4.6}],
    "hubspot":             [{"course_name":"HubSpot Marketing Software Certification","platform":"HubSpot Academy","url":"https://academy.hubspot.com/courses/hubspot-marketing-software","duration":"5 hours","level":"Beginner","rating":4.8}],
    "financial modeling":  [{"course_name":"Financial Modeling & Valuation Analyst (FMVA)","platform":"CFI","url":"https://corporatefinanceinstitute.com/certifications/financial-modeling-valuation-analyst-fmva-program/","duration":"6 months","level":"Intermediate","rating":4.8}],
    "excel":               [{"course_name":"Excel Skills for Business Specialization","platform":"Coursera (Macquarie)","url":"https://www.coursera.org/specializations/excel","duration":"4 months","level":"Beginner","rating":4.8}],
    "power bi":            [{"course_name":"Microsoft Power BI Desktop for Business Intelligence","platform":"Udemy","url":"https://www.udemy.com/course/microsoft-power-bi-up-running-with-power-bi-desktop/","duration":"18 hours","level":"Beginner","rating":4.7}],
    "figma":               [{"course_name":"Google UX Design Professional Certificate","platform":"Coursera (Google)","url":"https://www.coursera.org/professional-certificates/google-ux-design","duration":"6 months","level":"Beginner","rating":4.8}],
    "user research":       [{"course_name":"UX Research and Design Specialization","platform":"Coursera (Michigan)","url":"https://www.coursera.org/specializations/michiganux","duration":"4 months","level":"Intermediate","rating":4.6}],
    "legal research":      [{"course_name":"Legal Research & Writing","platform":"Coursera (Duke)","url":"https://www.coursera.org/learn/legal-research-writing","duration":"4 weeks","level":"Beginner","rating":4.5}],
    "gdpr":                [{"course_name":"GDPR Compliance: A Practical Guide","platform":"Udemy","url":"https://www.udemy.com/course/gdpr-the-practical-guide/","duration":"5 hours","level":"Beginner","rating":4.6}],
    "recruitment":         [{"course_name":"Recruiting, Hiring, and Onboarding Employees","platform":"Coursera (Minnesota)","url":"https://www.coursera.org/learn/recruiting-hiring-onboarding-employees","duration":"4 weeks","level":"Beginner","rating":4.6}],
    "hr analytics":        [{"course_name":"People Analytics","platform":"Coursera (Wharton)","url":"https://www.coursera.org/learn/people-analytics","duration":"4 weeks","level":"Intermediate","rating":4.7}],
    "gcp":                 [{"course_name":"Good Clinical Practice (GCP) Certification","platform":"CITI Program","url":"https://about.citiprogram.org/","duration":"Self-paced","level":"Beginner","rating":4.8}],
    "clinical trials":     [{"course_name":"Clinical Research Fundamentals","platform":"Coursera (Vanderbilt)","url":"https://www.coursera.org/specializations/clinical-research","duration":"3 months","level":"Intermediate","rating":4.6}],
    "penetration testing": [{"course_name":"Complete Ethical Hacking Bootcamp","platform":"Udemy","url":"https://www.udemy.com/course/complete-ethical-hacking-bootcamp-zero-to-mastery/","duration":"30 hours","level":"Intermediate","rating":4.7}],
    "mlops":               [{"course_name":"MLOps Specialization","platform":"Coursera (DeepLearning.AI)","url":"https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops","duration":"4 months","level":"Advanced","rating":4.7}],
    "data pipeline":       [{"course_name":"Data Engineering Specialization","platform":"Coursera (DeepLearning.AI)","url":"https://www.coursera.org/specializations/data-engineering","duration":"5 months","level":"Intermediate","rating":4.6}],
    "airflow":             [{"course_name":"The Complete Hands-On Introduction to Apache Airflow","platform":"Udemy","url":"https://www.udemy.com/course/the-complete-hands-on-course-to-master-apache-airflow/","duration":"8 hours","level":"Intermediate","rating":4.7}],
}

DOMAIN_GENERAL = {
    "technical":   {"course_name":"CS50: Introduction to Computer Science","platform":"edX (Harvard)","url":"https://www.edx.org/learn/computer-science/harvard-university-cs50-s-introduction-to-computer-science","duration":"12 weeks","level":"Beginner","rating":4.9,"skill":"Computer Science Fundamentals"},
    "marketing":   {"course_name":"Digital Marketing Specialization","platform":"Coursera (Illinois)","url":"https://www.coursera.org/specializations/digital-marketing","duration":"8 months","level":"Beginner","rating":4.5,"skill":"Digital Marketing"},
    "finance":     {"course_name":"Finance for Non-Financial Professionals","platform":"Coursera (Rice)","url":"https://www.coursera.org/learn/finance-for-non-finance-managers","duration":"4 weeks","level":"Beginner","rating":4.6,"skill":"Finance Fundamentals"},
    "healthcare":  {"course_name":"Healthcare Innovation","platform":"Coursera (HKU)","url":"https://www.coursera.org/learn/healthcare-innovation","duration":"6 weeks","level":"Beginner","rating":4.6,"skill":"Healthcare Management"},
    "design":      {"course_name":"Google UX Design Professional Certificate","platform":"Coursera (Google)","url":"https://www.coursera.org/professional-certificates/google-ux-design","duration":"6 months","level":"Beginner","rating":4.8,"skill":"UX Design"},
    "legal":       {"course_name":"Contract Law: From Trust to Promise to Contract","platform":"edX (Harvard)","url":"https://www.edx.org/learn/contract-law","duration":"8 weeks","level":"Beginner","rating":4.7,"skill":"Contract Law"},
    "hr":          {"course_name":"Human Resource Management Specialization","platform":"Coursera (Minnesota)","url":"https://www.coursera.org/specializations/human-resource-management","duration":"5 months","level":"Beginner","rating":4.7,"skill":"HR Management"},
    "sales":       {"course_name":"Sales Training: Practical Sales Techniques","platform":"Udemy","url":"https://www.udemy.com/course/sales-training-practical-sales-techniques/","duration":"3 hours","level":"Beginner","rating":4.4,"skill":"Sales Fundamentals"},
    "consulting":  {"course_name":"Strategic Management Specialization","platform":"Coursera (Copenhagen)","url":"https://www.coursera.org/specializations/strategic-management","duration":"5 months","level":"Intermediate","rating":4.5,"skill":"Strategy"},
    "operations":  {"course_name":"Supply Chain Management Specialization","platform":"Coursera (Rutgers)","url":"https://www.coursera.org/specializations/supply-chain-management","duration":"5 months","level":"Beginner","rating":4.6,"skill":"Supply Chain"},
}

def recommend_courses(missing_skills: List[str], domain: str, level: str) -> List[dict]:
    recs, seen = [], set()
    for skill in missing_skills:
        sk = skill.lower()
        course_list = COURSES.get(sk, [])
        if not course_list:
            for key in COURSES:
                if sk in key or key in sk:
                    course_list = COURSES[key]; break
        for c in course_list:
            nm = c["course_name"]
            if nm not in seen:
                seen.add(nm)
                recs.append({**c, "skill": skill})
                break

    if len(recs) < 5:
        gen = DOMAIN_GENERAL.get(domain)
        if gen and gen["course_name"] not in seen:
            recs.append(gen)

    return recs[:8]
