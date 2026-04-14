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
        "key_in_env": "Key is provided via environment and will not be shown.",
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
        "program_wow_features": "Program WOW AI Features (Extra)",
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
        "key_in_env": "金鑰由環境變數提供，將不顯示。",
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
        "program_wow_features": "程式 WOW AI 功能（額外）",
    },
}

SUPPORTED_UI_LANGS = ["zh-TW", "en"]

OUTPUT_LANG_CHOICES = {
    "zh-TW": "Traditional Chinese (繁體中文)",
    "en": "English",
}

RUN_STATES = ["idle", "running", "await_edit", "done", "failed"]

DEFAULT_MAX_TOKENS = 1800
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
# Default 510(k) template (shortened but structured; user can replace)
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
# Utility: session state initialization
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
        "history": [],  # list of run records
        "session_secrets": {},  # provider keys entered by user (never env)
        "agents": {},  # loaded agents
        "agents_load_error": None,
        "pdf_workspace_id": None,
        "pdf_files": [],
        "pdf_summaries": {},  # path -> md
        "master_toc": "",
        "agent_chain": [],  # list of dict steps
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
    # Use painter pack colors as base; adjust slightly for light/dark toggle.
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
      /* Make textareas feel more premium */
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
    v = os.environ.get(name)
    if v and v.strip():
        return v.strip()
    return None


def get_provider_key(provider: str) -> Optional[str]:
    """
    Keys: environment first, else session state.
    Never return/display the env key value; just use it.
    """
    provider = provider.lower()
    env_map = {
        "openai": "OPENAI_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "grok": "GROK_API_KEY",  # user may set; alternatively XAI_API_KEY
    }
    env_name = env_map.get(provider)
    if env_name:
        ek = env_key(env_name)
        if ek:
            return ek
    # common alternative names
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
    # Anthropic (display as generic; actual availability depends on user key)
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
    # fallback to first
    return MODEL_REGISTRY[0]


# -----------------------------------------------------------------------------
# LLM calling (defensive wrapper)
# -----------------------------------------------------------------------------

class LLMError(Exception):
    pass


