"""Basic Geometry course for VOCogni.

A compact learning path covering angles, perimeter, area, mixed application,
and a cumulative post-test. Content stays data-only; sections/course.py owns UI.
"""
from __future__ import annotations


def _numeric_question(qid, prompt, answer, explanation, skill):
    return {
        "id": qid,
        "type": "numeric",
        "prompt": prompt,
        "answer": answer,
        "tolerance": 0.01,
        "whole_number": True,
        "input_hint": "Enter the number only; the question gives the units.",
        "explanation": explanation,
        "skill_tag": skill,
        "mistake_tag": skill,
    }


def _mc_question(qid, prompt, options, answer, explanation, skill):
    return {
        "id": qid,
        "type": "mc",
        "prompt": prompt,
        "options": options,
        "answer": answer,
        "explanation": explanation,
        "skill_tag": skill,
        "mistake_tag": skill,
    }


def _point(point_id, criteria, marks=1, **rules):
    return {"id": point_id, "criteria": criteria, "marks": marks, **rules}


def _open_question(qid, prompt, answer, explanation, skill, points):
    return {
        "id": qid,
        "type": "open_ended",
        "grader": "math",
        "prompt": prompt,
        "answer": answer,
        "accepted_answers": [],
        "explanation": explanation,
        "skill_tag": skill,
        "mistake_tag": skill,
        "max_marks": sum(point["marks"] for point in points),
        "marking_points": points,
        "marking_note": (
            "Practice rubric: the configured numeric results are checked "
            "independently. Show your method and include units."
        ),
    }


def _lesson(number, title, explanation, worked_example, questions, *, kind="standard"):
    lesson = {
        "id": f"geometry_l{number}",
        "title": title,
        "kind": kind,
        "explanation": explanation,
        "worked_example": worked_example,
        "practice_questions": questions,
    }
    # Keep the existing single-question lesson schema available for compatibility;
    # the current structured UI uses practice_questions when that list is present.
    fallback_question = dict(questions[0])
    fallback_question["id"] = f"geometry_l{number}_screen3"
    lesson["interactive_question"] = fallback_question
    return lesson


