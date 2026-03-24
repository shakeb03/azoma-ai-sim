import time
from fastapi import APIRouter, HTTPException
from app.models import SimulateRequest, SimulateResponse
from app.services.scraper import scrape_product_page
from app.services.prompt_generator import extract_and_generate
from app.services.llm_runner import run_all_llms
from app.services.analyzer import analyze_responses

router = APIRouter()


@router.post("/simulate", response_model=SimulateResponse)
async def simulate(req: SimulateRequest):
    start = time.time()

    # Step 1: Scrape the product page
    try:
        listing = await scrape_product_page(req.url)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"detail": str(e), "stage": "scraping"},
        )

    # Step 2: Extract brand/category/price + generate 5 prompt variations
    try:
        brand, category, _price, generated_prompts = await extract_and_generate(listing)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"detail": str(e), "stage": "prompt_generation"},
        )

    # Step 3: Query all 4 LLMs in parallel with the generated prompts
    try:
        llm_responses = await run_all_llms(generated_prompts)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"detail": str(e), "stage": "llm_calls"},
        )

    # Step 4: Run gap analysis
    try:
        gap_report, visibility_score = await analyze_responses(listing, llm_responses)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"detail": str(e), "stage": "analysis"},
        )

    return SimulateResponse(
        brand=brand,
        product=category,
        scraped_listing=listing,
        generated_prompts=generated_prompts,
        llm_responses=llm_responses,
        gap_report=gap_report,
        visibility_score=visibility_score,
        duration_ms=int((time.time() - start) * 1000),
    )
    
