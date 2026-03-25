import os
import re
import json
import time
import pandas as pd
import streamlit as st
import pdfplumber
import docx
import anthropic
from openai import OpenAI
from google import genai as google_genai
from dotenv import load_dotenv

load_dotenv()

# ── Constants ──────────────────────────────────────────────────────────────────
CLAUDE_MODEL = "claude-sonnet-4-6"
GPT_MODEL = "gpt-4o"
GPT_54_MODEL = "gpt-5.4"
GEMINI_FLASH_MODEL = "gemini-2.5-flash"
GEMINI_PRO_MODEL = "gemini-2.5-pro"
GEMINI_31_PRO_MODEL = "gemini-3.1-pro-preview"
MAX_RESUME_CHARS = 24_000
MAX_TOKENS_RESPONSE = 512

MODEL_OPTIONS = {
    "GPT-5.4": "openai_54",
    "GPT-4o": "openai",
    "Claude (claude-sonnet-4-6)": "claude",
    "Gemini 3.1 Pro": "gemini_31_pro",
    "Gemini 2.5 Pro": "gemini_pro",
    "Gemini 2.5 Flash": "gemini_flash",
}

API_KEY_MAP = {
    "claude": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "openai_54": "OPENAI_API_KEY",
    "gemini_31_pro": "GOOGLE_API_KEY",
    "gemini_pro": "GOOGLE_API_KEY",
    "gemini_flash": "GOOGLE_API_KEY",
}

SYSTEM_PROMPT = """You are an expert technical recruiter and hiring manager.
You will receive a job description and a resume, and you must evaluate how well
the candidate matches the role.

You MUST respond with valid JSON only. No prose before or after the JSON.
Use exactly this schema:

{
  "candidate_name": "<full name of the candidate, or 'Unknown' if not found>",
  "match_score": <integer 1-10>,
  "key_strengths": [<string>, ...],
  "key_gaps": [<string>, ...],
  "summary": "<one sentence summary of the candidate>",
  "university": "<university name, or 'Not listed' if absent>",
  "major": "<degree and field of study, e.g. 'B.S. Computer Science', or 'Not listed' if absent>"
}

Scoring rubric — blended skills + character system (total 10 points):

=== PART A: SKILLS SCORE (0-7 points) ===

STEP 1 — Base score from REQUIRED skills (1-4 points):
   4: Meets 80%+ of required skills
   3: Meets 60-79% of required skills
   2: Meets 40-59% of required skills
   1: Meets <40% of required skills, completely different field, or unreadable resume

STEP 2 — Bonus from PREFERRED/nice-to-have skills (only if base >= 2):
   Each preferred skill present adds +1, up to a maximum of +3 bonus points.
   Preferred skills have NO effect if base score is 1.

Skills score = base + preferred bonus (max 7).

=== PART B: CHARACTER SCORE (0-3 points) ===

Look for evidence of personality, initiative, and moldability beyond academics:

   3 points: Two or more STRONG signals — military service, sustained volunteer work (semester+),
             elected club officer/team captain, meaningful personal project driven by passion
   2 points: One strong signal OR two minor signals — club member, one-time volunteer,
             hackathon participant, part-time job during school, casual hobby mentioned
   1 point:  One minor mention — e.g. "enjoys hiking", one club listed with no role
   0 points: Nothing beyond academics and internships; no extracurriculars or personal interests

Strong signals show the candidate is coachable, disciplined, and eager to grow.
Military experience always counts as a strong signal regardless of field.

=== STEP 3 — FINAL SCORE ===

Final score = Skills score + Character score, capped at 10.

Examples:
   Skills base=4 (strong), preferred +3, character=3 (veteran + volunteer) = 7+3 = 10
   Skills base=4 (strong), preferred +2, character=0 (no activities)       = 6+0 = 6
   Skills base=3 (partial), preferred +1, character=3 (club officer + hobby) = 4+3 = 7
   Skills base=2 (weak),    preferred +0, character=3 (military veteran)    = 2+3 = 5
   Skills base=1 (poor),    preferred +0, character=2 (volunteer)           = 1+2 = 3

Apply mechanically. Do not adjust scores based on subjective impressions beyond the rubric.
"""

USER_TEMPLATE = """JOB DESCRIPTION:
{job_description}

---

RESUME (filename: {filename}):
{resume_text}

---

Evaluate this resume against the job description and respond with JSON only."""


# ── Helper functions ───────────────────────────────────────────────────────────

def extract_text_from_pdf(uploaded_file) -> str | None:
    """Extract full text from a PDF UploadedFile. Returns None on failure."""
    try:
        text_parts = []
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text.strip())
        if not text_parts:
            return None
        full_text = "\n\n--- PAGE BREAK ---\n\n".join(text_parts)
        return full_text[:MAX_RESUME_CHARS]
    except Exception:
        return None


