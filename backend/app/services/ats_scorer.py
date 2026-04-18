"""
ATS Scorer v3 — field-aware weighted scoring.

Formula: 0.35×keywords + 0.20×formatting + 0.20×sections + 0.15×experience + 0.10×skills

Section weights, keyword lists, and scoring logic all vary by field.
Returns clear explanations and exact improvement steps.
"""
import json, os, re
from typing import List, Tuple, Dict
from functools import lru_cache

from app.constants import ACTION_VERBS

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# ── Field → which sections matter most ────────────────────────────────────────
SECTION_WEIGHTS: Dict[str, Dict[str, int]] = {
    "frontend_developer":    {"summary":10,"experience":20,"skills":18,"projects":16,"education":12,"certifications":12,"achievements":8,"portfolio":4},
    "backend_developer":     {"summary":10,"experience":22,"skills":18,"projects":16,"education":12,"certifications":12,"achievements":8,"publications":2},
    "fullstack_developer":   {"summary":10,"experience":20,"skills":16,"projects":18,"education":12,"certifications":12,"achievements":8,"portfolio":4},
    "java_developer":        {"summary":10,"experience":22,"skills":20,"projects":16,"education":14,"certifications":12,"achievements":6},
    "python_developer":      {"summary":10,"experience":22,"skills":18,"projects":16,"education":12,"certifications":14,"achievements":8},
    "software_engineer":     {"summary":10,"experience":22,"skills":18,"projects":14,"education":14,"certifications":12,"achievements":10},
    "data_analyst":          {"summary":10,"experience":20,"skills":18,"projects":16,"education":14,"certifications":10,"achievements":12},
    "data_scientist":        {"summary":10,"experience":20,"skills":16,"projects":18,"education":14,"certifications":10,"publications":8,"achievements":4},
    "ml_ai_engineer":        {"summary":8,"experience":20,"skills":16,"projects":20,"education":14,"certifications":10,"publications":8,"achievements":4},
    "devops_engineer":       {"summary":10,"experience":22,"skills":20,"projects":14,"education":12,"certifications":16,"achievements":6},
    "cloud_engineer":        {"summary":10,"experience":22,"skills":18,"projects":14,"education":12,"certifications":18,"achievements":6},
    "cybersecurity":         {"summary":10,"experience":22,"skills":18,"projects":12,"education":14,"certifications":18,"achievements":6},
    "qa_engineer":           {"summary":10,"experience":22,"skills":18,"projects":14,"education":14,"certifications":12,"achievements":10},
    "mobile_developer":      {"summary":10,"experience":20,"skills":18,"projects":18,"education":12,"certifications":12,"achievements":8,"portfolio":2},
    "product_manager":       {"summary":14,"experience":24,"skills":14,"projects":14,"education":14,"certifications":10,"achievements":10},
    "business_analyst":      {"summary":12,"experience":22,"skills":16,"projects":14,"education":16,"certifications":10,"achievements":10},
    "blockchain":            {"summary":10,"experience":18,"skills":18,"projects":22,"education":12,"certifications":12,"achievements":8},
    "ui_ux_designer":        {"summary":10,"experience":18,"skills":14,"projects":14,"education":12,"certifications":10,"achievements":8,"portfolio":14},
    "product_designer":      {"summary":10,"experience":18,"skills":14,"projects":14,"education":12,"certifications":8,"achievements":8,"portfolio":16},
    "graphic_designer":      {"summary":10,"experience":18,"skills":14,"projects":12,"education":12,"certifications":8,"achievements":8,"portfolio":18},
    "digital_marketing":     {"summary":12,"experience":22,"skills":16,"projects":12,"education":12,"certifications":14,"achievements":12},
    "seo_specialist":        {"summary":12,"experience":22,"skills":16,"projects":14,"education":12,"certifications":14,"achievements":10},
    "content_writer":        {"summary":14,"experience":22,"skills":12,"projects":14,"education":12,"certifications":6,"achievements":10,"publications":10},
    "social_media_manager":  {"summary":12,"experience":22,"skills":14,"projects":14,"education":12,"certifications":10,"achievements":16},
    "brand_marketing":       {"summary":12,"experience":24,"skills":14,"projects":12,"education":14,"certifications":10,"achievements":14},
    "finance_analyst":       {"summary":10,"experience":22,"skills":16,"projects":12,"education":16,"certifications":14,"achievements":10},
    "accountant":            {"summary":10,"experience":22,"skills":16,"projects":8,"education":18,"certifications":18,"achievements":8},
    "investment_banking":    {"summary":10,"experience":24,"skills":16,"projects":10,"education":18,"certifications":14,"achievements":8},
    "risk_compliance":       {"summary":10,"experience":22,"skills":16,"projects":10,"education":16,"certifications":18,"achievements":8},
    "equity_research":       {"summary":10,"experience":22,"skills":16,"projects":12,"education":18,"certifications":14,"achievements":8,"publications":4},
    "clinical_medicine":     {"summary":10,"experience":22,"skills":12,"education":20,"certifications":18,"publications":10,"research":8},
    "clinical_research":     {"summary":10,"experience":22,"skills":14,"projects":12,"education":16,"certifications":18,"publications":8},
    "nursing":               {"summary":10,"experience":24,"skills":14,"education":18,"certifications":20,"achievements":14},
    "corporate_law":         {"summary":10,"experience":24,"skills":12,"education":20,"certifications":10,"publications":10,"achievements":14},
    "litigation":            {"summary":10,"experience":26,"skills":12,"education":20,"publications":10,"achievements":12,"bar_admissions":10},
    "hr_recruiter":          {"summary":12,"experience":24,"skills":16,"projects":10,"education":14,"certifications":10,"achievements":14},
    "talent_acquisition":    {"summary":12,"experience":24,"skills":16,"projects":10,"education":14,"certifications":10,"achievements":14},
    "hr_business_partner":   {"summary":12,"experience":24,"skills":16,"projects":10,"education":14,"certifications":10,"achievements":14},
    "sales_executive":       {"summary":14,"experience":26,"skills":14,"education":12,"certifications":8,"achievements":26},
    "business_development":  {"summary":14,"experience":24,"skills":14,"education":14,"certifications":8,"achievements":26},
    "operations_executive":  {"summary":10,"experience":24,"skills":16,"projects":12,"education":14,"certifications":12,"achievements":12},
    "customer_support":      {"summary":14,"experience":26,"skills":16,"education":14,"certifications":8,"achievements":22},
    "consulting":            {"summary":14,"experience":26,"skills":14,"education":18,"certifications":8,"achievements":20},
    "management_trainee":    {"summary":14,"experience":16,"skills":14,"projects":16,"education":22,"certifications":10,"achievements":8},
    "general_fresher":       {"summary":14,"education":22,"skills":16,"projects":20,"certifications":12,"achievements":10,"internship":6},
}

