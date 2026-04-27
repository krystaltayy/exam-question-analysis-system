def classify_question(text):
    text = text.lower()

    remember_keywords = ["define", "list", "identify", "state"]
    understand_keywords = ["explain", "describe", "summarize", "discuss"]

    if any(word in text for word in remember_keywords):
        return "C1 - Remember"
    elif any(word in text for word in understand_keywords):
        return "C2 - Understand"
    else:
        return "Unknown"