def extract_text_from_docx(uploaded_file) -> str | None:
    """Extract full text from a DOCX UploadedFile. Returns None on failure."""
    try:
        doc = docx.Document(uploaded_file)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        if not paragraphs:
            return None
        return "\n\n".join(paragraphs)[:MAX_RESUME_CHARS]
    except Exception:
        return None


def extract_text(uploaded_file) -> str | None:
    """Route to correct extractor based on file extension."""
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    if name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    return None


def _page_has_contact_header(page_text: str) -> bool:
    """Check if a page starts with typical resume contact info.

    Counts distinct contact signals in the first 500 characters and requires
    at least 2.  This catches resumes that use hyperlink placeholders
    (e.g. 'Email | LinkedIn') instead of showing the raw address.
    """
    header = page_text[:500]
    signals = 0
    if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', header):
        signals += 1  # raw email address
    if re.search(r'[\+]?[\d\-\(\)\s]{7,}', header):
        signals += 1  # phone number
    if re.search(r'\bEmail\b', header, re.IGNORECASE):
        signals += 1  # "Email" as hyperlink placeholder
    if re.search(r'linkedin', header, re.IGNORECASE):
        signals += 1  # LinkedIn profile link or word
    if re.search(r'github', header, re.IGNORECASE):
        signals += 1  # GitHub profile link or word
    return signals >= 2


def _extract_contact_id(page_text: str) -> tuple[str | None, str | None]:
    """Extract the first email and first phone from a page header.

    Returns (email_or_None, phone_digits_or_None) for identity matching.
    """
    header = page_text[:500]
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', header)
    phone_match = re.search(r'[\+]?[\d\-\(\)\s]{7,}', header)
    email = email_match.group(0).lower() if email_match else None
    phone = re.sub(r'\D', '', phone_match.group(0)) if phone_match else None
    return email, phone


def split_combined_pdf(uploaded_file) -> list[tuple[str, str]]:
    """Split a combined PDF into individual resume texts by detecting contact-info boundaries.

    Each page whose header contains contact signals is treated as the start of
    a new resume.  Pages without are continuations.  After initial splitting,
    groups that share the same name AND (email or phone) are merged back
    together (handles resumes that repeat their header on every page).

    Returns a list of (label, text) tuples.
    """
    base_name = uploaded_file.name
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            pages_text: list[str | None] = []
            for page in pdf.pages:
                raw = page.extract_text()
                pages_text.append(raw.strip() if raw else None)
    except Exception:
        return []

    # Group pages into resume chunks based on contact-info detection
    groups: list[list[int]] = []  # each item is a list of page indices
    for i, text in enumerate(pages_text):
        if text is None:
            continue  # skip blank pages
        if i == 0 or _page_has_contact_header(text):
            groups.append([i])  # start a new resume
        else:
            if groups:
                groups[-1].append(i)
            else:
                groups.append([i])  # safety fallback

    # Merge groups that share the same identity (name + email or phone)
    def _group_identity(page_indices: list[int]) -> tuple[str, str | None, str | None]:
        first_text = pages_text[page_indices[0]] or ""
        name = first_text.split("\n")[0].strip().lower()
        email, phone = _extract_contact_id(first_text)
        return name, email, phone

    merged: list[list[int]] = []
    for group in groups:
        name, email, phone = _group_identity(group)
        # Try to find an existing merged group with matching identity
        found = False
        for existing in merged:
            ename, eemail, ephone = _group_identity(existing)
            if name and name == ename:
                if (email and email == eemail) or (phone and phone == ephone):
                    existing.extend(group)
                    found = True
                    break
        if not found:
            merged.append(group)

    entries: list[tuple[str, str]] = []
    for resume_num, page_indices in enumerate(merged, start=1):
        text_parts = [pages_text[idx] for idx in page_indices if pages_text[idx]]
        if not text_parts:
            continue

        full_text = "\n\n--- PAGE BREAK ---\n\n".join(text_parts)
        full_text = full_text[:MAX_RESUME_CHARS]

        first = page_indices[0] + 1
        last = page_indices[-1] + 1
        if first == last:
            label = f"{base_name} — Resume #{resume_num} (page {first})"
        else:
            label = f"{base_name} — Resume #{resume_num} (pages {first}-{last})"

        entries.append((label, full_text))

    return entries


def _parse_json(raw: str) -> dict:
    """Strip markdown fences and parse JSON."""
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def analyze_resume_claude(
    client: anthropic.Anthropic,
    job_description: str,
    resume_text: str,
    filename: str,
) -> dict | None:
    prompt = USER_TEMPLATE.format(
        job_description=job_description,
        filename=filename,
        resume_text=resume_text,
    )
    for attempt in range(2):
        try:
            message = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=MAX_TOKENS_RESPONSE,
                temperature=0,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            return _parse_json(message.content[0].text)
        except json.JSONDecodeError:
            if attempt == 0:
                continue
            return None
        except anthropic.RateLimitError:
            time.sleep(10)
            if attempt == 0:
                continue
            return None
        except Exception as e:
            return {"_error": str(e)}
    return None


