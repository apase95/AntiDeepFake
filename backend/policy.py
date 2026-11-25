import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class Decision:
    kind: str = 'benign'  # benign, pressure, coercive
    quote: str | None = None


def redact(text):
    text = re.sub(r'(?i)(\b(?:otp|code|pin|mã)\s*[:=]?\s*)\d{4,8}\b',
                  r'\1[REDACTED_NUM]', text)
    return re.sub(r'(?<!\w)\+?\d(?:[ .-]?\d){8,}(?!\w)', '[REDACTED_NUM]', text)


INJECTION = re.compile(r'ignore (?:all |the )?(?:previous |prior )?(?:rules|instructions)|'
                       r'output normal|reveal (?:the )?system prompt', re.I)


def normalize(text):
    text = unicodedata.normalize('NFKC', text).casefold().replace('’', "'")
    return ' '.join(re.sub(r"[^\w']", ' ', text).split())


def ground(quote, *transcripts):
    if not quote or not normalize(quote):
        return None
    for text in transcripts:
        if quote in text:
            return quote
        words = list(re.finditer(r"[\w'’]+", text))
        count = len(normalize(quote).split())
        for i in range(len(words) - count + 1):
            candidate = text[words[i].start():words[i + count - 1].end()]
            if normalize(candidate) == normalize(quote):
                return candidate
    return None


ACTIONS = {
    'normal': 'No warning from the available signals.',
    'visual_alert_only': 'Visual tampering detected; do not use video to verify identity.',
    'verbal_pressure_only': 'Pause and verify the request independently.',
    'confirmed_scam': 'Urgent Warning: Pause transfer and call your saved phone number to verify.',
    'evaluation_incomplete': 'Verification incomplete; do not rely on this result alone.',
}


def derive(status, score, decision, transcript):
    high = status == 'evaluated' and score >= .60
    if decision and decision.kind in {'pressure', 'coercive'}:
        if high:
            return 'confirmed_scam', .85, 'HIGH'
        return 'verbal_pressure_only', .70, 'HIGH' if decision.kind == 'coercive' else 'MEDIUM'
    if high:
        return 'visual_alert_only', score, 'MEDIUM'
    if decision is None or status == 'provider_error' or (
        status == 'insufficient_visual_data' and not transcript
    ):
        return 'evaluation_incomplete', 0., 'UNKNOWN'
    return 'normal', round(1 - (score or 0), 2), 'LOW'