LESSONS = [
    _lesson(
        1,
        "Angles",
        (
            "<p>An <strong>angle</strong> measures a turn and is measured in degrees (°).</p>"
            "<ul>"
            "<li><strong>Acute:</strong> less than 90°; <strong>right:</strong> exactly 90°.</li>"
            "<li><strong>Obtuse:</strong> more than 90° but less than 180°; "
            "<strong>straight:</strong> 180°.</li>"
            "<li><strong>Angles on a straight line</strong> add to 180°.</li>"
            "<li><strong>Angles around a point</strong> add to 360°.</li>"
            "<li><strong>Vertically opposite angles</strong> are equal.</li>"
            "<li>The interior angles of a triangle add to 180°.</li>"
            "</ul>"
            "<p><strong>Method:</strong> identify the rule, write an equation, then solve for the missing angle.</p>"
        ),
        (
            "A straight line is split into angles of 65° and x. "
            "Because angles on a straight line add to 180°, x = 180° − 65° = 115°."
        ),
        [
            _numeric_question(
                "geometry_l1_q1",
                "An angle and its adjacent angle lie on a straight line. One angle is 68°. Find the other angle (°).",
                112,
                "Angles on a straight line total 180°: 180 − 68 = 112°.",
                "Angles on a straight line",
            ),
            _numeric_question(
                "geometry_l1_q2",
                "Three angles around a point are 95°, 135°, and 70°. Find the fourth angle (°).",
                60,
                "Angles around a point total 360°: 360 − (95 + 135 + 70) = 60°.",
                "Angles around a point",
            ),
            _mc_question(
                "geometry_l1_q3",
                "One angle at an intersection is 47°. What is the vertically opposite angle?",
                ["43°", "47°", "133°", "313°"],
                "47°",
                "Vertically opposite angles are equal, so the opposite angle is 47°.",
                "Vertically opposite angles",
            ),
            _numeric_question(
                "geometry_l1_q4",
                "Two angles in a triangle are 52° and 68°. Find the third angle (°).",
                60,
                "Triangle angles total 180°: 180 − 52 − 68 = 60°.",
                "Angles in a triangle",
            ),
            _numeric_question(
                "geometry_l1_q5",
                "Two angles on a straight line are x and 3x. Find x (°).",
                45,
                "x + 3x = 180°, so 4x = 180° and x = 45°.",
                "Forming angle equations",
            ),
        ],
    ),
    _lesson(
        2,
        "Perimeter",
        (
            "<p><strong>Perimeter</strong> is the total distance around the outside of a 2D shape. "
            "Add every outside side exactly once.</p>"
            "<ul>"
            "<li>Rectangle: P = 2(length + width).</li>"
            "<li>Square: P = 4 × side length.</li>"
            "<li>Triangle or other polygon: add all side lengths.</li>"
            "</ul>"
            "<p>Perimeter uses <strong>linear units</strong>, such as mm, cm, or m. "
            "Do not include internal edges when finding the outside boundary of a compound shape.</p>"
        ),
        (
            "A rectangle is 8 cm long and 5 cm wide. "
            "P = 8 + 5 + 8 + 5 = 26 cm, or P = 2(8 + 5) = 26 cm."
        ),
        [
            _numeric_question(
                "geometry_l2_q1",
                "A rectangle has length 8 cm and width 5 cm. Find its perimeter (cm).",
                26,
                "P = 2(length + width) = 2(8 + 5) = 26 cm.",
                "Rectangle perimeter",
            ),
            _numeric_question(
                "geometry_l2_q2",
                "An equilateral triangle has side length 7 cm. Find its perimeter (cm).",
                21,
                "All three sides are 7 cm, so P = 7 + 7 + 7 = 21 cm.",
                "Polygon perimeter",
            ),
            _numeric_question(
                "geometry_l2_q3",
                "A square has perimeter 36 cm. Find the length of one side (cm).",
                9,
                "A square has four equal sides, so side = 36 ÷ 4 = 9 cm.",
                "Working backward from perimeter",
            ),
            _numeric_question(
                "geometry_l2_q4",
                "A rectangle has width 6 m and perimeter 34 m. Find its length (m).",
                11,
                "34 = 2(L + 6), so L + 6 = 17 and L = 11 m.",
                "Missing side from perimeter",
            ),
            _numeric_question(
                "geometry_l2_q5",
                "A five-sided plot has side lengths 4 m, 7 m, 5 m, 9 m, and 3 m. Find its perimeter (m).",
                28,
                "Add every side once: 4 + 7 + 5 + 9 + 3 = 28 m.",
                "Perimeter of an irregular polygon",
            ),
        ],
    ),
    _lesson(
        3,
        "Area",
        (
            "<p><strong>Area</strong> measures the surface covered by a 2D shape and uses square units "
            "(for example cm² or m²).</p>"
            "<ul>"
            "<li>Rectangle: A = length × width.</li>"
            "<li>Square: A = side².</li>"
            "<li>Triangle: A = ½ × base × perpendicular height.</li>"
            "<li>Parallelogram: A = base × perpendicular height.</li>"
            "</ul>"
            "<p>For a composite shape, split it into familiar shapes and add their areas. "
            "For a cut-out, subtract the missing area. The triangle's height must be perpendicular to its base.</p>"
        ),
        (
            "A triangle has base 12 cm and perpendicular height 7 cm. "
            "A = ½ × 12 × 7 = 42 cm². Do not use a sloping side as the height unless it is perpendicular."
        ),
        [
            _numeric_question(
                "geometry_l3_q1",
                "Find the area of a rectangle 9 cm long and 4 cm wide (cm²).",
                36,
                "A = length × width = 9 × 4 = 36 cm².",
                "Rectangle area",
            ),
            _numeric_question(
                "geometry_l3_q2",
                "A triangle has base 12 cm and perpendicular height 7 cm. Find its area (cm²).",
                42,
                "A = ½ × base × height = ½ × 12 × 7 = 42 cm².",
                "Triangle area",
            ),
            _numeric_question(
                "geometry_l3_q3",
                "A parallelogram has base 11 cm and perpendicular height 6 cm. Find its area (cm²).",
                66,
                "A = base × perpendicular height = 11 × 6 = 66 cm².",
                "Parallelogram area",
            ),
            _numeric_question(
                "geometry_l3_q4",
                "A square has area 81 cm². Find its side length (cm).",
                9,
                "The side length is √81 = 9 cm because 9 × 9 = 81.",
                "Working backward from area",
            ),
            _numeric_question(
                "geometry_l3_q5",
                "A composite shape is a 10 m by 8 m rectangle with a triangle on top. The triangle has base 10 m and height 4 m. Find the total area (m²).",
                100,
                "Rectangle area = 10 × 8 = 80 m². Triangle area = ½ × 10 × 4 = 20 m². Total = 100 m².",
                "Area of a composite shape",
            ),
        ],
    ),
    _lesson(
        4,
        "Mixed Application",
        (
            "<p>Real problems often require you to choose between an angle rule, perimeter, and area before calculating.</p>"
            "<ol>"
            "<li>List the facts and identify what the question asks for.</li>"
            "<li>Choose the relevant rule or formula.</li>"
            "<li>Keep units consistent and check whether your answer needs linear units (perimeter) or square units (area).</li>"
            "</ol>"
            "<p><strong>Challenge:</strong> Solve the L-shaped courtyard problem in Question 5. "
            "Show both the subtraction used for area and the boundary lengths used for perimeter.</p>"
        ),
        (
            "A 14 m by 8 m rectangular surface has a 4 m by 3 m rectangular section removed. "
            "Remaining area = 14 × 8 − 4 × 3 = 112 − 12 = 100 m². "
            "For a perimeter problem, trace the outside boundary only and add each boundary segment once."
        ),
        [
            _numeric_question(
                "geometry_l4_q1",
                "Two angles lie on a straight line. One is 124°. Find the other angle (°).",
                56,
                "180° − 124° = 56°.",
                "Selecting an angle rule",
            ),
            _numeric_question(
                "geometry_l4_q2",
                "A rectangular noticeboard is 18 cm by 7 cm. How much trim is needed to go all the way around it (cm)?",
                50,
                "The perimeter is 2(18 + 7) = 50 cm.",
                "Perimeter in context",
            ),
            _numeric_question(
                "geometry_l4_q3",
                "A triangular banner has base 12 cm and perpendicular height 5 cm. Find its area (cm²).",
                30,
                "Area = ½ × 12 × 5 = 30 cm².",
                "Area in context",
            ),
            _numeric_question(
                "geometry_l4_q4",
                "A 14 m by 8 m rectangular courtyard has a 4 m by 3 m rectangular section removed. Find the remaining area (m²).",
                100,
                "Outer rectangle: 14 × 8 = 112 m². Removed section: 4 × 3 = 12 m². Remaining area: 112 − 12 = 100 m².",
                "Area of a compound shape",
            ),
            _open_question(
                "geometry_l4_q5",
                "CHALLENGE — A 12 m by 8 m rectangular courtyard has a 4 m by 3 m rectangle removed from one corner, making an L-shape. Find (a) the remaining area in m² and (b) the outside perimeter in m. Show working.",
                "Area = 12 × 8 − 4 × 3 = 84 m²; perimeter = 40 m.",
                "Area = 96 − 12 = 84 m². For the L-shaped boundary, add 12 + 5 + 4 + 3 + 8 + 8 = 40 m. The missing corner removes 12 m² of area, while all six remaining outside edges form the perimeter.",
                "Multi-step geometry challenge",
                [
                    _point(
                        "area",
                        "Finds the remaining area of 84 m²",
                        2,
                        numeric_targets=[{"value": 84, "tolerance": 0.01}],
                    ),
                    _point(
                        "perimeter",
                        "Finds the outside perimeter of 40 m",
                        2,
                        numeric_targets=[{"value": 40, "tolerance": 0.01}],
                    ),
                ],
            ),
        ],
        kind="application",
    ),
    _lesson(
        5,
        "Final Check — Post-test",
        (
            "<p>This is the course post-test. It checks whether you can choose the right rule and apply it without worked examples.</p>"
            "<p>Answer all eight questions independently. Use the requested units and avoid opening earlier lesson explanations until you finish.</p>"
        ),
        (
            "Assessment instructions: complete each question before checking feedback. "
            "The result is saved as a separate attempt for this Final Check lesson."
        ),
        [
            _numeric_question(
                "geometry_l5_q1",
                "Two angles in a triangle are 41° and 67°. Find the third angle (°).",
                72,
                "180° − 41° − 67° = 72°.",
                "Triangle angle sum",
            ),
            _numeric_question(
                "geometry_l5_q2",
                "Two vertically opposite angles meet at an intersection. One is 83°. Find the opposite angle (°).",
                83,
                "Vertically opposite angles are equal, so the answer is 83°.",
                "Vertically opposite angles",
            ),
            _numeric_question(
                "geometry_l5_q3",
                "Angles x and 3x lie on a straight line. Find x (°).",
                45,
                "x + 3x = 180°, so x = 45°.",
                "Angle equation",
            ),
            _numeric_question(
                "geometry_l5_q4",
                "A rectangle is 13 m long and 6 m wide. Find its perimeter (m).",
                38,
                "P = 2(13 + 6) = 38 m.",
                "Rectangle perimeter",
            ),
            _numeric_question(
                "geometry_l5_q5",
                "A square has perimeter 48 cm. Find its area (cm²).",
                144,
                "Side = 48 ÷ 4 = 12 cm. Area = 12 × 12 = 144 cm².",
                "Connecting perimeter and area",
            ),
            _numeric_question(
                "geometry_l5_q6",
                "A triangle has base 14 cm and perpendicular height 9 cm. Find its area (cm²).",
                63,
                "A = ½ × 14 × 9 = 63 cm².",
                "Triangle area",
            ),
            _numeric_question(
                "geometry_l5_q7",
                "A 9 m by 8 m rectangular floor has a 3 m by 2 m storage area excluded. Find the remaining floor area (m²).",
                66,
                "Total floor area = 9 × 8 = 72 m². Subtract the storage area 3 × 2 = 6 m²: 72 − 6 = 66 m².",
                "Composite area",
            ),
            _numeric_question(
                "geometry_l5_q8",
                "A rectangular display board is 2 m long and 1 m wide. Find the perimeter (m).",
                6,
                "P = 2(2 + 1) = 6 m.",
                "Choosing perimeter in context",
            ),
        ],
        kind="assessment",
    ),
]