def analyze_resume_openai(
    client: OpenAI,
    job_description: str,
    resume_text: str,
    filename: str,
    model: str = GPT_MODEL,
) -> dict | None:
    prompt = USER_TEMPLATE.format(
        job_description=job_description,
        filename=filename,
        resume_text=resume_text,
    )
    for attempt in range(2):
        try:
            params = dict(
                model=model,
                temperature=0,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            if model == GPT_54_MODEL:
                params["max_completion_tokens"] = MAX_TOKENS_RESPONSE
            else:
                params["max_tokens"] = MAX_TOKENS_RESPONSE
            response = client.chat.completions.create(**params)
            return _parse_json(response.choices[0].message.content)
        except json.JSONDecodeError:
            if attempt == 0:
                continue
            return None
        except Exception as e:
            return {"_error": str(e)}
    return None


def analyze_resume_gemini(
    client,
    job_description: str,
    resume_text: str,
    filename: str,
    model: str = GEMINI_FLASH_MODEL,
) -> dict | None:
    prompt = SYSTEM_PROMPT + "\n\n" + USER_TEMPLATE.format(
        job_description=job_description,
        filename=filename,
        resume_text=resume_text,
    )
    for attempt in range(2):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )
            return _parse_json(response.text)
        except json.JSONDecodeError:
            if attempt == 0:
                continue
            return None
        except Exception as e:
            return {"_error": str(e)}
    return None


def analyze_resume(client, provider: str, job_description: str, resume_text: str, filename: str) -> dict | None:
    if provider == "claude":
        return analyze_resume_claude(client, job_description, resume_text, filename)
    if provider == "openai_54":
        return analyze_resume_openai(client, job_description, resume_text, filename, model=GPT_54_MODEL)
    if provider == "gemini_31_pro":
        return analyze_resume_gemini(client, job_description, resume_text, filename, model=GEMINI_31_PRO_MODEL)
    if provider == "gemini_pro":
        return analyze_resume_gemini(client, job_description, resume_text, filename, model=GEMINI_PRO_MODEL)
    if provider == "gemini_flash":
        return analyze_resume_gemini(client, job_description, resume_text, filename, model=GEMINI_FLASH_MODEL)
    return analyze_resume_openai(client, job_description, resume_text, filename)


def build_dataframe(results: list[dict]) -> pd.DataFrame:
    rows = []
    for rank, r in enumerate(results, start=1):
        rows.append(
            {
                "Rank": rank,
                "Name": r.get("candidate_name", "Unknown"),
                "Score (1-10)": r["match_score"],
                "University": r.get("university", "Not listed"),
                "Major": r.get("major", "Not listed"),
                "Key Strengths": " | ".join(r.get("key_strengths", [])),
                "Key Gaps": " | ".join(r.get("key_gaps", [])),
                "Summary": r.get("summary", ""),
                "Filename": r["filename"],
            }
        )
    return pd.DataFrame(rows)


# ── Streamlit UI ───────────────────────────────────────────────────────────────

