from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from app.services.report_generator import generate_json_report, generate_pdf_report

router = APIRouter()

@router.post("/json")
async def json_report(request: Request):
    try:
        body = await request.json()
        return Response(generate_json_report(body), media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=resume_analysis.json"})
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/pdf")
async def pdf_report(request: Request):
    try:
        body = await request.json()
        pdf = generate_pdf_report(body)
        return Response(pdf, media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=resume_analysis.pdf"})
    except ImportError:
        raise HTTPException(501, "Install reportlab: pip install reportlab")
    except Exception as e:
        raise HTTPException(500, str(e))