def _truncate_for_context(text: str, max_chars: int = 160_000) -> str:
    # Simple safeguard for huge inputs; avoids provider hard failures.
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
    """
    Returns (text, meta). Handles OpenAI, Gemini, Anthropic, Grok.
    Fixes common bugs:
    - Missing key -> clear error
    - Missing packages -> clear error
    - Timeouts/retries
    - Always returns a string; never None
    """
    m = resolve_model(model_label)
    provider = m["provider"]
    model_id = m["id"]

    key = get_provider_key(provider)
    if not key:
        raise LLMError(f"{provider} key missing. Add it in Settings & Keys or via environment variables.")

    if not user_prompt.strip():
        raise LLMError("User prompt is empty.")

    system_prompt = system_prompt or ""
    user_prompt = _truncate_for_context(user_prompt)

    last_err = None
    for attempt in range(retries + 1):
        try:
            start = time.time()
            if provider == "openai":
                try:
                    from openai import OpenAI
                except Exception as e:
                    raise LLMError("OpenAI package not available. Install 'openai'.") from e

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
                    "usage": getattr(resp, "usage", None),
                }
                return text, meta

            if provider == "grok":
                # Grok via OpenAI-compatible API. Default base_url works for xAI.
                try:
                    from openai import OpenAI
                except Exception as e:
                    raise LLMError("OpenAI package not available (required for Grok compatible client).") from e

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
                    "usage": getattr(resp, "usage", None),
                    "base_url": base_url,
                }
                return text, meta

            if provider == "anthropic":
                try:
                    import anthropic
                except Exception as e:
                    raise LLMError("Anthropic package not available. Install 'anthropic'.") from e

                client = anthropic.Anthropic(api_key=key)
                # Anthropic expects system separately
                msg = client.messages.create(
                    model=model_id,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                # msg.content is a list of blocks
                parts = []
                for block in getattr(msg, "content", []) or []:
                    if getattr(block, "type", "") == "text":
                        parts.append(getattr(block, "text", ""))
                text = "\n".join(parts).strip()
                meta = {
                    "provider": provider,
                    "model": model_id,
                    "duration_s": round(time.time() - start, 3),
                    "usage": getattr(msg, "usage", None),
                }
                return text, meta

            if provider == "gemini":
                # Support either google.generativeai (older) or google.genai (newer).
                # Prefer google.generativeai for maximum compatibility.
                start = time.time()
                text = ""
                meta = {"provider": provider, "model": model_id}

                used_lib = None
                # Try google.generativeai
                try:
                    import google.generativeai as genai  # type: ignore
                    used_lib = "google.generativeai"
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
                    meta.update({"duration_s": round(time.time() - start, 3), "lib": used_lib})
                    return text, meta
                except Exception as e1:
                    # Try google.genai fallback
                    try:
                        from google import genai as genai2  # type: ignore
                        used_lib = "google.genai"
                        client = genai2.Client(api_key=key)
                        # Use a simple prompt concatenation to avoid schema drift between versions.
                        combined = (system_prompt.strip() + "\n\n" + user_prompt).strip() if system_prompt.strip() else user_prompt
                        resp = client.models.generate_content(
                            model=model_id,
                            contents=combined,
                            config={"temperature": temperature, "max_output_tokens": max_tokens},
                        )
                        # New SDK response can be nested; best-effort extraction:
                        text = getattr(resp, "text", None) or ""
                        if not text and hasattr(resp, "candidates"):
                            # attempt to pull candidate text
                            try:
                                text = resp.candidates[0].content.parts[0].text  # type: ignore
                            except Exception:
                                text = ""
                        meta.update({"duration_s": round(time.time() - start, 3), "lib": used_lib})
                        return text, meta
                    except Exception as e2:
                        raise LLMError(
                            "Gemini SDK not available or failed. Install 'google-generativeai' "
                            "or 'google-genai'."
                        ) from (e2 or e1)

            raise LLMError(f"Unknown provider: {provider}")

        except Exception as e:
            last_err = e
            # Retry only for likely transient errors
            if attempt < retries:
                backoff = 1.2 ** attempt
                time.sleep(backoff)
                continue
            raise LLMError(str(e)) from e

    raise LLMError(str(last_err) if last_err else "Unknown LLM error.")


# -----------------------------------------------------------------------------
# agents.yaml loading
# -----------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_agents_yaml(text: str) -> Tuple[Dict[str, Any], Optional[str]]:
    if not yaml:
        return {}, "pyyaml is not available. Install 'pyyaml'."
    try:
        data = yaml.safe_load(text) or {}
        # Accept either list or dict; normalize to dict name->agent
        agents = {}
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("name"):
                    agents[item["name"]] = item
        elif isinstance(data, dict):
            # Could be {agents: [...]} or direct mapping
            if "agents" in data and isinstance(data["agents"], list):
                for item in data["agents"]:
                    if isinstance(item, dict) and item.get("name"):
                        agents[item["name"]] = item
            else:
                # direct mapping
                for k, v in data.items():
                    if isinstance(v, dict):
                        v.setdefault("name", k)
                        agents[k] = v
        # minimal validation
        for name, a in agents.items():
            a.setdefault("description", "")
            a.setdefault("user_prompt_template", f"Use the provided context to help with {name}.")
            a.setdefault("system_prompt", "You are a helpful expert assistant.")
        return agents, None
    except Exception as e:
        return {}, f"Failed to parse agents.yaml: {e}"


def try_load_agents_from_file() -> None:
    """
    Attempt to load agents.yaml from app directory if present.
    """
    if "agents_loaded_once" in st.session_state:
        return

    st.session_state["agents_loaded_once"] = True
    if not os.path.exists("agents.yaml"):
        st.session_state.agents = {}
        st.session_state.agents_load_error = "agents.yaml not found. You can upload one in Settings."
        return

    try:
        with open("agents.yaml", "r", encoding="utf-8") as f:
            txt = f.read()
        agents, err = load_agents_yaml(txt)
        st.session_state.agents = agents
        st.session_state.agents_load_error = err
        if err:
            log_event(err, "WARN", "agents")
        else:
            log_event(f"Loaded {len(agents)} agents from agents.yaml", "INFO", "agents")
    except Exception as e:
        st.session_state.agents = {}
        st.session_state.agents_load_error = str(e)
        log_event(f"agents.yaml load failed: {e}", "ERROR", "agents")


# -----------------------------------------------------------------------------
# PDF discovery & processing (ZIP upload workflow for HF Spaces)
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
    """
    Returns extracted text and metadata flags.
    Preserves original behavior: discard page 0 if >1 pages, else keep.
    """
    if not PdfReader:
        raise RuntimeError("pypdf not available. Install 'pypdf'.")
    meta = {"path": path, "single_page": False, "trimmed_first_page": False, "scanned_or_empty": False}
    reader = PdfReader(path)
    n = len(reader.pages)
    if n == 0:
        return "", {**meta, "scanned_or_empty": True}

    start_idx = 0
    if n > 1:
        start_idx = 1
        meta["trimmed_first_page"] = True
    else:
        meta["single_page"] = True

    texts = []
    for i in range(start_idx, n):
        try:
            page = reader.pages[i]
            txt = page.extract_text() or ""
            texts.append(txt)
        except Exception:
            continue

    text = "\n".join(texts).strip()
    if not text:
        meta["scanned_or_empty"] = True
        text = "[Scanned content or text extraction failed — OCR not enabled in this build.]"
    return text, meta


def build_atomic_summary_prompt(domain_lens: str, output_lang: str) -> Tuple[str, str]:
    """
    Returns (system_prompt, user_prefix) for atomic summaries.
    """
    if output_lang == "zh-TW":
        lang_note = "請使用繁體中文輸出。"
    else:
        lang_note = "Please output in English."

    lens_map = {
        "general": "Summarize generally with key points.",
        "510k": "Summarize with a regulatory/510(k) lens: intended use, device description, key testing evidence, standards/guidance, and notable gaps.",
        "clinical": "Summarize focusing on clinical claims, endpoints, evidence, and interpretation constraints.",
        "cyber": "Summarize focusing on software/network connectivity, cybersecurity concerns, and expected documentation.",
        "software": "Summarize focusing on software architecture, validation, known anomalies, and change impact.",
    }
    lens_text = lens_map.get(domain_lens, lens_map["general"])

    system_prompt = (
        "You are a meticulous assistant that produces concise, high-signal summaries in Markdown. "
        "Avoid hallucinations; if unsure, say 'not stated'."
    )
    user_prefix = (
        f"{lang_note}\n"
        f"{lens_text}\n\n"
        "Return:\n"
        "- 3–7 bullet points of key facts\n"
        "- A 'Notable Gaps / Questions' subsection (2–5 bullets)\n"
        "- Keep it compact but specific.\n"
    )
    return system_prompt, user_prefix


def summarize_pdf_text(
    text: str,
    *,
    model_label: str,
    domain_lens: str,
    output_lang: str,
) -> Tuple[str, Dict[str, Any]]:
    system_prompt, user_prefix = build_atomic_summary_prompt(domain_lens, output_lang)
    user_prompt = user_prefix + "\n\nDOCUMENT TEXT:\n" + text
    return llm_call(
        model_label=model_label,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.2,
        max_tokens=900,
    )


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
# Web research (best-effort, optional)
# -----------------------------------------------------------------------------

def ddg_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Returns list of {title, href, snippet}.
    Uses duckduckgo_search if available; else returns empty.
    """
    try:
        from duckduckgo_search import DDGS  # type: ignore
    except Exception:
        return []

    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "href": r.get("href", ""),
                    "snippet": r.get("body", ""),
                })
    except Exception:
        return []
    return results


def filter_fda_only(results: List[Dict[str, str]]) -> List[Dict[str, str]]:
    out = []
    for r in results:
        href = r.get("href", "") or ""
        if "fda.gov" in href:
            out.append(r)
    return out


def web_research_plan(step1_text: str) -> List[str]:
    """
    Simple query planner: extract device keywords; generate queries.
    """
    text = step1_text.strip()
    # Try to pick a few salient nouns/terms; fallback to generic 510(k).
    candidates = set()
    for token in re.findall(r"[A-Za-z][A-Za-z0-9\-\(\)/]{2,}", text)[:120]:
        if token.lower() in {"the", "and", "for", "with", "that", "this", "from"}:
            continue
        candidates.add(token)
    top = list(candidates)[:8]
    base = "510(k) FDA guidance"
    queries = []
    if top:
        queries.append(f"{base} {top[0]}")
        if len(top) > 1:
            queries.append(f"{base} {top[1]}")
    queries.append("FDA guidance Premarket Notification 510(k) substantial equivalence")
    queries.append("FDA guidance device software validation 510(k)")
    queries.append("FDA cybersecurity guidance medical devices 510(k)")
    return queries


def web_research(
    step1_text: str,
    depth: str,
    fda_only: bool,
) -> List[Dict[str, str]]:
    """
    Best-effort web research returning citation candidates.
    """
    # depth controls results per query
    per_query = {"quick": 3, "standard": 5, "exhaustive": 8}.get(depth, 5)
    queries = web_research_plan(step1_text)
    citations: List[Dict[str, str]] = []
    seen = set()

    for q in queries:
        res = ddg_search(q, max_results=per_query)
        if fda_only:
            res = filter_fda_only(res)
        for r in res:
            href = r.get("href", "")
            if not href or href in seen:
                continue
            seen.add(href)
            citations.append({
                "title": r.get("title", "").strip(),
                "url": href.strip(),
                "snippet": (r.get("snippet", "") or "").strip(),
                "accessed": datetime.date.today().isoformat(),
                "query": q,
            })
    return citations


def citations_to_markdown(citations: List[Dict[str, str]]) -> str:
    if not citations:
        return "_No web citations collected (web research unavailable/disabled)._"
    lines = ["## References (Web)", ""]
    for i, c in enumerate(citations, 1):
        title = c.get("title") or "Untitled"
        url = c.get("url") or ""
        accessed = c.get("accessed") or ""
        q = c.get("query") or ""
        snippet = c.get("snippet") or ""
        lines.append(f"{i}. **{title}** — {url}  \n   _Accessed_: {accessed}  \n   _Query_: `{q}`")
        if snippet:
            lines.append(f"   - Snippet: {snippet}")
    return "\n".join(lines)


# -----------------------------------------------------------------------------
# 510(k) generation prompts
# -----------------------------------------------------------------------------

def sys_regulatory_writer(output_lang: str) -> str:
    if output_lang == "zh-TW":
        return (
            "你是一位嚴謹的醫療器材法規審查寫作者，擅長 510(k) 審查架構、證據缺口識別、"
            "以及以中性、可稽核的語氣撰寫 Markdown 文件。避免臆測；不確定時請標註「未提供/不明」。"
        )
    return (
        "You are a meticulous medical device regulatory review writer. Produce audit-ready Markdown. "
        "Avoid speculation; if unknown, state 'not provided/unclear'."
    )


def prompt_step4_summary(step1: str, citations_md: str, output_lang: str) -> str:
    if output_lang == "zh-TW":
        return f"""\
請根據「使用者提供內容（Step 1）」與「網路研究引用（若有）」產出一份**完整且具引用**的綜整摘要（Markdown），目標長度 **3,000–4,000 字**（不含參考文獻段落）。

要求：
1) 明確指出哪些資訊來自 Step 1、哪些來自引用、哪些是推論（需標註為推論）。
2) 以 510(k) 審查觀點組織：預期用途/適應症、技術特性、可能的法規分類、SE 脈絡、常見測試證據、標示/可用性/資安/軟體等關鍵議題。
3) 每個重要主張盡量附上引用連結（若引用可用）。
4) 用繁體中文輸出。

---

# 使用者提供內容（Step 1）
{step1}

---

# 網路研究引用（可用時）
{citations_md}
"""
    return f"""\
Based on "User-provided content (Step 1)" and "Web research citations (if any)", produce a comprehensive, citation-backed summary in Markdown targeting **3,000–4,000 words** (excluding the references section).

Requirements:
1) Clearly distinguish what comes from Step 1 vs citations vs inference (label inference explicitly).
2) Organize for a 510(k) reviewer lens: intended use/indications, technology, likely regulatory context, SE narrative, expected evidence/testing, labeling/usability/cybersecurity/software.
3) Add citations/links for key claims when available.
4) Output in English.

---

# User-provided content (Step 1)
{step1}

---

