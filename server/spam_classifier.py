# spam_classifier.py
import re
from typing import Dict, Tuple
from dataclasses import dataclass
import time

@dataclass
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

    def extract_features(self, email_text: str, nb_confidence: float,
                         has_recipient_name: bool = False) -> EmailFeatures:
        text_lower = email_text.lower()
        text_length = len(email_text)

        capital_count = sum(1 for c in email_text if c.isupper())
        capital_ratio = capital_count / text_length if text_length > 0 else 0

        symbol_count = sum(1 for c in email_text if c in '!@#$%^&*()_+={}[]|\\:;"<>?,.')
        symbol_ratio = symbol_count / text_length if text_length > 0 else 0

        number_count = sum(1 for c in email_text if c.isdigit())
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

    def calculate_spam_score(self, features: EmailFeatures) -> float:
        score = 0.0
        weights = {'nb_base': 0.40, 'keywords': 0.20, 'formatting': 0.15,
                   'links': 0.15, 'personalization': 0.10}

        score += features.nb_confidence * weights['nb_base']

        keyword_score = 0
        if features.urgent_words_count > 0:
            keyword_score += min(features.urgent_words_count * 0.2, 0.4)
        if features.money_keywords_count > 0:
            keyword_score += min(features.money_keywords_count * 0.25, 0.4)
        if features.suspicious_phrases_count > 0:
            keyword_score += min(features.suspicious_phrases_count * 0.3, 0.5)
        score += min(keyword_score, 1.0) * weights['keywords']

        format_score = 0
        if features.capital_ratio > 0.3:
            format_score += 0.4
        if features.symbol_ratio > 0.15:
            format_score += 0.3
        if features.excessive_punctuation:
            format_score += 0.3
        score += min(format_score, 1.0) * weights['formatting']

        link_score = 0
        if features.url_count > 3:
            link_score += 0.6
        elif features.url_count > 0:
            link_score += 0.3
        if features.has_external_links and features.urgent_words_count > 0:
            link_score += 0.4
        score += min(link_score, 1.0) * weights['links']

        if not features.recipient_name_present:
            if features.suspicious_phrases_count > 0:
                score += 0.7 * weights['personalization']
            else:
                score += 0.3 * weights['personalization']

        return min(score, 1.0)

    def classify(self, email_text: str, nb_confidence: float,
                 has_recipient_name: bool = False) -> Tuple[str, float, Dict]:
        """
        Accepts a Naive Bayes confidence score from predict.py
        and generates a final spam classification, score, and reasoning.
        """
        # Ensure nb_confidence is a Python float
        nb_confidence = float(nb_confidence)

        features = self.extract_features(email_text, nb_confidence, has_recipient_name)
        spam_score = self.calculate_spam_score(features)

        reasoning = {
            'nb_confidence': nb_confidence,
            'spam_score': spam_score,
            'features': features,
            'decision_path': []
        }

        # Simple rule-based decision path
        if nb_confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
            reasoning['decision_path'].append('High NB confidence')
            if spam_score >= 0.75:
                reasoning['decision_path'].append('High spam score confirms')
                return 'spam', spam_score, reasoning
            else:
                reasoning['decision_path'].append('Moderate spam score')
                return 'spam', spam_score, reasoning
        elif nb_confidence >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            reasoning['decision_path'].append('Medium NB confidence')
            if spam_score >= 0.6:
                reasoning['decision_path'].append('Spam score supports spam')
                return 'spam', spam_score, reasoning
            else:
                reasoning['decision_path'].append('Spam score low - likely ham')
                return 'ham', spam_score, reasoning
        else:
            reasoning['decision_path'].append('Low NB confidence')
            if spam_score >= 0.7:
                reasoning['decision_path'].append('Spam score high - classify as spam')
                return 'spam', spam_score, reasoning
            else:
                reasoning['decision_path'].append('Spam score low - classify as ham')
                return 'ham', spam_score, reasoning

# Utility function to be called from server.py
def classify_email(email_text: str, nb_confidence: float, has_name: bool = False):
    start_time = time.perf_counter()  # Start the timer
    classifier = SpamDecisionTree()
    classification, spam_score, reasoning = classifier.classify(email_text, nb_confidence, has_recipient_name=has_name)
    end_time = time.perf_counter()  # Stop the timer
    elapsed_time = end_time - start_time
    return classification, spam_score, reasoning, elapsed_time
