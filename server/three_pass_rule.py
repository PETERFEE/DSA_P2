from collections import deque
import regex as re
import time
import math

def ruleFilter(body, confidence):
    timestamp = time.perf_counter()
    words = body.split()
    spamProbability = 0.0
    urls = [a or b for a, b in re.findall(r"(\bhttps?:\/\/[^\s,)]+)|(\b[-a-zA-Z0-9.\p{L}]+\.[a-zA-Z\p{L}]{2,}\b)", body)]
    if len(urls) > 0 and len(words) < 10:
        spamProbability += 0.2

    for url in urls:
        if url.startswith("http://"):
            index = url[7:].find("/")
            if index != -1:
                url = url[:index + 7]
        elif url.startswith("https://"):
            index = url[8:].find("/")
            if index != -1:
                url = url[:index + 8]
        else:
            index = url.find("/")
            if index != -1:
                url = url[:index]
        if any(ord(char) > 127 for char in url):
            return "SPAM", 1.0, round((1000 * (time.perf_counter() - timestamp)), 2)
        elif any(char.isdigit() for char in url.split('.')[-2].lower()):
            spamProbability += 0.5
        elif url.split('.')[-1].lower() in ('xyz', 'top', 'tk', 'pw', 'tk', 'ga', 'ml', 'work', 'download', 'win', 'zip', 'bar', 'party', 'info', 'ru', 'ws', 'cm'):
            spamProbability += 0.25

    spamWords = {"urgent": 0, "sale": 0, "win": 0, "trial": 0, "guaranteed": 0, "cash": 0, "act": 0, "claim": 0, "hurry": 0, "verify": 0, "congratulations": 0, "income": 0, "investment": 0, "limited": 0}
    spamWeight = {"urgent": 3, "sale": 2, "win": 3, "trial": 1, "guaranteed": 2, "cash": 2, "act": 2, "claim": 3, "hurry": 4, "verify": 1, "congratulations": 1, "income": 1, "investment": 2, "limited": 2}
    cumulative = 0
    maxWeight = sum(spamWeight.values())

    for word in words:
        if word.lower() in spamWords:
            spamWords[word.lower()] += 1

    for word in spamWords.keys():
        cumulative += spamWords[word] * spamWeight[word]

    spamProbability += cumulative / maxWeight
    spamProbability = min(1.0, spamProbability)

    thirdPass = False

    if abs(spamProbability - confidence) >= 0.3 or \
        0.4 <= spamProbability <= 0.6 or 0.4 <= confidence <= 0.6 or \
        spamProbability < 0.4 and confidence > 0.6:
        thirdPass = True

    if not thirdPass:
        if max(spamProbability, confidence) >= 0.5:
            return "SPAM", round(spamProbability, 2), round((1000 * (time.perf_counter() - timestamp)), 2)
        return "HAM", round(spamProbability, 2), round((1000 * (time.perf_counter() - timestamp)), 2)

    spamPhrases = ["win big", "win money", "claim prize", "free money", "easy money",
                    "get paid", "earn money", "double income", "limited time", "limited offer",
                    "order now", "act now", "free trial", "free access", "cancel anytime",
                    "credit score", "save big", "flash sale", "verify account", "click below",
                   "click link", "urgent action", "action required", "suspicious activity", "verify identity",
                   "lose weight", "burn fat", "anti aging", "improve performance", "limited supply",
                   "upgrade now", "free download", "contact support", "final notice", "last chance",
                   "immediate action", "account suspended", "payment required", "critical alert",
                   "important message", "click here", "miss your chance"]
    occurrence = 0
    scale = 0.25 / math.log1p(1)

    window = deque(maxlen = 4)
    for word in words:
        window.append(word.lower())
        setWindow = set(window)
        for phrase in spamPhrases:
            if set(phrase.split()) <= setWindow:
                occurrence += 1
    spamProbability += min(0.9, scale * math.log1p(occurrence))
    spamProbability = min(1.0, spamProbability)

    if spamProbability <= 0.05:
        return "HAM", round(spamProbability, 2), round((1000 * (time.perf_counter() - timestamp)), 2)
    elif confidence >= 0.98:
        return "SPAM", round(max(spamProbability, confidence), 2), round((1000 * (time.perf_counter() - timestamp)), 2)

    if spamProbability >= 0.5 and confidence >= 0.2 or confidence >= 0.8 and spamProbability >= 0.2:
        return "SPAM", round(max(spamProbability, confidence), 2), round((1000 * (time.perf_counter() - timestamp)), 2)
    else:
        return "HAM", round(spamProbability, 2), round((1000 * (time.perf_counter() - timestamp)), 2)


#if __name__ == "__main__":
#    text = "The link in the description "
#    label, probability, runtime = ruleFilter(text, 0.8)
#    print(f"Label: {label}", f"\nProbability: {probability}", f"\nRuntime: {runtime}ms")