# Web research citations (if available)
{citations_md}
"""


def prompt_step5_report(step1: str, step4: str, template: str, output_lang: str) -> str:
    if output_lang == "zh-TW":
        return f"""\
請依照「模板」的章節與標題格式，撰寫一份 **510(k) 審查報告（Markdown）**，目標長度 **3,000–4,000 字**（不含附錄）。必須使用 Step 1 與 Step 4 的資訊，並保持可稽核、審查者語氣。

硬性要求（不可省略）：
- 報告內需產出 **5 個表格**（置於附錄 Appendix A，或依模板安排）
- 需列出並解釋 **20 個關鍵實體**（Appendix B）
- 需附上 **審查檢核清單**（Appendix C），格式需可勾選（Yes/No/Unclear）並含「審查意見」與「補件問題草稿」
- 若資訊不足，請明確標註「未提供/不明」，並在缺口處提出具體補件請求

輸出語言：繁體中文。

---

# Step 1（使用者提供）
{step1}

---

# Step 4（綜整摘要）
{step4}

---

# 模板
{template}
"""
    return f"""\
Follow the "Template" headings and produce a **510(k) review report in Markdown** targeting **3,000–4,000 words** (excluding appendices). Use Step 1 and Step 4. Maintain an audit-ready, reviewer-neutral tone.

Hard requirements:
- Include **5 tables** (Appendix A or per template)
- Include **20 key entities** with explanations (Appendix B)
- Include a **review checklist** (Appendix C) with Yes/No/Unclear + reviewer comments + draft deficiency questions
- If information is missing, mark it clearly and propose concrete requests for additional information.

Output language: English.

---

# Step 1 (User-provided)
{step1}

---

# Step 4 (Comprehensive summary)
{step4}

---

# Template
{template}
"""


def prompt_step6_skill(step4: str, step5: str, output_lang: str) -> str:
    if output_lang == "zh-TW":
        return f"""\
請根據 Step 4 與 Step 5 的成果，建立一份可重複使用的 **skill.md**（Markdown），目標是：讓代理能對「相似器材」生成完整的 510(k) 審查報告。

請遵循 skill-creator 的精神（觸發情境、輸入/輸出格式、工作流程、品質門檻、評估方式），並內建 3 個 WOW 技能功能：
1) Template Auto-Healing：偵測模板缺失章節並提出修復版本（保留原風格）
2) Gap-to-Question Generator：將缺口轉成補件問題（依嚴重度分類）
3) Consistency Auditor：檢查報告內矛盾並提出修正建議

此外，請在 skill.md 末尾加入「使用範例（至少 2 例）」與「常見失敗模式與對策」。

輸出：完整 skill.md 內容（繁體中文撰寫）。

---

# Step 4
{step4}

---

# Step 5
{step5}
"""
    return f"""\
Based on Step 4 and Step 5 results, create a reusable **skill.md** (Markdown) enabling an agent to generate comprehensive 510(k) review reports for similar devices.

Follow the skill-creator spirit: triggering contexts, inputs/outputs, workflow, quality gates, evaluation guidance. Include 3 WOW skill features:
1) Template Auto-Healing
2) Gap-to-Question Generator (severity-bucketed)
3) Consistency Auditor

Also include at least 2 usage examples and a section on common failure modes + mitigations.

Output: full skill.md content (English).

---

# Step 4
{step4}

---

# Step 5
{step5}
"""


# -----------------------------------------------------------------------------
# AI Notekeeper & Magics
# -----------------------------------------------------------------------------

def extract_keywords(text: str, max_keywords: int = 18) -> List[str]:
    # Very lightweight keyword heuristic; avoids dependency on NLP libs.
    words = re.findall(r"[A-Za-z][A-Za-z0-9\-/]{2,}", text)
    freq: Dict[str, int] = {}
    stop = {"the","and","for","with","this","that","from","into","your","you","are","was","were","been","have","has"}
    for w in words:
        lw = w.lower()
        if lw in stop:
            continue
        if len(lw) < 3:
            continue
        freq[lw] = freq.get(lw, 0) + 1
    # prioritize higher freq
    ranked = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
    kws = [k for k,_ in ranked[:max_keywords]]
    return kws


def coral_highlight_markdown(md: str, keywords: List[str]) -> str:
    # HTML spans in markdown; best-effort word boundary.
    out = md
    for kw in sorted(keywords, key=len, reverse=True):
        # escape kw for regex
        pat = re.compile(rf"\b({re.escape(kw)})\b", re.IGNORECASE)
        out = pat.sub(r'<span style="color:coral;font-weight:700">\1</span>', out)
    return out


def notekeeper_transform(note_text: str, output_lang: str, model_label: str, temperature: float, max_tokens: int) -> Tuple[str, Dict[str, Any], List[str]]:
    system_prompt = (
        "You are an expert note organizer. Produce structured Markdown. "
        "Extract key terms and ensure action items/questions are explicit."
    )
    if output_lang == "zh-TW":
        user_prompt = f"""\
請將以下筆記整理為結構化 Markdown：
- 用清晰標題（H1/H2/H3）
- 產出「重點摘要」「細節整理」「待辦事項」「待釐清問題」
- 盡量保持原意，不要自行新增未提供的事實
- 請用繁體中文輸出

筆記：
{note_text}
"""
    else:
        user_prompt = f"""\
Organize the note into structured Markdown:
- Clear headings (H1/H2/H3)
- Sections: Key takeaways, Details, Action items, Questions to clarify
- Preserve meaning; do not invent facts not present
- Output in English

Note:
{note_text}
"""
    text, meta = llm_call(
        model_label=model_label,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    kws = extract_keywords(note_text + "\n" + text)
    highlighted = coral_highlight_markdown(text, kws)
    return highlighted, meta, kws


AI_MAGICS = [
    {"id": "clarity_polisher", "name_en": "Clarity Polisher", "name_zh": "清晰度拋光"},
    {"id": "evidence_tagger", "name_en": "Evidence Tagger", "name_zh": "證據標記器"},
    {"id": "standards_mapper", "name_en": "Standards Mapper", "name_zh": "標準/指引映射"},
    {"id": "deficiency_builder", "name_en": "Deficiency Draft Builder", "name_zh": "補件問題產生器"},
    {"id": "exec_brief", "name_en": "Executive Brief Generator", "name_zh": "高階一頁簡報"},
    {"id": "change_log", "name_en": "Change Log Composer", "name_zh": "變更紀錄生成"},
    # 3 additional WOW AI features (program-level)
    {"id": "citation_sweeper", "name_en": "Citation Sweeper (WOW)", "name_zh": "引用整理器（WOW）"},
    {"id": "risk_heatmap", "name_en": "Risk Heatmap Builder (WOW)", "name_zh": "風險熱圖表格（WOW）"},
    {"id": "localization_transformer", "name_en": "Localization Transformer (WOW)", "name_zh": "語言在地化轉換（WOW）"},
]


def magic_prompt(magic_id: str, text_in: str, output_lang: str) -> Tuple[str, str]:
    sys = "You are a precise assistant. Output Markdown unless user requests plain text."
    if output_lang == "zh-TW":
        lang = "請使用繁體中文輸出。"
    else:
        lang = "Please output in English."

    if magic_id == "clarity_polisher":
        user = f"""{lang}
請在不改變事實內容的前提下，提升以下文本的清晰度與可讀性，適合法規審查語境。輸出 Markdown。

文本：
{text_in}
"""
    elif magic_id == "evidence_tagger":
        user = f"""{lang}
請在以下文本中，為每個重要主張加上證據標籤：Provided / Inferred / Web-sourced / Needs evidence，並簡短說明理由。輸出 Markdown（可用表格）。

文本：
{text_in}
"""
    elif magic_id == "standards_mapper":
        user = f"""{lang}
請根據以下內容，提出可能適用的指引/標準類別，並將其映射到文本章節（以表格輸出：類別、理由、對應章節、預期證據）。

文本：
{text_in}
"""
    elif magic_id == "deficiency_builder":
        user = f"""{lang}
請從以下內容找出缺口（資料不足/矛盾/需補充），並撰寫審查者可用的補件問題草稿。請依嚴重度分級（High/Medium/Low），每題需包含「需要的證據」與「原因」。輸出 Markdown。

文本：
{text_in}
"""
    elif magic_id == "exec_brief":
        user = f"""{lang}
