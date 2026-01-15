# pipeline_utils.py
import os
import re
import json
import time
from typing import List, Dict, Any, Optional
import pdfplumber
from openai import OpenAI    
from tqdm import tqdm

# --------- 配置 -------------
MODEL = os.getenv("LLM_MODEL", "deepseek")   #  deepseek 模型名
BASE_URL = os.getenv("LLM_BASE_URL", None)       # 如果你使用自定义 base_url（比如 deepseek），用环境变量设置
# --------------------------------------------------------------------

def make_client():
    # 传入给 OpenAI
    api_key = os.environ.get("DEEPSEEK_API_KEY")  # 推荐用 DEEPSEEK_API_KEY 环境变量
    if not api_key:
        raise RuntimeError("请先设置环境变量 DEEPSEEK_API_KEY")
    if BASE_URL:
        return OpenAI(api_key=api_key, base_url=BASE_URL)
    else:
        return OpenAI(api_key=api_key)

client = make_client()

def safe_json_loads(s: str) -> Any:
    """从字符串中提取最靠近的 JSON 对象并解析，容错处理。"""
    s = s.strip()
    start = s.find('{')
    end = s.rfind('}')
    if start == -1 or end == -1 or end < start:
        # 不是纯 json，尝试直接 json.loads（可能报）
        try:
            return json.loads(s)
        except:
            # 返回原始字符串以便调试
            return {"__raw_text__": s}
    candidate = s[start:end+1]
    # 替换常见的单引号和多余换行造成的问题（谨慎）
    try:
        return json.loads(candidate)
    except Exception:
        # 把单引号换成双引号（可能破坏复杂文本），最后 fallback
        try:
            cand2 = candidate.replace("'", '"')
            return json.loads(cand2)
        except Exception:
            return {"__raw_text__": s}

def call_llm_json(prompt: str, system: Optional[str]=None, model: Optional[str]=None,
                  max_tokens: int=800, temp: float=0.0, retries: int=3) -> Dict:
    """
    统一调用 LLM 的方法：发送系统 + 用户 prompt，期望 LLM 只返回 JSON。
    返回：解析好的 dict（或包含 "__raw_text__" 的 dict）
    """
    model = model or MODEL
    for attempt in range(retries):
        try:
            messages = []
            if system:
                messages.append({"role":"system","content":system})
            messages.append({"role":"user","content":prompt})
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temp,
                max_tokens=max_tokens,
            )
            text = resp.choices[0].message.content
            parsed = safe_json_loads(text)
            return parsed
        except Exception as e:
            last_err = e
            time.sleep(1 + attempt*2)
    # 最后返回错误信息
    return {"__error__": str(last_err)}

# PDF 提取（尽量在本地先做 heuristics）
def extract_pdf_raw(path: str) -> Dict[str, Any]:
    """用 pdfplumber 提取每页文本和整体 raw_text。"""
    out = {"raw_text": ""}
    try:
        with pdfplumber.open(path) as pdf:
            pages = []
            for p in pdf.pages:
                txt = p.extract_text() or ""
                pages.append(txt)
            raw = "\n\n".join(pages)
            out["raw_text"] = raw
    except Exception as e:
        out["__error__"] = str(e)
    return out

# 简单的节定位器（找 header 行并截到下一个 header 或 references）
SECTION_HEADERS = [
    r'\babstract\b', r'\bintroduction\b', r'\bbackground\b', r'\bdata\b', r'\bdata and sample\b',
    r'\bmaterials and methods\b', r'\bmethodology\b', r'\bmethods\b', r'\bresults\b',
    r'\bconclusion\b', r'\breferences\b'
]

def extract_section(raw: str, header_keyword: str, max_chars: int = 4000) -> str:
    """在 raw 中找到 header_keyword（如 'introduction'）并截取该节到下个 header 或 references。"""
    raw_lower = raw.lower()
    idx = raw_lower.find(header_keyword.lower())
    if idx == -1:
        return ""
    # 寻找下一个 header after idx
    next_idx = None
    for h in SECTION_HEADERS:
        if h.lower().strip() == header_keyword.lower().strip():
            continue
        m = re.search(r'\n\s*[\d]*\s*' + re.escape(h), raw_lower[idx+10:])
        if m:
            cand = idx + 10 + m.start()
            if next_idx is None or cand < next_idx:
                next_idx = cand
    section = raw[idx: next_idx] if next_idx else raw[idx:]
    return section[:max_chars]