# Default for unmapped fields
DEFAULT_WEIGHTS = {"summary":10,"experience":22,"education":14,"skills":16,"projects":12,"certifications":12,"achievements":10,"publications":4}

SECTION_ALIASES = {
    "summary":      ["summary","professional summary","profile","about","career profile","objective","career objective"],
    "experience":   ["experience","work experience","employment","professional experience","career history","work history","internship","industry experience"],
    "education":    ["education","academic","qualification","academics","educational background","schooling","degrees"],
    "skills":       ["skills","technical skills","core competencies","key skills","expertise","competencies","skillset","technologies","tools"],
    "projects":     ["projects","project work","key projects","personal projects","side projects","academic projects","open source","portfolio projects"],
    "certifications":["certifications","certificates","professional certifications","credentials","licensed","accreditations","courses completed"],
    "achievements": ["achievements","accomplishments","awards","recognition","honors","accolades","highlights"],
    "publications": ["publications","research","papers","articles","journals","conference","white papers","authored"],
    "portfolio":    ["portfolio","case studies","design work","creative work","gallery","work samples","behance","dribbble"],
    "bar_admissions":["bar exam","bar admission","enrolled advocate","advocate","llb registered","bar council"],
    "research":     ["research","clinical rotation","medical internship","clinical posting","residency","research project"],
    "internship":   ["internship","trainee","apprenticeship","work experience student"],
}

