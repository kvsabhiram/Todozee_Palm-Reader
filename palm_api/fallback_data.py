"""Canned palmistry phrases used by the dynamic fallback reading.

When the LLM isn't ready (model failed to load, OOM, etc.), the predictor
deterministically picks one phrase from each pool — seeded by the image's
MD5 — so the same image always yields the same fallback reading.
"""
from __future__ import annotations

HEART_LINE_READINGS = [
    "The Heart Line is long and deep, curving gently toward the index finger, indicating a deeply romantic and emotionally expressive nature. You lead with feeling and form bonds that are intense and lasting.",
    "Your Heart Line is relatively straight and ends near the middle finger, suggesting a more practical approach to love. You value stability and reliability in relationships over grand gestures.",
    "The Heart Line shows a small fork at its end, which traditionally signals versatility in love — you adapt well to your partner's needs and thrive in relationships built on mutual respect.",
    "A chain-like pattern appears along your Heart Line, reflecting emotional sensitivity. You feel things deeply and may need quiet time to process your feelings before responding.",
    "Your Heart Line curves sharply upward, a sign traditionally linked to passionate intensity. When you love, you commit fully and expect the same loyalty in return.",
    "The Heart Line is short but deeply etched, suggesting fewer but profoundly meaningful emotional connections throughout life. Quality matters far more to you than quantity.",
    "Your Heart Line runs almost parallel to the Head Line for a stretch, indicating a person who thinks carefully before acting on emotion — a rare and valuable balance.",
    "There is a small island on the Heart Line near the center of the palm, which may point to a period of emotional uncertainty or searching before finding real clarity in love.",
    "The Heart Line ends with a clean, single branch pointing toward the Jupiter mount, traditionally read as a sign of idealistic and selfless love.",
    "Your Heart Line is moderately curved with no breaks, signaling steady emotional health and a generous capacity for empathy and compassion.",
]

HEAD_LINE_READINGS = [
    "The Head Line is long, stretching well across the palm, which traditionally indicates a highly analytical and intellectually curious mind. You enjoy exploring ideas from multiple angles.",
    "Your Head Line is short but very clear and deep, suggesting focused, decisive thinking. You cut through complexity quickly and trust your judgment.",
    "The Head Line slopes gently downward as it moves across the palm, a traditional sign of imagination and creative thinking. You approach problems with originality.",
    "A slight curve upward in your Head Line points to optimistic thinking and an ability to see opportunities where others see obstacles.",
    "The Head Line connects briefly to the Life Line at its start, indicating a person whose early environment shaped their thinking habits deeply. With time, independent thought has become your strength.",
    "Your Head Line is straight and clear, running parallel to the Heart Line, reflecting logical and structured reasoning. You plan carefully and think before you act.",
    "There is a small break in the Head Line, which can signal a shift in how you think or approach decisions at some point in life — often a sign of growth, not weakness.",
    "The Head Line branches into two directions near the end, traditionally read as adaptability in thinking. You can shift between analytical and intuitive modes with ease.",
    "Your Head Line is moderately long with a gentle wave, suggesting a mind that balances practicality with an appreciation for nuance and complexity.",
    "The Head Line is deeply etched and runs with purpose across the palm, pointing to strong mental clarity and a natural ability to stay focused under pressure.",
]

LIFE_LINE_READINGS = [
    "Your Life Line is a strong, deep arc that sweeps widely across the palm — a traditional indicator of robust vitality, enthusiasm for life, and resilience through challenges.",
    "The Life Line is close to the base of the thumb with a gentle curve, suggesting a more introspective energy. You recharge through reflection and personal space.",
    "A small line branches off from your Life Line and rises upward, traditionally read as a period of renewed energy or a fresh start at some stage of life.",
    "The Life Line is clear and unbroken, running steadily across the lower palm, indicating consistent stamina and a grounded approach to life's ups and downs.",
    "Your Life Line shows a slight interruption that is quickly resumed — traditionally this does not indicate illness but rather a significant shift or turning point in your path.",
    "The Life Line is moderately arced and accompanied by faint secondary lines running parallel, which may reflect a life rich in experience and multiple avenues of growth.",
    "A deep, continuous Life Line that extends well into the palm suggests strong physical and emotional endurance. You tend to recover quickly from setbacks.",
    "The Life Line begins high near the index finger and curves down smoothly, indicating an active and engaged approach to the world from an early age.",
    "Your Life Line is etched clearly but with a natural pause near the center — often read as a moment of reassessment that leads to a more purposeful direction.",
    "The Life Line runs close to the wrist with moderate depth, suggesting steady but thoughtful energy. You conserve your strength and apply it where it matters most.",
]

