"""
logic.py — Progress engine for VOCogni Version 1.

Deliberately framework-free: every function here takes plain data
(profile / progress dicts) as arguments and returns plain data. Nothing in
this file imports streamlit or touches st.session_state directly.

Why: this is exactly the boundary described in spec section 22
("organize the code so [a real database, LLM API, adaptive recommendation
system] can later be added without completely rewriting the application").
Because these functions don't know where `progress` came from, they will
work unchanged whether `progress` is loaded from st.session_state (today)
or fetched from a real database per logged-in user (later).
"""

import base64
import io
import math
import struct
import wave

import data

APPLICATION_TAG = data.APPLICATION_MISTAKE_TAG


# ---------------------------------------------------------------------------
# Answer checking
# ---------------------------------------------------------------------------

def check_answer(question, user_answer):
    """Return True if user_answer is correct for the given question dict."""
    if question["type"] == "mc":
        return user_answer == question["answer"]

    # numeric
    try:
        user_val = float(user_answer)
    except (TypeError, ValueError):
        return False
    tolerance = question.get("tolerance", 0.01)
    return abs(user_val - float(question["answer"])) <= tolerance


# ---------------------------------------------------------------------------
# Recording activity
# ---------------------------------------------------------------------------

def blank_course_progress():
    return {
        "started": False,
        "completed_lessons": [],
        "questions_attempted": 0,
        "correct_answers": 0,
        "mistakes": {},
    }


def record_answer(progress, course_id, question, is_correct):
    """Mutate `progress` in place to record one answered question."""
    prog = progress.setdefault(course_id, blank_course_progress())
    prog["started"] = True
    prog["questions_attempted"] += 1
    if is_correct:
        prog["correct_answers"] += 1
    else:
        tag = question.get("mistake_tag", "Other")
        prog["mistakes"][tag] = prog["mistakes"].get(tag, 0) + 1


def mark_lesson_complete(progress, course_id, lesson_id):
    """Mutate `progress` in place to mark a lesson finished."""
    prog = progress.setdefault(course_id, blank_course_progress())
    if lesson_id not in prog["completed_lessons"]:
        prog["completed_lessons"].append(lesson_id)
    prog["started"] = True


# ---------------------------------------------------------------------------
# Lesson locking
# ---------------------------------------------------------------------------

def is_lesson_unlocked(progress, course_id, lesson_index):
    """Lesson 0 is always unlocked; lesson N unlocks once lesson N-1 is done."""
    if lesson_index == 0:
        return True
    course = data.get_course(course_id)
    prev_lesson = course["lessons"][lesson_index - 1]
    prog = progress.get(course_id, {})
    return prev_lesson["id"] in prog.get("completed_lessons", [])


def next_incomplete_lesson(progress, course_id):
    """Return the first not-yet-completed lesson dict, or None if all done."""
    course = data.get_course(course_id)
    prog = progress.get(course_id, {})
    completed = set(prog.get("completed_lessons", []))
    for lesson in course["lessons"]:
        if lesson["id"] not in completed:
            return lesson
    return None


# ---------------------------------------------------------------------------
# Progress / accuracy calculations
# ---------------------------------------------------------------------------

def course_accuracy(progress, course_id):
    """Accuracy percentage (0-100) for a course, or None if never attempted."""
    prog = progress.get(course_id, {})
    attempted = prog.get("questions_attempted", 0)
    if attempted == 0:
        return None
    return prog.get("correct_answers", 0) / attempted * 100


def course_lesson_progress_percent(progress, course_id):
    course = data.get_course(course_id)
    total = len(course["lessons"])
    if total == 0:
        return 0
    prog = progress.get(course_id, {})
    done = len(prog.get("completed_lessons", []))
    return int(round(done / total * 100))


def classify_strength(accuracy):
    """
    Prototype logic only — a simple accuracy threshold, not an AI-diagnosed
    assessment of the learner's cognition (see spec section 12).
    """
    if accuracy is None:
        return None
    if accuracy >= 80:
        return "Strength"
    if accuracy < 60:
        return "Weakness"
    return "Developing"


def common_mistakes_for_course(progress, course_id):
    """List of (mistake_tag, count) for a course, sorted most-common first."""
    prog = progress.get(course_id, {})
    mistakes = prog.get("mistakes", {})
    items = [(tag, count) for tag, count in mistakes.items() if count > 0]
    items.sort(key=lambda kv: kv[1], reverse=True)
    return items


def per_course_stats(progress):
    """One summary dict per course — used by the Progress page and the
    prototype AI summary."""
    stats = []
    for course_id in data.COURSE_ORDER:
        course = data.get_course(course_id)
        prog = progress.get(course_id, {})
        attempted = prog.get("questions_attempted", 0)
        correct = prog.get("correct_answers", 0)
        accuracy = (correct / attempted * 100) if attempted else None
        stats.append({
            "course_id": course_id,
            "topic_label": course["topic_label"],
            "questions_attempted": attempted,
            "correct_answers": correct,
            "accuracy": accuracy,
            "top_mistakes": common_mistakes_for_course(progress, course_id)[:2],
        })
    return stats


def overall_stats(progress):
    """Aggregate stats across all courses, for the Progress page overview."""
    courses_attempted = 0
    courses_completed = 0
    lessons_completed = 0
    questions_attempted = 0
    correct_answers = 0
    total_mistakes = 0

    for course_id in data.COURSE_ORDER:
        course = data.get_course(course_id)
        prog = progress.get(course_id, {})
        if prog.get("started"):
            courses_attempted += 1
        done = len(prog.get("completed_lessons", []))
        lessons_completed += done
        if done > 0 and done == len(course["lessons"]):
            courses_completed += 1
        questions_attempted += prog.get("questions_attempted", 0)
        correct_answers += prog.get("correct_answers", 0)
        total_mistakes += sum(prog.get("mistakes", {}).values())

    return {
        "courses_attempted": courses_attempted,
        "courses_completed": courses_completed,
        "lessons_completed": lessons_completed,
        "questions_attempted": questions_attempted,
        "correct_answers": correct_answers,
        "total_mistakes": total_mistakes,
    }


