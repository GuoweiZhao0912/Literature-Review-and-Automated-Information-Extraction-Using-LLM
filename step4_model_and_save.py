# step4_model_and_save.py
import glob
import pandas as pd
from pipeline_utils import extract_pdf_raw, extract_section, call_llm_json
from step1_extract_meta import extract_meta_for_pdf
from step2_theory_model import extract_intro_model
from step3_data import extract_data_info

SYSTEM = "You are a high-precision academic paper parser. Output ONLY valid JSON, no other text."
PROMPT_MODEL = """
Task: Extract the main empirical regression equation from the academic paper excerpt below.

Content:
{content}

Output JSON:
{
  "empirical_model": ""  # Main empirical regression equation if clearly stated; otherwise empty string
}

Rules:
- Extract clear mathematical equations with variables and coefficients
- Must be empirical specifications (panel models, DiD, IV, regression equations)
- Use standard notation (Y, X, β, ε, etc.)
- Prefer the primary/main specification if multiple exist
- Do NOT extract: theoretical models, variable definitions only, results tables, unclear equations
- If introduction_has_theory_model = 0 and has_data_section = 1, MUST extract empirical model
- Return empty string if no clear equation identified

Output ONLY valid JSON.
"""

def extract_empirical_model(path: str):
    raw = extract_pdf_raw(path)
    # 优先抓 results/methods 段
    content = extract_section(raw.get("raw_text",""), "results", max_chars=5000)
    if not content:
        content = extract_section(raw.get("raw_text",""), "method", max_chars=5000)
    if not content:
        # fallback: 使用全文前几千字
        content = raw.get("raw_text","")[:8000]
    prompt = PROMPT_MODEL.format(content=content)
    res = call_llm_json(prompt, system=SYSTEM, max_tokens=300, temp=0.0)
    if not isinstance(res, dict):
        return {"path": path, "empirical_model": "", "__raw_llm__": res}
    res["path"] = path
    return res

def process_folder_and_save(pdf_folder: str, out_excel: str = "result_summary.xlsx"):
    pdfs = glob.glob(pdf_folder.rstrip("/") + "/*.pdf")
    records = []
    for p in pdfs:
        print("Processing:", p)
        meta = extract_meta_for_pdf(p)
        intro = extract_intro_model(p)
        data = extract_data_info(p)
        model = extract_empirical_model(p)

        # 合并，按你指定列名
        rec = {
            "path": p,
            "title": meta.get("title",""),
            "authors": meta.get("authors",""),
            "year": meta.get("year",""),
            "journal": meta.get("journal",""),
            "abstract": meta.get("abstract",""),
            "introduction_has_theory_model": intro.get("introduction_has_theory_model",0),
            "theory_model_description": intro.get("theory_model_description",""),
            "has_data_section": data.get("has_data_section",0),
            "data_section_text": data.get("data_section_text",""),
            "data_mentions_labor": data.get("data_mentions_labor",0),
            "labor_related_text": data.get("labor_related_text",""),
            "data_country": data.get("data_country",""),
            "if_us_data_level": data.get("if_us_data_level",""),
            "firm_sample_period": data.get("firm_sample_period",""),
            "firm_data_frequency": data.get("firm_data_frequency",""),
            "empirical_model": model.get("empirical_model","")
        }
        records.append(rec)
    df = pd.DataFrame(records)
    # 保存为 excel
    df.to_excel(out_excel, index=False)
    print("Saved to", out_excel)
    return df

# 测试（运行整个目录）
if __name__ == "__main__":
    df = process_folder_and_save("/Users/mac/Documents/RA/Huangsheng/labour_lit_review/papers/JF_test", out_excel="papers_summary.xlsx")
    print(df.head())