FATE_LINE_READINGS = [
    "A clear Fate Line runs from the base of the palm upward, traditionally indicating a strong sense of purpose and direction in career and life choices.",
    "Your Fate Line begins partway up the palm rather than at the wrist, which may suggest that your career or life direction solidified later than some — but with greater clarity and intention.",
    "The Fate Line is faint but present, indicating that while external circumstances influence your path, your own choices play the dominant role in shaping your future.",
    "There is a break in the Fate Line that is bridged by a short parallel line — traditionally read as a career change or shift in life direction that ultimately proves positive.",
    "Your Fate Line is deep and unbroken, running straight toward the Saturn mount. This is often associated with discipline, long-term planning, and a steady rise in one's chosen field.",
    "The Fate Line curves slightly toward the Apollo mount near its end, suggesting that recognition or creative fulfillment may become increasingly important to you over time.",
    "A small branch extends from the Fate Line toward the Jupiter mount, traditionally linked to ambition and leadership potential emerging at a certain stage of life.",
    "The Fate Line is absent or very faint, which does not indicate a lack of direction — rather, it may mean your path is highly flexible and shaped by personal freedom and adaptability.",
    "Your Fate Line starts from the Luna mount and travels upward, a traditional sign of someone whose career or life path is shaped significantly by public interaction or travel.",
    "The Fate Line is moderately deep with a slight wobble, suggesting that while your overall direction is clear, you may navigate some unexpected turns that add richness to your journey.",
]

# (element_label, description) pairs
HAND_SHAPE_READINGS = [
    ("Earth", "Your palm is broad and square with shorter fingers, a shape traditionally associated with practicality, patience, and a grounded approach to life. You value tangible results and steady progress."),
    ("Air",   "Your palm is square but with noticeably longer fingers, traditionally linked to intellectual curiosity, communication skills, and a love of ideas. You think quickly and express yourself well."),
    ("Fire",  "Your palm is long with shorter fingers, a shape often associated with energy, ambition, and an active lifestyle. You are drawn to action and thrive on momentum."),
    ("Water", "Your palm is long and narrow with long, graceful fingers, traditionally read as a sign of sensitivity, intuition, and emotional depth. You are attuned to feelings — your own and others'."),
]

FINGER_READINGS = [
    "The index finger is slightly longer than average relative to the others, which may indicate natural leadership tendencies and a desire to take initiative.",
    "Your middle finger is the longest, as is common, but its proportion to the ring finger is notable — suggesting a balance between responsibility and creativity.",
    "The ring finger is relatively long, traditionally associated with a love of beauty, artistic appreciation, and a flair for the creative or expressive.",
    "Your little finger is noticeably long and flexible, often linked to eloquence in communication and quick, sharp thinking.",
    "The fingers are evenly spaced when held naturally, which may suggest an open and adaptable personality — comfortable in both social and solitary settings.",
    "Your fingertips appear rounded, a shape traditionally associated with empathy, intuition, and an emotionally intelligent approach to the world.",
    "The fingers show a slight curve when relaxed, sometimes read as flexibility of mind and a willingness to adapt plans when circumstances change.",
    "Your thumb is long and well-proportioned relative to the hand, traditionally indicating strong willpower and an ability to follow through on decisions.",
]

# (mount_name, developed_description, flat_description) triples
MOUNT_READINGS = [
    ("Jupiter", "The Jupiter mount is well-developed, traditionally associated with confidence, leadership, and a natural desire to expand your horizons and influence.",
     "The Jupiter mount is relatively flat, which may suggest that leadership and ambition manifest more quietly in your life — through steady action rather than bold declaration."),
    ("Saturn", "The Saturn mount is prominent, often linked to discipline, wisdom, and a deep respect for responsibility and long-term thinking.",
     "The Saturn mount is moderate, suggesting a balanced relationship with structure — you appreciate order but do not let it restrict your freedom."),
    ("Apollo", "The Apollo mount is raised and well-formed, traditionally connected to creativity, aesthetic appreciation, and a desire for recognition in your chosen field.",
     "The Apollo mount is subtle, which may indicate that creative expression shows up in your life in quieter, more personal ways."),
    ("Mercury", "The Mercury mount is developed, traditionally associated with sharp communication skills, adaptability, and an ability to read situations quickly.",
     "The Mercury mount is moderate, suggesting steady communication abilities that serve you well in both personal and professional contexts."),
    ("Venus", "The Venus mount is full and firm, traditionally linked to warmth, affection, physical vitality, and a generous spirit.",
     "The Venus mount is present but not dominant, indicating a balanced approach to relationships and physical well-being."),
    ("Luna", "The Luna mount is noticeable, often connected to imagination, intuition, and a sensitivity to the world around you.",
     "The Luna mount is subtle, suggesting that intuition plays a role in your life but is complemented strongly by practical reasoning."),
]

