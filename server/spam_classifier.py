import re
from typing import Dict, Tuple
from dataclasses import dataclass

@dataclass()
class EmailFeatures:
    nb_confidence: float
    message_length: int
    capital_ratio: float
    symbol_ratio: float
    number_ratio: float
    url_count: int
    urgent_words_count: int
    money_keywords_count: int
    suspicious_phrases_count: int
    has_external_links: bool
    recipient_name_present: bool
    excessive_punctuation: bool


class SpamDecisionTree:
    def __init__(self):
        self.HIGH_CONFIDENCE_THRESHOLD = 0.80
        self.MEDIUM_CONFIDENCE_THRESHOLD = 0.60
        self.LOW_CONFIDENCE_THRESHOLD = 0.30

        self.URGENT_WORDS = [
            'urgent', 'immediate', 'action required', 'act now',
            'limited time', 'expire', 'hurry', "don't miss",
            'last chance', 'today only'
        ]
        self.MONEY_KEYWORDS = [
            'free money', 'cash bonus', 'prize', 'winner', 'claim',
            'million dollars', '$$$', 'income', 'earn money',
            'investment opportunity', 'risk-free', 'guarantee'
        ]
        self.SUSPICIOUS_PHRASES = [
            'click here', 'verify your account', 'confirm your identity',
            'update your information', 'suspended account', 'unusual activity',
            'dear customer', 'dear user', "congratulations you've won"
        ]

    def extract_features(self, email_text: str, nb_confidence: float, has_recipient_name: bool = False) -> EmailFeatures:
        text_lower = email_text.lower()
        text_length = len(email_text)

        capital_count = sum(1 for c in email_text if c.isupper())
        symbol_count = sum(1 for c in email_text if c in '!@#$%^&*()_+={}[]|\\:;"<>?,.')
        number_count = sum(1 for c in email_text if c.isdigit())

        capital_ratio = capital_count / text_length if text_length > 0 else 0
        symbol_ratio = symbol_count / text_length if text_length > 0 else 0
        number_ratio = number_count / text_length if text_length > 0 else 0

        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        url_count = len(re.findall(url_pattern, email_text))
        has_external_links = url_count > 0 or 'click here' in text_lower

        urgent_count = sum(1 for word in self.URGENT_WORDS if word in text_lower)
        money_count = sum(1 for word in self.MONEY_KEYWORDS if word in text_lower)
        suspicious_count = sum(1 for phrase in self.SUSPICIOUS_PHRASES if phrase in text_lower)
        excessive_punct = bool(re.search(r'[!?]{3,}', email_text))

        return EmailFeatures(
            nb_confidence=nb_confidence,
            message_length=text_length,
            capital_ratio=capital_ratio,
            symbol_ratio=symbol_ratio,
            number_ratio=number_ratio,
            url_count=url_count,
            urgent_words_count=urgent_count,
            money_keywords_count=money_count,
            suspicious_phrases_count=suspicious_count,
            has_external_links=has_external_links,
            recipient_name_present=has_recipient_name,
            excessive_punctuation=excessive_punct
        )

    def calculate_spam_score(self, f: EmailFeatures) -> float:
        score = 0.0
        w = {'nb_base': 0.40, 'keywords': 0.20, 'formatting': 0.15, 'links': 0.15, 'personalization': 0.10}
        score += f.nb_confidence * w['nb_base']

        keyword_score = min(
            (f.urgent_words_count * 0.2) + (f.money_keywords_count * 0.25) + (f.suspicious_phrases_count * 0.3), 1.0
        )
        score += keyword_score * w['keywords']

        format_score = 0
        if f.capital_ratio > 0.3: format_score += 0.4
        if f.symbol_ratio > 0.15: format_score += 0.3
        if f.excessive_punctuation: format_score += 0.3
        score += min(format_score, 1.0) * w['formatting']

        link_score = 0
        if f.url_count > 3: link_score += 0.6
        elif f.url_count > 0: link_score += 0.3
        if f.has_external_links and f.urgent_words_count > 0: link_score += 0.4
        score += min(link_score, 1.0) * w['links']

        if not f.recipient_name_present:
            score += (0.7 if f.suspicious_phrases_count > 0 else 0.3) * w['personalization']

        return min(score, 1.0)

    def classify(self, text: str, nb_conf: float, has_name: bool = False) -> Tuple[str, float, Dict]:
        f = self.extract_features(text, nb_conf, has_name)
        s = self.calculate_spam_score(f)
        r = {'nb_confidence': nb_conf, 'spam_score': s, 'decision_path': []}

        if nb_conf >= 0.8:
            r['decision_path'].append('High NB confidence')
            if s >= 0.75:
                r['decision_path'].append('High spam score confirms')
                return 'spam', 0.95, r
            elif s < 0.4:
                r['decision_path'].append('Low spam score contradicts')
                return 'ham', 0.70, r
            return 'spam', 0.85, r

        elif nb_conf >= 0.6:
            r['decision_path'].append('Medium-high NB confidence')
            if (f.urgent_words_count + f.money_keywords_count + f.suspicious_phrases_count) >= 3:
                r['decision_path'].append('Multiple spam keywords')
                return 'spam', 0.80, r
            if s >= 0.65:
                r['decision_path'].append('Spam score supports classification')
                return 'spam', 0.75, r
            elif s < 0.45:
                r['decision_path'].append('Spam score suggests ham')
                return 'ham', 0.65, r
            if f.has_external_links and not f.recipient_name_present:
                r['decision_path'].append('Generic message with links')
                return 'spam', 0.70, r
            return 'spam', 0.60, r

        elif nb_conf >= 0.3:
            r['decision_path'].append('Low-medium NB confidence')
            if s >= 0.75:
                r['decision_path'].append('High spam score detected')
                return 'spam', 0.70, r
            if f.suspicious_phrases_count >= 2 and f.has_external_links:
                r['decision_path'].append('Phishing pattern detected')
                return 'spam', 0.75, r
            count = sum([
                f.urgent_words_count > 0, f.money_keywords_count > 0,
                f.capital_ratio > 0.25, f.excessive_punctuation, not f.recipient_name_present
            ])
            if count >= 3:
                r['decision_path'].append(f'{count} spam indicators')
                return 'spam', 0.65, r
            elif count <= 1:
                r['decision_path'].append(f'Only {count} spam indicators')
                return 'ham', 0.60, r
            return ('spam' if s >= 0.55 else 'ham'), 0.55, r

        else:
            r['decision_path'].append('Low NB confidence')
            if s >= 0.80:
                r['decision_path'].append('Very high spam score overrides NB')
                return 'spam', 0.65, r
            if s < 0.35:
                r['decision_path'].append('Low spam score - likely ham')
                return 'ham', 0.75, r
            if f.suspicious_phrases_count >= 2:
                r['decision_path'].append('Multiple suspicious phrases')
                return 'spam', 0.60, r
            return 'ham', 0.70, r


#  Helper for Flask
def classify_spam(email_text: str, nb_confidence: float, has_recipient_name: bool):
    classifier = SpamDecisionTree()
    return classifier.classify(email_text, nb_confidence, has_recipient_name)