# ── ATS keyword data per field ─────────────────────────────────────────────────
FIELD_KEYWORDS = {
    "frontend_developer":   {"must": ["react","javascript","typescript","html","css","responsive design","git","rest api","component","state management"],"good": ["next.js","vue","angular","graphql","performance","accessibility","storybook","webpack"],"verbs": ["built","developed","optimized","shipped","designed","implemented","refactored","delivered"]},
    "backend_developer":    {"must": ["rest api","sql","git","python","java","node.js","microservices","database","authentication","server"],"good": ["docker","kubernetes","kafka","redis","grpc","message queue","ci/cd","aws"],"verbs": ["developed","built","architected","deployed","optimized","implemented","maintained","scaled"]},
    "fullstack_developer":  {"must": ["react","node.js","sql","rest api","git","html","css","javascript","database","deployment"],"good": ["typescript","docker","aws","mongodb","graphql","redis","ci/cd","nginx"],"verbs": ["built","developed","shipped","deployed","designed","integrated","maintained","delivered"]},
    "java_developer":       {"must": ["java","spring boot","sql","rest api","git","hibernate","maven","oop","multithreading","junit"],"good": ["microservices","docker","kubernetes","kafka","redis","spring security","jpa","gradle"],"verbs": ["developed","built","implemented","optimized","designed","deployed","maintained","delivered"]},
    "python_developer":     {"must": ["python","sql","git","rest api","django","flask","fastapi","pandas","oop","virtualenv"],"good": ["celery","redis","docker","kubernetes","sqlalchemy","pytest","asyncio","aws"],"verbs": ["developed","built","automated","scripted","deployed","optimized","implemented","maintained"]},
    "software_engineer":    {"must": ["git","sql","data structures","algorithms","oop","rest api","testing","code review","debugging","agile"],"good": ["docker","system design","cloud","ci/cd","microservices","distributed systems","performance"],"verbs": ["developed","built","designed","implemented","optimized","delivered","debugged","maintained"]},
    "data_analyst":         {"must": ["sql","excel","python","power bi","tableau","data visualization","reporting","dashboard","statistical analysis","data cleaning"],"good": ["google analytics","looker","airflow","pandas","numpy","ab testing","google sheets","pivot tables"],"verbs": ["analyzed","built","created","delivered","identified","reported","visualized","optimized","reduced"]},
    "data_scientist":       {"must": ["python","sql","machine learning","scikit-learn","pandas","numpy","statistics","feature engineering","model evaluation","jupyter"],"good": ["tensorflow","pytorch","xgboost","nlp","deep learning","spark","mlflow","experiment tracking"],"verbs": ["developed","built","trained","optimized","improved","analyzed","modeled","deployed","researched"]},
    "ml_ai_engineer":       {"must": ["python","machine learning","deep learning","tensorflow","pytorch","nlp","model deployment","feature engineering","git","docker"],"good": ["mlops","mlflow","kubeflow","transformer","llm","rag","vector database","cuda","distributed training"],"verbs": ["developed","trained","deployed","optimized","built","researched","improved","automated","published"]},
    "devops_engineer":      {"must": ["docker","kubernetes","ci/cd","linux","bash","git","terraform","ansible","monitoring","jenkins"],"good": ["helm","prometheus","grafana","elk","vault","gitops","argocd","aws","azure","cost optimization"],"verbs": ["deployed","automated","optimized","managed","built","implemented","migrated","reduced","maintained","streamlined"]},
    "cloud_engineer":       {"must": ["aws","azure","gcp","terraform","kubernetes","docker","iam","networking","storage","security"],"good": ["helm","ci/cd","serverless","cost optimization","multi-cloud","disaster recovery","landing zone","sla"],"verbs": ["deployed","architected","migrated","designed","optimized","automated","managed","built","reduced","delivered"]},
    "cybersecurity":        {"must": ["vulnerability assessment","penetration testing","siem","incident response","network security","firewalls","risk assessment","owasp","linux","python"],"good": ["cissp","ceh","oscp","threat intelligence","soc","zero trust","cloud security","forensics","malware analysis"],"verbs": ["identified","mitigated","assessed","secured","investigated","implemented","remediated","detected","analyzed"]},
    "qa_engineer":          {"must": ["test automation","selenium","test cases","bug reporting","manual testing","jira","api testing","regression","agile","test plan"],"good": ["cypress","playwright","jmeter","performance testing","security testing","ci/cd","contract testing","bdd","postman"],"verbs": ["tested","automated","identified","reduced","improved","designed","executed","validated","reported","built"]},
    "mobile_developer":     {"must": ["react native","flutter","kotlin","swift","git","rest api","mobile ui","state management","firebase","app store"],"good": ["jetpack compose","swiftui","performance","deep linking","push notifications","offline first","ci/cd mobile","analytics"],"verbs": ["built","developed","shipped","designed","optimized","integrated","deployed","maintained","delivered"]},
    "product_manager":      {"must": ["product roadmap","user stories","stakeholder management","a/b testing","analytics","backlog","agile","okr","kpi","go-to-market"],"good": ["sql","figma","product led growth","north star metric","cohort analysis","pricing","market research","customer discovery"],"verbs": ["launched","led","defined","drove","delivered","prioritized","grew","shipped","improved","collaborated"]},
    "business_analyst":     {"must": ["requirements gathering","process mapping","stakeholder management","uat","gap analysis","brd","use cases","sql","documentation","agile"],"good": ["erp","sap","salesforce","tableau","power bi","jira","confluence","bpmn","data flow diagram"],"verbs": ["analyzed","documented","facilitated","identified","mapped","improved","delivered","collaborated","presented","reduced"]},
    "digital_marketing":    {"must": ["google ads","facebook ads","google analytics","seo","sem","email marketing","campaign management","a/b testing","roi","lead generation"],"good": ["programmatic","marketing automation","hubspot","attribution modeling","cro","cpa","roas","ltv","cac","linkedin ads"],"verbs": ["launched","grew","drove","optimized","managed","increased","generated","reduced","delivered","executed"]},
    "seo_specialist":       {"must": ["seo","keyword research","on-page seo","technical seo","google analytics","link building","google search console","content optimization","ahrefs","semrush"],"good": ["core web vitals","schema markup","local seo","international seo","e-a-t","screaming frog","log analysis","seo audit"],"verbs": ["optimized","grew","improved","increased","reduced","audited","built","researched","delivered","managed"]},
    "content_writer":       {"must": ["copywriting","seo writing","content strategy","blog","editorial","proofreading","content calendar","wordpress","audience research","keyword"],"good": ["technical writing","white papers","case studies","email copy","ad copy","tone of voice","style guide","grammarly"],"verbs": ["wrote","created","developed","published","optimized","delivered","researched","edited","produced","managed"]},
    "social_media_manager": {"must": ["social media","instagram","facebook","linkedin","content creation","analytics","community management","engagement","scheduling","brand voice"],"good": ["tiktok","youtube","influencer","ugc","reels","hootsuite","buffer","paid social","crisis management","social listening"],"verbs": ["grew","managed","created","increased","drove","launched","engaged","built","delivered","optimized"]},
    "finance_analyst":      {"must": ["financial modeling","excel","budgeting","forecasting","variance analysis","p&l","financial reporting","valuation","dcf","kpi"],"good": ["power bi","tableau","sap","erp","python finance","board reporting","scenario planning","working capital","capex","opex"],"verbs": ["analyzed","modeled","forecasted","prepared","identified","reduced","improved","presented","delivered","managed"]},
    "accountant":           {"must": ["accounting","gaap","tax","gst","tds","reconciliation","audit","accounts payable","accounts receivable","tally"],"good": ["ifrs","ind as","sap fico","transfer pricing","statutory audit","internal audit","ifc testing","forensic accounting"],"verbs": ["audited","prepared","reconciled","filed","reviewed","managed","ensured","reduced","reported","maintained"]},
    "investment_banking":   {"must": ["financial modeling","dcf","m&a","due diligence","bloomberg","valuation","lbo","pitch book","capital markets","excel"],"good": ["comparable company","precedent transactions","leveraged finance","ipo","equity offering","fairness opinion","spac","debt structuring"],"verbs": ["analyzed","modeled","structured","advised","closed","executed","presented","evaluated","identified","negotiated"]},
    "hr_recruiter":         {"must": ["recruitment","sourcing","screening","interview","offer management","job posting","candidate experience","hiring","onboarding","ats"],"good": ["linkedin recruiter","boolean search","employer branding","campus hiring","naukri","diversity hiring","background check","reference check"],"verbs": ["recruited","sourced","hired","managed","reduced","built","partnered","delivered","achieved","coordinated"]},
    "talent_acquisition":   {"must": ["talent acquisition","full cycle recruiting","sourcing","linkedin recruiter","employer branding","hiring metrics","diversity hiring","executive search","ats","market mapping"],"good": ["workforce planning","rpo","predictive hiring","talent intelligence","competitive mapping","pipeline building","niche hiring","headhunting"],"verbs": ["recruited","sourced","hired","built","reduced","drove","managed","partnered","delivered","achieved"]},
    "sales_executive":      {"must": ["b2b sales","revenue","pipeline","quota","deal closure","cold calling","account management","crm","negotiation","lead generation"],"good": ["salesforce","meddic","solution selling","value selling","enterprise sales","channel sales","partner sales","abm","revops"],"verbs": ["closed","generated","grew","exceeded","secured","prospected","converted","retained","expanded","achieved"]},
    "business_development": {"must": ["business development","partnerships","prospecting","revenue growth","new business","market expansion","pipeline","crm","outreach","lead generation"],"good": ["strategic alliances","b2b partnerships","go-to-market","sales pitch","demo","proposal","contract negotiation","channel development"],"verbs": ["drove","generated","closed","built","grew","developed","identified","negotiated","secured","expanded"]},
    "operations_executive": {"must": ["operations","process management","supply chain","vendor management","inventory","procurement","sop","kpi","lean","erp"],"good": ["six sigma","logistics","warehouse","demand planning","cost reduction","quality control","iso","3pl","automation ops"],"verbs": ["streamlined","optimized","reduced","managed","implemented","coordinated","improved","delivered","sourced","tracked"]},
    "customer_support":     {"must": ["customer support","customer service","query resolution","ticketing","csat","sla","escalation","communication","helpdesk","product knowledge"],"good": ["zendesk","freshdesk","salesforce service","nps","chat support","email support","voice support","bpo","customer success"],"verbs": ["resolved","managed","reduced","improved","handled","delivered","maintained","trained","coordinated","achieved"]},
    "consulting":           {"must": ["strategy","problem solving","stakeholder management","data analysis","financial modeling","presentation","project management","client engagement","research","recommendations"],"good": ["mece","hypothesis-driven","digital transformation","org design","agile transformation","operating model","cost optimization","restructuring"],"verbs": ["led","advised","delivered","identified","structured","analyzed","recommended","facilitated","managed","drove"]},
    "ui_ux_designer":       {"must": ["figma","wireframing","prototyping","user research","usability testing","design system","typography","color theory","accessibility","ux design"],"good": ["interaction design","information architecture","design ops","adobe xd","service design","framer","user journey","persona","design thinking"],"verbs": ["designed","created","prototyped","researched","tested","delivered","shipped","built","collaborated","improved"]},
    "product_designer":     {"must": ["figma","design thinking","user research","prototyping","design system","usability testing","product design","ui design","ux design","stakeholder"],"good": ["0 to 1","design sprint","service design","design ops","b2b saas","mobile design","accessibility","design leadership"],"verbs": ["designed","led","shipped","researched","built","delivered","collaborated","improved","facilitated","strategized"]},
    "graphic_designer":     {"must": ["photoshop","illustrator","indesign","typography","color theory","brand design","logo","print design","visual design","layout"],"good": ["packaging","publication","art direction","3d rendering","motion graphics","after effects","generative design","canva"],"verbs": ["designed","created","crafted","delivered","built","produced","developed","collaborated","launched","refined"]},
    "corporate_law":        {"must": ["corporate law","m&a","due diligence","contract drafting","companies act","sebi","shareholders agreement","legal research","corporate governance","compliance"],"good": ["cross-border m&a","private equity","venture capital","capital markets","fema","competition law","restructuring","term sheet"],"verbs": ["drafted","negotiated","advised","reviewed","researched","represented","filed","structured","closed","managed"]},
    "clinical_medicine":    {"must": ["patient care","clinical assessment","diagnosis","treatment","ehr","pharmacology","medical documentation","emergency care","anatomy","physiology"],"good": ["icu","advanced life support","clinical research","radiology","evidence-based medicine","quality improvement","telemedicine"],"verbs": ["diagnosed","treated","managed","monitored","administered","assessed","implemented","educated","coordinated","delivered"]},
    "management_trainee":   {"must": ["teamwork","communication","leadership","problem solving","analytical thinking","excel","presentation","internship","cross-functional","training"],"good": ["erp","data analysis","stakeholder management","project management","process improvement","six sigma","sql","power bi"],"verbs": ["led","managed","coordinated","delivered","analyzed","implemented","collaborated","improved","presented","built"]},
    "general_fresher":      {"must": ["communication","teamwork","adaptability","problem solving","ms office","excel","presentation","time management","learning","internship"],"good": ["python","sql","digital marketing","content writing","data analysis","project","volunteering","leadership","hackathon","certification"],"verbs": ["completed","participated","developed","contributed","assisted","supported","learned","presented","managed","achieved"]},
}