# ---------------------------------------------------------------------------
# Recommendations — rule-based prototype logic
#
# TO REPLACE WITH A REAL RECOMMENDATION MODEL LATER:
#   Keep the signature `generate_recommendations(progress) -> list[str]`
#   (or evolve it to return structured dicts instead of strings). Swap the
#   rule checks below for a call to your model / service. Every caller
#   (sections/browse.py, sections/progress.py) only reads the returned
#   list, so nothing else needs to change.
# ---------------------------------------------------------------------------

def generate_recommendations(progress, limit=4):
    recs = []

    for course_id in data.COURSE_ORDER:
        course = data.get_course(course_id)
        prog = progress.get(course_id, {})
        if not prog.get("started"):
            recs.append(f"Start {course['title']}")

    for course_id in data.COURSE_ORDER:
        course = data.get_course(course_id)
        acc = course_accuracy(progress, course_id)
        if acc is not None and acc < 60:
            recs.append(f"Review {course['title']}")

    fractions_acc = course_accuracy(progress, "fractions")
    algebra_acc = course_accuracy(progress, "algebra")
    if (
        fractions_acc is not None and fractions_acc >= 80
        and algebra_acc is not None and algebra_acc < 60
    ):
        recs.append("Continue Algebra Basics")

    seen = set()
    deduped = []
    for rec in recs:
        if rec not in seen:
            seen.add(rec)
            deduped.append(rec)
    return deduped[:limit]


# ---------------------------------------------------------------------------
# Simulated AI progress summary
#
# TO REPLACE WITH A REAL LLM LATER:
#   1. pip install anthropic, and add it to requirements.txt.
#   2. Provide an API key via an environment variable or st.secrets
#      (never hard-code a key in source).
#   3. Keep this function's exact signature:
#        generate_progress_summary(profile, progress) -> str
#      sections/progress.py calls it without knowing how it's implemented.
#   4. Inside, build a short prompt from the same stats gathered below
#      (per_course_stats, weakest/strongest topic, top mistakes) and send
#      it to client.messages.create(model=..., messages=[...]), returning
#      the response text instead of the template text below.
#   5. Wrap the API call in try/except and fall back to the template
#      version if the call fails or no key is configured, so the Progress
#      page always shows something.
# ---------------------------------------------------------------------------

def generate_progress_summary(profile, progress):
    name = (profile.get("name") or "").strip() or "there"
    stats = per_course_stats(progress)
    attempted = [s for s in stats if s["questions_attempted"] > 0]

    if not attempted:
        body = (
            f"Hi {name}. You haven't attempted any practice questions yet.\n\n"
            "Start any course from the Browse page — this summary will "
            "update with real feedback based on your activity."
        )
        return _wrap_summary(body)

    strongest = max(attempted, key=lambda s: s["accuracy"])
    weakest = min(attempted, key=lambda s: s["accuracy"])

    lines = [f"Hi {name}. Here is where your practice stands right now.", ""]

    if strongest["accuracy"] >= 80:
        lines.append(
            f"You have made strong progress in {strongest['topic_label']}, "
            f"answering {strongest['accuracy']:.0f}% of attempted questions "
            "correctly."
        )
    else:
        lines.append(
            f"Your strongest area so far is {strongest['topic_label']}, at "
            f"{strongest['accuracy']:.0f}% accuracy."
        )

    if weakest["course_id"] != strongest["course_id"]:
        lines.append(
            f"Your main difficulty right now is {weakest['topic_label']} "
            f"({weakest['accuracy']:.0f}% accuracy)."
        )

    if weakest["top_mistakes"]:
        lines.append("")
        lines.append("You should review:")
        for i, (tag, _count) in enumerate(weakest["top_mistakes"], start=1):
            lines.append(f"{i}. {tag}")

    lines.append("")
    lines.append(f"Recommended next step: {_recommend_next_step(progress, weakest)}")

    return _wrap_summary("\n".join(lines))


def _recommend_next_step(progress, weakest_stat):
    course_id = weakest_stat["course_id"]
    course = data.get_course(course_id)
    lesson = next_incomplete_lesson(progress, course_id)
    if lesson is not None:
        return f"Complete the \u201c{lesson['title']}\u201d lesson in {course['topic_label']}."
    return f"Revisit the {course['topic_label']} lessons for extra practice."


def _wrap_summary(body):
    return "VOCogni Learning Summary \u2014 Prototype\n\n" + body


# ---------------------------------------------------------------------------
# Optional sound cue — generated on the fly with the standard library only,
# so Version 1 needs no bundled audio asset.
# ---------------------------------------------------------------------------

def _generate_beep_wav_bytes(frequency=880.0, duration_ms=150, volume=0.25, sample_rate=22050):
    n_samples = int(sample_rate * duration_ms / 1000)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            fade = 1.0 - (i / n_samples)  # avoid a click at the tail
            sample = volume * fade * math.sin(2 * math.pi * frequency * t)
            frames += struct.pack("<h", int(sample * 32767))
        wf.writeframes(bytes(frames))
    return buf.getvalue()


def get_correct_answer_beep_base64():
    """Base64-encoded short WAV beep, used for the Settings > Sound option."""
    return base64.b64encode(_generate_beep_wav_bytes()).decode("ascii")