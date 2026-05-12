"""
job_matcher.py — Field-aware Job Matching Engine

Features:
  - Universal field resolver (no wrong fallback to software_engineering)
  - Synonym-aware skill matching
  - Scoring: 65% skill overlap + 35% keyword overlap
  - Returns top 5 matched jobs per field+level
  - Correct company recommendations per exact field
"""

import json
import os
import re
from typing import List, Dict, Tuple, Optional

from app.services.skill_analyzer import resolve_field, _normalise, _skill_present

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

_JOBS_CACHE:      dict | None = None
_COMPANIES_CACHE: dict | None = None
_SKILLS_CACHE:    dict | None = None


def _load_jobs() -> dict:
    global _JOBS_CACHE
    if _JOBS_CACHE is None:
        path = os.path.join(DATA_DIR, 'jobs_dataset.json')
        with open(path, 'r', encoding='utf-8') as f:
            _JOBS_CACHE = json.load(f)
    return _JOBS_CACHE


def _load_companies() -> dict:
    global _COMPANIES_CACHE
    if _COMPANIES_CACHE is None:
        path = os.path.join(DATA_DIR, 'companies_dataset.json')
        with open(path, 'r', encoding='utf-8') as f:
            _COMPANIES_CACHE = json.load(f)
    return _COMPANIES_CACHE


def _load_skills_ds() -> dict:
    global _SKILLS_CACHE
    if _SKILLS_CACHE is None:
        path = os.path.join(DATA_DIR, 'skills_dataset.json')
        with open(path, 'r', encoding='utf-8') as f:
            _SKILLS_CACHE = json.load(f)
    return _SKILLS_CACHE


# ── Level normalisation ───────────────────────────────────────────────────────

def _resolve_level(level: str) -> str:
    level = (level or '').strip().lower()
    if level in ('fresher', 'entry', 'entry level', 'intern', 'trainee', '0', 'junior'):
        return 'fresher'
    if level in ('junior', 'associate', '1', '2'):
        return 'junior'
    if level in ('mid', 'mid-level', 'middle', '3', '4', '5'):
        return 'mid'
    if level in ('senior', 'lead', 'principal', 'staff', '6', '7', '8', '9'):
        return 'senior'
    return 'mid'


# ── Synonym-aware keyword matching ────────────────────────────────────────────

def _build_synonym_map(field_key: str) -> Dict[str, List[str]]:
    """
    Returns {canonical_name: [synonym1, synonym2, ...]} for the given field.
    Used to do synonym-aware skill matching when scoring jobs.
    """
    ds = _load_skills_ds()
    field_data = ds.get(field_key, {})
    synonym_map: Dict[str, List[str]] = {}
    for section in ('core_skills', 'advanced_skills', 'soft_skills'):
        for canonical, syns in field_data.get(section, {}).items():
            synonym_map[canonical.lower()] = [s.lower() for s in syns]
    return synonym_map


def _skill_match_score(
    resume_text_norm: str,
    found_skills: List[str],
    required_skills: List[str],
    synonym_map: Dict[str, List[str]],
) -> Tuple[float, List[str], List[str]]:
    """
    Match required_skills against resume using synonym expansion.
    Returns (ratio 0-1, matched_list, missing_list).
    """
    if not required_skills:
        return 0.0, [], []

    matched  = []
    missing  = []
    found_lower = {s.lower() for s in found_skills}

    for req in required_skills:
        req_l = req.lower()

        # 1. Direct match against found_skills
        if req_l in found_lower:
            matched.append(req)
            continue

        # 2. Synonym expansion: look up synonyms in the map
        synonyms = synonym_map.get(req_l, [req_l])
        if _skill_present(resume_text_norm, synonyms):
            matched.append(req)
            continue

        # 3. Partial substring check (catches "Advanced Excel" matching "Excel")
        found_in_text = any(
            req_l in s_l or s_l in req_l
            for s_l in found_lower
        )
        if found_in_text:
            matched.append(req)
            continue

        missing.append(req)

    ratio = len(matched) / max(len(required_skills), 1)
    return ratio, matched, missing


