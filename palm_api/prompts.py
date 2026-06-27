"""All LLM prompt templates: palm analysis, summary, and the 7 daily prompts.

Each template is a plain string with `{...}` placeholders filled in via
`str.format(...)` at call time.
"""
from __future__ import annotations

# ── palm analysis (multimodal: text + image) ─────────────────────────────
PALM_ANALYSIS_PROMPT = """[Analysis ID: {analysis_id}]
You are an expert palmistry reader analyzing this palm image.
This is the user's {hand_upper} hand.

IMPORTANT: This is a UNIQUE palm. Study the specific lines, curves, mounts, and markings
visible in THIS image carefully. Do NOT give a generic reading — every palm is different.

TASK:
Analyze the provided palm image in detail using traditional palmistry principles,
adapting all observations strictly to the visible features of the specific palm shown.

ANALYZE THE FOLLOWING:

1. Major Lines:
   - Heart Line: length, depth, curvature, start/end points, breaks, chains, forks.
   - Head Line: clarity, direction, connection with Life Line, interruptions or branches.
   - Life Line: depth, continuity, arc, visible changes or markings.
   - Fate Line: presence/absence, strength, origin point, interruptions.

2. Palm Shape & Fingers:
   - Hand shape: Identify elemental type (earth, air, fire, water).
   - Finger length and characteristics.
   - Thumb structure.

3. Mounts (raised areas):
   Jupiter, Saturn, Apollo, Mercury, Venus, Luna.

4. Special Markings:
   Stars, crosses, islands, chains, breaks/gaps, minor lines.

IMPORTANT RULES:
- Base interpretations strictly on traditional palmistry beliefs
- Do NOT make absolute predictions or fixed outcomes
- Clearly state uncertainty when features are faint or unclear
- Highlight dominant traits and recurring life themes

OUTPUT FORMAT:
A comprehensive palmistry reading covering major lines, hand characteristics, mounts,
and special markings. Focus on personality tendencies, strengths, challenges, and life themes,
framed as traditional belief-based guidance."""


# ── plain-language summary (text-only) ───────────────────────────────────
SUMMARY_PROMPT = """Write a SHORT summary (50-70 words) of the palm reading below.

STRICT RULES:
- Use simple, everyday English. NO technical palmistry words.
- Briefly mention each of the four main lines:
    * Heart line (love and emotions)
    * Head line (thinking and decisions)
    * Life line (energy and vitality)
    * Fate line (life path and direction)
- One short sentence per line, then a final calm closing line.
- Do NOT predict specific events.

PALM READING:
{palm_reading}

Summary:"""


# ── 7 day-themed prediction prompts (text-only) ──────────────────────────
_MONDAY = """Generate a short daily astrology-style message based on palm reading insights.

STRICT RULES:
- Based on traditional palmistry beliefs for guidance only
- Do NOT make absolute predictions or guarantees
- Do NOT mention technical palmistry terms in the output
- Keep it inspirational and reflective

LANGUAGE: English ONLY, simple and modern
STYLE: Calm, reflective, grounding - suitable for Monday

STRUCTURE:
1. Soft opening line (e.g., "A Peaceful Beginning")
2. Core energy insight (2-3 sentences)
3. Inner reflection guidance (2-3 sentences)
4. Calm closing line

LENGTH: 70-90 words total

PALM READING CONTEXT:
{palm_reading}

Generate today's guidance:"""

_TUESDAY = """Generate a motivating daily message based on palm reading insights.

STRICT RULES:
- Traditional belief-based guidance only
- No absolute predictions
- No technical jargon
- Positive and empowering tone

LANGUAGE: English ONLY, energetic and clear
STYLE: Motivating, action-oriented, confident

STRUCTURE:
1. Uplifting opening (e.g., "Harness Your Power")
2. Today's motivational energy (2-3 sentences)
3. Action-focused guidance (2-3 sentences)
4. Encouraging closing line

LENGTH: 70-90 words total

PALM READING CONTEXT:
{palm_reading}

Generate today's guidance:"""

_WEDNESDAY = """Generate a focused, clarity-driven message based on palm reading.

STRICT RULES:
- Belief-based guidance only
- No predictions
- No technical terms
- Clear and practical

LANGUAGE: English ONLY, precise and clear
STYLE: Focused, practical, clarity-oriented

STRUCTURE:
1. Clear opening (e.g., "Mental Clarity Prevails")
2. Focus theme (2-3 sentences)
3. Practical guidance (2-3 sentences)
4. Clarity-focused closing

LENGTH: 70-90 words total

PALM READING CONTEXT:
{palm_reading}

Generate today's guidance:"""

_THURSDAY = """Generate a grounding and balanced message based on palm reading.

STRICT RULES:
- Traditional belief-based only
- No fear or absolute predictions
- No technical terms
- Reassuring and stable tone

LANGUAGE: English ONLY, gentle and steady
STYLE: Grounding, balanced, reassuring

STRUCTURE:
1. Calm opening (e.g., "Finding Balance")
2. Stability-focused energy (2-3 sentences)
3. Balance guidance (2-3 sentences)
4. Grounding closing line

LENGTH: 70-90 words total

PALM READING CONTEXT:
{palm_reading}

Generate today's guidance:"""

_FRIDAY = """Generate a gentle yet confident message based on palm reading.

STRICT RULES:
- Belief-based only
- No absolute predictions
- No technical terms
- Warm and confident tone

LANGUAGE: English ONLY, warm and positive
STYLE: Gentle confidence, social ease

STRUCTURE:
1. Warm opening (e.g., "Embrace Connection")
2. Confidence-related energy (2-3 sentences)
3. Social/relationship guidance (2-3 sentences)
4. Positive closing line

LENGTH: 70-90 words total

PALM READING CONTEXT:
{palm_reading}

Generate today's guidance:"""

_SATURDAY = """Generate an introspective message based on palm reading.

STRICT RULES:
- Belief-based reflection only
- No predictions
- No technical terms
- Calm and contemplative

LANGUAGE: English ONLY, soft and reflective
STYLE: Introspective, inward-looking, calm

STRUCTURE:
1. Gentle opening (e.g., "Turn Inward")
2. Inner reflection (2-3 sentences)
3. Release/acceptance guidance (2-3 sentences)
4. Peaceful closing line

LENGTH: 60-80 words total

PALM READING CONTEXT:
{palm_reading}

Generate today's guidance:"""

_SUNDAY = """Generate an uplifting and refreshing message based on palm reading.

STRICT RULES:
- Belief-based only
- No absolute predictions
- No technical terms
- Light and hopeful tone

LANGUAGE: English ONLY, positive and bright
STYLE: Uplifting, hopeful, refreshing

STRUCTURE:
1. Bright opening (e.g., "A Fresh Start")
2. Positive energy (2-3 sentences)
3. Renewal guidance (2-3 sentences)
4. Hopeful closing line

LENGTH: 70-90 words total

PALM READING CONTEXT:
{palm_reading}

Generate today's guidance:"""

# Indexed by `datetime.weekday()` (Mon=0 … Sun=6).
DAILY_PROMPTS = {
    0: _MONDAY,
    1: _TUESDAY,
    2: _WEDNESDAY,
    3: _THURSDAY,
    4: _FRIDAY,
    5: _SATURDAY,
    6: _SUNDAY,
}
