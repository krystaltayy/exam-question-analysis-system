c1_keywords = [
    "who", "what", "when", "where", "which", "whose",
    "cite", "define", "describe", "extract", "find",
    "identify", "know", "label", "list", "locate",
    "match", "measure", "memorise", "name",
    "organise", "outline", "present", "pronounce",
    "quote", "recall", "recite", "recognise",
    "record", "recount", "relate", "reproduce",
    "select", "state", "tell", "underline", "write"
]

c2_keywords = [
    "account", "alter", "change", "clarify",
    "classify", "compare", "comprehend", "contrast",
    "convert", "defend", "depict", "describe",
    "discover", "discuss", "distinguish", "estimate",
    "exemplify", "explain", "express", "extend",
    "find", "formulate", "generalise", "give",
    "give examples", "illustrate", "indicate",
    "infer", "interpret", "justify", "locate",
    "manage", "match"
]

def detect_bloom_level(question):
    question = question.lower()

    for keyword in c2_keywords:
        if keyword in question:
            return "C2 - Understand"
        
    for keyword in c1_keywords:
        if keyword in question:
            return "C1 - Remember"
        
    return "No match"