def _keyword_match_score(
    resume_text_norm: str,
    keywords: List[str],
) -> float:
    """Simple keyword overlap ratio against resume text (case-insensitive)."""
    if not keywords:
        return 0.0
    hits = sum(
        1 for kw in keywords
        if re.search(r'\b' + re.escape(kw.lower()) + r'\b', resume_text_norm)
        or kw.lower() in resume_text_norm
    )
    return hits / max(len(keywords), 1)


# ── Main matching function ────────────────────────────────────────────────────

def match_jobs(
    text: str,
    field_key: str,
    level: str,
    found_skills: List[str],
) -> List[dict]:
    """
    Match the resume against jobs in the dataset.

    Algorithm:
      score = 0.65 × skill_match + 0.35 × keyword_match
      capped at 97%

    Returns up to 6 sorted results.
    """
    jobs_data = _load_jobs()
    canonical = resolve_field(field_key)
    level_key = _resolve_level(level)

    text_norm    = _normalise(text)
    synonym_map  = _build_synonym_map(canonical)

    # Get jobs for this field
    field_jobs: dict = jobs_data.get(canonical, {})

    # If field has no jobs, try a graceful broadening for closely related fields
    if not field_jobs:
        # Map non-tech fields with thin job datasets to closest parent
        PARENT_MAP = {
            "consulting":       "sales",          # consulting has strategy
            "education":        "operations",     # operations overlap
        }
        parent = PARENT_MAP.get(canonical)
        if parent:
            field_jobs = jobs_data.get(parent, {})
        if not field_jobs:
            return []

    # Level fallback order
    LEVEL_FALLBACK = {
        'fresher': ['fresher', 'junior', 'mid'],
        'junior':  ['junior', 'fresher', 'mid'],
        'mid':     ['mid', 'junior', 'senior'],
        'senior':  ['senior', 'mid'],
    }

    job_list: List[dict] = []
    for lvl in LEVEL_FALLBACK.get(level_key, ['mid']):
        if lvl in field_jobs:
            job_list = field_jobs[lvl]
            break

    if not job_list:
        # Last attempt: any level from this field
        for lvl in ('mid', 'fresher', 'junior', 'senior'):
            if lvl in field_jobs:
                job_list = field_jobs[lvl]
                break

    if not job_list:
        return []

    results = []
    for job in job_list:
        required  = job.get('required_skills', [])
        kw_list   = job.get('job_match_keywords', required)

        skill_ratio, matched, missing = _skill_match_score(
            text_norm, found_skills, required, synonym_map
        )
        kw_ratio = _keyword_match_score(text_norm, kw_list)

        score = round(min(0.65 * skill_ratio + 0.35 * kw_ratio, 0.97) * 100, 1)

        results.append({
            'role':           job.get('role', 'Unknown Role'),
            'match_percent':  score,
            'required_skills':required,
            'matched_skills': matched,
            'missing_skills': missing[:5],
            'companies':      job.get('companies', []),
            'avg_salary':     job.get('avg_salary', 'N/A'),
            'level':          level_key,
        })

    results.sort(key=lambda x: x['match_percent'], reverse=True)
    return results[:6]


# ── Company recommendations ───────────────────────────────────────────────────


# ── Company → Official Careers Page ──────────────────────────────────────────
# Keys are lowercase for case-insensitive lookup.
# All links point directly to the company's careers/jobs page.