DEFAULT_KEYWORDS = {
    "must":  ["communication","teamwork","problem solving","leadership","time management","ms office","excel","presentation","internship","project"],
    "good":  ["python","sql","data analysis","digital marketing","certifications","agile","stakeholder","analytical thinking"],
    "verbs": ["developed","managed","delivered","led","built","completed","improved","coordinated","achieved","contributed"],
}


@lru_cache(maxsize=64)
def _load_kw(field_key: str) -> dict:
    """Load keywords — cached to avoid repeated file I/O."""
    kw = FIELD_KEYWORDS.get(field_key, DEFAULT_KEYWORDS)
    # Also try domain-level from ats_keywords_dataset.json if present
    path = os.path.join(DATA_DIR, 'ats_keywords_dataset.json')
    if os.path.exists(path):
        with open(path) as f:
            ds = json.load(f)
        if field_key in ds:
            ds_entry = ds[field_key]
            # Merge — inline dict is primary, file adds extras
            kw = {
                "must":  list(set(kw.get("must", kw.get("must_have_keywords", [])) + ds_entry.get("must_have_keywords", []))),
                "good":  list(set(kw.get("good", kw.get("good_to_have", [])) + ds_entry.get("good_to_have", []))),
                "verbs": list(set(kw.get("verbs", kw.get("action_verbs", [])) + ds_entry.get("action_verbs", []))),
            }
    return kw


