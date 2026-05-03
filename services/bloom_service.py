def classify_question(text):

    text = text.lower()

    c1_keywords = [
        "cite", "define", "describe", "extract", "find",
        "identify", "know", "label", "list", "locate",
        "match", "measure", "memorise", "name", "organise",
        "outline", "present", "pronounce", "quote", "recall",
        "recite", "recognise", "record", "recount", "relate",
        "reproduce", "select", "state", "tell", "underline",
        "write"
    ]

    c2_keywords = [
        "account", "alter", "change", "clarify", "classify",
        "compare", "comprehend", "contrast", "convert", "defend",
        "depict", "describe", "discover", "discuss", "distinguish",
        "estimate", "exemplify", "explain", "express", "extend",
        "find", "formulate", "generalise", "give", "give examples",
        "illustrate", "indicate", "infer", "interpret", "justify",
        "locate", "manage", "match"
    ]
    for word in c2_keywords:
      if word in text:
        return "C2 - Understand"

    for word in c1_keywords:
     if word in text:
        return "C1 - Remember"

    return "Unknown"