COMPANY_APPLY_LINKS: Dict[str, str] = {
    # ── Global Tech MNCs ──────────────────────────────────────────────────────
    "google":                       "https://careers.google.com",
    "google (chrome/web)":          "https://careers.google.com",
    "google (deepmind/ai)":         "https://careers.google.com",
    "google (gcp)":                 "https://careers.google.com",
    "microsoft":                    "https://careers.microsoft.com",
    "microsoft (m365/teams)":       "https://careers.microsoft.com",
    "microsoft (azure)":            "https://careers.microsoft.com",
    "microsoft (github)":           "https://careers.microsoft.com",
    "apple":                        "https://www.apple.com/careers",
    "meta":                         "https://www.metacareers.com",
    "amazon":                       "https://www.amazon.jobs",
    "amazon (aws)":                 "https://www.amazon.jobs",
    "netflix":                      "https://jobs.netflix.com",
    "adobe":                        "https://www.adobe.com/careers.html",
    "adobe (dx cloud)":             "https://www.adobe.com/careers.html",
    "salesforce":                   "https://careers.salesforce.com",
    "oracle":                       "https://careers.oracle.com",
    "sap":                          "https://jobs.sap.com",
    "ibm":                          "https://www.ibm.com/employment",
    "accenture":                    "https://www.accenture.com/us-en/careers",
    "deloitte":                     "https://apply.deloitte.com",
    "pwc":                          "https://www.pwc.com/gx/en/careers.html",
    "ey":                           "https://careers.ey.com",
    "kpmg":                         "https://home.kpmg/xx/en/home/careers.html",
    "mckinsey":                     "https://www.mckinsey.com/careers",
    "bcg":                          "https://careers.bcg.com",
    "bain":                         "https://www.bain.com/careers",
    "jpmorgan":                     "https://careers.jpmorgan.com",
    "jpmorgan chase":               "https://careers.jpmorgan.com",
    "goldman sachs":                "https://www.goldmansachs.com/careers",
    "morgan stanley":               "https://www.morganstanley.com/people/campus",
    "citigroup":                    "https://jobs.citi.com",
    "barclays":                     "https://search.jobs.barclays",
    "hsbc":                         "https://www.hsbc.com/careers",
    "deutsche bank":                "https://careers.db.com",
    "ubs":                          "https://www.ubs.com/global/en/careers.html",
    "airbnb":                       "https://careers.airbnb.com",
    "uber":                         "https://www.uber.com/global/en/careers",
    "lyft":                         "https://www.lyft.com/careers",
    "twitter":                      "https://careers.twitter.com",
    "linkedin":                     "https://careers.linkedin.com",
    "snap":                         "https://careers.snap.com",
    "spotify":                      "https://www.lifeatspotify.com",
    "shopify":                      "https://www.shopify.com/careers",
    "stripe":                       "https://stripe.com/jobs",
    "atlassian":                    "https://www.atlassian.com/company/careers",
    "cloudflare":                   "https://www.cloudflare.com/careers",
    "datadog":                      "https://www.datadoghq.com/careers",
    "twilio":                       "https://www.twilio.com/en-us/company/jobs",
    "okta":                         "https://www.okta.com/company/careers",
    "crowdstrike":                  "https://www.crowdstrike.com/careers",
    "palantir":                     "https://jobs.lever.co/palantir",
    "figma":                        "https://www.figma.com/careers",
    "notion":                       "https://www.notion.so/careers",
    "slack":                        "https://slack.com/careers",
    "zoom":                         "https://careers.zoom.us",
    "hubspot":                      "https://www.hubspot.com/careers",
    "zendesk":                      "https://www.zendesk.com/jobs",
    "twitch":                       "https://www.twitch.tv/jobs",
    "roblox":                       "https://careers.roblox.com",
    "nvidia":                       "https://www.nvidia.com/en-us/about-nvidia/careers",
    "amd":                          "https://jobs.amd.com",
    "intel":                        "https://jobs.intel.com",
    "qualcomm":                     "https://www.qualcomm.com/company/careers",
    "arm":                          "https://careers.arm.com",
    "siemens":                      "https://jobs.siemens.com",
    "bosch":                        "https://www.bosch.com/careers",
    # ── India-HQ / India-presence companies ───────────────────────────────────
    "tcs":                          "https://www.tcs.com/careers",
    "tata consultancy services":    "https://www.tcs.com/careers",
    "infosys":                      "https://career.infosys.com",
    "wipro":                        "https://careers.wipro.com",
    "hcl technologies":             "https://www.hcltech.com/careers",
    "hcl":                          "https://www.hcltech.com/careers",
    "tech mahindra":                "https://careers.techmahindra.com",
    "capgemini":                    "https://www.capgemini.com/in-en/careers",
    "cognizant":                    "https://careers.cognizant.com",
    "mphasis":                      "https://careers.mphasis.com",
    "hexaware":                     "https://hexaware.com/careers",
    "l&t technology services":      "https://www.ltts.com/careers",
    "persistent systems":           "https://www.persistent.com/careers",
    "mindtree":                     "https://www.mindtree.com/careers",
    "ltimindtree":                  "https://www.ltimindtree.com/careers",
    "mphasis":                      "https://careers.mphasis.com",
    "coforge":                      "https://www.coforge.com/careers",
    "niit technologies":            "https://www.niit.com/en/careers",
    "oracle (india)":               "https://careers.oracle.com",
    "samsung research india":       "https://research.samsung.com/sri",
    "flipkart":                     "https://www.flipkartcareers.com",
    "swiggy":                       "https://careers.swiggy.com",
    "zomato":                       "https://www.zomato.com/careers",
    "ola":                          "https://www.olacabs.com/careers",
    "paytm":                        "https://paytm.com/careers",
    "phonepe":                      "https://careers.phonepe.com",
    "navi":                         "https://navi.com/careers",
    "razorpay":                     "https://razorpay.com/jobs",
    "zepto":                        "https://www.zepto.com/careers",
    "blinkit":                      "https://blinkit.com/rn/career/",
    "meesho":                       "https://meesho.io/careers",
    "dream11":                      "https://dream11.freshteam.com/jobs",
    "cred":                         "https://cred.club/careers",
    "groww":                        "https://groww.in/careers",
    "upstox":                       "https://upstox.com/careers",
    "zerodha":                      "https://zerodha.com/careers",
    "angel one":                    "https://www.angelone.in/careers",
    "policybazaar":                 "https://www.policybazaar.com/careers",
    "nykaa":                        "https://careers.nykaa.com",
    "cars24":                       "https://www.cars24.com/careers",
    "lenskart":                     "https://lenskart.com/careers",
    "mamaearth":                    "https://mamaearth.in/pages/careers",
    "urban company":                "https://www.urbancompany.com/careers",
    "dunzo":                        "https://www.dunzo.com/careers",
    "byju's":                       "https://byjus.com/careers",
    "unacademy":                    "https://unacademy.com/careers",
    "vedantu":                      "https://www.vedantu.com/career",
    "freshworks":                   "https://careers.freshworks.com",
    "zoho":                         "https://www.zoho.com/careers",
    "hasura":                       "https://hasura.io/careers",
    "postman":                      "https://www.postman.com/company/careers",
    "browserstack":                 "https://www.browserstack.com/careers",
    "testbook":                     "https://testbook.com/careers",
    "moengage":                     "https://www.moengage.com/careers",
    "clevertap":                    "https://clevertap.com/careers",
    "chargebee":                    "https://www.chargebee.com/careers",
    "leadsquared":                  "https://www.leadsquared.com/careers",
    "sprinklr":                     "https://www.sprinklr.com/careers",
    "druva":                        "https://www.druva.com/careers",
    "icici bank":                   "https://www.icicicareers.com",
    "hdfc bank":                    "https://www.hdfcbank.com/content/bbp/repositories/723fb80a-2dde-42a3-9793-7ae1be57c87f/?folderPath=/Personal%20Banking/Careers",
    "axis bank":                    "https://www.axisbank.com/career",
    "kotak mahindra bank":          "https://www.kotak.com/en/careers.html",
    "bajaj finserv":                "https://bajajfinserv.in/careers",
    "reliance industries":          "https://ril.com/OurPeople/Careers.aspx",
    "mahindra group":               "https://careers.mahindra.com",
    "tata group":                   "https://www.tata.com/careers",
    "airtel":                       "https://www.airtel.in/careers",
    "jio":                          "https://careers.ril.com",
    "aazol":                        "https://aazol.in/careers",
    # ── Design / Creative ─────────────────────────────────────────────────────
    "canva":                        "https://www.canva.com/careers",
    "sketch":                       "https://www.sketch.com/careers",
    "invision":                     "https://www.invisionapp.com/company/careers",
    "framer":                       "https://framer.com/jobs",
    "zeplin":                       "https://zeplin.io/careers",
    "miro":                         "https://miro.com/careers",
    "figma (design)":               "https://www.figma.com/careers",
    # ── Data / AI / ML ────────────────────────────────────────────────────────
    "openai":                       "https://openai.com/careers",
    "anthropic":                    "https://www.anthropic.com/careers",
    "cohere":                       "https://cohere.com/careers",
    "hugging face":                 "https://apply.workable.com/huggingface",
    "databricks":                   "https://www.databricks.com/company/careers",
    "snowflake":                    "https://careers.snowflake.com",
    "dbt labs":                     "https://www.getdbt.com/dbt-labs/open-roles",
    "scale ai":                     "https://scale.com/careers",
    "weights & biases":             "https://wandb.ai/site/company/careers",
    "langchain":                    "https://jobs.ashbyhq.com/langchain",
    "comet ml":                     "https://www.comet.com/site/company/careers",
    "h2o.ai":                       "https://h2o.ai/careers",
    # ── Cybersecurity ─────────────────────────────────────────────────────────
    "palo alto networks":           "https://www.paloaltonetworks.com/company/careers",
    "fortinet":                     "https://www.fortinet.com/corporate/careers",
    "check point":                  "https://careers.checkpoint.com",
    "rapid7":                       "https://www.rapid7.com/company/careers",
    "sentinelone":                  "https://www.sentinelone.com/careers",
    "tenable":                      "https://careers.tenable.com",
    "darktrace":                    "https://www.darktrace.com/en/careers",
    "zscaler":                      "https://www.zscaler.com/careers",
    "secureworks":                  "https://www.secureworks.com/company/careers",
    "mandiant":                     "https://www.mandiant.com/company/careers",
    # ── DevOps / Cloud ────────────────────────────────────────────────────────
    "hashicorp":                    "https://www.hashicorp.com/jobs",
    "chef":                         "https://www.chef.io/careers",
    "puppet":                       "https://www.puppet.com/company/careers",
    "circleci":                     "https://circleci.com/careers",
    "gitlab":                       "https://about.gitlab.com/jobs",
    "github":                       "https://careers.github.com",
    "jetbrains":                    "https://www.jetbrains.com/careers",
    "docker":                       "https://www.docker.com/careers",
    "rancher labs":                 "https://www.rancher.com/careers",
    "redhat":                       "https://www.redhat.com/en/jobs",
    "red hat":                      "https://www.redhat.com/en/jobs",
    # ── Finance / Banking ─────────────────────────────────────────────────────
    "blackrock":                    "https://careers.blackrock.com",
    "vanguard":                     "https://www.vanguardjobs.com",
    "fidelity investments":         "https://jobs.fidelity.com",
    "charles schwab":               "https://www.schwab.com/about-schwab/careers",
    "nomura":                       "https://www.nomura.com/careers",
    "credit suisse":                "https://www.credit-suisse.com/careers",
    "bnp paribas":                  "https://group.bnpparibas/en/careers",
    "société générale":             "https://careers.societegenerale.com",
    "standard chartered":           "https://careers.standardchartered.com",
    "wells fargo":                  "https://www.wellsfargo.com/about/careers",
    "bank of america":              "https://careers.bankofamerica.com",
    "citibank":                     "https://jobs.citi.com",
    "american express":             "https://www.americanexpress.com/en-us/careers",
    "visa":                         "https://usa.visa.com/about-visa/careers.html",
    "mastercard":                   "https://careers.mastercard.com",
    "paypal":                       "https://careers.pypl.com",
    "square":                       "https://careers.squareup.com",
    "robinhood":                    "https://careers.robinhood.com",
    "coinbase":                     "https://www.coinbase.com/careers",
    "bloomberg":                    "https://careers.bloomberg.com",
    "refinitiv":                    "https://careers.refinitiv.com",
    # ── HR / Talent ───────────────────────────────────────────────────────────
    "naukri":                       "https://infoedge.in/careers",
    "linkedin (talent)":            "https://careers.linkedin.com",
    "adp":                          "https://jobs.adp.com",
    "workday":                      "https://www.workday.com/en-us/company/careers.html",
    "bamboohr":                     "https://www.bamboohr.com/careers",
    "greenhouse":                   "https://www.greenhouse.io/careers",
    "lever":                        "https://www.lever.co/careers",
    "icims":                        "https://www.icims.com/company/careers",
    "successfactors":               "https://jobs.sap.com",
    "keka":                         "https://www.keka.com/careers",
    "darwinbox":                    "https://darwinbox.com/careers",
    # ── Marketing / Content ───────────────────────────────────────────────────
    "wpengine":                     "https://wpengine.com/careers",
    "semrush":                      "https://www.semrush.com/company/careers",
    "ahrefs":                       "https://ahrefs.com/jobs",
    "moz":                          "https://moz.com/about/jobs",
    "mailchimp":                    "https://mailchimp.com/about/careers",
    "convertkit":                   "https://convertkit.com/careers",
    "sprout social":                "https://sproutsocial.com/careers",
    "hootsuite":                    "https://careers.hootsuite.com",
    "buffer":                       "https://buffer.com/journey",
    "wistia":                       "https://wistia.com/about/jobs",
    "vidyard":                      "https://www.vidyard.com/about/careers",
    "contentful":                   "https://www.contentful.com/careers",
    "wp engine":                    "https://wpengine.com/careers",
    # ── Legal ─────────────────────────────────────────────────────────────────
    "azb & partners":               "https://www.azbpartners.com/careers",
    "cyril amarchand mangaldas":    "https://www.cyrilamarchandmangaldas.com/careers",
    "shardul amarchand mangaldas":  "https://www.shardulamarchand.com/careers",
    "trilegal":                     "https://trilegal.com/careers",
    "khaitan & co":                 "https://khaitanco.com/careers",
    "induslaw":                     "https://induslaw.com/careers",
    "luthra & luthra":              "https://www.luthraluthra.com/careers",
    "nishith desai associates":     "https://www.nishithdesai.com/careers",
    "j sagar associates":           "https://www.jsalaw.com/careers",
    "lakshmikumaran & sridharan":   "https://www.lakshmisri.com/careers",
    # ── E-commerce / Retail ───────────────────────────────────────────────────
    "myntra":                       "https://careers.myntra.com",
    "ajio":                         "https://careers.jio.com",
    "bigbasket":                    "https://www.bigbasket.com/careers",
    "jiomart":                      "https://careers.jio.com",
    "amazon india":                 "https://www.amazon.jobs/en/locations/india",
    "walmart global tech":          "https://careers.walmart.com",
    "target india":                 "https://corporate.target.com/careers",
    "ikea":                         "https://jobs.ikea.com",
    "ebay":                         "https://jobs.ebayinc.com",
}

