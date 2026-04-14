from __future__ import annotations

import os
import re
import io
import json
import time
import math
import uuid
import queue
import random
import zipfile
import textwrap
import datetime
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

# Soft imports
try:
    import yaml
except Exception:
    yaml = None

try:
    import requests
except Exception:
    requests = None

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None


# -----------------------------------------------------------------------------
# Constants & UI i18n
# -----------------------------------------------------------------------------

APP_TITLE_EN = "WOW Agentic PDF & 510(k) Review Intelligence System"
APP_TITLE_ZH = "WOW 智能 PDF 與 510(k) 審查助理系統"

UI_TEXT = {
    "en": {
        "nav_dashboard": "Home / Dashboard",
        "nav_pdf": "PDF Discovery & ToC",
        "nav_agents": "Agent Workspace",
        "nav_510k": "510(k) Review Suite",
        "nav_notes": "AI Notekeeper",
        "nav_settings": "Settings & Keys",
        "nav_history": "Run History / Exports",
        "theme": "Theme",
        "language": "UI Language",
        "output_language": "Output Language",
        "light": "Light",
        "dark": "Dark",
        "style_pack": "Painter Style Pack",
        "jackslot": "Jackslot (Random Style)",
        "lock_style": "Lock style across session",
        "status": "Status",
        "live_log": "Live Log",
        "clear_log": "Clear Log",
        "download_log": "Download Log",
        "providers": "Providers",
        "connected": "Connected",
        "missing_key": "Missing key",
        "error": "Error",
        "idle": "Idle",
        "running": "Running",
        "await_edit": "Awaiting user edit",
        "done": "Completed",
        "failed": "Failed",
        "upload_zip": "Upload a ZIP (folder of PDFs)",
        "scan": "Scan & Index PDFs",
        "found_pdfs": "PDFs Found",
        "processed": "Processed",
        "flagged": "Flagged",
        "toc": "Master ToC (editable)",
        "summarize_model": "Summarization model",
        "domain_lens": "Domain lens",
        "lens_general": "General",
        "lens_510k": "510(k) / Regulatory",
        "lens_clinical": "Clinical",
        "lens_cyber": "Cybersecurity",
        "lens_software": "Software",
        "run_agent": "Run Agent",
        "run_chain": "Run Chain",
        "add_to_chain": "Add to Chain",
        "chain_builder": "Chain Builder",
        "step": "Step",
        "prompt": "Prompt",
        "model": "Model",
        "input_source": "Input source",
        "input_toc": "Master ToC",
        "input_prev": "Previous step output",
        "input_custom": "Custom text",
        "execute_step": "Execute step",
        "edit_output": "Edit output (used as input to next step)",
        "text_view": "Text view",
        "markdown_view": "Markdown view",
        "download_md": "Download (.md)",
        "download_txt": "Download (.txt)",
        "notes_paste": "Paste note (TXT or Markdown)",
        "notes_transform": "Transform into organized Markdown",
        "keywords_coral": "Highlight keywords in coral color",
        "ai_magics": "AI Magics",
        "keep_prompting": "Keep prompting",
        "web_research": "Web research",
        "web_depth": "Research depth",
        "quick": "Quick",
        "standard": "Standard",
        "exhaustive": "Exhaustive",
        "fda_only": "Only FDA sources (fda.gov)",
        "step1": "Step 1: Paste 510(k) submission summary / review note / guidance",
        "step2": "Step 2: Paste review report template (optional) or use default",
        "use_default_template": "Use default template",
        "step4": "Step 4: Generate comprehensive guidance-linked summary (3,000–4,000 words)",
        "step5": "Step 5: Generate comprehensive 510(k) review report (3,000–4,000 words) + tables/entities/checklist",
        "step6": "Step 6: Generate skill.md for similar-device reviews (+ 3 WOW skill features)",
        "generate": "Generate",
        "edit": "Edit",
        "history": "History",
        "export": "Export",
        "api_keys": "API Keys",
        "openai_key": "OpenAI API Key",
        "gemini_key": "Gemini API Key",
        "anthropic_key": "Anthropic API Key",
        "grok_key": "Grok (xAI) API Key",
        "key_in_env": "Key is securely provided (Env/Secrets) and masked.",
        "enter_key": "Enter key (stored only in this session)",
        "clear_secrets": "Clear session secrets",
        "advanced": "Advanced",
        "temperature": "Temperature",
        "max_tokens": "Max output tokens (approx)",
        "citations_required": "Require citations (where applicable)",
        "tables_required": "Require tables (where applicable)",
        "safety_note": "Disclaimer: This tool drafts and summarizes. Final regulatory judgments require qualified reviewer oversight.",
        "bugs_panel": "LLM Health Checks",
        "run_health": "Run health checks",
        "health_ok": "Health checks passed.",
        "health_warn": "Some checks failed; see details.",
        "program_wow_features": "Program WOW AI Features",
    },
    "zh-TW": {
        "nav_dashboard": "首頁 / 儀表板",
        "nav_pdf": "PDF 探勘與目錄 ToC",
        "nav_agents": "代理工作區",
        "nav_510k": "510(k) 審查套件",
        "nav_notes": "AI 筆記管家",
        "nav_settings": "設定與金鑰",
        "nav_history": "執行歷史 / 匯出",
        "theme": "主題",
        "language": "介面語言",
        "output_language": "輸出語言",
        "light": "淺色",
        "dark": "深色",
        "style_pack": "畫家風格套件",
        "jackslot": "Jackslot（隨機風格）",
        "lock_style": "本次工作階段鎖定風格",
        "status": "狀態",
        "live_log": "即時日誌",
        "clear_log": "清除日誌",
        "download_log": "下載日誌",
        "providers": "供應商",
        "connected": "已連線",
        "missing_key": "缺少金鑰",
        "error": "錯誤",
        "idle": "閒置",
        "running": "執行中",
        "await_edit": "等待使用者編輯",
        "done": "已完成",
        "failed": "失敗",
        "upload_zip": "上傳 ZIP（包含 PDF 的資料夾）",
        "scan": "掃描並建立索引",
        "found_pdfs": "找到 PDF 數量",
        "processed": "已處理",
        "flagged": "已標記",
        "toc": "主目錄 ToC（可編輯）",
        "summarize_model": "摘要模型",
        "domain_lens": "領域視角",
        "lens_general": "一般",
        "lens_510k": "510(k) / 法規",
        "lens_clinical": "臨床",
        "lens_cyber": "資安",
        "lens_software": "軟體",
        "run_agent": "執行代理",
        "run_chain": "執行鏈",
        "add_to_chain": "加入鏈",
        "chain_builder": "鏈式建構器",
        "step": "步驟",
        "prompt": "提示詞",
        "model": "模型",
        "input_source": "輸入來源",
        "input_toc": "主目錄 ToC",
        "input_prev": "前一步輸出",
        "input_custom": "自訂文字",
        "execute_step": "執行步驟",
        "edit_output": "編輯輸出（作為下一步輸入）",
        "text_view": "文字檢視",
        "markdown_view": "Markdown 檢視",
        "download_md": "下載（.md）",
        "download_txt": "下載（.txt）",
        "notes_paste": "貼上筆記（TXT 或 Markdown）",
        "notes_transform": "轉換為結構化 Markdown",
        "keywords_coral": "以珊瑚色標示關鍵字",
        "ai_magics": "AI 魔法",
        "keep_prompting": "持續追問",
        "web_research": "網路研究",
        "web_depth": "研究深度",
        "quick": "快速",
        "standard": "標準",
        "exhaustive": "深入",
        "fda_only": "僅 FDA 來源（fda.gov）",
        "step1": "步驟 1：貼上 510(k) 總結 / 審查筆記 / 指引",
        "step2": "步驟 2：貼上審查報告模板（可選）或使用預設模板",
        "use_default_template": "使用預設模板",
        "step4": "步驟 4：產出完整指引連結摘要（3,000–4,000 字）",
        "step5": "步驟 5：產出完整 510(k) 審查報告（3,000–4,000 字）＋表格/實體/清單",
        "step6": "步驟 6：產出 skill.md 以便審查相似器材（＋3 個 WOW 技能功能）",
        "generate": "生成",
        "edit": "編輯",
        "history": "歷史",
        "export": "匯出",
        "api_keys": "API 金鑰",
        "openai_key": "OpenAI API 金鑰",
        "gemini_key": "Gemini API 金鑰",
        "anthropic_key": "Anthropic API 金鑰",
        "grok_key": "Grok（xAI）API 金鑰",
        "key_in_env": "金鑰已安全載入（環境變數/Secrets），為保護安全不予顯示。",
        "enter_key": "輸入金鑰（僅儲存在本次工作階段）",
        "clear_secrets": "清除工作階段金鑰",
        "advanced": "進階",
        "temperature": "溫度",
        "max_tokens": "最大輸出 tokens（約略）",
        "citations_required": "需要引用（適用時）",
        "tables_required": "需要表格（適用時）",
        "safety_note": "聲明：本工具用於草稿與摘要。最終法規結論須由合格審查者確認。",
        "bugs_panel": "LLM 健康檢查",
        "run_health": "執行健康檢查",
        "health_ok": "健康檢查通過。",
        "health_warn": "部分檢查未通過，請查看細節。",
        "program_wow_features": "程式 WOW AI 功能",
    },
}

