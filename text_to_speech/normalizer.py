import json, re
from pathlib import Path
from num2words import num2words

PRON_PATH = Path(__file__).parent / "pronunciations.json"
# Acronyms people say as words, so we must NOT spell them letter by letter
SAY_AS_WORD = {"NASA", "ISRO", "UNESCO", "NATO", "LASER", "RADAR"}
CURRENCY = {"₹": "rupees", "$": "dollars", "€": "euros", "£": "pounds"}


def load_pronunciations():
    try:
        return json.loads(PRON_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def _apply(rule, pattern, fn, text, changes, flags=0):
    """Run one regex rule and record every change it makes."""
    def wrapper(m):
        new = fn(m)
        if new != m.group(0):
            changes.append({"rule": rule, "before": m.group(0), "after": new})
        return new
    return re.sub(pattern, wrapper, text, flags=flags)


def _to_words(s):
    s = s.replace(",", "")
    return num2words(float(s)) if "." in s else num2words(int(s))


def normalize(text, pron=None):
    """Returns (cleaned_text, list_of_changes)."""
    pron = load_pronunciations() if pron is None else pron
    changes = []

    # 1. custom pronunciation dictionary
    for word, respelling in pron.items():
        text = _apply("pronunciation", rf"\b{re.escape(word)}\b",
                      lambda m, r=respelling: r, text, changes, re.IGNORECASE)

    # 2. URLs -> just the domain
    text = _apply("url", r"https?://(?:www\.)?([\w.-]+)\S*",
                  lambda m: "link to " + m.group(1).replace(".", " dot "), text, changes)

    # 3. emails
    text = _apply("email", r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+",
                  lambda m: m.group(0).replace("@", " at ").replace(".", " dot "), text, changes)

    # 4. money
    text = _apply("money", r"([₹$€£])\s?(\d[\d,]*(?:\.\d+)?)",
                  lambda m: f"{_to_words(m.group(2))} {CURRENCY[m.group(1)]}", text, changes)

    # 5. percentages
    text = _apply("percent", r"(\d+(?:\.\d+)?)\s?%",
                  lambda m: f"{_to_words(m.group(1))} percent", text, changes)

    # 6. plain numbers
    text = _apply("number", r"\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b|\b\d+(?:\.\d+)?\b",
                  lambda m: _to_words(m.group(0)), text, changes)

    # 7. acronyms -> spelled out letter by letter
    text = _apply("acronym", r"\b[A-Z]{2,6}\b",
                  lambda m: m.group(0) if m.group(0) in SAY_AS_WORD else " ".join(m.group(0)),
                  text, changes)

    return text, changes