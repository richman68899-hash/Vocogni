# VOCogni — Prototype (Version 1)

A functional prototype of VOCogni, an applied/vocational learning platform
built around one loop:

**Discover → Learn → Practice → Apply → Record → Reflect → Next Step**

This is a concept-testing prototype, not a production platform. It runs
entirely locally, in one browser session, with no external services and no
AI API calls — everything, including the "AI progress summary," is real
working code driven by data you generate as you use the app.

---

## Quick start

```bash
# from inside the project folder
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Streamlit will open the app at `http://localhost:8501`. Run the command
from the project root (the folder containing `app.py`) so the `assets/`
and `.streamlit/` folders are found correctly.

---

## File tree

```
vocogni/
├── app.py                   # Entry point: page config, sidebar, routing
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml          # Base (light) Streamlit theme colors/fonts
├── assets/
│   └── README.txt           # Where to put vocogni_logo.png (see below)
├── data.py                  # All course/lesson/question content (static)
├── state.py                 # st.session_state shape + defaults
├── logic.py                 # Progress engine — pure functions, no UI code
├── styles.py                # CSS design tokens + injection
└── sections/
    ├── __init__.py
    ├── profile.py            # Profile
    ├── browse.py              # Browse (+ delegates into course.py)
    ├── course.py               # Course detail + interactive lesson flow
    ├── progress.py            # Progress
    ├── notes.py                # Notes
    └── settings.py              # Settings
```

### Why more files than the minimum `app.py` / `requirements.txt` / `README.md`

The spec allows this when genuinely useful, and at this feature count (five
sections, a locking/progress engine, mistake tracking, a simulated AI
summary, and rule-based recommendations) a single file would run into the
thousands of lines and be hard to navigate or hand off. Splitting along
`data` / `state` / `logic` / `styles` / `sections` mirrors exactly the axes
called out in the spec for future expansion (swap the data source, swap the
logic, swap the UI) without touching the other layers.

---

## Architecture

- **`data.py`** — The three Version 1 courses, their lessons, and every
  question, as plain dictionaries. Nothing here imports Streamlit. Swap
  this for a database/CMS call later and nothing else changes.
- **`state.py`** — Defines the shape of `st.session_state` (profile,
  progress, notes, settings, navigation) and sets it up once per session.
- **`logic.py`** — The "brain": answer checking, mistake recording,
  strengths/weaknesses, common mistakes, recommendations, and the
  simulated AI summary. Every function takes plain data in and returns
  plain data out — no `import streamlit` anywhere in this file. That's
  deliberate: these functions will work unchanged if `progress` starts
  coming from a real database instead of `st.session_state`.
- **`styles.py`** — All CSS, generated from the current Settings (theme,
  text size, motion). See "Design notes" below.
- **`sections/*.py`** — One module per sidebar item, each exposing a single
  `render()` function that `app.py` calls. `browse.py` also owns the
  Browse → Course → Lesson drill-down (`course.py`), since that's one
  continuous flow rather than a separate nav item.
- **`app.py`** — Page setup, the sidebar (logo + nav), and routing to
  whichever section is active. No feature logic lives here.

### The core interactive loop

Browse → select a course → lessons unlock in order as you complete the one
before → each lesson is explanation → practice questions with immediate
right/wrong feedback → the final lesson in every course is a **Real-World
Challenge** that asks you to apply the concept to a realistic scenario
(pricing, recipe scaling, trip budgeting) instead of repeating a formula →
progress, accuracy, and mistakes update automatically → Progress page shows
strengths/weaknesses, common mistakes, and rule-based recommendations.

---

## Design notes

- **Color has one job each.** A single teal accent is used for every
  primary action and every progress indicator, so it always means "go /
  progress." A second, warm amber accent appears *only* on Real-World
  Challenge lessons — color itself signals "you're in the Apply stage,"
  rather than decorating the page.
- **Structure, not shadows.** Cards are defined by a hairline border, not
  a stacked drop shadow, and every card looks the same *unless* it's a
  challenge (amber edge) or the lesson you're currently on (accent edge).