SUPPORTED_UI_LANGS = ["zh-TW", "en"]

OUTPUT_LANG_CHOICES = {
    "zh-TW": "Traditional Chinese (繁體中文)",
    "en": "English",
}

RUN_STATES = ["idle", "running", "await_edit", "done", "failed"]

DEFAULT_MAX_TOKENS = 8000
DEFAULT_TEMPERATURE = 0.2


# -----------------------------------------------------------------------------
# Painter style packs (20)
# -----------------------------------------------------------------------------

PAINTER_STYLES = [
    {"id": "da-vinci", "name": "Leonardo da Vinci", "bg": "#F6F1E8", "fg": "#1E1E1E", "accent": "#7A5C3A"},
    {"id": "van-gogh", "name": "Vincent van Gogh", "bg": "#081A3A", "fg": "#F9F3C2", "accent": "#F6C445"},
    {"id": "monet", "name": "Claude Monet", "bg": "#F2F7FB", "fg": "#15202B", "accent": "#6EA8C7"},
    {"id": "picasso", "name": "Pablo Picasso", "bg": "#F9F7F2", "fg": "#111111", "accent": "#D7263D"},
    {"id": "dali", "name": "Salvador Dalí", "bg": "#0B0B0F", "fg": "#F2E9E4", "accent": "#FFB703"},
    {"id": "rembrandt", "name": "Rembrandt", "bg": "#14110F", "fg": "#F3E9DC", "accent": "#B8860B"},
    {"id": "vermeer", "name": "Johannes Vermeer", "bg": "#0E1A2B", "fg": "#E8E6DF", "accent": "#2A9D8F"},
    {"id": "klimt", "name": "Gustav Klimt", "bg": "#111111", "fg": "#F5E6B3", "accent": "#D4AF37"},
    {"id": "kahlo", "name": "Frida Kahlo", "bg": "#1B1B1B", "fg": "#F6F6F6", "accent": "#2EC4B6"},
    {"id": "okeeffe", "name": "Georgia O’Keeffe", "bg": "#FAFAF7", "fg": "#0F172A", "accent": "#7C3AED"},
    {"id": "kandinsky", "name": "Wassily Kandinsky", "bg": "#0B1320", "fg": "#F8FAFC", "accent": "#3B82F6"},
    {"id": "pollock", "name": "Jackson Pollock", "bg": "#0E0E10", "fg": "#FAFAFA", "accent": "#F97316"},
    {"id": "hopper", "name": "Edward Hopper", "bg": "#0B1F2A", "fg": "#F5F5F5", "accent": "#F59E0B"},
    {"id": "matisse", "name": "Henri Matisse", "bg": "#FFF7ED", "fg": "#111827", "accent": "#EF4444"},
    {"id": "cezanne", "name": "Paul Cézanne", "bg": "#FBF7F2", "fg": "#1F2937", "accent": "#10B981"},
    {"id": "michelangelo", "name": "Michelangelo", "bg": "#F3F4F6", "fg": "#111827", "accent": "#6B7280"},
    {"id": "warhol", "name": "Andy Warhol", "bg": "#0A0A0A", "fg": "#FDF2F8", "accent": "#EC4899"},
    {"id": "hokusai", "name": "Hokusai", "bg": "#F6FAFF", "fg": "#0F172A", "accent": "#2563EB"},
    {"id": "caravaggio", "name": "Caravaggio", "bg": "#0B0B0B", "fg": "#F3F4F6", "accent": "#DC2626"},
    {"id": "magritte", "name": "René Magritte", "bg": "#EAF2FF", "fg": "#0B1220", "accent": "#1D4ED8"},
]

