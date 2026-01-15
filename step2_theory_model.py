# step2_intro_theory.py
from pipeline_utils import extract_pdf_raw, extract_section, call_llm_json

SYSTEM = "You are an academic information extractor. Output ONLY JSON."
PROMPT = """
Task: Judge if the introduction contains theoretical model construction (mathematical equations, frameworks, hypothesis derivation, optimization problems, simulation models).

Return JSON:
{{
  "introduction_has_theory_model": 0,   # 0 or 1 - must have clear evidence
  "theory_model_description": ""        # If 1, extract original model description text (max 300 words); if 0, empty string
}}

Content:
-----
{introduction}
-----

Requirements:
- Be strict: Only 1 if unambiguous theoretical model evidence exists
- Extract verbatim text for description, no paraphrasing
- Output ONLY the specified JSON, no other text
- If uncertain, choose 0
"""

import re

def extract_intro_model(path: str):
    raw = extract_pdf_raw(path)
    text = raw.get("raw_text", "")
    
    # ===  extract "Introduction" 段落 ===
    intro = extract_section(text, "introduction", max_chars=3500)

    # ===  if fail, turn to heuristics ===
    if not intro:
        # 将文本前一部分（前 20%）取出来分析
        head_text = text[:int(len(text) * 0.2)]
        
        # 切分可能的章节标题
        split_pattern = re.compile(
            r"\n\s*(?:1\.|Ⅰ\.|I\.|2\.|Ⅱ\.|II\.|Literature Review|Model|Methodology|Data|Empirical|Background)\b",
            re.IGNORECASE
        )
        parts = re.split(split_pattern, head_text)
        
        if len(parts) > 1:
            intro = parts[0].strip()
        else:
            # 如果完全没匹配上，就取前 3500 个字符
            intro = text[:3500]
    
    # === 如果还没有，就返回空结果 ===
    if not intro or len(intro) < 100:
        return {{
            "introduction_has_theory_model": 0,
            "theory_model_description": ""
        }}

    # === 构造 prompt 调用 LLM ===
    prompt = PROMPT.format(introduction=intro)
    res = call_llm_json(prompt, system=SYSTEM, max_tokens=300, temp=0.0)

    # === 后处理 ===
    if not isinstance(res, dict):
        return {
            "introduction_has_theory_model": 0,
            "theory_model_description": "",
            "__raw_llm__": res
        }

    # res["path"] = path
    # 强制类型转换
    flag = str(res.get("introduction_has_theory_model", "0")).lower()
    if flag in ("yes", "true", "1"):
        res["introduction_has_theory_model"] = 1
    else:
        res["introduction_has_theory_model"] = 0

    return res


# 测试
if __name__ == "__main__":
    sample_pdf_path = "/Users/mac/Documents/RA/Huangsheng/labour_lit_review/papers/JF/A Labor Capital Asset Pricing Model_JF_2017.pdf"  # 替换为你的测试 PDF 路径
    print(extract_intro_model(sample_pdf_path))