def _get_apply_link(company_name: str) -> str:
    """Case-insensitive lookup of a company's careers page."""
    return COMPANY_APPLY_LINKS.get(company_name.lower(), "https://www.linkedin.com/jobs/search/?keywords=" + company_name.replace(" ", "+"))


def get_company_recommendations(field_key: str, level: str) -> dict:
    companies_data = _load_companies()

    # 🔥 mapping fix (MOST IMPORTANT)
    company_key_map = {
        "accounting": "accountant",
        "financial_analysis": "finance_analyst",
        "sales": "sales_executive",
        "hr": "hr_recruiter",
        "frontend_development": "frontend_developer",
        "software_engineering": "software_engineer",
        "data_science": "data_scientist",
        "ui_ux_design": "ui_ux_designer",
        "product_management": "product_manager",
        "operations": "operations_executive",
        "mobile_development": "mobile_developer",
        "devops_cloud": "devops_engineer",
        "cybersecurity": "cybersecurity_analyst",
        "consulting": "management_consultant",
        "education": "education_professional",
        "marketing": "marketing_specialist"
    }

    canonical = company_key_map.get(field_key, field_key)
    field_companies = companies_data.get(canonical, {})

    def _enrich(company_list: list, limit: int) -> list:
        result = []
        for c in company_list[:limit]:
            result.append({
                "name":             c["name"],
                "ats_strictness":   c.get("ats_strictness", "medium"),
                "preferred_skills": c.get("preferred_skills", []),
                "apply_link":       _get_apply_link(c["name"]),
            })
        return result

    return {
        "mncs":              _enrich(field_companies.get("mncs", []),              30),
        "startups":          _enrich(field_companies.get("startups", []),          38),
        "product_companies": _enrich(field_companies.get("product_companies", []), 25),
    }