DEFAULT_STYLE_ID = "monet"


# -----------------------------------------------------------------------------
# Default 510(k) template
# -----------------------------------------------------------------------------

DEFAULT_510K_TEMPLATE = """\
# 510(k) Review Report (Draft)

## 1. Executive Summary
- Device overview:
- Review scope:
- Key conclusions:
- Key gaps / additional information needed:

## 2. Device Description & Intended Use
### 2.1 Device description
### 2.2 Intended use / indications for use
### 2.3 Technological characteristics (hardware/software/connectivity)

## 3. Regulatory Context
### 3.1 Device classification (21 CFR, product code, class) (if known/inferred)
### 3.2 Predicate / reference devices and rationale

## 4. Substantial Equivalence (SE) Assessment
### 4.1 Intended use comparison
### 4.2 Technology comparison
### 4.3 Differences analysis and impact on safety/effectiveness

## 5. Standards & Guidance Mapping
- Applicable FDA guidance and recognized standards
- Evidence expected vs. provided

## 6. Performance Testing Review
### 6.1 Bench/performance testing
### 6.2 Electrical safety & EMC
### 6.3 Software validation & cybersecurity documentation
### 6.4 Biocompatibility / reprocessing / sterilization (if applicable)
### 6.5 Clinical evidence (if applicable)

## 7. Labeling / IFU / Usability
- Key labeling review points
- Human factors considerations

## 8. Risk Management Assessment (ISO 14971)
- Risk analysis summary
- Mitigations and verification evidence
- Residual risks

## 9. Reviewer Conclusions & Recommendations
- Overall assessment
- Requests for additional information
- Recommended disposition (draft)

---

# Appendices
## Appendix A: Required Tables (5)
## Appendix B: Key Entities (20)
## Appendix C: Review Checklist
## Appendix D: References & Citations
"""


# -----------------------------------------------------------------------------
# Utility: session state & WOW Effects
# -----------------------------------------------------------------------------