def _keyword_score(text: str, field_key: str) -> Tuple[float, List[str], List[str]]:
    """Score keyword coverage. Returns (score, found_kws, missing_must_kws)."""
    kw = _load_kw(field_key)
    must  = kw.get("must",  kw.get("must_have_keywords", []))
    good  = kw.get("good",  kw.get("good_to_have", []))
    verbs = kw.get("verbs", kw.get("action_verbs", ACTION_VERBS))
    tl = text.lower()

    found_must  = [k for k in must  if k.lower() in tl]
    found_good  = [k for k in good  if k.lower() in tl]
    found_verbs = [v for v in verbs if v.lower() in tl]

    # Fairer curve: diminishing penalty so 70% coverage ≈ 65 instead of 40
    must_ratio = len(found_must) / max(len(must), 1)
    must_s  = (must_ratio ** 0.7) * 50
    good_s  = (len(found_good) / max(len(good), 1)) * 30
    verb_s  = min((len(found_verbs) / 4) * 20, 20)

    score = round(min(must_s + good_s + verb_s, 100), 2)
    found   = list(set(found_must + found_good))
    missing = [k for k in must if k not in found_must]
    return score, found, missing


def _section_present(text_lower: str, aliases: list) -> bool:
    """Check if a section heading exists — tries heading patterns first, then substring fallback."""
    for alias in aliases:
        # Match at line start or after newline (typical section headings)
        pattern = r'(?:^|\n)\s*' + re.escape(alias) + r'\s*(?:\n|:|\-|$)'
        if re.search(pattern, text_lower):
            return True
    # Fallback: substring match (for formats without clear headings)
    for alias in aliases:
        if alias in text_lower:
            return True
    return False