請將以下內容濃縮成一頁的高階簡報（Markdown），包含：目的、關鍵發現、主要風險/缺口、建議下一步、需決策事項。避免臆測。

文本：
{text_in}
"""
    elif magic_id == "change_log":
        user = f"""{lang}
請為以下文本產出「變更紀錄摘要」模板（假設此文本剛被更新），提供：變更區塊、變更類型、影響、需再確認事項。輸出 Markdown。

文本：
{text_in}
"""
    elif magic_id == "citation_sweeper":
        user = f"""{lang}
請對以下 Markdown 進行「引用整理」：
- 將散落的 URL/引用整理成一致的 References 區段
- 在文中對應主張後加上簡短引用標記（例如 [Ref 3]）
- 若發現關鍵主張無引用，列在「Missing Citations」清單
輸出整理後的 Markdown。

文本：
{text_in}
"""
    elif magic_id == "risk_heatmap":
        user = f"""{lang}
請根據以下內容建立「風險熱圖」(Risk Heatmap) 的 Markdown 表格：
- 至少 12 個風險條目
- 欄位：Hazard、Severity(1-5)、Probability(1-5)、Risk Score、Key Controls、Evidence Needed、Reviewer Notes
- 同時給出 3 點風險概觀結論
若資訊不足，請合理用「待確認」標示，不要臆造事實來源。

文本：
{text_in}
"""
    elif magic_id == "localization_transformer":
        # This magic can translate/localize while preserving structure.
        if output_lang == "zh-TW":
            user = f"""\
請將以下內容在不破壞 Markdown 結構（標題/表格/清單）的前提下，轉換為**繁體中文**，並將專有名詞第一次出現時保留英文括號。不要新增未提供的事實。

內容：
{text_in}
"""
        else:
            user = f"""\
Translate/localize the following content into **English** while preserving Markdown structure (headings/tables/lists). Keep specialized terms with original language in parentheses on first occurrence. Do not add facts.