def ss_init():
    defaults = {
        "ui_lang": "zh-TW",
        "output_lang": "zh-TW",
        "theme": "dark",
        "style_id": DEFAULT_STYLE_ID,
        "lock_style": True,
        "run_state": "idle",
        "live_log": [],
        "history": [],  
        "session_secrets": {},  
        "agents": {},  
        "agents_load_error": None,
        "pdf_workspace_id": None,
        "pdf_files": [],
        "pdf_summaries": {},  
        "master_toc": "",
        "agent_chain": [],  
        "notes_input": "",
        "notes_output": "",
        "notes_keywords": [],
        "510k_step1": "",
        "510k_template": "",
        "510k_step4": "",
        "510k_step5": "",
        "510k_skill_md": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def trigger_wow_effect(message: str = "Task completed brilliantly!"):
    """Fires a visual reward upon AI task completion."""
    effects = [st.balloons, st.snow]
    random.choice(effects)()
    st.toast(f"🌟 WOW! {message}", icon="✨")

def t(key: str) -> str:
    lang = st.session_state.get("ui_lang", "zh-TW")
    if lang not in UI_TEXT:
        lang = "en"
    return UI_TEXT[lang].get(key, key)


def now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def log_event(message: str, level: str = "INFO", module: str = "app"):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {"ts": ts, "level": level, "module": module, "message": message}
    st.session_state.live_log.append(entry)


def format_log_text() -> str:
    lines = []
    for e in st.session_state.live_log:
        lines.append(f"[{e['ts']}] [{e['level']}] [{e['module']}] {e['message']}")
    return "\n".join(lines)


# -----------------------------------------------------------------------------
# WOW Styling (theme + painter pack)
# -----------------------------------------------------------------------------

def apply_wow_css():
    style_id = st.session_state.style_id
    style = next((s for s in PAINTER_STYLES if s["id"] == style_id), None) or PAINTER_STYLES[0]
    bg = style["bg"]
    fg = style["fg"]
    accent = style["accent"]

    theme = st.session_state.theme
    if theme == "dark":
        page_bg = "#0B0F14"
        card_bg = "rgba(255,255,255,0.04)"
        border = "rgba(255,255,255,0.10)"
        muted = "rgba(255,255,255,0.65)"
        text = "#F8FAFC"
    else:
        page_bg = bg
        card_bg = "rgba(0,0,0,0.03)"
        border = "rgba(0,0,0,0.10)"
        muted = "rgba(0,0,0,0.60)"
        text = fg

    css = f"""
    <style>
      .stApp {{
        background: {page_bg};
        color: {text};
      }}
      .wow-card {{
        background: {card_bg};
        border: 1px solid {border};
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 12px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
      }}
      .wow-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
      }}
      .wow-pill {{
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        border: 1px solid {border};
        background: {card_bg};
        margin-right: 8px;
        font-size: 12px;
        color: {muted};
      }}
      .wow-accent {{
        color: {accent};
        font-weight: 700;
      }}
      .wow-muted {{
        color: {muted};
      }}
      .wow-kpi {{
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: {text};
      }}
      .wow-sub {{
        font-size: 12px;
        color: {muted};
      }}
      a {{
        color: {accent} !important;
      }}
      code, pre {{
        border-radius: 12px;
      }}
      textarea {{
        border-radius: 12px !important;
      }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Provider keys & model registry
# -----------------------------------------------------------------------------

def env_key(name: str) -> Optional[str]:
    # Check OS env first
    v = os.environ.get(name)
    if v and v.strip():
        return v.strip()
    # Safely check st.secrets (Fixes Streamlit Cloud issues)
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return None

def get_provider_key(provider: str) -> Optional[str]:
    provider = provider.lower()
    env_map = {
        "openai": "OPENAI_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "grok": "GROK_API_KEY", 
    }
    env_name = env_map.get(provider)
    if env_name:
        ek = env_key(env_name)
        if ek:
            return ek
    if provider == "grok":
        alt = env_key("XAI_API_KEY")
        if alt:
            return alt

    return st.session_state.session_secrets.get(provider)


MODEL_REGISTRY = [
    # OpenAI
    {"provider": "openai", "id": "gpt-4o-mini", "label": "OpenAI — gpt-4o-mini"},
    {"provider": "openai", "id": "gpt-4.1-mini", "label": "OpenAI — gpt-4.1-mini"},
    # Gemini
    {"provider": "gemini", "id": "gemini-2.5-flash", "label": "Gemini — 2.5 Flash"},
    {"provider": "gemini", "id": "gemini-3-flash-preview", "label": "Gemini — 3 Flash Preview"},
    # Anthropic
    {"provider": "anthropic", "id": "claude-3-5-sonnet-latest", "label": "Anthropic — Claude Sonnet (latest)"},
    {"provider": "anthropic", "id": "claude-3-5-haiku-latest", "label": "Anthropic — Claude Haiku (latest)"},
    # Grok
    {"provider": "grok", "id": "grok-4-fast-reasoning", "label": "Grok — grok-4-fast-reasoning"},
    {"provider": "grok", "id": "grok-3-mini", "label": "Grok — grok-3-mini"},
]


def list_models() -> List[str]:
    return [m["label"] for m in MODEL_REGISTRY]

def resolve_model(label: str) -> Dict[str, str]:
    for m in MODEL_REGISTRY:
        if m["label"] == label:
            return m
    return MODEL_REGISTRY[0]


# -----------------------------------------------------------------------------
# LLM calling (defensive wrapper)
# -----------------------------------------------------------------------------

class LLMError(Exception):
    pass

def _truncate_for_context(text: str, max_chars: int = 160_000) -> str:
    if text is None:
        return ""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[...TRUNCATED FOR CONTEXT LIMIT...]\n"


def llm_call(
    *,
    model_label: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    timeout_s: int = 60,
    retries: int = 2,
) -> Tuple[str, Dict[str, Any]]:
    m = resolve_model(model_label)
    provider = m["provider"]
    model_id = m["id"]

    key = get_provider_key(provider)
    if not key:
        raise LLMError(f"{provider} key missing. Add it in Settings & Keys or via environment variables/secrets.")

    if not user_prompt.strip():
        raise LLMError("User prompt is empty.")

    system_prompt = system_prompt or ""
    user_prompt = _truncate_for_context(user_prompt)

    last_err = None
    for attempt in range(retries + 1):
        try:
            start = time.time()
            if provider == "openai":
                from openai import OpenAI
                client = OpenAI(api_key=key)
                resp = client.chat.completions.create(
                    model=model_id,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                text = resp.choices[0].message.content or ""
                meta = {
                    "provider": provider,
                    "model": model_id,
                    "duration_s": round(time.time() - start, 3),
                }
                return text, meta

            if provider == "grok":
                from openai import OpenAI
                base_url = os.environ.get("GROK_BASE_URL", "https://api.x.ai/v1")
                client = OpenAI(api_key=key, base_url=base_url)
                resp = client.chat.completions.create(
                    model=model_id,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                text = resp.choices[0].message.content or ""
                meta = {
                    "provider": provider,
                    "model": model_id,
                    "duration_s": round(time.time() - start, 3),
                }
                return text, meta

            if provider == "anthropic":
                import anthropic
                client = anthropic.Anthropic(api_key=key)
                msg = client.messages.create(
                    model=model_id,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                parts = []
                for block in getattr(msg, "content", []) or []:
                    if getattr(block, "type", "") == "text":
                        parts.append(getattr(block, "text", ""))
                text = "\n".join(parts).strip()
                meta = {
                    "provider": provider,
                    "model": model_id,
                    "duration_s": round(time.time() - start, 3),
                }
                return text, meta

            if provider == "gemini":
                start = time.time()
                try:
                    import google.generativeai as genai  # type: ignore
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel(
                        model_name=model_id,
                        system_instruction=system_prompt if system_prompt.strip() else None,
                    )
                    resp = model.generate_content(
                        user_prompt,
                        generation_config={"temperature": temperature, "max_output_tokens": max_tokens},
                    )
                    text = getattr(resp, "text", "") or ""
                    return text, {"provider": provider, "model": model_id, "duration_s": round(time.time() - start, 3)}
                except Exception as e1:
                    try:
                        from google import genai as genai2  # type: ignore
                        client = genai2.Client(api_key=key)
                        combined = (system_prompt.strip() + "\n\n" + user_prompt).strip() if system_prompt.strip() else user_prompt
                        resp = client.models.generate_content(
                            model=model_id,
                            contents=combined,
                            config={"temperature": temperature, "max_output_tokens": max_tokens},
                        )
                        text = getattr(resp, "text", None) or ""
                        if not text and hasattr(resp, "candidates"):
                            try:
                                text = resp.candidates[0].content.parts[0].text
                            except Exception:
                                text = ""
                        return text, {"provider": provider, "model": model_id, "duration_s": round(time.time() - start, 3)}
                    except Exception as e2:
                        raise LLMError("Gemini SDK not available or failed.") from (e2 or e1)

            raise LLMError(f"Unknown provider: {provider}")

        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(1.2 ** attempt)
                continue
            raise LLMError(str(e)) from e

    raise LLMError(str(last_err) if last_err else "Unknown LLM error.")


# -----------------------------------------------------------------------------
# PDF discovery & process 
# -----------------------------------------------------------------------------

def extract_zip_to_tmp(zip_bytes: bytes) -> str:
    ws_id = f"ws_{uuid.uuid4().hex[:10]}"
    base = os.path.join("/tmp", ws_id)
    os.makedirs(base, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        z.extractall(base)
    return base

def discover_pdfs(root_dir: str) -> List[str]:
    pdfs = []
    for dirpath, _, filenames in os.walk(root_dir):
        for fn in filenames:
            if fn.lower().endswith(".pdf"):
                pdfs.append(os.path.join(dirpath, fn))
    return sorted(pdfs)

def pdf_extract_text_trim_first_page(path: str) -> Tuple[str, Dict[str, Any]]:
    if not PdfReader:
        raise RuntimeError("pypdf not available. Install 'pypdf'.")
    meta = {"path": path, "single_page": False, "trimmed_first_page": False, "scanned_or_empty": False}
    reader = PdfReader(path)
    n = len(reader.pages)
    if n == 0:
        return "", {**meta, "scanned_or_empty": True}

    start_idx = 1 if n > 1 else 0
    if n > 1: meta["trimmed_first_page"] = True
    else: meta["single_page"] = True

    texts = []
    for i in range(start_idx, n):
        try:
            texts.append(reader.pages[i].extract_text() or "")
        except Exception:
            continue

    text = "\n".join(texts).strip()
    if not text:
        meta["scanned_or_empty"] = True
        text = "[Scanned content or text extraction failed]"
    return text, meta


def build_master_toc(summaries: Dict[str, str]) -> str:
    md = ["# Master Table of Contents", ""]
    i = 1
    for path, summ in summaries.items():
        fn = os.path.basename(path)
        md.append(f"## {i}. {fn}")
        md.append(summ.strip())
        md.append("")
        i += 1
    return "\n".join(md).strip() + "\n"

# -----------------------------------------------------------------------------
# WOW Magics & Prompts
# -----------------------------------------------------------------------------

AI_MAGICS = [
    {"id": "clarity_polisher", "name_en": "Clarity Polisher", "name_zh": "清晰度拋光"},
    {"id": "evidence_tagger", "name_en": "Evidence Tagger", "name_zh": "證據標記器"},
    {"id": "standards_mapper", "name_en": "Standards Mapper", "name_zh": "標準/指引映射"},
    {"id": "deficiency_builder", "name_en": "Deficiency Draft Builder", "name_zh": "補件問題產生器"},
    {"id": "exec_brief", "name_en": "Executive Brief Generator", "name_zh": "高階一頁簡報"},
    {"id": "change_log", "name_en": "Change Log Composer", "name_zh": "變更紀錄生成"},
    # Old WOW AI features
    {"id": "citation_sweeper", "name_en": "Citation Sweeper (WOW)", "name_zh": "引用整理器（WOW）"},
    {"id": "risk_heatmap", "name_en": "Risk Heatmap Builder (WOW)", "name_zh": "風險熱圖表格（WOW）"},
    {"id": "localization_transformer", "name_en": "Localization Transformer (WOW)", "name_zh": "語言在地化轉換（WOW）"},
    # 3 NEW WOW AI features
    {"id": "sentiment_analyzer", "name_en": "Regulatory Sentiment Analyzer (WOW)", "name_zh": "法規語氣分析器（WOW）"},
    {"id": "cross_ref_validator", "name_en": "Cross-Reference Validator (WOW)", "name_zh": "交互參照驗證器（WOW）"},
    {"id": "predicate_pathfinder", "name_en": "Predicate Pathfinder (WOW)", "name_zh": "類似品導航器（WOW）"},
]

def magic_prompt(magic_id: str, text_in: str, output_lang: str) -> Tuple[str, str]:
    sys = "You are a precise assistant. Output Markdown unless user requests plain text."
    lang = "請使用繁體中文輸出。" if output_lang == "zh-TW" else "Please output in English."

    if magic_id == "clarity_polisher":
        user = f"{lang}\n請在不改變事實的前提下，提升以下文本的可讀性，適合法規審查語境。輸出 Markdown。\n\n文本：\n{text_in}"
    elif magic_id == "evidence_tagger":
        user = f"{lang}\n請在文本中為每個重要主張加上證據標籤 (Provided/Inferred/Needs evidence) 並說明理由。輸出 Markdown 表格。\n\n文本：\n{text_in}"
    elif magic_id == "standards_mapper":
        user = f"{lang}\n提出可能適用的指引/標準類別，映射到文本章節（表格：類別、理由、對應章節、預期證據）。\n\n文本：\n{text_in}"
    elif magic_id == "deficiency_builder":
        user = f"{lang}\n找出缺口並撰寫補件問題草稿，依嚴重度分級（High/Medium/Low），包含「需要的證據」與「原因」。\n\n文本：\n{text_in}"
    elif magic_id == "exec_brief":
        user = f"{lang}\n濃縮成一頁高階簡報 (Markdown)：目的、發現、主要風險、建議下一步、需決策事項。\n\n文本：\n{text_in}"
    elif magic_id == "change_log":
        user = f"{lang}\n為文本產出變更紀錄摘要模板：變更區塊、類型、影響、確認事項。\n\n文本：\n{text_in}"
    elif magic_id == "citation_sweeper":
        user = f"{lang}\n整理 URL 成 References 區段，並在文中補上標記。無引用的列在 Missing Citations 區。\n\n文本：\n{text_in}"
    elif magic_id == "risk_heatmap":
        user = f"{lang}\n建立 12 個條目的風險熱圖表格 (Hazard, Severity, Probability, Risk Score, Controls, Evidence)。\n\n文本：\n{text_in}"
    elif magic_id == "localization_transformer":
        user = f"Translate the following content appropriately into {output_lang} keeping Markdown structure intact.\n\nContent:\n{text_in}"
    # New WOW AI Prompts
    elif magic_id == "sentiment_analyzer":
        user = f"{lang}\n請分析文本中是否有行銷用語或偏見。將其改寫為中立、客觀、具權威性的法規審查員語氣。\n\n文本：\n{text_in}" if output_lang == "zh-TW" else f"Analyze the text for marketing fluff or bias. Rewrite it into a neutral, objective, and authoritative regulatory reviewer tone.\n\nText:\n{text_in}"
    elif magic_id == "cross_ref_validator":
        user = f"{lang}\n請檢查文本中的表格、圖表、附錄參照是否連貫正確。列出斷鏈，並提供修正後的文本。\n\n文本：\n{text_in}" if output_lang == "zh-TW" else f"Check references to Tables, Figures, Appendices. Verify they are numbered consistently. List broken references and output corrected text.\n\nText:\n{text_in}"
    elif magic_id == "predicate_pathfinder":
        user = f"{lang}\n根據描述，建議 3 個可能適合的 FDA 產品代碼 (Procodes) 作為類似品。列出預期需要的主要性能測試（如 EMC、生物相容性）。以 Markdown 表格呈現。\n\n描述：\n{text_in}" if output_lang == "zh-TW" else f"Suggest 3 likely FDA product codes (procodes) that could serve as predicates. List typical performance testing required for each. Present as a table.\n\nDescription:\n{text_in}"
    else:
        user = f"{lang}\n請改善以下內容並輸出 Markdown：\n\n{text_in}"
    
    return sys, user


# -----------------------------------------------------------------------------
# UI components
# -----------------------------------------------------------------------------

def wow_header():
    ui_lang = st.session_state.ui_lang
    title = APP_TITLE_ZH if ui_lang == "zh-TW" else APP_TITLE_EN
    st.markdown(f"<div class='wow-card'><div class='wow-kpi'>{title}</div>"
                f"<div class='wow-sub'>{t('safety_note')}</div></div>", unsafe_allow_html=True)


def wow_status_bar():
    def provider_status(provider: str) -> Tuple[str, str]:
        if get_provider_key(provider): return t("connected"), "OK"
        return t("missing_key"), "MISSING"

    openai_s, _ = provider_status("openai")
    gemini_s, _ = provider_status("gemini")
    anthropic_s, _ = provider_status("anthropic")
    grok_s, _ = provider_status("grok")

    state_label = {
        "idle": t("idle"), "running": t("running"), "await_edit": t("await_edit"),
        "done": t("done"), "failed": t("failed")
    }.get(st.session_state.run_state, st.session_state.run_state)

    st.markdown(
        "<div class='wow-card'>"
        f"<span class='wow-pill'><span class='wow-accent'>{t('status')}:</span> {state_label}</span>"
        f"<span class='wow-pill'><span class='wow-accent'>OpenAI</span>: {openai_s}</span>"
        f"<span class='wow-pill'><span class='wow-accent'>Gemini</span>: {gemini_s}</span>"
        f"<span class='wow-pill'><span class='wow-accent'>Anthropic</span>: {anthropic_s}</span>"
        f"<span class='wow-pill'><span class='wow-accent'>Grok</span>: {grok_s}</span>"
        "</div>",
        unsafe_allow_html=True
    )


def live_log_panel(key_suffix: str):
    """Render the log panel with a dynamic key suffix to prevent Streamlit Duplicate ID errors."""
    st.markdown("### " + t("live_log"))
    text = format_log_text()
    st.text_area("", value=text, height=220, key=f"live_log_{key_suffix}")


def sidebar_controls():
    st.sidebar.markdown("## WOW Controls")
    st.sidebar.selectbox(t("language"), SUPPORTED_UI_LANGS, index=SUPPORTED_UI_LANGS.index(st.session_state.ui_lang), key="ui_lang")
    st.sidebar.selectbox(t("output_language"), list(OUTPUT_LANG_CHOICES.keys()), format_func=lambda k: OUTPUT_LANG_CHOICES[k], index=list(OUTPUT_LANG_CHOICES.keys()).index(st.session_state.output_lang), key="output_lang")
    st.sidebar.selectbox(t("theme"), ["dark", "light"], index=0 if st.session_state.theme == "dark" else 1, format_func=lambda x: t("dark") if x == "dark" else t("light"), key="theme")

    style_ids = [s["id"] for s in PAINTER_STYLES]
    cur_idx = style_ids.index(st.session_state.style_id) if st.session_state.style_id in style_ids else 0

    st.sidebar.selectbox(t("style_pack"), style_ids, index=cur_idx, format_func=lambda sid: next((s["name"] for s in PAINTER_STYLES if s["id"] == sid), sid), key="style_id", disabled=bool(st.session_state.lock_style))
    st.sidebar.checkbox(t("lock_style"), value=st.session_state.lock_style, key="lock_style")

    if st.sidebar.button(t("jackslot")):
        st.session_state.style_id = random.choice(style_ids)
        st.sidebar.info(f"Selected: {next(s['name'] for s in PAINTER_STYLES if s['id']==st.session_state.style_id)}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("## " + t("live_log"))
    if st.sidebar.button(t("clear_log")): st.session_state.live_log = []
    st.sidebar.download_button(t("download_log"), data=format_log_text().encode("utf-8"), file_name="live_log.txt", mime="text/plain", use_container_width=True)


def dashboard_panel():
    st.markdown("### " + t("nav_dashboard"))
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"<div class='wow-card'><div class='wow-kpi'>{len(st.session_state.pdf_files)}</div><div class='wow-sub'>{t('found_pdfs')}</div></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='wow-card'><div class='wow-kpi'>{len(st.session_state.pdf_summaries)}</div><div class='wow-sub'>{t('processed')}</div></div>", unsafe_allow_html=True)
    flagged = sum(1 for s in st.session_state.pdf_summaries.values() if "Scanned content" in s)
    col3.markdown(f"<div class='wow-card'><div class='wow-kpi'>{flagged}</div><div class='wow-sub'>{t('flagged')}</div></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='wow-card'><div class='wow-kpi'>{len(st.session_state.agent_chain)}</div><div class='wow-sub'>Agent chain steps</div></div>", unsafe_allow_html=True)

    st.markdown("### " + t("program_wow_features"))
    st.markdown(
        "- **Core AI Magics (6)**: Clarity, Evidence Tagging, Standards Mapping, Deficiency Drafting, Exec Brief, Change Log\n"
        "- **WOW AI Features (6)**: Citation Sweeper, Risk Heatmap Builder, Localization Transformer, Sentiment Analyzer (NEW), Cross-Ref Validator (NEW), Predicate Pathfinder (NEW)\n"
        "- **Agentic Architecture**: Chain-of-Agents with editable prompts and per-step model selection.\n"
    )

def settings_panel():
    st.markdown("### " + t("nav_settings"))
    st.markdown("<div class='wow-card'><div class='wow-sub'>"+t("api_keys")+"</div></div>", unsafe_allow_html=True)

    def key_widget(provider: str, label: str, env_var_names: List[str]):
        if any(env_key(n) for n in env_var_names):
            st.info(f"{label}: {t('key_in_env')}")
            return
        v = st.text_input(label + " — " + t("enter_key"), type="password")
        if v and v.strip():
            st.session_state.session_secrets[provider] = v.strip()

    key_widget("openai", t("openai_key"), ["OPENAI_API_KEY"])
    key_widget("gemini", t("gemini_key"), ["GEMINI_API_KEY"])
    key_widget("anthropic", t("anthropic_key"), ["ANTHROPIC_API_KEY"])
    key_widget("grok", t("grok_key"), ["GROK_API_KEY", "XAI_API_KEY"])

    if st.button(t("clear_secrets")):
        st.session_state.session_secrets = {}
        st.success("Secrets cleared.")

def pdf_panel():
    st.markdown("### " + t("nav_pdf"))
    uploaded_zip = st.file_uploader(t("upload_zip"), type=["zip"])
    colA, colB = st.columns([1, 1])
    with colA: summarization_model = st.selectbox(t("summarize_model"), list_models(), index=0, key="pdf_sum_model")
    with colB: lens = st.selectbox(t("domain_lens"), ["general", "510k", "clinical", "cyber", "software"], key="pdf_domain_lens")

    if st.button(t("scan"), disabled=uploaded_zip is None):
        st.session_state.run_state = "running"
        try:
            zip_bytes = uploaded_zip.read()
            root = extract_zip_to_tmp(zip_bytes)
            pdfs = discover_pdfs(root)
            st.session_state.pdf_files = pdfs

            summaries: Dict[str, str] = {}
            progress = st.progress(0)
            for idx, path in enumerate(pdfs):
                try:
                    text, meta = pdf_extract_text_trim_first_page(path)
                    sys_prompt = "Summarize concisely."
                    user_prompt = f"Summarize {lens} details:\n{text}"
                    summ, smeta = llm_call(model_label=summarization_model, system_prompt=sys_prompt, user_prompt=user_prompt, temperature=0.2, max_tokens=800)
                    summaries[path] = f"**Path**: `{path}`\n\n{summ.strip()}"
                except Exception as e:
                    summaries[path] = f"**Error**: {e}"
                progress.progress((idx + 1) / max(1, len(pdfs)))

            st.session_state.pdf_summaries = summaries
            st.session_state.master_toc = build_master_toc(summaries)
            st.session_state.run_state = "done"
            trigger_wow_effect("PDFs scanned and Master ToC built successfully!")
        except Exception as e:
            st.session_state.run_state = "failed"
            st.error(str(e))

    st.markdown("### " + t("toc"))
    st.session_state.master_toc = st.text_area("", value=st.session_state.master_toc, height=320, key="pdf_master_toc_area")

def agent_workspace_panel():
    st.markdown("### " + t("nav_agents"))
    agents = st.session_state.agents or {}
    agent_names = sorted(list(agents.keys()))
    selected_agent = st.selectbox("Select agent", agent_names) if agent_names else None

    model_label = st.selectbox(t("model"), list_models(), index=0, key="agent_model_single")
    prompt = st.text_area(t("prompt"), value="", height=160, key="agent_prompt_single")

    if st.button(t("run_agent"), disabled=(not selected_agent or not st.session_state.master_toc)):
        st.session_state.run_state = "running"
        try:
            user_prompt = f"CONTEXT:\n{st.session_state.master_toc}\n\nINSTRUCTIONS:\n{prompt}"
            out, meta = llm_call(model_label=model_label, system_prompt="Helpful assistant.", user_prompt=user_prompt)
            st.session_state.run_state = "await_edit"
            st.session_state.agent_temp_output = out
            trigger_wow_effect("Agent task executed perfectly!")
        except Exception as e:
            st.session_state.run_state = "failed"
            st.error(str(e))
            
    if hasattr(st.session_state, "agent_temp_output"):
        st.text_area(t("edit_output"), value=st.session_state.agent_temp_output, height=240, key="agent_output_single_edit")


def notekeeper_panel():
    st.markdown("### " + t("nav_notes"))
    model_label = st.selectbox(t("model"), list_models(), index=0, key="notes_model")
    st.session_state.notes_input = st.text_area(t("notes_paste"), value=st.session_state.notes_input, height=200, key="notes_input_area")

    if st.button(t("notes_transform")):
        st.session_state.run_state = "running"
        try:
            sys_prompt = "You are an expert note organizer. Extract key terms."
            user_prompt = f"Organize the note into structured Markdown:\n{st.session_state.notes_input}"
            out, meta = llm_call(model_label=model_label, system_prompt=sys_prompt, user_prompt=user_prompt)
            st.session_state.notes_output = out
            st.session_state.run_state = "await_edit"
            trigger_wow_effect("Notes organized effortlessly!")
        except Exception as e:
            st.session_state.run_state = "failed"
            st.error(str(e))

    if st.session_state.notes_output:
        st.session_state.notes_output = st.text_area("", value=st.session_state.notes_output, height=260, key="notes_out_md")
        
        # Magics
        magic_options = [m["id"] for m in AI_MAGICS]
        magic_labels = {m["id"]: (m["name_zh"] if st.session_state.ui_lang == "zh-TW" else m["name_en"]) for m in AI_MAGICS}
        magic_id = st.selectbox("Magic", magic_options, format_func=lambda mid: magic_labels[mid], key="notes_magic")
        
        if st.button("Run Magic", key="notes_run_magic"):
            st.session_state.run_state = "running"
            try:
                sys, user = magic_prompt(magic_id, st.session_state.notes_output, st.session_state.output_lang)
                out, meta = llm_call(model_label=model_label, system_prompt=sys, user_prompt=user, temperature=0.2)
                st.session_state.notes_output = out
                st.session_state.run_state = "await_edit"
                trigger_wow_effect(f"Magic '{magic_labels[magic_id]}' Applied!")
            except Exception as e:
                st.session_state.run_state = "failed"
                st.error(str(e))

def panel_510k():
    st.markdown("### " + t("nav_510k"))
    model_label = st.selectbox(t("model"), list_models(), index=0, key="510k_model")
    st.session_state["510k_step1"] = st.text_area("Step 1: Paste Details", value=st.session_state["510k_step1"], height=200, key="510k_step1_area")

    if st.button("Generate Step 4 (Summary)", key="510k_gen_step4"):
        st.session_state.run_state = "running"
        try:
            sys = "Regulatory writer."
            user = f"Write comprehensive review summary.\n{st.session_state['510k_step1']}"
            out, meta = llm_call(model_label=model_label, system_prompt=sys, user_prompt=user)
            st.session_state["510k_step4"] = out
            st.session_state.run_state = "await_edit"
            trigger_wow_effect("Step 4 Summary Generated!")
        except Exception as e:
            st.session_state.run_state = "failed"
            st.error(str(e))

    if st.session_state["510k_step4"].strip():
        st.session_state["510k_step4"] = st.text_area("", value=st.session_state["510k_step4"], height=260, key="510k_step4_edit")

        if st.button("Generate Step 5 (Report)", key="510k_gen_step5"):
            st.session_state.run_state = "running"
            try:
                sys = "Regulatory writer."
                user = f"Write 510k review report based on summary.\n{st.session_state['510k_step4']}"
                out, meta = llm_call(model_label=model_label, system_prompt=sys, user_prompt=user)
                st.session_state["510k_step5"] = out
                st.session_state.run_state = "await_edit"
                trigger_wow_effect("Step 5 Report Masterpiece Generated!")
            except Exception as e:
                st.session_state.run_state = "failed"
                st.error(str(e))
                
    if st.session_state["510k_step5"].strip():
        st.session_state["510k_step5"] = st.text_area("", value=st.session_state["510k_step5"], height=320, key="510k_step5_edit")

def history_panel():
    st.markdown("### " + t("nav_history"))
    st.info("Session run history enables export of your data.")

# -----------------------------------------------------------------------------
# Main Execution
# -----------------------------------------------------------------------------

def main():
    st.set_page_config(page_title="WOW Agentic Intelligence", layout="wide")
    ss_init()

    sidebar_controls()
    apply_wow_css()
    wow_header()
    wow_status_bar()

    nav = st.tabs([
        t("nav_dashboard"), t("nav_pdf"), t("nav_agents"),
        t("nav_510k"), t("nav_notes"), t("nav_settings"), t("nav_history")
    ])

    with nav[0]: 
        dashboard_panel()
        live_log_panel("dashboard")
    with nav[1]: 
        pdf_panel()
        live_log_panel("pdf")
    with nav[2]: 
        agent_workspace_panel()
        live_log_panel("agents")
    with nav[3]: 
        panel_510k()
        live_log_panel("510k")
    with nav[4]: 
        notekeeper_panel()
        live_log_panel("notes")
    with nav[5]: 
        settings_panel()
        live_log_panel("settings")
    with nav[6]: 
        history_panel()
        live_log_panel("history")

if __name__ == "__main__":
    main()
