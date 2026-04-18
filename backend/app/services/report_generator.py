import json, io
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.enums import TA_CENTER
    REPORTLAB = True
except ImportError:
    REPORTLAB = False

BLUE = "#2563EB"

def generate_json_report(data: dict) -> str:
    return json.dumps({"report_generated": datetime.now().isoformat(), "version": "2.0.0", **data}, indent=2, default=str)

def generate_pdf_report(data: dict) -> bytes:
    if not REPORTLAB:
        raise ImportError("pip install reportlab")
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=0.7*inch, leftMargin=0.7*inch, topMargin=0.7*inch, bottomMargin=0.7*inch)
    styles = getSampleStyleSheet()
    BL = colors.HexColor(BLUE); DK = colors.HexColor("#1E293B"); LG = colors.HexColor("#F1F5F9")
    t = lambda s, **kw: ParagraphStyle(s, parent=styles.get("Normal", styles["Normal"]), **kw)
    TS = t("TI", textColor=BL, fontSize=20, spaceAfter=4, fontName="Helvetica-Bold")
    H2 = t("H2", textColor=DK, fontSize=13, spaceBefore=12, spaceAfter=4, fontName="Helvetica-Bold")
    BD = t("BD", fontSize=10, spaceAfter=3, leading=13)
    SM = t("SM", fontSize=9, textColor=colors.grey)
    story = []
    story.append(Paragraph("AI Resume Analyzer — Full Analysis Report", TS))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y  %H:%M')}", SM))
    story.append(HRFlowable(width="100%", thickness=2, color=BL, spaceAfter=10))

    # Candidate
    story.append(Paragraph("Candidate Overview", H2))
    rows = [["Name", data.get("candidate_name","N/A")], ["Detected Field", data.get("detected_field","N/A")],
            ["Sub-Field", data.get("detected_subfield","N/A")], ["Experience Level", data.get("experience_level","N/A").title()],
            ["Years of Experience", f"{data.get('years_experience',0):.1f} years"],
            ["File Type", data.get("file_type","PDF")]]
    tbl = Table(rows, colWidths=[2*inch, 4.2*inch])
    tbl.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1),LG),("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),9),("GRID",(0,0),(-1,-1),0.4,colors.lightgrey),("PADDING",(0,0),(-1,-1),5)]))
    story.append(tbl); story.append(Spacer(1,8))

    # ATS
    ats = data.get("ats_score", {})
    story.append(Paragraph("ATS Score Breakdown", H2))
    ats_rows = [["Component","Score","Weight"],
        ["Keyword Relevance", f"{ats.get('keyword_score',0):.1f}/100","35%"],
        ["Formatting",        f"{ats.get('formatting_score',0):.1f}/100","20%"],
        ["Section Completeness",f"{ats.get('section_score',0):.1f}/100","20%"],
        ["Experience Quality", f"{ats.get('experience_score',0):.1f}/100","15%"],
        ["Skill Coverage",    f"{ats.get('skill_score',0):.1f}/100","10%"],
        ["TOTAL",             f"{ats.get('total',0):.1f}/100", f"Grade: {ats.get('grade','N/A')}"],
    ]
    at = Table(ats_rows, colWidths=[2.5*inch,1.5*inch,1.5*inch])
    at.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),BL),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("BACKGROUND",(0,-1),(-1,-1),DK),
        ("TEXTCOLOR",(0,-1),(-1,-1),colors.white),("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),
        ("GRID",(0,0),(-1,-1),0.4,colors.lightgrey),("FONTSIZE",(0,0),(-1,-1),9),("PADDING",(0,0),(-1,-1),5),
        ("ROWBACKGROUNDS",(0,1),(-1,-2),[colors.white,LG])]))
    story.append(at)
    story.append(Paragraph(ats.get("interpretation",""), SM)); story.append(Spacer(1,8))

    # Skills
    skills = data.get("skill_analysis", {})
    story.append(Paragraph("Skill Analysis", H2))
    story.append(Paragraph(f"<b>Found:</b> {', '.join(skills.get('found',[])[:15]) or 'None'}", BD))
    story.append(Paragraph(f"<b>Missing Core Skills:</b> {', '.join(skills.get('missing',[])[:10]) or 'None'}", BD))
    if skills.get("duplicates"):
        story.append(Paragraph(f"<b>Duplicates:</b> {', '.join(skills['duplicates'])}", BD))
    story.append(Spacer(1,8))

    # Jobs
    jobs = data.get("job_matches", [])
    if jobs:
        story.append(Paragraph("Top Job Role Matches", H2))
        jd = [["Role","Match %","Avg Salary"]] + [[j["role"],f"{j['match_percent']:.1f}%",j["avg_salary"]] for j in jobs[:5]]
        jt = Table(jd, colWidths=[2.8*inch,1.1*inch,2*inch])
        jt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),BL),("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("GRID",(0,0),(-1,-1),0.4,colors.lightgrey),
            ("FONTSIZE",(0,0),(-1,-1),9),("PADDING",(0,0),(-1,-1),5),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,LG])]))
        story.append(jt); story.append(Spacer(1,8))

    # SW
    sw = data.get("strengths_weaknesses", {})
    story.append(Paragraph("Strengths & Weaknesses", H2))
    for s in sw.get("strengths",[])[:5]: story.append(Paragraph(f"✓ {s}", BD))
    for w in sw.get("weaknesses",[])[:5]: story.append(Paragraph(f"⚠ {w}", BD))

    story.append(Spacer(1,14)); story.append(HRFlowable(width="100%",thickness=1,color=colors.lightgrey))
    story.append(Paragraph("Generated by AI Resume Analyzer v2.0 | Not for redistribution", SM))
    doc.build(story)
    return buf.getvalue()