- **Two typefaces, one job each.** Space Grotesk for headings, IBM Plex
  Sans for body/UI text, and IBM Plex Mono only for the numbers on the
  Progress page — so progress reads like a measurement, not a game score.
- No gradients, no confetti/celebration animations, no streaks or badges.

---

## Known prototype limitations

- **Local, single-session data only.** Everything lives in
  `st.session_state`. Closing the tab, restarting the server, or opening a
  second browser resets all data. There is no database, login, or
  cross-device sync (see spec section 21 — deliberately out of scope for
  Version 1).
- **No real AI.** The "AI progress summary" is template text built from
  your own stored statistics. See "Connecting a real LLM" below.
- **No real recommendation model.** Recommendations are the fixed rules in
  `logic.generate_recommendations()`.
- **Dark mode is a CSS approximation.** Streamlit does not currently expose
  a public API to switch its native theme at runtime, so Settings > Dark
  applies an app-wide CSS override on top of the fixed light base theme in
  `.streamlit/config.toml`, rather than a true native theme swap. It covers
  backgrounds, text, and all custom components; a few native widget
  chrome details may not fully invert.
- **Sound is generated on the fly** (a short tone synthesized with Python's
  standard `wave` module — no bundled audio file) and depends on the
  browser's autoplay policy; if a browser blocks it, the app continues
  normally without erroring.
- **Difficulty (Adaptive/Easy/Medium/Hard)** is stored as a real preference
  and currently shows a hint on numeric questions in Easy mode. It does not
  yet change which or how many questions are served — the spec explicitly
  excludes adaptive ML for Version 1.
- **Completed lessons aren't replayed.** Reopening a finished lesson shows
  the explanation again plus a short recap, rather than re-asking questions
  and double-counting attempts/mistakes.
- **Exactly three courses, by design** (Simple Fractions, Algebra Basics,
  Word Problems), per spec section 6.

---

## Connecting a real LLM to the AI progress summary

`logic.generate_progress_summary(profile, progress)` is the one function to
change; nothing else in the app calls an AI model or needs to know it
changed.

1. `pip install anthropic` and add `anthropic` to `requirements.txt`.
2. Provide an API key via an environment variable (e.g. `ANTHROPIC_API_KEY`)
   or `st.secrets` — never hard-code a key in source.
3. Keep the function signature exactly as-is:
   `generate_progress_summary(profile, progress) -> str`.
4. Inside the function, build a short prompt from the same stats already
   gathered there (`per_course_stats()`, weakest/strongest topic, top
   mistakes) and call `client.messages.create(model=..., messages=[...])`,
   returning the response text instead of the template text.
5. Wrap the API call in `try/except` and fall back to the current template
   version on failure or a missing key, so the Progress page always shows
   something.

## Replacing the recommendation engine

Same pattern: `logic.generate_recommendations(progress)` returns a list of
strings today. Keep that signature (or evolve it to return structured
data) and swap the rule checks inside for a call to a real model or
service — `sections/browse.py` and `sections/progress.py` only read the
returned list.

---

## Testing performed

This sandbox has no network access, so a live Streamlit server couldn't be
installed or clicked through here. Before delivery I: (1) syntax-checked
every file, (2) validated the full course/lesson/question data schema
programmatically, (3) confirmed all 21 questions across all 3 courses
check as correct against their own stored answer, and (4) ran a
mock-Streamlit harness (24 checks) that drives `logic.py` directly
(mistake recording, lesson locking, strength thresholds, recommendations,
the AI summary) and renders every section — including all 12 lessons and
the full intro → question → feedback → complete state machine in both
feedback-timing modes, dark mode, and edge cases like an empty profile or
special characters in free-text fields — to catch runtime errors that
syntax-checking alone wouldn't. That harness isn't part of the delivered
project; it's a stand-in for a real browser, so please still click through
the app yourself after installing. If anything looks off, the most likely
spots are noted above.

## Logo

Drop a real `vocogni_logo.png` into `assets/` (see `assets/README.txt`).
Until then, the sidebar shows a clean text wordmark, as the spec requires.