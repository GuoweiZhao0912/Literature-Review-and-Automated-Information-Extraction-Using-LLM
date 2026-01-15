# step1_meta.py
from pipeline_utils import extract_pdf_raw, call_llm_json
from typing import Dict

SYSTEM = "You are a high-precision paper information extractor. You must return strictly compliant JSON without any additional content. If a field cannot be determined, use an empty string."
PROMPT_TEMPLATE = """
Please extract metadata from the following article text (extract from the original text as much as possible) and return it directly as JSON with no explanations.

Output fields:
{{
  "title": "",
  "authors": "",
  "year": "",
  "journal": "",
  "abstract": ""
}}

Article text:
----
{raw_text}
----

Requirements:
- "title": Extract the original title of the article. If unavailable, use an empty string.
- "authors": Extract the original author information (e.g., multiple authors separated by commas). If unavailable, use an empty string.
- "year": Return only a 4-digit numeric string (e.g., "2018") if a clear year is identified; otherwise, use an empty string.
- "journal": Extract the original journal or conference name. If unavailable, use an empty string.
- "abstract": Prioritize returning the original abstract from the text. If no explicit abstract exists, return the first paragraph that most resembles an abstract (keep the original text as much as possible). If completely unavailable, use an empty string.
- Output only the specified JSON fields. Do not add, modify, or omit any fields, and do not include any other content.
"""

def extract_meta_for_pdf(path: str) -> Dict:
    raw_info = extract_pdf_raw(path)
    raw_text = raw_info.get("raw_text", "")
    prompt = PROMPT_TEMPLATE.format(raw_text=raw_text[:8000])  # cut to first 8000 chars
    res = call_llm_json(prompt, system=SYSTEM, max_tokens=600)
    
    # return result
    if isinstance(res, dict):
        return res
    else:
        return {"__raw_llm__": res}

# test
if __name__ == "__main__":
    sample_pdf_path = "/Users/mac/Documents/RA/Huangsheng/labour_lit_review/papers/JFE_test/A-large-scale-approach-for-evaluating-asset-pri_2019_Journal-of-Financial-Ec.pdf"  # 替换为你的测试 PDF 路径
    r = extract_meta_for_pdf(sample_pdf_path)
    print(r)