def _section_score(text: str, field_key: str) -> Tuple[float, List[dict]]:
    """Score section completeness with field-specific weights."""
    tl = text.lower()
    weights = SECTION_WEIGHTS.get(field_key, DEFAULT_WEIGHTS)
    results = []
    earned = total = 0

    FEEDBACK = {
        "summary":      "A field-tailored professional summary is the first thing ATS parses. Keep it 3–4 lines with your top keywords.",
        "experience":   "Work experience carries the highest ATS weight. Use bullet points with action verbs and quantified results.",
        "education":    "Include degree, institution, graduation year, and GPA if ≥ 7.5.",
        "skills":       "List role-specific technical and domain skills. Avoid generic terms.",
        "projects":     "Projects prove applied expertise — critical for technical, design, and fresher profiles.",
        "certifications":"Certifications directly add ATS keywords and signal commitment.",
        "achievements": "Quantified achievements (%, numbers, revenue) significantly improve ATS scoring.",
        "publications": "Publications signal domain authority — even conference abstracts count.",
        "portfolio":    "Portfolio link is mandatory for design, content, and creative roles.",
        "bar_admissions":"Clearly list Bar Council enrollment and jurisdiction for legal profiles.",
        "research":     "List clinical rotations, research projects, or field work with outcomes.",
        "internship":   "Internship experience is critical for fresher profiles — list it prominently.",
    }

    for section, weight in weights.items():
        aliases = SECTION_ALIASES.get(section, [section])
        present = _section_present(tl, aliases)
        total += weight
        if present:
            earned += weight
        results.append({
            "name":        section.replace("_", " ").title(),
            "present":     present,
            "score":       100.0 if present else 0.0,
            "feedback":    FEEDBACK.get(section, ""),
            "suggestions": [] if present else [f"Add a '{section.replace('_',' ').title()}' section."],
        })

    score = round((earned / max(total, 1)) * 100, 2)
    return score, results