SPECIAL_MARKINGS = [
    "A small star marking is visible on one of the mounts, traditionally read as a point of special talent or significance in that area of life.",
    "There is a cross marking near the center of the palm, often interpreted as a crossroads or a moment of important decision-making.",
    "A triangle is faintly visible, traditionally associated with a gift — whether intellectual, communicative, or spiritual — depending on its location.",
    "No prominent special markings are clearly visible, which simply means the major lines and mounts carry the primary story of your palm.",
    "A small island appears on one of the minor lines, which may indicate a brief period of uncertainty in that area that eventually resolves.",
    "There appears to be a horizontal line crossing one of the major lines — sometimes read as an external influence or challenge at a particular life stage.",
    "A forked ending on one of the lines is visible, traditionally suggesting multiple paths or options available in that area of life.",
    "The lines are generally clean and well-defined with no major interruptions, indicating clarity and consistency in the themes they represent.",
]

GUIDANCE_PARAGRAPHS = [
    "Trust your instincts while maintaining practical grounding. Your natural abilities in communication and analysis serve you well. Balance ambition with emotional well-being.",
    "Lean into your creative side — the ideas that excite you deserve exploration. At the same time, stay rooted in what gives you stability and joy.",
    "Pay attention to the relationships that energize you. The people who appreciate your depth are the ones worth investing in. Do not shrink your ambitions for anyone.",
    "This is a time to build quietly. Not every phase of growth is loud or visible. Your steady effort is compounding in ways you may not yet see.",
    "Your emotional intelligence is one of your greatest assets. Use it not only for others but also for yourself. Check in with how you truly feel, not just how you think you should feel.",
    "The tension between your analytical mind and your intuitive heart is not a flaw — it is a strength. The best decisions you make will come from honoring both.",
    "Embrace change as information, not as threat. Your adaptability is well-developed; now pair it with a clear sense of what you truly want.",
    "Rest is not a reward — it is a foundation. The energy you invest in self-care returns to you in clarity, creativity, and stronger connections.",
    "You have a natural ability to bring people together. This gift is worth cultivating intentionally. Surround yourself with those who value honesty and growth.",
    "Focus on one thing at a time. Your mind is capable of juggling many thoughts, but your deepest satisfaction will come from sustained attention to what matters most.",
]

# Indexed by `datetime.weekday()` (Mon=0 … Sun=6).
DAILY_FALLBACK_MESSAGES = {
    0: "A Peaceful Beginning\nThis Monday invites you to start gently. Let your inner compass guide your first steps of the week. Small, intentional actions set a powerful tone. Trust the quiet wisdom within you — today is about planting seeds, not harvesting them. Carry calm with you.",
    1: "Harness Your Power\nTuesday brings a spark of motivation. Channel that energy into something that matters to you. Your determination is stronger than you realise right now. Take one bold step — even a small one — and let momentum build from there. You've got this.",
    2: "Mental Clarity Prevails\nMidweek is your time to focus. Cut through the noise and zero in on what truly needs your attention. A clear mind leads to clear choices. Trust your ability to see things as they are, not as others expect them to be. Clarity is your gift today.",
    3: "Finding Balance\nThursday asks you to pause and ground yourself. Not every day needs to be productive — some days are for steadiness. Check in with yourself: body, mind, and heart. Let stability be your anchor as you move through the day with quiet confidence.",
    4: "Embrace Connection\nFriday carries a warm, social energy. Reach out to someone you value — a kind word or a genuine question can strengthen a bond. You have a natural ability to make others feel seen. Let that light shine today.",
    5: "Turn Inward\nSaturday is for reflection. Give yourself permission to slow down and sit with your thoughts. What has this week taught you? Let the answers come without forcing them. Peace lives in the space between doing and being.",
    6: "A Fresh Start\nSunday is renewal. Breathe in possibility and let go of what no longer serves you. The week ahead is a blank page — and you hold the pen. Start with gratitude, and let hope guide the rest.",
}

# Generic 4-line summary used when the summary LLM call fails.
DEFAULT_SUMMARY = (
    "Heart line: shows your way of loving. "
    "Head line: shows how you think. "
    "Life line: shows your energy and health. "
    "Fate line: shows your direction in life."
)

DAY_NAMES = {
    0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
    4: "Friday", 5: "Saturday", 6: "Sunday",
}
