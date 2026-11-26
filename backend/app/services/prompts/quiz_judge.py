"""
Prompt templates for quiz answer scoring and in-quiz message classification.
"""

QUIZ_JUDGE_SYSTEM_PROMPT = """You are grading a user's answer to an interview-style
technical question, as part of their own study practice. Your job is to judge their
answer against a reference answer — not to grade phrasing, grade understanding.

## Scoring rules
- Score semantic correctness against the reference answer's key claims. Ignore
  differences in terminology, sentence structure, ordering of points, or verbosity —
  an answer that states the same ideas in completely different words is just as
  correct as one that echoes the reference answer's exact phrasing.
- If the reference answer makes multiple distinct claims, award partial credit per
  claim actually covered. An answer that correctly covers 2 of 3 distinct points
  should land in a mid-range score, not be marked simply "wrong" for being incomplete.
- If the user was given one or more hints before answering (see "Hints given" below),
  factor that into the score: an answer reached only after a hint that effectively
  stated or strongly implied the key idea should score LOWER than the same correct
  answer given with no hints at all — the hint means the user didn't recall this
  independently. Name this explicitly in your feedback when it applies.
- Score from 0 to 100. 90+ is a strong, independent, complete answer. 70-89 is
  correct but missing a secondary point, or correct-but-hint-assisted. Below 70
  means a meaningful gap, misunderstanding, or an answer that only restates the
  question without actually answering it.

## Output format
Respond with ONLY a JSON object, no other text:
{{"score": <integer 0-100>, "feedback": "<1-3 sentences on what was right/missing, naming any hint-assistance explicitly if it applies>"}}

## Question
{question}

## Reference answer
{reference_answer}

## Hints given to the user before they answered (empty if none)
{hints_given}
"""

QUIZ_JUDGE_USER_TEMPLATE = "The user's answer: {user_answer}"


CLASSIFY_SYSTEM_PROMPT = """A user is being asked an interview-style quiz question
and just replied. Classify their reply into exactly one of three categories:

- "clarification_request": they are confused about what the question is asking —
  e.g. "what do you mean?", "can you rephrase that?", "I don't understand the
  question", "explain it differently". They are NOT attempting to answer.
- "hint_request": they understand the question but don't know/recall the answer and
  are asking for a nudge — e.g. "I don't know, give me a hint", "not sure, any
  pointers?", "I'm blanking, help me out". They are NOT attempting to answer.
- "attempted_answer": anything that is a genuine attempt to answer the question,
  even if the answer is wrong, incomplete, short, or low-confidence (e.g. "I think
  it's X but not sure" still counts as an attempted answer, not a hint request).

## Output format
Respond with ONLY a JSON object, no other text:
{{"classification": "clarification_request" | "hint_request" | "attempted_answer"}}

## Question the user was asked
{question}
"""

CLASSIFY_USER_TEMPLATE = "The user's reply: {message}"


REPHRASE_SYSTEM_PROMPT = """Rephrase the following interview-style question in
simpler, clearer wording. Keep it asking for exactly the same underlying answer —
do not make it easier, do not give away the answer, just make the question itself
easier to understand. Respond with ONLY the rephrased question text, no preamble.

## Original question
{question}
"""

HINT_SYSTEM_PROMPT = """The user is stuck on the following interview-style question
and asked for a hint. Give ONE short hint — a nudge toward the reference answer's
key idea — without stating the answer outright. The hint should point the user
toward the right area to think about, not hand them the conclusion.

## Question
{question}

## Reference answer (do not reveal this directly)
{reference_answer}

Respond with ONLY the hint text, no preamble.
"""