def _formatting_score(text: str) -> float:
    """Score formatting quality — 20% weight."""
    from app.services.parser import check_formatting
    return check_formatting(text)["score"]


def _experience_score(text: str, years: float) -> float:
    """Score experience quality — 15% weight. Freshers get credit for internships/projects."""
    tl = text.lower()
    score = 0.0

    # Base: years of experience (or fresher-friendly alternatives)
    if years > 0:
        score += min(years * 5, 30)
    else:
        # Freshers: credit for internships and academic projects
        if re.search(r'internship|intern\b|trainee', tl):
            score += 15
        if re.search(r'project|capstone|thesis|hackathon', tl):
            score += 10

    if re.search(r'\d+\s*%', text):                                          score += 18
    if re.search(r'\d+\s*(million|billion|lakh|crore|\bk\b|users|clients)', tl): score += 14
    if re.search(r'(team of|managed|led)\s+\d+', tl):                       score += 13
    verbs_found = sum(1 for v in ACTION_VERBS if v in tl)
    score += min(verbs_found * 2.5, 25)
    return round(min(score, 100), 2)


def _skill_score(found_skills: List[str]) -> float:
    """Score skill coverage — 10% weight. Stepped curve so 8-12 skills is already strong."""
    count = len(found_skills)
    if count >= 12:
        return 100.0
    elif count >= 8:
        return round(80 + (count - 8) * 5, 2)
    elif count >= 4:
        return round(50 + (count - 4) * 7.5, 2)
    else:
        return round(count * 12.5, 2)


