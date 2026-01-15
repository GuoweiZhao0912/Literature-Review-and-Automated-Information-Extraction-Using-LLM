# step3_data.py
from pipeline_utils import extract_pdf_raw, extract_section, call_llm_json

SYSTEM = "You are a meticulous academic information extractor. Output ONLY valid JSON, no other text."
PROMPT = """
Task: Extract fields from the Data section below and return as JSON.

Data:
{data_section}

Output JSON with these fields:
{
  "has_data_section": 0,                # 1 if data sources/variables/collection mentioned or empirical paper; 0 otherwise
  "data_section_text": "",              # If has_data_section=1, original text describing data (max 300 words); else 0
  "data_mentions_labor": 0,             # 1 only if labor/workforce/employment variables explicitly mentioned
  "labor_related_text": "",             # If data_mentions_labor=1, specific labor data sentences (max 200 words); else 0
  "data_country": "",                   # All countries mentioned in data, comma-separated; empty if unclear
  "if_us_data_level": "",               # Only if US in data_country: "firm", "labor_market", "both", or empty
  "if_firm_level": "",                  # Only if if_us_data_level is "firm" or "both": 0 or 1 for firm-level data
  "firm_sample_period": "",             # Only if if_firm_level=1: sample period like "1990-2017"
  "firm_data_frequency": ""             # Only if if_firm_level=1: "annual", "quarterly", "monthly", "daily", "other"
}

Rules:
- has_data_section: 1 if data sources/variables/collection mentioned or empirical paper
- Extract original text verbatim; no paraphrasing
- Be conservative: only mark 1 when evidence is clear
- All fields empty string when unclear/unspecified
- Output must be valid JSON only
"""

def extract_data_info(path: str):
    raw = extract_pdf_raw(path)
    data_section = extract_section(raw.get("raw_text",""), "data", max_chars=6000)
    if not data_section:
        # LLM 也来确认一下（防止 header 命名不是 data）
        # 直接询问模型文章是否包含 data 部分：但先返回 0，随后可选择对全文调用
        return {"path": path, "has_data_section": 0, "data_section_text": "", "data_mentions_labor": 0, "labor_related_text": "", 
                "data_country": "", "if_us_data_level": "", "firm_sample_period": "", "firm_data_frequency": ""}
    prompt = PROMPT.format(data_section=data_section)
    res = call_llm_json(prompt, system=SYSTEM, max_tokens=800, temp=0.0)
    if not isinstance(res, dict):
        return {"path": path, "has_data_section": 0, "__raw_llm__": res}
    # 强制类型转换
    # res["path"] = path
    try:
        res["has_data_section"] = int(res.get("has_data_section",0))
    except:
        res["has_data_section"] = 1 if str(res.get("has_data_section","")).lower() in ("1","true","yes") else 0
    try:
        res["data_mentions_labor"] = int(res.get("data_mentions_labor",0))
    except:
        res["data_mentions_labor"] = 1 if str(res.get("data_mentions_labor","")).lower() in ("1","true","yes") else 0
    return res

# 测试
if __name__ == "__main__":
    sample_pdf_path = "/Users/mac/Documents/RA/Huangsheng/labour_lit_review/papers/JF/A Labor Capital Asset Pricing Model_JF_2017.pdf"  # 替换为你的测试 PDF 路径
    print(extract_data_info(sample_pdf_path))
