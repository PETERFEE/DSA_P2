
import re
from typing import Dict, Tuple
from dataclasses import dataclass

@dataclass()
class EmailFeatures:
    #Email features, ways we will classify
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
#tree will split depending on high,medium,low, based off the model it will run through prior

    def __init__(self):
        #percentage for which branch the email will go through
        self.HIGH_CONFIDENCE_THRESHOLD = 0.80
        self.MEDIUM_CONFIDENCE_THRESHOLD = 0.60
        self.LOW_CONFIDENCE_THRESHOLD = 0.30

        # indicator word
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

    def extract_features(self, email_text: str, nb_confidence: float,
                         has_recipient_name: bool = False) -> EmailFeatures:
    #extract email text

        text_lower = email_text.lower()
        text_length = len(email_text)

        # Character ratios
        capital_count = sum(1 for c in email_text if c.isupper())
        capital_ratio = capital_count / text_length if text_length > 0 else 0

        symbol_count = sum(1 for c in email_text if c in '!@#$%^&*()_+={}[]|\\:;"<>?,.')
        symbol_ratio = symbol_count / text_length if text_length > 0 else 0

        number_count = sum(1 for c in email_text if c.isdigit())
        number_ratio = number_count / text_length if text_length > 0 else 0

        #Dectect URL
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        url_count = len(re.findall(url_pattern, email_text))

        #search for any external links
        has_external_links = url_count > 0 or 'click here' in text_lower

        # # of spam words
        urgent_count = sum(1 for word in self.URGENT_WORDS if word in text_lower)
        money_count = sum(1 for word in self.MONEY_KEYWORDS if word in text_lower)
        suspicious_count = sum(1 for phrase in self.SUSPICIOUS_PHRASES if phrase in text_lower)

        # lots of punctuation like !!!
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
        #score from 0 ham(not spam) to 1 (spam
        score = 0.0

        #how calculation is made, each section is weigthed
        weights = {
            'nb_base': 0.40,
            'keywords': 0.20,
            'formatting': 0.15,
            'links': 0.15,
            'personalization': 0.10
        }

        #Score received from model
        score += features.nb_confidence * weights['nb_base']

        #Keyword indications
        keyword_score = 0
        if features.urgent_words_count > 0:
            keyword_score += min(features.urgent_words_count * 0.2, 0.4)
        if features.money_keywords_count > 0:
            keyword_score += min(features.money_keywords_count * 0.25, 0.4)
        if features.suspicious_phrases_count > 0:
            keyword_score += min(features.suspicious_phrases_count * 0.3, 0.5)
        score += min(keyword_score, 1.0) * weights['keywords']

        #issues with formatting such as lots of capitals or lots of symbols
        format_score = 0
        if features.capital_ratio > 0.3:  # if more than 30% capitals
            format_score += 0.4
        if features.symbol_ratio > 0.15:  # if more than 15% symbols
            format_score += 0.3
        if features.excessive_punctuation:
            format_score += 0.3
        score += min(format_score, 1.0) * weights['formatting']

        # link indiacations (could be a phishing attempt)
        link_score = 0
        if features.url_count > 3:
            link_score += 0.6
        elif features.url_count > 0:
            link_score += 0.3
        if features.has_external_links and features.urgent_words_count > 0:
            link_score += 0.4  # Links + urgency = phishing risk
        score += min(link_score, 1.0) * weights['links']

        # Less names(therefore less personalized aka more likely spam(
        if not features.recipient_name_present:
            if features.suspicious_phrases_count > 0:
                score += 0.7 * weights['personalization']
            else:
                score += 0.3 * weights['personalization']

        return min(score, 1.0)

    def classify(self, email_text: str, nb_confidence: float,
                 has_recipient_name: bool = False) -> Tuple[str, float, Dict]:

        #Main classification method using decision tree method
        #Returns: 1)classification: 'spam' or 'ham' 2) confidence: float 0-1 3) reasoning: dict with decision path



        features = self.extract_features(email_text, nb_confidence, has_recipient_name)
        spam_score = self.calculate_spam_score(features)

        reasoning = {
            'nb_confidence': nb_confidence,
            'spam_score': spam_score,
            'decision_path': []
        }



        # 1st Branch for high NB confidence (more than 80%)
        if nb_confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
            reasoning['decision_path'].append('High NB confidence')
            if spam_score >= 0.75:
                reasoning['decision_path'].append('High spam score confirms')
                return 'spam', 0.95, reasoning
            elif spam_score < 0.4:
                reasoning['decision_path'].append('Low spam score contradicts - checking features')
                if features.urgent_words_count == 0 and features.money_keywords_count == 0:
                    return 'ham', 0.70, reasoning
            return 'spam', 0.85, reasoning

        #2nd Branch for medium NB confidence (60% to 80%)
        elif nb_confidence >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            reasoning['decision_path'].append('Medium-high NB confidence')

            # checks spam keywords
            if (features.urgent_words_count + features.money_keywords_count +
                features.suspicious_phrases_count) >= 3:
                reasoning['decision_path'].append('Multiple spam keywords detected')
                return 'spam', 0.80, reasoning

            if spam_score >= 0.65:
                reasoning['decision_path'].append('Spam score supports classification')
                return 'spam', 0.75, reasoning
            elif spam_score < 0.45:
                reasoning['decision_path'].append('Spam score suggests ham')
                return 'ham', 0.65, reasoning

            # extra checks: links or names for personalization
            if features.has_external_links and not features.recipient_name_present:
                reasoning['decision_path'].append('Generic message with links - likely spam')
                return 'spam', 0.70, reasoning

            return 'spam', 0.60, reasoning

        # 3rd Branch for low NB confidence (30% to 60%)
        elif nb_confidence >= self.LOW_CONFIDENCE_THRESHOLD:
            reasoning['decision_path'].append('Low-medium NB confidence - rely on features')

            # High spam score overrides
            if spam_score >= 0.75:
                reasoning['decision_path'].append('High spam score detected')
                return 'spam', 0.70, reasoning

            # Check for external links
            if (features.suspicious_phrases_count >= 2 and
                    features.has_external_links):
                reasoning['decision_path'].append('Phishing pattern detected')
                return 'spam', 0.75, reasoning

            # Search through all spam keys
            indicator_count = sum([
                features.urgent_words_count > 0,
                features.money_keywords_count > 0,
                features.capital_ratio > 0.25,
                features.excessive_punctuation,
                not features.recipient_name_present
            ])

            if indicator_count >= 3:
                reasoning['decision_path'].append(f'{indicator_count} spam indicators present')
                return 'spam', 0.65, reasoning
            elif indicator_count <= 1:
                reasoning['decision_path'].append(f'Only {indicator_count} spam indicators')
                return 'ham', 0.60, reasoning

            # decison for whether spam or ham
            if spam_score >= 0.55:
                return 'spam', 0.55, reasoning
            else:
                return 'ham', 0.55, reasoning

        # 4th Branch for very low NB confidence (less than 30%)
        else:
            reasoning['decision_path'].append('Low NB confidence - feature-driven decision')

            # will go against model if score over 80
            if spam_score >= 0.80:
                reasoning['decision_path'].append('Very high spam score overrides NB')
                return 'spam', 0.65, reasoning

            # likely ham(not spam)
            if spam_score < 0.35:
                reasoning['decision_path'].append('Low spam score - likely ham')
                return 'ham', 0.75, reasoning

            # Check for suspicious phrases, if found then spam
            if features.suspicious_phrases_count >= 2:
                reasoning['decision_path'].append('Multiple suspicious phrases')
                return 'spam', 0.60, reasoning

            return 'ham', 0.70, reasoning



if __name__ == "__main__":
    classifier = SpamDecisionTree()

    test_emails = [
        {
            'text': "CONGRATULATIONS!!! You've WON $1,000,000! Click here NOW to claim your prize before it EXPIRES!!!",
            'nb_conf': 0.92,
            'has_name': False
        },
        {
            'text': "Hi John, Here's the report you requested. Let me know if you need any changes. Thanks, Sarah",
            'nb_conf': 0.15,
            'has_name': True
        },
        {
            'text': "Dear Customer, Urgent action required. Your account has unusual activity. Click here to verify your identity.",
            'nb_conf': 0.78,
            'has_name': False
        }
    ]

    for i, email in enumerate(test_emails, 1):
        result, confidence, reasoning = classifier.classify(
            email['text'],
            email['nb_conf'],
            email['has_name']
        )

        print(f"\n{'=' * 60}")
        print(f"Email {i}:")
        print(f"Text: {email['text'][:80]}...")
        print(f"NB Confidence: {email['nb_conf']:.2f}")
        print(f"\nClassification: {result.upper()}")
        print(f"Confidence: {confidence:.2f}")
        print(f"Decision Path: {' -> '.join(reasoning['decision_path'])}")
        print(f"Spam Score: {reasoning['spam_score']:.2f}")