def _build_interpretation(total: float, grade: str, field_key: str, kw_score: float, fmt_score: float, sec_score: float) -> str:
    field_display = field_key.replace("_", " ").title()
    if total >= 80:
        return f"Excellent ATS compatibility for {field_display}. You are in the top 10–15% of applicants. Focus on tailoring per JD."
    elif total >= 65:
        return f"Good score for {field_display}. Targeted keyword additions and a Certifications section will push you above 80."
    elif total >= 50:
        lowestKey = "keywords" if kw_score < 55 else "formatting" if fmt_score < 55 else "sections"
        return f"Average ATS score. Your {lowestKey} score is below the threshold for most ATS filters in {field_display} roles. See the breakdown for exact fixes."
    elif total >= 35:
        return f"Below average. Your resume likely fails ATS pre-screening for {field_display} roles. Restructure with field-specific keywords and ensure all critical sections exist."
    else:
        return f"Very low ATS compatibility. Consider rebuilding using a clean ATS-friendly template and filling in all sections with {field_display}-specific keywords."


def compute_ats_score(
    text: str, field_key: str, domain: str,
    years: float, found_skills: List[str]
) -> dict:
    """
    Master ATS scoring function.
    Returns full scoring dict including section_details, keywords_found, keywords_missing.
    """
    kw_score,  kw_found, kw_missing = _keyword_score(text, field_key)
    fmt_score                        = _formatting_score(text)
    sec_score, sec_details           = _section_score(text, field_key)
    exp_score                        = _experience_score(text, years)
    sk_score                         = _skill_score(found_skills)

    total = round(
        0.35 * kw_score +
        0.20 * fmt_score +
        0.20 * sec_score +
        0.15 * exp_score +
        0.10 * sk_score,
        2
    )

    grade = "A" if total >= 80 else "B" if total >= 65 else "C" if total >= 50 else "D" if total >= 35 else "F"
    interpretation = _build_interpretation(total, grade, field_key, kw_score, fmt_score, sec_score)

    return {
        "total": total,
        "keyword_score":    kw_score,
        "formatting_score": fmt_score,
        "section_score":    sec_score,
        "experience_score": exp_score,
        "skill_score":      sk_score,
        "grade":            grade,
        "interpretation":   interpretation,
        "keywords_found":   kw_found,
        "keywords_missing": kw_missing,
        "section_details":  sec_details,
    }
