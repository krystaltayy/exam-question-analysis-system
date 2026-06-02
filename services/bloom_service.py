c1_keywords = [
    "who", "what", "when", "where", "which", "whose",
    "cite", "define", "describe", "extract", "find",
    "identify", "know", "label", "list", "locate",
    "match", "measure", "memorise", "memorize", "name",
    "organise", "outline", "present", "pronounce",
    "quote", "recall", "recite", "recognise", "recognize",
    "record", "recount", "relate", "repeat",
    "reproduce", "retrieve", "select", "show",
    "state", "tabulate", "tell", "trace",
    "underline", "write", "draw", "read",
    "indicate", "point out", "arrange", "choose"
]

c2_keywords = [
    "why", "how", "account", "alter", "change",
    "clarify", "classify", "compare", "comprehend",
    "contrast", "convert", "defend", "depict",
    "describe", "discover", "discuss", "distinguish",
    "differentiate", "estimate", "exemplify",
    "explain", "express", "extend", "extrapolate",
    "find", "formulate", "generalise", "generalize",
    "give", "give examples", "give an example of",
    "illustrate", "indicate", "infer", "interpret",
    "justify", "locate", "manage", "match",
    "paraphrase", "predict", "recognize",
    "relate", "rephrase", "report", "restate",
    "rewrite", "review", "select", "summarize",
    "translate", "associate", "demonstrate",
    "what would happen if", "in your own words"
]

def classify_question(text):
    text = text.lower()

    for word in c2_keywords:
        if word in text:
            return "C2 - Understand"

    for word in c1_keywords:
        if word in text:
            return "C1 - Remember"

    return "Unknown"