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
    excessive_punctuation: bool


class SpamDecisionTree:
    def __init__(self):
        self.HIGH_CONFIDENCE_THRESHOLD = 0.80
        self.MEDIUM_CONFIDENCE_THRESHOLD = 0.60
        self.LOW_CONFIDENCE_THRESHOLD = 0.30

        self.URGENT_WORDS = [
            'urgent', 'immediate', 'action required', 'act now',
            'limited time', 'expire', 'hurry', 'don\'t miss',
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
            'dear customer', 'dear user', 'congratulations you\'ve won'
        ]

    def extract_features(self, email_text: str, nb_confidence: float) -> EmailFeatures:
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
            excessive_punctuation=excessive_punct
        )

    def calculate_spam_score(self, features: EmailFeatures) -> float:
        score = 0.0
        weights = {
            'nb_base': 0.45,
            'keywords': 0.25,
            'formatting': 0.15,
            'links': 0.15
        }

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

        return min(score, 1.0)

    def classify(self, email_text: str, nb_confidence: float) -> Tuple[str, Dict]:
        features = self.extract_features(email_text, nb_confidence)
        spam_score = self.calculate_spam_score(features)

        reasoning = {
            'nb_confidence': nb_confidence,
            'spam_score': spam_score,
            'decision_path': []
        }

        if nb_confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
            reasoning['decision_path'].append('High NB confidence')
            if spam_score >= 0.75:
                reasoning['decision_path'].append('High spam score confirms')
                return 'spam', reasoning
            elif spam_score < 0.4:
                reasoning['decision_path'].append('Low spam score contradicts')
                return 'ham', reasoning
            return 'spam', reasoning

        elif nb_confidence >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            reasoning['decision_path'].append('Medium NB confidence')
            if (features.urgent_words_count + features.money_keywords_count +
                features.suspicious_phrases_count) >= 3:
                reasoning['decision_path'].append('Multiple spam keywords detected')
                return 'spam', reasoning
            if spam_score >= 0.65:
                reasoning['decision_path'].append('Spam score supports classification')
                return 'spam', reasoning
            elif spam_score < 0.45:
                reasoning['decision_path'].append('Spam score suggests ham')
                return 'ham', reasoning
            if features.has_external_links:
                reasoning['decision_path'].append('External links present - likely spam')
                return 'spam', reasoning
            return 'spam', reasoning

        elif nb_confidence >= self.LOW_CONFIDENCE_THRESHOLD:
            reasoning['decision_path'].append('Low NB confidence - rely on features')
            if spam_score >= 0.75:
                reasoning['decision_path'].append('High spam score detected')
                return 'spam', reasoning
            if (features.suspicious_phrases_count >= 2 and features.has_external_links):
                reasoning['decision_path'].append('Phishing pattern detected')
                return 'spam', reasoning

            indicator_count = sum([
                features.urgent_words_count > 0,
                features.money_keywords_count > 0,
                features.capital_ratio > 0.25,
                features.excessive_punctuation
            ])

            if indicator_count >= 3:
                reasoning['decision_path'].append(f'{indicator_count} spam indicators present')
                return 'spam', reasoning
            elif indicator_count <= 1:
                reasoning['decision_path'].append(f'Only {indicator_count} spam indicators')
                return 'ham', reasoning

            if spam_score >= 0.55:
                return 'spam', reasoning
            else:
                return 'ham', reasoning

        else:
            reasoning['decision_path'].append('Very low NB confidence - feature-driven')
            if spam_score >= 0.80:
                reasoning['decision_path'].append('Very high spam score overrides NB')
                return 'spam', reasoning
            if spam_score < 0.35:
                reasoning['decision_path'].append('Low spam score - likely ham')
                return 'ham', reasoning
            if features.suspicious_phrases_count >= 2:
                reasoning['decision_path'].append('Multiple suspicious phrases')
                return 'spam', reasoning
            return 'ham', reasoning


if __name__ == "__main__":
    classifier = SpamDecisionTree()

    test_emails = [
        {
            'text': "CONGRATULATIONS!!! You've WON $1,000,000! Click here NOW to claim your prize before it EXPIRES!!!",
            'nb_conf': 0.92
        },
        {
            'text': "Hi John, Here's the report you requested. Let me know if you need any changes. Thanks, Sarah",
            'nb_conf': 0.15
        },
        {
            'text': "Materials regarding your recent investment Hi Peter, Congratulations on your recent investment. As a shareholder, you're entitled to receive the fund's prospectus which outlines the goals, fees, risks, and management of the fund. You are receiving this notification because you purchased this fund in your individual account.View your documents through the links below.",
            'nb_conf': 0.96
        }
    ]

    for i, email in enumerate(test_emails, 1):
        result, reasoning = classifier.classify(email['text'], email['nb_conf'])
        print(f"\n{'=' * 60}")
        print(f"Email {i}:")
        print(f"Text: {email['text'][:80]}...")
        print(f"NB Confidence: {email['nb_conf']:.2f}")
        print(f"\nClassification: {result.upper()}")
        print(f"Spam Score: {reasoning['spam_score']:.2f}")
        print(f"Decision Path: {' -> '.join(reasoning['decision_path'])}")