def main():
    st.set_page_config(page_title="Resume Screener", layout="wide")
    st.title("Resume Screener")

    # ── Sidebar: model selection + API key status ──
    st.sidebar.header("Settings")
    model_label = st.sidebar.selectbox("AI Model", list(MODEL_OPTIONS.keys()))
    provider = MODEL_OPTIONS[model_label]
    num_to_pick = st.sidebar.number_input(
        "How many candidates to pick",
        min_value=1,
        max_value=100,
        value=10,
        step=1,
        help="Number of top candidates to highlight in the results.",
    )

    key_name = API_KEY_MAP[provider]
    api_key = os.environ.get(key_name)
    if not api_key:
        try:
            api_key = st.secrets.get(key_name)
        except Exception:
            api_key = None

    if not api_key:
        st.sidebar.error(f"{key_name} not set.")
        st.error(
            f"{key_name} environment variable is not set. "
            f"Set it in your shell or add it to a .env file alongside app.py."
        )
        st.stop()
    else:
        st.sidebar.success(f"{key_name} loaded.")

    st.caption(f"Using: {model_label}")

    # ── Inputs ──
    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded_files = st.file_uploader(
            "Upload Resumes (PDF or DOCX)",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            help="Select one or more PDF or Word resume files.",
        )
        is_combined_pdf = st.checkbox(
            "This is a combined PDF (multiple resumes in one file)",
            value=False,
            help="Check this if you uploaded a single PDF containing multiple resumes. "
                 "The app will auto-detect where each resume starts.",
        )
    with col2:
        st.markdown("**Job Description / Position Prompt**")
        jd_file = st.file_uploader(
            "Upload job description (PDF or DOCX) — optional",
            type=["pdf", "docx"],
            accept_multiple_files=False,
            key="jd_file",
        )
        jd_text_input = st.text_area(
            "Or paste job description here",
            height=220,
            placeholder=(
                "Paste the full job description here, including required skills, "
                "experience level, and responsibilities..."
            ),
        )
        # File upload takes priority; fall back to text area
        if jd_file is not None:
            job_description = extract_text(jd_file) or ""
            if job_description:
                st.success(f"Loaded job description from {jd_file.name}")
            else:
                st.error(f"Could not extract text from {jd_file.name}")
                job_description = jd_text_input
        else:
            job_description = jd_text_input

    inputs_ready = bool(uploaded_files) and bool(job_description.strip())
    run_button = st.button("Screen Resumes", disabled=not inputs_ready, type="primary")

    if not inputs_ready and not run_button:
        if not uploaded_files:
            st.info("Upload one or more resumes to get started.")
        elif not job_description.strip():
            st.info("Enter or upload a job description to continue.")

    if run_button:
        # ── Processing ──
        if provider == "claude":
            client = anthropic.Anthropic(api_key=api_key)
        elif provider in ("gemini_31_pro", "gemini_pro", "gemini_flash"):
            client = google_genai.Client(api_key=api_key)
        else:
            client = OpenAI(api_key=api_key)

        # ── Phase 1: Build resume entry list ──
        resume_entries: list[tuple[str, str]] = []
        failures = []

        if is_combined_pdf:
            if len(uploaded_files) != 1 or not uploaded_files[0].name.lower().endswith(".pdf"):
                st.warning(
                    "Combined PDF mode works with a single PDF file. "
                    "Processing each file as a separate resume instead."
                )
                is_combined_pdf = False

        if is_combined_pdf:
            entries = split_combined_pdf(uploaded_files[0])
            if not entries:
                failures.append(f"{uploaded_files[0].name} (could not split combined PDF)")
            else:
                resume_entries = entries
                st.info(f"Split combined PDF into {len(entries)} resume(s).")
        else:
            for uploaded_file in uploaded_files:
                text = extract_text(uploaded_file)
                if text:
                    resume_entries.append((uploaded_file.name, text))
                else:
                    failures.append(f"{uploaded_file.name} (could not extract text)")

        # ── Phase 2: Score each entry ──
        results = []
        total = len(resume_entries)
        progress_bar = st.progress(0, text="Starting...")

        for i, (label, resume_text) in enumerate(resume_entries):
            progress_bar.progress(
                i / total if total > 0 else 0,
                text=f"Analyzing {label} ({i + 1}/{total})...",
            )

            analysis = analyze_resume(client, provider, job_description, resume_text, label)
            if analysis and "_error" not in analysis:
                analysis["filename"] = label
                results.append(analysis)
            else:
                error_msg = analysis.get("_error", "unknown error") if analysis else "no response"
                failures.append(f"{label}: {error_msg}")

        progress_bar.progress(1.0, text="Done.")

        if failures:
            st.warning(
                f"Could not process {len(failures)} file(s):\n"
                + "\n".join(f"- {f}" for f in failures)
            )

        if not results:
            st.error("No resumes were successfully analyzed.")
            return

        results.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        st.session_state["screening_results"] = results

    # ── Results (persisted across reruns) ──
    results = st.session_state.get("screening_results")
    if results:
        top_n = results[:num_to_pick]

        st.success(f"Screened {len(results)} resume(s). Showing top {len(top_n)} pick(s).")

        df_display = build_dataframe(top_n)
        st.dataframe(df_display, width="stretch", hide_index=True)

        df_all = build_dataframe(results)
        csv = df_all.to_csv(index=False)
        st.download_button(
            label=f"Download All {len(results)} Results as CSV",
            data=csv,
            file_name="screening_results.csv",
            mime="text/csv",
        )

        # ── Detail cards ──
        st.divider()
        st.subheader("Detailed Breakdown")
        for rank, r in enumerate(top_n, start=1):
            score = r.get("match_score", "N/A")
            name = r.get("candidate_name", "Unknown")
            with st.expander(f"#{rank} — {name} — Score: {score}/10"):
                st.write("**Summary:**", r.get("summary", ""))
                st.write("**University:**", r.get("university", "Not listed"))
                st.write("**Major:**", r.get("major", "Not listed"))

                strengths = r.get("key_strengths", [])
                if strengths:
                    st.write("**Key Strengths:**")
                    for s in strengths:
                        st.write(f"- {s}")

                gaps = r.get("key_gaps", [])
                if gaps:
                    st.write("**Key Gaps:**")
                    for g in gaps:
                        st.write(f"- {g}")


if __name__ == "__main__":
    main()