COURSE_ENTRY_DIAGNOSTIC = {
    "version": 1,
    "prerequisite_review": (
        "Review the meaning of angles, basic arithmetic, the difference between "
        "perimeter and area, and the need to use square units for area. "
        "Then work through the relevant lesson explanation before retaking practice."
    ),
    "questions": [
        {
            "id": "geometry_entry_d1",
            "type": "mc",
            "stage": "prerequisite",
            "skill_tag": "Angle arithmetic",
            "prompt": "Angles on a straight line add to:",
            "options": ["90°", "180°", "270°", "360°"],
            "answer": "180°",
            "explanation": "A straight angle measures 180°.",
            "mistake_tag": "Angle arithmetic",
        },
        {
            "id": "geometry_entry_d2",
            "type": "mc",
            "stage": "level_1",
            "skill_tag": "Rectangle perimeter",
            "prompt": "A rectangle is 5 cm by 3 cm. What is its perimeter?",
            "options": ["8 cm", "15 cm", "16 cm", "30 cm"],
            "answer": "16 cm",
            "explanation": "P = 2(5 + 3) = 16 cm.",
            "mistake_tag": "Rectangle perimeter",
        },
        {
            "id": "geometry_entry_d3",
            "type": "mc",
            "stage": "level_2",
            "skill_tag": "Triangle area",
            "prompt": "A triangle has base 8 cm and perpendicular height 5 cm. What is its area?",
            "options": ["13 cm²", "20 cm²", "40 cm²", "80 cm²"],
            "answer": "20 cm²",
            "explanation": "A = ½ × 8 × 5 = 20 cm².",
            "mistake_tag": "Triangle area",
        },
        {
            "id": "geometry_entry_d4",
            "type": "mc",
            "stage": "level_3",
            "skill_tag": "Composite area",
            "prompt": "A 10 m by 6 m rectangle has a 2 m by 3 m section removed. What area remains?",
            "options": ["54 m²", "60 m²", "66 m²", "72 m²"],
            "answer": "54 m²",
            "explanation": "The original area is 60 m² and the removed section is 6 m², leaving 54 m².",
            "mistake_tag": "Composite area",
        },
        {
            "id": "geometry_entry_d5",
            "type": "mc",
            "stage": "project",
            "skill_tag": "Geometry in context",
            "prompt": "An L-shaped courtyard is made by removing a 4 m by 3 m corner from a 12 m by 8 m rectangle. What is its remaining area?",
            "options": ["72 m²", "84 m²", "88 m²", "96 m²"],
            "answer": "84 m²",
            "explanation": "12 × 8 − 4 × 3 = 96 − 12 = 84 m².",
            "mistake_tag": "Geometry in context",
        },
    ],
    # Reuse authored lesson questions by ID so the placement route does not
    # silently expand any requested five-question lesson into a longer set.
    "pathways": {
        "level_2": {"questions": [dict(LESSONS[0]["practice_questions"][3])]},
        "level_3": {"questions": [dict(LESSONS[0]["practice_questions"][4])]},
        "project": {
            "intro": "Apply angle rules in context, then calculate perimeter and area with appropriate units.",
            "questions": [dict(LESSONS[0]["practice_questions"][4])],
        },
    },
}

LESSONS[0]["diagnostic"] = COURSE_ENTRY_DIAGNOSTIC


GEOMETRY_COURSE = {
    "id": "basic_geometry",
    "title": "Basic Geometry",
    "short_description": "Learn angle rules, perimeter, area, and apply them in practical problems.",
    "difficulty": "Beginner",
    "topic_label": "Geometry",
    "category_id": "academics",
    "subject_id": "mathematics",
    "level": "Middle / high school foundations",
    "curriculum": "General",
    "lessons": LESSONS,
}
