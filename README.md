# Vocogni — Learning Prototype (v1.4 development)

Vocogni is an applied-learning prototype built around the loop:

**Understand → Solve → Apply → Advance**

The current architecture uses Streamlit, Auth0 OIDC for authentication, and
Supabase PostgreSQL for durable learner-state persistence. It is still a
prototype and is not yet production-validated.

The Progress summary and v1.4 lesson diagnostic are transparent rule-based
logic. No external generative AI or trained diagnostic model is called. The
v1.4 diagnostic work is on a feature branch and remains unreleased until its
acceptance tests pass.

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
├── data.py                  # Courses, lessons, question and diagnostic content
├── diagnostics.py           # Reusable rule-based diagnostic scoring/placement
├── state.py                 # Session state, durable progress, autosave coordination
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

Separate modules keep authored course content, diagnostic rules, durable
state, progress logic, styling, and UI rendering independently understandable.
The diagnostic engine is intentionally framework-free so scoring rules and
assessment-schema checks can be unit-tested without launching Streamlit.

---

## Architecture

- **`data.py`** — Course, lesson, question, diagnostic, and pathway content
  as plain Python dictionaries. Nothing here imports Streamlit.
- **`diagnostics.py`** — Validates the reusable five-item diagnostic schema,
  scores answers, identifies author-tagged weaknesses, explains placement,
  and selects the corresponding practice question set. It is rule-based
  prototype decision support, not a trained AI model.
- **`state.py`** — Defines session state, durable learner progress, diagnostic
  records, notes, settings, and autosave coordination.
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

Browse → select a course → lesson unlocks in sequence → configured foundation
lessons begin with a one-time baseline diagnostic → the transparent rule engine
flags missed skill tags and recommends prerequisite review, Easy, Medium, Hard,
or a real-life project → lesson explanation and routed practice → feedback and
application → separate diagnostic and practice measures appear on Progress.
The diagnostic currently covers only the three initial foundation lessons.

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

## Chemistry course and open-ended practice marking

The Chemistry Formulae and Equations course is authored in
`chemistry_course.py` as twelve lessons with concept explanations, worked
examples, open-ended practice questions, and configured marking points. The
course content follows the learner-provided chemistry master note.

`assessment.py` provides deterministic, auditable rubric marking. It awards
marks by configured marking point, accepts selected equivalent notation and
orthographic variants, and issues spelling/terminology warnings without
rewriting the learner's response. It is practice marking—not an official
Cambridge mark scheme or an external examiner judgment. Validate authored
rubrics against the intended question and syllabus before using results for
high-stakes decisions. Unit and regression tests live under `tests/`.

## Known prototype limitations

- **Prototype, not production validated.** Auth0 OIDC handles identity and
  Supabase stores the learner state. Live persistence, account isolation,
  failure recovery, and all UI flows still require release-specific tests.
- **No real generative AI.** The Progress summary and recommendations use
  templates/rules. The v1.4 diagnostic engine is an explainable rule-based
  system; it does not call an LLM or claim to infer cognition.
- **Diagnostics are early heuristics.** Diagnostic content is attached
  to configured foundation lessons across the current courses. Five-item
  placement thresholds are not validated assessment instruments. Learner-facing
  results should be interpreted as a starting-point signal, not a definitive
  mastery label.
- **Baseline and post-lesson values are not equivalent tests.** The Progress
  page records a diagnostic score and later practice accuracy. Their
  percentage-point difference is descriptive, not evidence of causal or
  validated learning gain.
- **Adaptive scope is limited.** Only lessons with a `diagnostic` config use
  the placement engine. Future lessons need their own five tagged items,
  prerequisite review text, and pathway question sets. Existing Settings
  difficulty preferences still do not constitute machine-learning adaptation.
- **Course catalogue:** course cards use shared category, subject,
  level, curriculum, and derived lesson-count metadata. Current course content
  includes Simple Fractions, Algebra Basics, Word Problems, and the
  12-lesson Chemical Formulae and Equations course (Cambridge 9701 terminology).
- **Dark mode is a CSS approximation.** Streamlit's native widget chrome may
  not fully invert under the app-wide CSS override.
- **Audio depends on browser policy.** A blocked sound cue should not interrupt
  the learning flow.

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

## Testing and release verification

The diagnostic unit tests are included under `tests/test_diagnostics.py`.
Run from the repository root:

```bash
python -m unittest discover -s tests -v
python -m py_compile data.py diagnostics.py logic.py state.py sections/course.py sections/progress.py
```

These checks cover the reusable scoring and placement engine; they do not
replace live UI tests. Before releasing v1.4, also complete
`docs/testing/lesson-diagnostics-acceptance.md`, including persistence after
refresh/re-login, existing-record compatibility, multi-account isolation,
mobile layout, and save-failure behavior.

Do not treat a passing syntax/unit-test run as proof that the deployed
Auth0/Streamlit/Supabase application has been validated.

## Logo

Drop a real `vocogni_logo.png` into `assets/` (see `assets/README.txt`).
Until then, the sidebar shows a clean text wordmark, as the spec requires.