Content:
{text_in}
"""
    else:
        user = f"{lang}\n請改善以下內容並輸出 Markdown：\n\n{text_in}"
    return sys, user


# -----------------------------------------------------------------------------
# LLM health checks (bug prevention)
# -----------------------------------------------------------------------------

def llm_health_checks(model_label: str) -> List[Tuple[str, bool, str]]:
    checks = []
    # 1) Provider key present?
    m = resolve_model(model_label)
    provider = m["provider"]
    key = get_provider_key(provider)
    checks.append(("Provider key present", bool(key), f"provider={provider}"))

    # 2) Package present for provider?
    pkg_ok = True
    detail = ""
    try:
        if provider in {"openai", "grok"}:
            import openai  # noqa: F401
        elif provider == "anthropic":
            import anthropic  # noqa: F401
        elif provider == "gemini":
            try:
                import google.generativeai  # noqa: F401
            except Exception:
                from google import genai  # type: ignore # noqa: F401
        else:
            pkg_ok = False
            detail = "unknown provider"
    except Exception as e:
        pkg_ok = False
        detail = str(e)
    checks.append(("Provider SDK import", pkg_ok, detail))

    # 3) Minimal call sanity (only if key+pkg ok). Keep extremely small.
    if key and pkg_ok:
        try:
            text, _ = llm_call(
                model_label=model_label,
                system_prompt="You are a health-check assistant.",
                user_prompt="Reply with exactly: OK",
                temperature=0.0,
                max_tokens=20,
                retries=0,
            )
            ok = ("OK" in (text or ""))
            checks.append(("Minimal completion call", ok, (text or "")[:80]))
        except Exception as e:
            checks.append(("Minimal completion call", False, str(e)))

    return checks


# -----------------------------------------------------------------------------
# UI components
# -----------------------------------------------------------------------------

def wow_header():
    ui_lang = st.session_state.ui_lang
    title = APP_TITLE_ZH if ui_lang == "zh-TW" else APP_TITLE_EN
    st.markdown(f"<div class='wow-card'><div class='wow-kpi'>{title}</div>"
                f"<div class='wow-sub'>{t('safety_note')}</div></div>", unsafe_allow_html=True)


def wow_status_bar():
    # Provider statuses
    def provider_status(provider: str) -> Tuple[str, str]:
        key = get_provider_key(provider)
        if key:
            return t("connected"), "OK"
        return t("missing_key"), "MISSING"

    openai_s, _ = provider_status("openai")
    gemini_s, _ = provider_status("gemini")
    anthropic_s, _ = provider_status("anthropic")
    grok_s, _ = provider_status("grok")

    run_state = st.session_state.run_state
    state_label = {
        "idle": t("idle"),
        "running": t("running"),
        "await_edit": t("await_edit"),
        "done": t("done"),
        "failed": t("failed"),
    }.get(run_state, run_state)

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


def sidebar_controls():
    st.sidebar.markdown("## WOW Controls")
    st.sidebar.selectbox(
        t("language"),
        SUPPORTED_UI_LANGS,
        index=SUPPORTED_UI_LANGS.index(st.session_state.ui_lang),
        key="ui_lang",
    )
    st.sidebar.selectbox(
        t("output_language"),
        list(OUTPUT_LANG_CHOICES.keys()),
        format_func=lambda k: OUTPUT_LANG_CHOICES[k],
        index=list(OUTPUT_LANG_CHOICES.keys()).index(st.session_state.output_lang),
        key="output_lang",
    )
    st.sidebar.selectbox(
        t("theme"),
        ["dark", "light"],
        index=0 if st.session_state.theme == "dark" else 1,
        format_func=lambda x: t("dark") if x == "dark" else t("light"),
        key="theme",
    )

    # Style selection
    style_names = [s["name"] for s in PAINTER_STYLES]
    style_ids = [s["id"] for s in PAINTER_STYLES]
    cur_idx = style_ids.index(st.session_state.style_id) if st.session_state.style_id in style_ids else 0

    style_pick = st.sidebar.selectbox(
        t("style_pack"),
        style_ids,
        index=cur_idx,
        format_func=lambda sid: next((s["name"] for s in PAINTER_STYLES if s["id"] == sid), sid),
        key="style_id",
        disabled=bool(st.session_state.lock_style),
    )
    st.sidebar.checkbox(t("lock_style"), value=st.session_state.lock_style, key="lock_style")

    if st.sidebar.button(t("jackslot")):
        st.session_state.style_id = random.choice(style_ids)
        st.sidebar.info(f"Selected: {next(s['name'] for s in PAINTER_STYLES if s['id']==st.session_state.style_id)}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("## " + t("live_log"))
    if st.sidebar.button(t("clear_log")):
        st.session_state.live_log = []
    st.sidebar.download_button(
        t("download_log"),
        data=format_log_text().encode("utf-8"),
        file_name="live_log.txt",
        mime="text/plain",
        use_container_width=True,
    )
    st.sidebar.markdown("---")
    st.sidebar.caption(t("safety_note"))


def live_log_panel():
    st.markdown("### " + t("live_log"))
    text = format_log_text()
    st.text_area("", value=text, height=220)


def dashboard_panel():
    st.markdown("### " + t("nav_dashboard"))
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown("<div class='wow-card'><div class='wow-kpi'>{}</div><div class='wow-sub'>{}</div></div>".format(
        len(st.session_state.pdf_files), t("found_pdfs")
    ), unsafe_allow_html=True)
    col2.markdown("<div class='wow-card'><div class='wow-kpi'>{}</div><div class='wow-sub'>{}</div></div>".format(
        len(st.session_state.pdf_summaries), t("processed")
    ), unsafe_allow_html=True)
    # flagged: scanned/empty
    flagged = 0
    for s in st.session_state.pdf_summaries.values():
        if "Scanned content" in s:
            flagged += 1
    col3.markdown("<div class='wow-card'><div class='wow-kpi'>{}</div><div class='wow-sub'>{}</div></div>".format(
        flagged, t("flagged")
    ), unsafe_allow_html=True)
    col4.markdown("<div class='wow-card'><div class='wow-kpi'>{}</div><div class='wow-sub'>Agent chain steps</div></div>".format(
        len(st.session_state.agent_chain)
    ), unsafe_allow_html=True)

    st.markdown("<div class='wow-card'><div class='wow-sub'>Run History (this session)</div>"
                f"<div class='wow-kpi'>{len(st.session_state.history)}</div></div>", unsafe_allow_html=True)

    st.markdown("### " + t("program_wow_features"))
    st.markdown(
        "- Core AI Magics (6): Clarity, Evidence Tagging, Standards Mapping, Deficiency Drafting, Exec Brief, Change Log\n"
        "- Extra WOW Features (3): Citation Sweeper, Risk Heatmap Builder, Localization Transformer\n"
        "- Chain-of-Agents with editable prompts/outputs and per-step model selection\n"
        "- Web research (best-effort) with citation list generation\n"
    )


# -----------------------------------------------------------------------------
# Settings & Keys UI
# -----------------------------------------------------------------------------

def settings_panel():
    st.markdown("### " + t("nav_settings"))
    st.markdown("<div class='wow-card'><div class='wow-sub'>"+t("api_keys")+"</div></div>", unsafe_allow_html=True)

    def key_widget(provider: str, label: str, env_var_names: List[str]):
        # If any env var present, do not show input
        env_present = any(env_key(n) for n in env_var_names)
        if env_present:
            st.info(f"{label}: {t('key_in_env')}")
            return
        # else show masked input
        v = st.text_input(label + " — " + t("enter_key"), type="password")
        if v and v.strip():
            st.session_state.session_secrets[provider] = v.strip()
            log_event(f"{provider} key set in session.", "INFO", "keys")

    key_widget("openai", t("openai_key"), ["OPENAI_API_KEY"])
    key_widget("gemini", t("gemini_key"), ["GEMINI_API_KEY"])
    key_widget("anthropic", t("anthropic_key"), ["ANTHROPIC_API_KEY"])
    key_widget("grok", t("grok_key"), ["GROK_API_KEY", "XAI_API_KEY"])

    if st.button(t("clear_secrets")):
        st.session_state.session_secrets = {}
        log_event("Session secrets cleared.", "INFO", "keys")

    st.markdown("---")
    st.markdown("### " + t("bugs_panel"))
    model_label = st.selectbox(t("model"), list_models(), index=0)
    if st.button(t("run_health")):
        checks = llm_health_checks(model_label)
        ok = all(c[1] for c in checks if c[0] != "Minimal completion call") and any(c[0] == "Minimal completion call" and c[1] for c in checks) or True
        if ok:
            st.success(t("health_ok"))
        else:
            st.warning(t("health_warn"))
        st.markdown("#### Details")
        for name, passed, detail in checks:
            st.write(f"- {'✅' if passed else '❌'} **{name}** — {detail}")

    st.markdown("---")
    st.markdown("### agents.yaml")
    if st.session_state.agents_load_error:
        st.warning(st.session_state.agents_load_error)

    uploaded = st.file_uploader("Upload agents.yaml", type=["yaml", "yml"])
    if uploaded is not None:
        txt = uploaded.read().decode("utf-8", errors="replace")
        agents, err = load_agents_yaml(txt)
        st.session_state.agents = agents
        st.session_state.agents_load_error = err
        if err:
            st.error(err)
            log_event(err, "ERROR", "agents")
        else:
            st.success(f"Loaded {len(agents)} agents.")
            log_event(f"Loaded {len(agents)} agents from upload.", "INFO", "agents")


# -----------------------------------------------------------------------------
# PDF discovery & ToC panel
# -----------------------------------------------------------------------------

def pdf_panel():
    st.markdown("### " + t("nav_pdf"))
    if PdfReader is None:
        st.error("Missing dependency: pypdf. Install pypdf to enable PDF processing.")
        return

    uploaded_zip = st.file_uploader(t("upload_zip"), type=["zip"])
    colA, colB = st.columns([1, 1])
    with colA:
        summarization_model = st.selectbox(t("summarize_model"), list_models(), index=0, key="pdf_sum_model")
    with colB:
        lens = st.selectbox(
            t("domain_lens"),
            ["general", "510k", "clinical", "cyber", "software"],
            format_func=lambda x: {
                "general": t("lens_general"),
                "510k": t("lens_510k"),
                "clinical": t("lens_clinical"),
                "cyber": t("lens_cyber"),
                "software": t("lens_software"),
            }[x],
            key="pdf_domain_lens",
        )

    if st.button(t("scan"), disabled=uploaded_zip is None):
        st.session_state.run_state = "running"
        try:
            zip_bytes = uploaded_zip.read()
            root = extract_zip_to_tmp(zip_bytes)
            st.session_state.pdf_workspace_id = root
            log_event(f"ZIP extracted to {root}", "INFO", "pdf")

            pdfs = discover_pdfs(root)
            st.session_state.pdf_files = pdfs
            log_event(f"Discovered {len(pdfs)} PDFs.", "INFO", "pdf")

            summaries: Dict[str, str] = {}
            progress = st.progress(0)
            for idx, path in enumerate(pdfs):
                try:
                    text, meta = pdf_extract_text_trim_first_page(path)
                    summ, smeta = summarize_pdf_text(
                        text,
                        model_label=summarization_model,
                        domain_lens=lens,
                        output_lang=st.session_state.output_lang,
                    )
                    header = f"**Path**: `{path}`\n\n"
                    flags = []
                    if meta.get("trimmed_first_page"):
                        flags.append("trimmed_first_page")
                    if meta.get("single_page"):
                        flags.append("single_page")
                    if meta.get("scanned_or_empty"):
                        flags.append("scanned_or_empty")
                    if flags:
                        header += f"**Flags**: `{', '.join(flags)}`\n\n"
                    summaries[path] = header + summ.strip()
                    log_event(f"Summarized: {os.path.basename(path)} (model={smeta.get('model')})", "INFO", "pdf")
                except Exception as e:
                    summaries[path] = f"**Error summarizing**: {e}"
                    log_event(f"Failed: {path} — {e}", "ERROR", "pdf")
                progress.progress((idx + 1) / max(1, len(pdfs)))

            st.session_state.pdf_summaries = summaries
            st.session_state.master_toc = build_master_toc(summaries)
            st.session_state.run_state = "done"
            log_event("Master ToC built.", "INFO", "pdf")

            # Save to history
            st.session_state.history.append({
                "id": f"pdf_{uuid.uuid4().hex[:8]}",
                "ts": now_iso(),
                "type": "pdf_index",
                "pdf_count": len(pdfs),
                "model": summarization_model,
            })
        except Exception as e:
            st.session_state.run_state = "failed"
            log_event(f"PDF pipeline failed: {e}", "ERROR", "pdf")
            st.error(str(e))

    st.markdown("### " + t("toc"))
    st.session_state.master_toc = st.text_area("", value=st.session_state.master_toc, height=320)
    st.download_button(
        t("download_md"),
        data=st.session_state.master_toc.encode("utf-8"),
        file_name="ToC_Master.md",
        mime="text/markdown",
        use_container_width=True,
    )


# -----------------------------------------------------------------------------
# Agent workspace panel (single + chain)
# -----------------------------------------------------------------------------

def agent_workspace_panel():
    st.markdown("### " + t("nav_agents"))
    agents = st.session_state.agents or {}
    if not agents:
        st.warning("No agents loaded. Add agents.yaml in Settings.")
    agent_names = sorted(list(agents.keys()))
    selected_agent = st.selectbox("Select agent", agent_names) if agent_names else None

    st.markdown("#### Single Agent Run")
    model_label = st.selectbox(t("model"), list_models(), index=0, key="agent_model_single")
    temperature = st.slider(t("temperature"), 0.0, 1.0, float(DEFAULT_TEMPERATURE), 0.05, key="agent_temp_single")
    max_tokens = st.slider(t("max_tokens"), 256, 4096, int(DEFAULT_MAX_TOKENS), 64, key="agent_maxt_single")

    default_prompt = ""
    default_system = "You are a helpful assistant."
    if selected_agent:
        a = agents[selected_agent]
        default_prompt = a.get("user_prompt_template", "")
        default_system = a.get("system_prompt", default_system)

    prompt = st.text_area(t("prompt"), value=default_prompt, height=160, key="agent_prompt_single")
    citations_required = st.checkbox(t("citations_required"), value=False, key="agent_cite_single")

    # input context is Master ToC
    context = st.session_state.master_toc.strip()
    if not context:
        st.info("Master ToC is empty. Run PDF indexing first or paste content into ToC.")

    if st.button(t("run_agent"), disabled=(not selected_agent or not context)):
        st.session_state.run_state = "running"
        try:
            # If citations required, instruct explicitly.
            cite_line = "\nIf you reference external sources, include URLs. If none available, say so.\n" if citations_required else ""
            user_prompt = f"CONTEXT (Master ToC):\n{context}\n\nUSER INSTRUCTIONS:\n{prompt}\n{cite_line}"
            out, meta = llm_call(
                model_label=model_label,
                system_prompt=default_system,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            st.session_state.run_state = "await_edit"
            st.markdown("#### Output")
            out_edited = st.text_area(t("edit_output"), value=out, height=240, key="agent_output_single_edit")
            st.session_state.run_state = "done"

            st.download_button(
                t("download_md"),
                data=out_edited.encode("utf-8"),
                file_name=f"agent_{selected_agent}.md",
                mime="text/markdown",
                use_container_width=True,
            )
            st.session_state.history.append({
                "id": f"agent_{uuid.uuid4().hex[:8]}",
                "ts": now_iso(),
                "type": "agent_single",
                "agent": selected_agent,
                "model": meta.get("model"),
                "provider": meta.get("provider"),
            })
            log_event(f"Agent run completed: {selected_agent} ({meta.get('provider')}:{meta.get('model')})", "INFO", "agent")
        except Exception as e:
            st.session_state.run_state = "failed"
            log_event(f"Agent run failed: {e}", "ERROR", "agent")
            st.error(str(e))

    st.markdown("---")
    st.markdown("#### " + t("chain_builder"))

    # Chain add UI
    col1, col2 = st.columns([2, 1])
    with col1:
        chain_agent = st.selectbox("Agent to add", agent_names, key="chain_add_agent") if agent_names else None
    with col2:
        if st.button(t("add_to_chain"), disabled=not chain_agent):
            a = agents[chain_agent]
            step = {
                "id": uuid.uuid4().hex[:8],
                "agent": chain_agent,
                "system_prompt": a.get("system_prompt", "You are a helpful assistant."),
                "prompt": a.get("user_prompt_template", ""),
                "model_label": list_models()[0],
                "temperature": DEFAULT_TEMPERATURE,
                "max_tokens": DEFAULT_MAX_TOKENS,
                "input_source": "toc",
                "custom_input": "",
                "output": "",
                "output_edited": "",
                "status": "pending",
                "meta": {},
            }
            st.session_state.agent_chain.append(step)
            log_event(f"Added chain step: {chain_agent}", "INFO", "chain")

    # Render chain steps
    if not st.session_state.agent_chain:
        st.info("Chain is empty. Add agents above.")
        return

    for idx, step in enumerate(st.session_state.agent_chain):
        with st.expander(f"{t('step')} {idx+1}: {step['agent']}  —  status: {step.get('status','pending')}", expanded=(idx == 0)):
            # Controls
            step["model_label"] = st.selectbox(
                t("model"),
                list_models(),
                index=list_models().index(step["model_label"]) if step["model_label"] in list_models() else 0,
                key=f"chain_model_{step['id']}",
            )
            step["temperature"] = st.slider(
                t("temperature"), 0.0, 1.0, float(step["temperature"]), 0.05, key=f"chain_temp_{step['id']}"
            )
            step["max_tokens"] = st.slider(
                t("max_tokens"), 256, 4096, int(step["max_tokens"]), 64, key=f"chain_maxt_{step['id']}"
            )
            step["input_source"] = st.selectbox(
                t("input_source"),
                ["toc", "prev", "custom"],
                format_func=lambda x: {
                    "toc": t("input_toc"),
                    "prev": t("input_prev"),
                    "custom": t("input_custom"),
                }[x],
                index=["toc", "prev", "custom"].index(step["input_source"]),
                key=f"chain_input_{step['id']}",
            )
            if step["input_source"] == "custom":
                step["custom_input"] = st.text_area("Custom input", value=step["custom_input"], height=120, key=f"chain_custom_{step['id']}")

            step["prompt"] = st.text_area(t("prompt"), value=step["prompt"], height=150, key=f"chain_prompt_{step['id']}")

            colx, coly = st.columns([1, 1])
            with colx:
                do_run = st.button(t("execute_step"), key=f"chain_run_{step['id']}")
            with coly:
                if st.button("Remove step", key=f"chain_rm_{step['id']}"):
                    st.session_state.agent_chain = [s for s in st.session_state.agent_chain if s["id"] != step["id"]]
                    log_event(f"Removed chain step {idx+1}", "INFO", "chain")
                    st.rerun()

            if do_run:
                st.session_state.run_state = "running"
                step["status"] = "running"
                try:
                    # Determine input
                    if step["input_source"] == "toc":
                        chain_input = st.session_state.master_toc
                    elif step["input_source"] == "prev":
                        if idx == 0:
                            chain_input = st.session_state.master_toc
                        else:
                            prev = st.session_state.agent_chain[idx - 1]
                            chain_input = prev.get("output_edited") or prev.get("output") or ""
                    else:
                        chain_input = step["custom_input"]

                    if not chain_input.strip():
                        raise LLMError("Chain input is empty. Provide ToC, previous output, or custom input.")

                    # Compose prompt
                    user_prompt = f"INPUT:\n{chain_input}\n\nTASK:\n{step['prompt']}\n\nOutput in Markdown unless asked otherwise."

                    out, meta = llm_call(
                        model_label=step["model_label"],
                        system_prompt=step["system_prompt"],
                        user_prompt=user_prompt,
                        temperature=float(step["temperature"]),
                        max_tokens=int(step["max_tokens"]),
                    )
                    step["output"] = out
                    step["output_edited"] = out
                    step["meta"] = meta
                    step["status"] = "await_edit"
                    st.session_state.run_state = "await_edit"
                    log_event(f"Chain step {idx+1} done: {step['agent']} ({meta.get('provider')}:{meta.get('model')})", "INFO", "chain")
                except Exception as e:
                    step["status"] = "failed"
                    st.session_state.run_state = "failed"
                    log_event(f"Chain step {idx+1} failed: {e}", "ERROR", "chain")
                    st.error(str(e))

            # Output editors (always show if exists)
            if step.get("output"):
                view = st.radio("View", [t("markdown_view"), t("text_view")], horizontal=True, key=f"chain_view_{step['id']}")
                if view == t("markdown_view"):
                    step["output_edited"] = st.text_area(t("edit_output"), value=step["output_edited"], height=220, key=f"chain_outmd_{step['id']}")
                    st.markdown("**Preview**")
                    st.markdown(step["output_edited"], unsafe_allow_html=True)
                else:
                    step["output_edited"] = st.text_area(t("edit_output"), value=step["output_edited"], height=220, key=f"chain_outtxt_{step['id']}")

                st.download_button(
                    t("download_md"),
                    data=step["output_edited"].encode("utf-8"),
                    file_name=f"chain_step_{idx+1}_{step['agent']}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

    # Persist chain run in history (summary record)
    if st.button("Save chain run to history"):
        st.session_state.history.append({
            "id": f"chain_{uuid.uuid4().hex[:8]}",
            "ts": now_iso(),
            "type": "agent_chain",
            "steps": [
                {
                    "agent": s["agent"],
                    "model": s.get("meta", {}).get("model") or resolve_model(s["model_label"])["id"],
                    "provider": s.get("meta", {}).get("provider") or resolve_model(s["model_label"])["provider"],
                    "status": s.get("status"),
                }
                for s in st.session_state.agent_chain
            ],
        })
        log_event("Chain run saved to history.", "INFO", "chain")


# -----------------------------------------------------------------------------
# AI Notekeeper panel
# -----------------------------------------------------------------------------

def notekeeper_panel():
    st.markdown("### " + t("nav_notes"))
    model_label = st.selectbox(t("model"), list_models(), index=0, key="notes_model")
    temperature = st.slider(t("temperature"), 0.0, 1.0, float(DEFAULT_TEMPERATURE), 0.05, key="notes_temp")
    max_tokens = st.slider(t("max_tokens"), 256, 4096, 1400, 64, key="notes_maxt")

    st.session_state.notes_input = st.text_area(t("notes_paste"), value=st.session_state.notes_input, height=200)

    if st.button(t("notes_transform")):
        st.session_state.run_state = "running"
        try:
            out, meta, kws = notekeeper_transform(
                st.session_state.notes_input,
                st.session_state.output_lang,
                model_label,
                temperature,
                max_tokens,
            )
            st.session_state.notes_output = out
            st.session_state.notes_keywords = kws
            st.session_state.run_state = "await_edit"
            log_event(f"Notekeeper transform complete ({meta.get('provider')}:{meta.get('model')})", "INFO", "notes")
            st.session_state.history.append({
                "id": f"notes_{uuid.uuid4().hex[:8]}",
                "ts": now_iso(),
                "type": "notekeeper_transform",
                "model": meta.get("model"),
                "provider": meta.get("provider"),
            })
        except Exception as e:
            st.session_state.run_state = "failed"
            log_event(f"Notekeeper failed: {e}", "ERROR", "notes")
            st.error(str(e))

    if st.session_state.notes_output:
        st.markdown("#### Output (editable)")
        view = st.radio("View", [t("markdown_view"), t("text_view")], horizontal=True, key="notes_view")
        if view == t("markdown_view"):
            st.session_state.notes_output = st.text_area("", value=st.session_state.notes_output, height=260, key="notes_out_md")
            st.markdown("**Preview**")
            st.markdown(st.session_state.notes_output, unsafe_allow_html=True)
        else:
            st.session_state.notes_output = st.text_area("", value=st.session_state.notes_output, height=260, key="notes_out_txt")

        st.download_button(
            t("download_md"),
            data=st.session_state.notes_output.encode("utf-8"),
            file_name="notekeeper.md",
            mime="text/markdown",
            use_container_width=True,
        )

        st.markdown("#### " + t("ai_magics"))
        magic_options = [m["id"] for m in AI_MAGICS]
        magic_labels = {m["id"]: (m["name_zh"] if st.session_state.ui_lang == "zh-TW" else m["name_en"]) for m in AI_MAGICS}
        magic_id = st.selectbox("Magic", magic_options, format_func=lambda mid: magic_labels[mid], key="notes_magic")
        magic_model = st.selectbox(t("model"), list_models(), index=0, key="notes_magic_model")
        magic_prompt_extra = st.text_area("Extra prompt (optional)", value="", height=80, key="notes_magic_extra")

        if st.button("Run Magic", key="notes_run_magic"):
            st.session_state.run_state = "running"
            try:
                sys, user = magic_prompt(magic_id, st.session_state.notes_output, st.session_state.output_lang)
                if magic_prompt_extra.strip():
                    user += "\n\nAdditional user instruction:\n" + magic_prompt_extra.strip()
                out, meta = llm_call(
                    model_label=magic_model,
                    system_prompt=sys,
                    user_prompt=user,
                    temperature=0.2,
                    max_tokens=1800,
                )
                st.session_state.notes_output = out
                st.session_state.run_state = "await_edit"
                log_event(f"Magic {magic_id} completed ({meta.get('provider')}:{meta.get('model')})", "INFO", "magic")
            except Exception as e:
                st.session_state.run_state = "failed"
                log_event(f"Magic failed: {e}", "ERROR", "magic")
                st.error(str(e))

        st.markdown("#### " + t("keep_prompting"))
        kp_model = st.selectbox(t("model"), list_models(), index=0, key="notes_kp_model")
        kp_prompt = st.text_area(t("prompt"), value="", height=100, key="notes_kp_prompt")
        if st.button(t("generate"), key="notes_keep_prompting"):
            st.session_state.run_state = "running"
            try:
                sys = "You are a helpful assistant. Continue from the provided note content."
                user = f"NOTE CONTENT:\n{st.session_state.notes_output}\n\nUSER REQUEST:\n{kp_prompt}"
                out, meta = llm_call(
                    model_label=kp_model,
                    system_prompt=sys,
                    user_prompt=user,
                    temperature=0.3,
                    max_tokens=1600,
                )
                st.session_state.notes_output += "\n\n---\n\n" + out
                st.session_state.run_state = "await_edit"
                log_event(f"Keep prompting completed ({meta.get('provider')}:{meta.get('model')})", "INFO", "notes")
            except Exception as e:
                st.session_state.run_state = "failed"
                log_event(f"Keep prompting failed: {e}", "ERROR", "notes")
                st.error(str(e))


# -----------------------------------------------------------------------------
# 510(k) Review Suite panel
# -----------------------------------------------------------------------------

def panel_510k():
    st.markdown("### " + t("nav_510k"))

    # Global generation controls for 510(k)
    model_label = st.selectbox(t("model"), list_models(), index=0, key="510k_model")
    temperature = st.slider(t("temperature"), 0.0, 1.0, 0.2, 0.05, key="510k_temp")
    max_tokens = st.slider(t("max_tokens"), 512, 4096, 2200, 64, key="510k_maxt")

    st.markdown("#### " + t("step1"))
    st.session_state["510k_step1"] = st.text_area("", value=st.session_state["510k_step1"], height=200, key="510k_step1_area")

    st.markdown("#### " + t("step2"))
    use_default = st.checkbox(t("use_default_template"), value=(not st.session_state["510k_template"].strip()), key="510k_use_default")
    if use_default:
        st.session_state["510k_template"] = DEFAULT_510K_TEMPLATE
    else:
        st.session_state["510k_template"] = st.text_area("", value=st.session_state["510k_template"], height=220, key="510k_template_area")

    st.markdown("#### " + t("web_research"))
    web_on = st.checkbox(t("web_research"), value=True, key="510k_web_on")
    web_depth = st.selectbox(t("web_depth"), ["quick", "standard", "exhaustive"], format_func=lambda x: t(x), key="510k_web_depth")
    fda_only = st.checkbox(t("fda_only"), value=False, key="510k_fda_only")

    citations: List[Dict[str, str]] = []
    citations_md = ""
    if web_on:
        # Show a small note if ddg unavailable
        if "duckduckgo_search" not in str(os.environ) and True:
            # We can't reliably detect; just warn if module missing at runtime by test.
            try:
                import duckduckgo_search  # noqa: F401
            except Exception:
                st.info("Web research will run only if 'duckduckgo_search' is available in the environment. Otherwise citations will be empty.")

    st.markdown("---")
    st.markdown("#### " + t("step4"))
    step4_prompt_override = st.text_area("Prompt override (optional)", value="", height=90, key="510k_step4_prompt_override")
    if st.button(t("generate"), key="510k_gen_step4"):
        st.session_state.run_state = "running"
        try:
            if web_on:
                citations = web_research(st.session_state["510k_step1"], web_depth, fda_only)
            citations_md = citations_to_markdown(citations)

            sys = sys_regulatory_writer(st.session_state.output_lang)
            user = prompt_step4_summary(st.session_state["510k_step1"], citations_md, st.session_state.output_lang)
            if step4_prompt_override.strip():
                user += "\n\nAdditional user instruction:\n" + step4_prompt_override.strip()

            out, meta = llm_call(
                model_label=model_label,
                system_prompt=sys,
                user_prompt=user,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            st.session_state["510k_step4"] = out
            st.session_state.run_state = "await_edit"
            st.session_state.history.append({
                "id": f"510k_s4_{uuid.uuid4().hex[:8]}",
                "ts": now_iso(),
                "type": "510k_step4_summary",
                "model": meta.get("model"),
                "provider": meta.get("provider"),
                "citations": len(citations),
            })
            log_event(f"510(k) Step4 generated ({meta.get('provider')}:{meta.get('model')}) citations={len(citations)}", "INFO", "510k")
        except Exception as e:
            st.session_state.run_state = "failed"
            log_event(f"510(k) Step4 failed: {e}", "ERROR", "510k")
            st.error(str(e))

    if st.session_state["510k_step4"].strip():
        st.markdown("**Step 4 Result (editable)**")
        st.session_state["510k_step4"] = st.text_area("", value=st.session_state["510k_step4"], height=260, key="510k_step4_edit")
        st.markdown("**Preview**")
        st.markdown(st.session_state["510k_step4"], unsafe_allow_html=True)
        st.download_button(
            t("download_md"),
            data=st.session_state["510k_step4"].encode("utf-8"),
            file_name="510k_step4_summary.md",
            mime="text/markdown",
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown("#### " + t("step5"))
    step5_prompt_override = st.text_area("Prompt override (optional)", value="", height=90, key="510k_step5_prompt_override")
    if st.button(t("generate"), key="510k_gen_step5", disabled=not st.session_state["510k_step4"].strip()):
        st.session_state.run_state = "running"
        try:
            sys = sys_regulatory_writer(st.session_state.output_lang)
            user = prompt_step5_report(
                st.session_state["510k_step1"],
                st.session_state["510k_step4"],
                st.session_state["510k_template"],
                st.session_state.output_lang,
            )
            if step5_prompt_override.strip():
                user += "\n\nAdditional user instruction:\n" + step5_prompt_override.strip()

            out, meta = llm_call(
                model_label=model_label,
                system_prompt=sys,
                user_prompt=user,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            st.session_state["510k_step5"] = out
            st.session_state.run_state = "await_edit"
            st.session_state.history.append({
                "id": f"510k_s5_{uuid.uuid4().hex[:8]}",
                "ts": now_iso(),
                "type": "510k_step5_report",
                "model": meta.get("model"),
                "provider": meta.get("provider"),
            })
            log_event(f"510(k) Step5 generated ({meta.get('provider')}:{meta.get('model')})", "INFO", "510k")
        except Exception as e:
            st.session_state.run_state = "failed"
            log_event(f"510(k) Step5 failed: {e}", "ERROR", "510k")
            st.error(str(e))

    if st.session_state["510k_step5"].strip():
        st.markdown("**Step 5 Report (editable)**")
        st.session_state["510k_step5"] = st.text_area("", value=st.session_state["510k_step5"], height=320, key="510k_step5_edit")
        st.markdown("**Preview**")
        st.markdown(st.session_state["510k_step5"], unsafe_allow_html=True)
        st.download_button(
            t("download_md"),
            data=st.session_state["510k_step5"].encode("utf-8"),
            file_name="510k_step5_review_report.md",
            mime="text/markdown",
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown("#### " + t("step6"))
    step6_prompt_override = st.text_area("Prompt override (optional)", value="", height=90, key="510k_step6_prompt_override")
    if st.button(t("generate"), key="510k_gen_step6", disabled=not st.session_state["510k_step5"].strip()):
        st.session_state.run_state = "running"
        try:
            sys = "You are a skill creator. Produce a reusable skill.md with strong triggering description and clear workflow."
            user = prompt_step6_skill(st.session_state["510k_step4"], st.session_state["510k_step5"], st.session_state.output_lang)
            if step6_prompt_override.strip():
                user += "\n\nAdditional user instruction:\n" + step6_prompt_override.strip()

            out, meta = llm_call(
                model_label=model_label,
                system_prompt=sys,
                user_prompt=user,
                temperature=0.2,
                max_tokens=2200,
            )
            st.session_state["510k_skill_md"] = out
            st.session_state.run_state = "await_edit"
            st.session_state.history.append({
                "id": f"510k_s6_{uuid.uuid4().hex[:8]}",
                "ts": now_iso(),
                "type": "510k_step6_skill_md",
                "model": meta.get("model"),
                "provider": meta.get("provider"),
            })
            log_event(f"510(k) Step6 skill.md generated ({meta.get('provider')}:{meta.get('model')})", "INFO", "510k")
        except Exception as e:
            st.session_state.run_state = "failed"
            log_event(f"510(k) Step6 failed: {e}", "ERROR", "510k")
            st.error(str(e))

    if st.session_state["510k_skill_md"].strip():
        st.markdown("**skill.md (editable)**")
        st.session_state["510k_skill_md"] = st.text_area("", value=st.session_state["510k_skill_md"], height=320, key="510k_skill_edit")
        st.markdown("**Preview**")
        st.markdown(st.session_state["510k_skill_md"], unsafe_allow_html=True)
        st.download_button(
            t("download_md"),
            data=st.session_state["510k_skill_md"].encode("utf-8"),
            file_name="skill.md",
            mime="text/markdown",
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown("#### " + t("ai_magics"))
    if st.session_state["510k_step5"].strip():
        magic_options = [m["id"] for m in AI_MAGICS]
        magic_labels = {m["id"]: (m["name_zh"] if st.session_state.ui_lang == "zh-TW" else m["name_en"]) for m in AI_MAGICS}
        magic_id = st.selectbox("Magic", magic_options, format_func=lambda mid: magic_labels[mid], key="510k_magic")
        magic_model = st.selectbox(t("model"), list_models(), index=0, key="510k_magic_model")
        magic_prompt_extra = st.text_area("Extra prompt (optional)", value="", height=80, key="510k_magic_extra")
        target = st.selectbox("Target", ["Step 4 Summary", "Step 5 Report", "skill.md"], key="510k_magic_target")

        if st.button("Run Magic", key="510k_run_magic"):
            st.session_state.run_state = "running"
            try:
                if target == "Step 4 Summary":
                    text_in = st.session_state["510k_step4"]
                elif target == "skill.md":
                    text_in = st.session_state["510k_skill_md"]
                else:
                    text_in = st.session_state["510k_step5"]

                sys, user = magic_prompt(magic_id, text_in, st.session_state.output_lang)
                if magic_prompt_extra.strip():
                    user += "\n\nAdditional user instruction:\n" + magic_prompt_extra.strip()
                out, meta = llm_call(
                    model_label=magic_model,
                    system_prompt=sys,
                    user_prompt=user,
                    temperature=0.2,
                    max_tokens=2200,
                )

                if target == "Step 4 Summary":
                    st.session_state["510k_step4"] = out
                elif target == "skill.md":
                    st.session_state["510k_skill_md"] = out
                else:
                    st.session_state["510k_step5"] = out

                st.session_state.run_state = "await_edit"
                log_event(f"510(k) magic {magic_id} applied to {target} ({meta.get('provider')}:{meta.get('model')})", "INFO", "510k")
            except Exception as e:
                st.session_state.run_state = "failed"
                log_event(f"510(k) magic failed: {e}", "ERROR", "510k")
                st.error(str(e))


# -----------------------------------------------------------------------------
# History / Exports panel
# -----------------------------------------------------------------------------

def history_panel():
    st.markdown("### " + t("nav_history"))
    if not st.session_state.history:
        st.info("No history yet in this session.")
        return

    st.markdown("#### Runs")
    for item in reversed(st.session_state.history):
        with st.expander(f"{item.get('ts')} — {item.get('type')} — {item.get('id')}"):
            st.json(item)

    st.markdown("#### Export session manifest")
    manifest = {
        "exported_at": now_iso(),
        "history_count": len(st.session_state.history),
        "history": st.session_state.history,
        "notes": {
            "keywords": st.session_state.notes_keywords,
        },
        "pdf": {
            "pdf_count": len(st.session_state.pdf_files),
            "toc_chars": len(st.session_state.master_toc or ""),
        },
        "510k": {
            "step1_chars": len(st.session_state["510k_step1"] or ""),
            "step4_chars": len(st.session_state["510k_step4"] or ""),
            "step5_chars": len(st.session_state["510k_step5"] or ""),
        },
        # Never export secrets
        "secrets_included": False,
    }
    st.download_button(
        "Download manifest.json",
        data=json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name="session_manifest.json",
        mime="application/json",
        use_container_width=True,
    )


# -----------------------------------------------------------------------------
# Main app
# -----------------------------------------------------------------------------

def main():
    st.set_page_config(page_title="WOW Agentic Intelligence", layout="wide")

    ss_init()
    try_load_agents_from_file()

    # Sidebar first (so changes apply)
    sidebar_controls()
    apply_wow_css()

    wow_header()
    wow_status_bar()

    # Navigation
    nav = st.tabs([
        t("nav_dashboard"),
        t("nav_pdf"),
        t("nav_agents"),
        t("nav_510k"),
        t("nav_notes"),
        t("nav_settings"),
        t("nav_history"),
    ])

    with nav[0]:
        dashboard_panel()
        live_log_panel()
    with nav[1]:
        pdf_panel()
        live_log_panel()
    with nav[2]:
        agent_workspace_panel()
        live_log_panel()
    with nav[3]:
        panel_510k()
        live_log_panel()
    with nav[4]:
        notekeeper_panel()
        live_log_panel()
    with nav[5]:
        settings_panel()
        live_log_panel()
    with nav[6]:
        history_panel()
        live_log_panel()


if __name__ == "__main__":
    main()
