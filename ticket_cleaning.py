"""Ticket text cleaning rules shared by the exploration and classification notebooks.

Every rule traces to a measurement in `1. Exploration.ipynb` (section "Text cleaning").
"""
import json
import re

# --- Patterns, each traceable to a measurement above -------------------------
PLACEHOLDER_RE = re.compile(r"<[^<>\n]{1,60}>")
HTML_BR_RE = re.compile(r"(?i)<br\s*/?>")
HTML_TAG_RE = re.compile(r"<[^<>\n]{1,40}>")

GREETING_RE = re.compile(
    r"(?i)^\W*(car[oa]s?|prezad[oa]s?|ol[áa]|oi|sauda[çc][õo]es|bom dia|boa tarde|boa noite)"
    r"\b[^,\n]{0,90}[,:\n]")

SIGNOFF_RE = re.compile(
    r"(?i)\n?\s*\b(atenciosamente|cordialmente|atentamente|respeitosamente|"
    r"melhores cumprimentos|abra[çc]os|agradecemos por escolher|obrigad[oa])\b[\s\S]*$")

PLEASANTRY_RES = [
    re.compile(r"(?i)espero que (esta|este|o|a)\b[^.!?]{0,60}(encontre|encontrem)[^.!?]{0,25}bem[.!?]?"),
    re.compile(r"(?i)espero que (voc[êe]s?|o senhor|a senhora)\b[^.!?]{0,40}(esteja|estejam)[^.!?]{0,15}bem[.!?]?"),
    re.compile(r"(?i)aguard(o|ando|amos)[^.!?]{0,45}(resposta|retorno|assist[êe]ncia)[^.!?]{0,25}[.!?]?"),
    re.compile(r"(?i)agrade[çc](o|emos)[^.!?]{0,45}(antecipadamente|aten[çc][ãa]o|assist[êe]ncia)[^.!?]{0,25}[.!?]?"),
    re.compile(r"(?i)obrigad[oa][^.!?]{0,45}(aten[çc][ãa]o|assist[êe]ncia|apoio|suporte|compreens[ãa]o)[^.!?]{0,25}[.!?]?"),
    re.compile(r"(?i)\b(sinta-se [àa] vontade|fique [àa] vontade)\b[^.!?]{0,70}[.!?]?"),
    re.compile(r"(?i)\bpor favor,?\s*(me )?(avise|informe|deixe-me saber)\b[^.!?]{0,70}[.!?]?"),
]

DANGLING_PUNCT_RE = re.compile(r"\s+([.,;:!?])")
REPEAT_PUNCT_RE = re.compile(r"([.,;:])(\s*\1)+")
EMPTY_CLAUSE_RE = re.compile(r"(?<=[.:,])\s*[,;]")

# Only treat a signoff marker as a signoff if it appears late in the document.
# Justified by the positional analysis: the 10th percentile for signoff markers is
# 0.85+, so a 0.60 threshold will not cut a mid-body "obrigado".
SIGNOFF_MIN_POS = 0.60

def unwrap_json_body(text):
    """Ticket 3299 stores its body as a JSON string; recover the prose."""
    stripped = text.strip()
    if not stripped.startswith("{"):
        return text
    try:
        payload = json.loads(stripped)
    except (json.JSONDecodeError, ValueError):
        return text
    return " ".join(v for v in payload.values() if isinstance(v, str))


def tidy_punctuation(text):
    """Repair the orphaned punctuation left behind by removing spans."""
    text = DANGLING_PUNCT_RE.sub(r"\1", text)
    text = REPEAT_PUNCT_RE.sub(r"\1", text)
    text = EMPTY_CLAUSE_RE.sub("", text)
    return re.sub(r"\s+", " ", text).strip(" ,;:")


def clean_body(text):
    """Apply the rules in order: structural, then positional, then phrasal."""
    text = unwrap_json_body(text)
    text = HTML_BR_RE.sub("\n", text)
    text = PLACEHOLDER_RE.sub(" ", text)

    match = SIGNOFF_RE.search(text)
    if match and match.start() / max(len(text), 1) >= SIGNOFF_MIN_POS:
        text = text[:match.start()]

    text = GREETING_RE.sub(" ", text.lstrip())
    for pattern in PLEASANTRY_RES:
        text = pattern.sub(" ", text)
    return tidy_punctuation(text)

def clean_subject(text):
    """Subjects carry no greeting or signoff - only structural noise."""
    return tidy_punctuation(HTML_TAG_RE.sub(" ", text))


def clean_ticket(subject, body):
    """Clean one ticket the way the exploration notebook does for the whole corpus.

    Subject and body are cleaned separately (positional rules only make sense against the
    body's own start and end). A body stripped below 20 characters falls back to a
    structural-only clean so no ticket is ever lost.
    """
    subject = clean_subject(subject or "")
    raw_body = body or ""
    body = clean_body(raw_body)
    if len(body) < 20:
        body = tidy_punctuation(PLACEHOLDER_RE.sub(" ", HTML_BR_RE.sub(" ", unwrap_json_body(raw_body))))
    return body if subject == "" else f"{subject}. {body}"
