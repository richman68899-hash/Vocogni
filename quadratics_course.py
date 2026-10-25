"""Quadratics, graphs, inequalities, simultaneous equations, and integration.

Course content follows the supplied 19-page Quadratics, Graphs, Inequalities,
Simultaneous Equations and Integrals Master Note. Integration is explicitly
labelled as an extension in keeping with that source.
"""
from __future__ import annotations


def _point(point_id, criteria, marks=1, **rules):
    return {"id": point_id, "criteria": criteria, "marks": marks, **rules}


def _q(qid, prompt, answer, explanation, skill, points, accepted_answers=None):
    return {
        "id": qid,
        "type": "open_ended",
        "grader": "math",
        "prompt": prompt,
        "answer": answer,
        "accepted_answers": list(accepted_answers or []),
        "explanation": explanation,
        "skill_tag": skill,
        "mistake_tag": skill,
        "max_marks": sum(int(point.get("marks", 1)) for point in points),
        "marking_points": points,
        "marking_note": (
            "Practice rubric: partial credit is based on visible mathematical "
            "evidence. Equivalent correct algebraic forms are accepted where configured."
        ),
    }


def _diagnostic_question(qid, stage, skill, prompt, answer, explanation, points):
    question = _q(qid, prompt, answer, explanation, skill, points)
    question["stage"] = stage
    return question


COURSE_DIAGNOSTIC = {
    "version": 1,
    "prerequisite_review": (
        "Review substitution, factorising simple quadratics, solving equations, "
        "coordinates, and the distinction between an equation and an inequality."
    ),
    "questions": [
        _diagnostic_question(
            "quad_entry_d1", "prerequisite", "Substitution and powers",
            "For y = x², calculate y when x = −2. Explain why the answer is positive.",
            "y = (−2)² = 4 because the negative number is squared.",
            "Substitute the complete value in brackets: (−2)² = (−2)(−2) = 4.",
            [
                _point("value", "Obtains y = 4", numeric_targets=[{"value": 4, "tolerance": 0}]),
                _point("reason", "Explains that the negative number is multiplied by itself", match_groups=[["negative", "−2", "-2"], ["multipl", "square"], ["positive", "4"]]),
            ],
        ),
        _diagnostic_question(
            "quad_entry_d2", "level_1", "Factorising quadratics",
            "Factorise x² − 5x + 6 and state its roots.",
            "(x − 2)(x − 3) = 0; roots x = 2 and x = 3.",
            "Two numbers multiply to +6 and add to −5: −2 and −3.",
            [
                _point("factor", "Factorises as (x − 2)(x − 3)", match_any=["(x-2)(x-3)", "(x-3)(x-2)"]),
                _point("roots", "States both roots 2 and 3", match_groups=[["2"], ["3"], ["root", "x="]]),
            ],
        ),
        _diagnostic_question(
            "quad_entry_d3", "level_2", "Completing the square",
            "Complete the square for y = x² − 4x + 1. Give the vertex.",
            "y = (x − 2)² − 3; vertex (2, −3).",
            "Half −4 to get −2, square it to get 4, then write x² − 4x + 1 = (x − 2)² − 3.",
            [
                _point("form", "Gives (x − 2)² − 3", match_any=["(x-2)^2-3", "(x-2)²-3"]),
                _point("vertex", "Gives vertex (2, −3)", match_groups=[["vertex", "(2,-3)", "(2,−3)"], ["-3", "−3"]]),
            ],
        ),
        _diagnostic_question(
            "quad_entry_d4", "level_3", "Quadratic inequalities",
            "Solve −x² + 4x − 3 > 0. Include the endpoint rule.",
            "1 < x < 3; endpoints excluded because the inequality is strict.",
            "The roots are 1 and 3. The downward parabola is above the axis between the roots; > excludes equality.",
            [
                _point("interval", "Gives 1 < x < 3", match_any=["1<x<3", "1<x and x<3", "1 < x < 3"]),
                _point("strict", "Explains strict inequality excludes endpoints", match_groups=[[">", "strict"], ["exclude", "not include", "open endpoint"]]),
            ],
        ),
        _diagnostic_question(
            "quad_entry_d5", "project", "Line–parabola intersections",
            "Find the intersection points of y = x² and y = x + 2.",
            "x² = x + 2 gives x = −1 or 2; points (−1, 1) and (2, 4).",
            "Equate the expressions for y, factor x² − x − 2 = (x − 2)(x + 1), then substitute each x-value.",
            [
                _point("xvalues", "Finds x = −1 and x = 2", match_groups=[["-1", "−1"], ["2"]]),
                _point("points", "Gives both ordered pairs (−1, 1) and (2, 4)", match_groups=[["(-1,1)", "(−1,1)", "(-1, 1)"], ["(2,4)", "(2, 4)"]]),
            ],
        ),
    ],
    "pathways": {
        "level_2": {
            "questions": [
                _q(
                    "quad_entry_l2",
                    "Find the vertex and axis of symmetry of y = 2x² − 8x + 3.",
                    "y = 2(x − 2)² − 5; vertex (2, −5), axis x = 2.",
                    "Factor out 2 from the quadratic and linear terms: 2(x² − 4x) + 3 = 2[(x − 2)² − 4] + 3.",
                    "Completing the square",
                    [
                        _point("form", "Completes the square to 2(x − 2)² − 5", match_any=["2(x-2)^2-5", "2(x-2)²-5"]),
                        _point("vertex", "States vertex (2, −5) and axis x = 2", match_groups=[["(2,-5)", "(2,−5)"], ["x=2", "x = 2"]]),
                    ],
                )
            ]
        },
        "level_3": {
            "questions": [
                _q(
                    "quad_entry_l3",
                    "For y = x² − 7x + 12, find both roots and use them to calculate the axis of symmetry.",
                    "Roots 3 and 4; axis x = (3 + 4)/2 = 3.5.",
                    "Factor to (x − 3)(x − 4); their midpoint is 3.5.",
                    "Roots and symmetry",
                    [
                        _point("roots", "Finds roots 3 and 4", match_groups=[["3"], ["4"], ["root", "x="]]),
                        _point("axis", "Calculates midpoint and axis x = 3.5", match_any=["x=3.5", "x = 3.5", "(3+4)/2"]),
                    ],
                )
            ]
        },
        "project": {
            "questions": [
                _q(
                    "quad_entry_project",
                    "Find the area between y = x + 2 and y = x² from x = −1 to x = 2. Show which function is subtracted from which.",
                    "Area = ∫₋₁²[(x + 2) − x²] dx = 9/2 square units.",
                    "The line is above the parabola on this interval, so integrate upper minus lower: [x²/2 + 2x − x³/3]₋₁² = 9/2.",
                    "Area between curves",
                    [
                        _point("integrand", "Uses (x + 2) − x² as upper minus lower", match_any=["x+2-x^2", "x+2−x²", "(x+2)-x^2"]),
                        _point("bounds", "Uses bounds −1 and 2", match_groups=[["-1", "−1"], ["2"], ["bound", "integral", "integrate"]]),
                        _point("area", "Obtains 9/2 or 4.5 square units", match_any=["9/2", "4.5", "4.50"]),
                    ],
                )
            ]
        },
    },
}


LESSONS = [
    {
        "id": "quad_l01",
        "title": "Functions and the Meaning of a Quadratic",
        "kind": "standard",
        "visual_key": "coefficient_family",
        "skill_ids": ["quadratic_function", "substitution", "second_differences"],
        "explanation": """
<h3>A graph is a record of input–output pairs</h3>
<p>A function takes an input <em>x</em> and produces an output <em>y</em>. In <strong>y = f(x)</strong>, each plotted point (x, y) satisfies the rule. A quadratic has the form <strong>y = ax² + bx + c</strong>, where <strong>a ≠ 0</strong>.</p>
<h3>Why a parabola appears</h3>
<p>For y = x² and equally spaced x-values 0, 1, 2, 3, 4, the outputs are 0, 1, 4, 9, 16. First differences are +1, +3, +5, +7: not constant. Second differences are +2, +2, +2. For unit x-steps, the second difference of ax² + bx + c is <strong>2a</strong>.</p>
<ul><li><strong>a</strong> controls opening and width.</li><li><strong>b</strong> affects the horizontal position of the vertex together with a.</li><li><strong>c</strong> is the y-intercept because substituting x = 0 gives y = c.</li></ul>
<p>If a = 0, the x² term disappears, so the function is no longer quadratic.</p>
""",
        "worked_example": """
<h4>Worked example: detect a quadratic pattern</h4>
<table><tr><th>x</th><th>y = x²</th><th>First difference</th><th>Second difference</th></tr>
<tr><td>0</td><td>0</td><td>—</td><td>—</td></tr><tr><td>1</td><td>1</td><td>+1</td><td>—</td></tr><tr><td>2</td><td>4</td><td>+3</td><td>+2</td></tr><tr><td>3</td><td>9</td><td>+5</td><td>+2</td></tr><tr><td>4</td><td>16</td><td>+7</td><td>+2</td></tr></table>
<p>The changing first differences and constant second differences identify a quadratic pattern.</p>
""",
        "interactive_question": _q("quad_l01_q1", "For y = 3x² − 2x + 7, identify a, b and c, calculate the y-intercept, and state the second difference for unit x-steps.", "a = 3, b = −2, c = 7; y-intercept (0, 7); second difference = 6.", "Read the coefficients in standard form. Setting x = 0 gives y = 7, and the second difference is 2a = 6.", "Quadratic coefficients", [
            _point("coefficients", "Identifies a = 3, b = −2, c = 7", match_groups=[["a=3", "a = 3"], ["b=-2", "b = -2", "b=−2"], ["c=7", "c = 7"]]),
            _point("intercept", "Gives y-intercept (0, 7)", match_any=["(0,7)", "(0, 7)", "y-intercept 7", "y intercept 7"]),
            _point("second_difference", "Uses 2a = 6", match_groups=[["2a"], ["6"], ["second difference", "second differences"]]),
        ]),
        "questions": [], "practice_questions": [],
    },
    {
        "id": "quad_l02",
        "title": "Three Useful Forms of a Quadratic",
        "kind": "standard",
        "visual_key": "quadratic_features",
        "skill_ids": ["standard_form", "vertex_form", "factor_form"],
        "explanation": """
<h3>One parabola, three equivalent descriptions</h3>
<table><tr><th>Form</th><th>Structure</th><th>Feature exposed</th></tr>
<tr><td>Standard</td><td>y = ax² + bx + c</td><td>y-intercept (0, c); opening from a</td></tr>
<tr><td>Vertex</td><td>y = a(x − h)² + k</td><td>Vertex (h, k); symmetry line x = h</td></tr>
<tr><td>Factor</td><td>y = a(x − r₁)(x − r₂)</td><td>Roots r₁ and r₂ when real</td></tr></table>
<p>These are not different functions. Select the form that reveals the requested information most directly.</p>
""",
        "worked_example": """
<h4>The running example: y = x² − 5x + 6</h4>
<ul><li>Standard: y = x² − 5x + 6, so the y-intercept is (0, 6).</li><li>Vertex: y = (x − 2.5)² − 0.25, so the vertex is (2.5, −0.25).</li><li>Factor: y = (x − 2)(x − 3), so the roots are 2 and 3.</li></ul>
<p>Cross-check: the axis x = 2.5 is the midpoint of roots 2 and 3.</p>
""",
        "interactive_question": _q("quad_l02_q1", "Rewrite y = x² − 5x + 6 in factor form and vertex form. State the x-intercepts, vertex, axis of symmetry, and y-intercept.", "Factor: (x − 2)(x − 3). Vertex: (x − 2.5)² − 0.25. Roots 2 and 3; vertex (2.5, −0.25); axis x = 2.5; y-intercept (0, 6).", "Factorisation exposes roots; completing the square exposes the vertex; standard form exposes c.", "Quadratic forms", [
            _point("factor", "Gives (x − 2)(x − 3)", match_any=["(x-2)(x-3)", "(x-3)(x-2)"]),
            _point("vertex_form", "Gives (x − 2.5)² − 0.25", match_any=["(x-2.5)^2-0.25", "(x-2.5)²-0.25"]),
            _point("roots", "Identifies roots 2 and 3", match_groups=[["2"], ["3"], ["root", "x="]]),
            _point("vertex_axis", "Identifies vertex and axis x = 2.5", match_groups=[["(2.5,-0.25)", "(2.5,−0.25)", "vertex"], ["x=2.5", "x = 2.5"]]),
            _point("y_intercept", "Identifies y-intercept (0, 6)", match_any=["(0,6)", "(0, 6)"]),
        ]),
        "questions": [], "practice_questions": [],
    },
    {
        "id": "quad_l03",
        "title": "Curve Shape: What a, b and c Control",
        "kind": "standard",
        "visual_key": "quadratic_family",
        "skill_ids": ["opening_direction", "width", "y_intercept"],
        "explanation": """
<h3>Opening direction</h3>
<p>If <strong>a &gt; 0</strong>, a parabola opens upward and its vertex is a minimum. If <strong>a &lt; 0</strong>, it opens downward and its vertex is a maximum. In vertex form, the squared term is non-negative, so multiplying it by a sets which side of k the curve occupies.</p>
<h3>Width and intercept</h3>
<p>Larger |a| makes the curve narrower/steeper relative to the vertex. When 0 &lt; |a| &lt; 1, the curve is wider/flatter. The y-intercept is (0, c), not generally the vertex.</p>
<p>y = −x² is the reflection of y = x² across the x-axis: the vertex and axis remain (0, 0) and x = 0, while each output changes sign.</p>
""",
        "worked_example": """
<h4>Compare y = x² and y = −x²</h4>
<p>Both have vertex (0, 0) and symmetry line x = 0. The first opens up and has a minimum; the second opens down and has a maximum. For a = 2 the curve is narrower than y = x²; for a = 0.5 it is wider.</p>
""",
        "interactive_question": _q("quad_l03_q1", "Compare y = −2(x − 1)² + 4 with y = 0.5(x − 1)² + 4. State their shared vertex and axis, then compare opening and width.", "Both have vertex (1, 4) and axis x = 1. The first opens down and is narrower; the second opens up and is wider.", "The vertex form makes (h, k) immediate. The sign of a sets opening and |a| sets relative width.", "Curve shape", [
            _point("vertex", "States shared vertex (1, 4)", match_any=["(1,4)", "(1, 4)"]),
            _point("axis", "States axis x = 1", match_any=["x=1", "x = 1"]),
            _point("opening", "Explains −2 opens down and 0.5 opens up", match_groups=[["-2", "−2"], ["down", "downward"], ["0.5"], ["up", "upward"]]),
            _point("width", "Identifies |−2| curve narrower and |0.5| curve wider", match_groups=[["narrow", "steep"], ["wide", "flat"]]),
        ]),
        "questions": [], "practice_questions": [],
    },
    {
        "id": "quad_l04",
        "title": "Completing the Square from First Principles",
        "kind": "standard",
        "visual_key": "quadratic_features",
        "skill_ids": ["completing_square", "vertex_form", "negative_coefficients"],
        "explanation": """
<h3>Why the method works</h3>
<p>The identity (x + p)² = x² + 2px + p² means the x-coefficient is twice the number in the bracket. For x² + bx + c, halve b, square it, add and subtract that square so the value is unchanged.</p>
<p><strong>x² + bx + c = (x + b/2)² − (b/2)² + c</strong>.</p>
<h3>General case</h3>
<ol><li>Factor a from the x² and x terms: a[x² + (b/a)x] + c.</li><li>Halve b/a to get b/(2a).</li><li>Add and subtract its square inside, rewrite a perfect square, then simplify.</li></ol>
<p><strong>y = a(x + b/(2a))² + c − b²/(4a)</strong>, so h = −b/(2a) and k = c − b²/(4a).</p>
""",
        "worked_example": """
<h4>Example A: coefficient of x² is 1</h4>
<p>x² − 5x + 6 = (x − 5/2)² − 25/4 + 6 = (x − 2.5)² − 0.25.</p>
<h4>Example B: coefficient of x² is not 1</h4>
<p>3x² + 6x − 10 = 3(x² + 2x) − 10 = 3[(x + 1)² − 1] − 10 = 3(x + 1)² − 13. Vertex (−1, −13).</p>
<p><strong>Precision trap:</strong> factor a from both x² and x terms first. Keep negative signs and brackets visible.</p>
""",
        "interactive_question": _q("quad_l04_q1", "Complete the square for y = −2x² + 12x − 7. State the vertex, axis of symmetry, and whether the vertex is a minimum or maximum.", "y = −2(x − 3)² + 11; vertex (3, 11); axis x = 3; maximum.", "Factor −2 from quadratic and linear terms: −2(x² − 6x) − 7 = −2[(x − 3)² − 9] − 7.", "Completing the square", [
            _point("form", "Obtains −2(x − 3)² + 11", match_any=["-2(x-3)^2+11", "−2(x-3)^2+11", "-2(x-3)²+11"]),
            _point("vertex", "States vertex (3, 11)", match_any=["(3,11)", "(3, 11)"]),
            _point("axis", "States x = 3", match_any=["x=3", "x = 3"]),
            _point("max", "Identifies a maximum because a is negative", match_groups=[["maximum", "max"], ["negative", "-2", "−2"]]),
        ]),
        "questions": [], "practice_questions": [],
    },
    {
        "id": "quad_l05",
        "title": "Vertex, Minimum/Maximum and Symmetry",
        "kind": "standard",
        "visual_key": "symmetry_explorer",
        "skill_ids": ["vertex", "axis_of_symmetry", "symmetric_points"],
        "explanation": """
<h3>Vertex and axis</h3>
<p>In y = a(x − h)² + k, the square is smallest at x = h, where it is zero. The vertex is (h, k) and the axis of symmetry is the vertical line <strong>x = h</strong>, not y = h.</p>
<p>For y = ax² + bx + c, <strong>h = −b/(2a)</strong> and <strong>k = f(h) = c − b²/(4a)</strong>. Substitute h into the original function as a useful independent check. If a &gt; 0, k is a minimum; if a &lt; 0, k is a maximum.</p>
<h3>Symmetry mechanism</h3>
<p>For x = h + d and x = h − d, the squared term is d² in both cases. Therefore f(h + d) = f(h − d). If the roots are r₁ and r₂, their midpoint is the axis: h = (r₁ + r₂)/2 = −b/(2a).</p>
""",
        "worked_example": """
<h4>Find the vertex and a symmetric point</h4>
<p>For y = x² − 5x + 6, h = −(−5)/(2 × 1) = 2.5 and k = −0.25. The axis is x = 2.5. If the point with x = 1 has y = 2, the point equally far to the right has x = 4 and also y = 2.</p>
""",
        "interactive_question": _q("quad_l05_q1", "For y = x² − 7x + 12, find the axis using the roots, then find the other x-coordinate that has the same y-value as the point at x = 1.", "Roots 3 and 4 give axis x = 3.5. The symmetric partner of x = 1 is x = 6.", "The roots' midpoint is (3 + 4)/2 = 3.5. The reflected coordinate is 2(3.5) − 1 = 6.", "Symmetry", [
            _point("roots", "Finds roots 3 and 4", match_groups=[["3"], ["4"], ["root"]]),
            _point("axis", "Finds axis x = 3.5", match_any=["x=3.5", "x = 3.5"]),
            _point("partner", "Finds symmetric x-coordinate 6", match_groups=[["6"], ["symmetric", "same y", "same distance"]]),
        ]),
        "questions": [], "practice_questions": [],
    },
    {
        "id": "quad_l06",
        "title": "Roots, Intercepts and the Discriminant",
        "kind": "standard",
        "visual_key": "discriminant",
        "skill_ids": ["roots", "intercepts", "discriminant"],
        "explanation": """
<h3>Roots and intercepts</h3>
<p>The x-axis has y = 0, so set the quadratic equal to zero to find roots. The y-intercept is found by setting x = 0, giving (0, c).</p>
<h3>Discriminant</h3>
<p>For ax² + bx + c = 0, <strong>D = b² − 4ac</strong>.</p>
<ul><li>D &gt; 0: two distinct real roots; the parabola crosses the x-axis twice.</li><li>D = 0: one repeated real root; the graph touches the x-axis at the vertex.</li><li>D &lt; 0: no real roots; the graph does not meet the x-axis.</li></ul>
<p>The quadratic formula is x = (−b ± √D)/(2a). The vertex y-coordinate also satisfies k = −D/(4a), connecting roots and turning point.</p>
""",
        "worked_example": """
<h4>Example: x² + 4x + 8 = 0</h4>
<p>D = 4² − 4(1)(8) = 16 − 32 = −16. Since D &lt; 0, there are no real roots and the upward-opening graph stays above the x-axis.</p>
<p>For x² − 5x + 6 = 0, D = 25 − 24 = 1, so there are two roots: x = 2 and x = 3.</p>
""",
        "interactive_question": _q("quad_l06_q1", "Use the discriminant to determine the number of real roots of 2x² + 4x + 5 = 0. Also state the y-intercept of y = 2x² + 4x + 5.", "D = 4² − 4(2)(5) = −24, so there are no real roots; y-intercept (0, 5).", "The discriminant is negative. Substitute x = 0 for the y-intercept.", "Discriminant", [
            _point("D", "Calculates D = −24", match_any=["-24", "−24"]),
            _point("roots", "Concludes no real roots because D < 0", match_groups=[["no real", "zero real"], ["negative", "d<0", "discriminant"]]),
            _point("yint", "Gives y-intercept (0, 5)", match_any=["(0,5)", "(0, 5)"]),
        ]),
        "questions": [], "practice_questions": [],
    },
    {
        "id": "quad_l07",
        "title": "Sketching and Solving Quadratic Equations",
        "kind": "standard",
        "visual_key": "quadratic_features",
        "skill_ids": ["quadratic_sketch", "factorising", "quadratic_formula", "contextual_roots"],
        "explanation": """
<h3>A reliable sketch sequence</h3>
<ol><li>Check a to determine opening.</li><li>Find the vertex and axis.</li><li>Mark y-intercept (0, c).</li><li>Set y = 0 and find any real x-intercepts.</li><li>Use symmetry to add matching points and draw a smooth parabola.</li><li>Check the sketch against the algebra.</li></ol>
<h3>Choose a solving method</h3>
<p><strong>Factorising:</strong> use when factors are simple; a product is zero if at least one factor is zero. <strong>Completing the square:</strong> useful for the vertex form and square-root solutions. <strong>Quadratic formula:</strong> works for every quadratic with a ≠ 0. <strong>Graphical estimate:</strong> useful for approximate roots/intersections, but depends on the graph scale.</p>
<p>In context (for example, height versus time), only keep roots inside the physically valid domain.</p>
""",
        "worked_example": """
<h4>Complete-square solution of x² − 5x + 6 = 0</h4>
<p>(x − 2.5)² − 0.25 = 0 → (x − 2.5)² = 0.25 → x − 2.5 = ±0.5 → x = 2 or x = 3.</p>
<p>The ± is essential because both +0.5 and −0.5 square to 0.25.</p>
""",
        "interactive_question": _q("quad_l07_q1", "Solve 2x² − 8x + 3 = 0 using the quadratic formula. Give exact roots and approximate values to 2 decimal places.", "x = 2 ± √10/2, approximately 0.42 and 3.58.", "x = [8 ± √(64 − 24)]/4 = [8 ± √40]/4 = 2 ± √10/2.", "Solving quadratics", [
            _point("formula", "Uses the quadratic formula with correct substitution", match_groups=[["quadratic formula", "±", "plus or minus"], ["64", "sqrt(40)", "√40", "√10"]]),
            _point("exact", "Gives exact roots 2 ± √10/2", match_any=["2+sqrt(10)/2", "2-sqrt(10)/2", "2±sqrt(10)/2", "2 + √10/2"]),
            _point("approx", "Gives approximately 0.42 and 3.58", match_groups=[["0.42", "0.41"], ["3.58", "3.59"]]),
        ]),
        "questions": [], "practice_questions": [],
    },
    {
        "id": "quad_l08",
        "title": "Quadratic Inequalities and Sign Charts",
        "kind": "standard",
        "visual_key": "sign_chart",
        "skill_ids": ["quadratic_inequality", "sign_chart", "endpoint_inclusion"],
        "explanation": """
<h3>Roots split the number line into sign intervals</h3>
<p>Solving x² − 5x + 6 &gt; 0 asks where the graph is above the x-axis. Factor to (x − 2)(x − 3). The roots divide the line into x &lt; 2, 2 &lt; x &lt; 3 and x &gt; 3. Test one value in each interval: the signs are +, −, +.</p>
<table><tr><th>Opening</th><th>Expression &gt; 0</th><th>Expression &lt; 0</th></tr><tr><td>a &gt; 0</td><td>Outside two roots</td><td>Between two roots</td></tr><tr><td>a &lt; 0</td><td>Between two roots</td><td>Outside two roots</td></tr></table>
<p>This rule assumes two distinct real roots. At a repeated root the sign does not switch; with no real roots the expression keeps the sign of a.</p>
<h3>Strict versus inclusive</h3>
<p>&gt; or &lt; excludes roots; ≥ or ≤ includes them. Never multiply or divide an inequality by a negative number without reversing the inequality sign.</p>
""",
        "worked_example": """
<h4>Two inequalities</h4>
<p>x² − 5x + 6 ≥ 0 gives x ≤ 2 or x ≥ 3. The strict version x² − 5x + 6 &lt; 0 gives 2 &lt; x &lt; 3.</p>
<p>For −x² + 4x − 3 ≥ 0, the roots are 1 and 3; the downward parabola is above or on the axis between them, so 1 ≤ x ≤ 3.</p>
""",
        "interactive_question": _q("quad_l08_q1", "Solve x² − 7x + 12 ≤ 0. Show the factorisation and explain whether the endpoints are included.", "x² − 7x + 12 = (x − 3)(x − 4); solution 3 ≤ x ≤ 4, endpoints included.", "The upward parabola is at or below the axis between its roots; ≤ includes equality at both roots.", "Quadratic inequalities", [
            _point("factor", "Factorises to (x − 3)(x − 4)", match_any=["(x-3)(x-4)", "(x-4)(x-3)"]),
            _point("interval", "Gives 3 ≤ x ≤ 4", match_any=["3<=x<=4", "3≤x≤4", "3 <= x <= 4", "3 to 4 inclusive"]),
            _point("endpoints", "Explains endpoints included because of ≤", match_groups=[["include", "closed", "equal"], ["≤", "<=", "less than or equal"]]),
        ]),
        "questions": [], "practice_questions": [],
    },
    {
        "id": "quad_l09",
        "title": "Graphing Inequalities and Shaded Regions",
        "kind": "standard",
        "visual_key": "inequality_overlap",
        "skill_ids": ["boundary_lines", "test_point", "systems_of_inequalities"],
        "explanation": """
<h3>Two-variable inequalities describe regions</h3>
<p>The boundary y = f(x) separates the plane. For y &gt; f(x), shade above with a dashed boundary; for y ≥ f(x), shade above/on with a solid boundary. For y &lt; f(x), shade below with a dashed boundary; for y ≤ f(x), shade below/on with a solid boundary.</p>
<h3>Test-point method</h3>
<ol><li>Draw each boundary.</li><li>Use dashed for strict &gt;/&lt;; solid for ≥/≤.</li><li>Choose a point not on the boundary (often (0, 0)); substitute it.</li><li>If it satisfies the inequality, shade its side; otherwise shade the opposite side.</li></ol>
<p>A system of inequalities requires every condition to hold. Keep only the overlapping shaded region, not the entire area from either single inequality.</p>
""",
        "worked_example": """
<h4>Overlap: y ≥ 2x − 1 and y ≤ −x + 5</h4>
<p>The first region is above the rising line; the second is below the falling line. Their boundaries meet where 2x − 1 = −x + 5, so x = 2 and y = 3. Both boundaries are included; keep the shared region to the left of (2, 3).</p>
""",
        "interactive_question": _q("quad_l09_q1", "For y ≥ x + 1 and y ≤ −2x + 7, find the boundary intersection and describe the feasible region. State whether each boundary is solid or dashed.", "Intersection (2, 3); shade above/on y = x + 1 and below/on y = −2x + 7, where they overlap; both boundaries solid.", "Equate x + 1 = −2x + 7 to get x = 2 and y = 3. Inclusive inequalities use solid boundaries.", "Graphing inequalities", [
            _point("point", "Finds intersection (2, 3)", match_any=["(2,3)", "(2, 3)"]),
            _point("sides", "Describes above the first line and below the second", match_groups=[["above", "over"], ["below", "under"]]),
            _point("boundaries", "States both boundaries are solid/included", match_groups=[["both", "each"], ["solid", "included"]]),
        ]),
        "questions": [], "practice_questions": [],
    },
    {
        "id": "quad_l10",
        "title": "Simultaneous Equations: Graphs and Algebra",
        "kind": "standard",
        "visual_key": "line_parabola_intersections",
        "skill_ids": ["simultaneous_equations", "line_curve_intersection", "discriminant_intersection"],
        "explanation": """
<h3>Same ordered pair, two equations</h3>
<p>Simultaneous equations require the same (x, y) to satisfy both equations. Graphically it is an intersection. Algebraically, if both equations are given as y = expressions, equate them, solve for x, then substitute to find y.</p>
<h3>Line–line example</h3>
<p>y = 2x + 1 and y = −x + 7 gives 2x + 1 = −x + 7, so x = 2, y = 5. Different non-parallel lines meet once; parallel lines do not meet; identical lines have infinitely many solutions.</p>
<h3>Line–parabola example</h3>
<p>For y = x² and y = x + 2: x² = x + 2 → (x − 2)(x + 1) = 0. The intersections are (2, 4) and (−1, 1). After equating a line and quadratic, the discriminant tells whether there are two, one repeated/tangent, or no real intersections.</p>
<p>For two parabolas, set f(x) = g(x); the x² terms may cancel and leave a linear equation. Use graphs to understand and algebra to calculate exact results, then check each point in both equations.</p>
""",
        "worked_example": """
<h4>Line–parabola intersections</h4>
<p>x² = x + 2 → x² − x − 2 = 0 → (x − 2)(x + 1) = 0. Thus x = 2 or −1. Substitute: y = 4 or 1. The ordered pairs are (2, 4) and (−1, 1).</p>
""",
        "interactive_question": _q("quad_l10_q1", "Find all intersection points of y = x² and y = 2x + 3. Verify each point in both equations.", "x² = 2x + 3 gives (x − 3)(x + 1) = 0, so points (3, 9) and (−1, 1).", "Equate y-values, solve the quadratic, and substitute each root into either original equation.", "Simultaneous equations", [
            _point("equation", "Forms x² − 2x − 3 = 0", match_any=["x^2-2x-3=0", "x²-2x-3=0"]),
            _point("roots", "Finds x = 3 and x = −1", match_groups=[["3"], ["-1", "−1"]]),
            _point("points", "Gives (3, 9) and (−1, 1)", match_groups=[["(3,9)", "(3, 9)"], ["(-1,1)", "(−1,1)", "(-1, 1)"]]),
        ]),
        "questions": [], "practice_questions": [],
    },
    {
        "id": "quad_l11",
        "title": "Symmetry Shortcuts and a Graph-Based Checklist",
        "kind": "standard",
        "visual_key": "symmetry_explorer",
        "skill_ids": ["symmetry_shortcut", "feature_selection", "verification"],
        "explanation": """
<h3>Useful deductions</h3>
<ul><li>If roots are r₁ and r₂, the axis is x = (r₁ + r₂)/2 = −b/(2a).</li><li>If a horizontal line intersects a parabola twice, the two x-coordinates have the axis value as their average.</li><li>Completing the square isolates (x − h)², revealing both the vertex and why points equally spaced from h have equal y-values.</li></ul>
<table><tr><th>Feature</th><th>Fastest reliable method</th><th>Write as</th></tr><tr><td>Opening</td><td>Sign of a</td><td>Up/down; min/max</td></tr><tr><td>Vertex</td><td>Complete square or h = −b/(2a)</td><td>(h, k)</td></tr><tr><td>Axis</td><td>Vertex x-coordinate</td><td>x = h</td></tr><tr><td>x-intercepts</td><td>Set y = 0</td><td>(r₁, 0), (r₂, 0)</td></tr><tr><td>y-intercept</td><td>Set x = 0</td><td>(0, c)</td></tr><tr><td>Number of roots</td><td>D = b² − 4ac</td><td>0, 1 repeated, or 2 real</td></tr></table>
""",
        "worked_example": """
<h4>Recover a symmetric coordinate</h4>
<p>The axis is x = 2.5 and one point at a chosen horizontal level has x = 1. Its partner is x = 2(2.5) − 1 = 4. The midpoint of 1 and 4 is 2.5.</p>
""",
        "interactive_question": _q("quad_l11_q1", "A parabola has roots −2 and 8. Find its axis of symmetry. If a horizontal line crosses it at x = 1 on the left side, find the other x-coordinate.", "Axis x = (−2 + 8)/2 = 3; the other x-coordinate is 5.", "The axis is the midpoint. Reflect x = 1 across x = 3: the partner is 2(3) − 1 = 5.", "Symmetry deductions", [
            _point("axis", "Finds axis x = 3", match_any=["x=3", "x = 3"]),
            _point("partner", "Finds partner x = 5", match_any=["x=5", "x = 5"]),
            _point("reason", "Uses midpoint/reflection reasoning", match_any=["midpoint", "reflect", "equal distance", "symmetr"]),
        ]),
        "questions": [], "practice_questions": [],
    },
    {
        "id": "quad_l12",
        "title": "Integration of Quadratic Curves (Extension)",
        "kind": "standard",
        "visual_key": "integral_under_curve",
        "skill_ids": ["integration_power_rule", "definite_integral", "signed_area"],
        "explanation": """
<div style="border-left:4px solid #B8842E;padding:0.75rem 1rem;background:#FFF7E5;margin-bottom:1rem"><strong>Extension beyond the located school source</strong><br>The master note explicitly marks integration as an extension. Treat this as an introduction to area and accumulation, not as evidence that integration is in the original school revision paper.</div>
<h3>What an integral measures</h3>
<p>A definite integral adds signed area in thin vertical strips. Area above the x-axis contributes positively; area below contributes negatively. A definite integral is not automatically the total geometric area.</p>
<h3>Power rule</h3>
<p>Integration reverses differentiation: increase the exponent by 1 and divide by the new exponent. For n ≠ −1, ∫xⁿ dx = xⁿ⁺¹/(n + 1) + C.</p>
<p>Therefore ∫(ax² + bx + c) dx = (a/3)x³ + (b/2)x² + cx + C. Indefinite integrals include + C; definite integrals evaluate upper bound minus lower bound.</p>
""",
        "worked_example": """
<h4>Find the signed area under y = x² from x = 0 to x = 2</h4>
<p>∫₀² x² dx = [x³/3]₀² = 8/3 − 0 = 8/3 square units. The curve stays above the x-axis here, so signed area equals geometric area.</p>
""",
        "interactive_question": _q("quad_l12_q1", "Evaluate ∫₁³ (2x + 1) dx. Show the antiderivative and the upper-bound-minus-lower-bound calculation.", "Antiderivative x² + x; value (9 + 3) − (1 + 1) = 10.", "Integrate 2x + 1 to obtain x² + x, then evaluate F(3) − F(1).", "Definite integration", [
            _point("anti", "Finds antiderivative x² + x", match_any=["x^2+x", "x²+x"]),
            _point("bounds", "Evaluates F(3) − F(1)", match_groups=[["f(3)", "upper", "9+3", "12"], ["f(1)", "lower", "1+1", "2"]]),
            _point("answer", "Obtains 10", numeric_targets=[{"value": 10, "tolerance": 0}]),
        ]),
        "questions": [], "practice_questions": [],
    },
    {
        "id": "quad_l13",
        "title": "Area Between Curves and Integration Workflow (Extension)",
        "kind": "standard",
        "visual_key": "area_between_curves",
        "skill_ids": ["area_between_curves", "integration_bounds", "upper_minus_lower"],
        "explanation": """
<h3>Area between two curves</h3>
<ol><li>Find the intersection points; their x-coordinates give the bounds.</li><li>Determine which graph is upper on that interval.</li><li>Integrate upper − lower.</li><li>Evaluate F(upper bound) − F(lower bound).</li><li>Check that geometric area is non-negative.</li></ol>
<p>For area against the x-axis, split the interval at any roots if the curve crosses the axis. Signed area and geometric area are different when parts of the curve lie below the axis.</p>
""",
        "worked_example": """
<h4>Area between y = x + 2 and y = x²</h4>
<p>The curves meet at x = −1 and x = 2. On this interval the line is above the parabola.</p>
<p>Area = ∫₋₁²[(x + 2) − x²] dx = [x²/2 + 2x − x³/3]₋₁² = 9/2 square units.</p>
""",
        "interactive_question": _q("quad_l13_q1", "Explain why the area between y = x + 2 and y = x² from x = −1 to x = 2 uses (x + 2) − x². Then state the bounds and the area.", "The line is above the parabola; area = ∫₋₁²[(x + 2) − x²] dx = 9/2 square units.", "Subtract lower curve from upper curve. The intersections set bounds −1 and 2; integration gives 9/2.", "Area between curves", [
            _point("upper_lower", "Uses line minus parabola, x + 2 − x²", match_any=["x+2-x^2", "x+2−x²", "(x+2)-x^2"]),
            _point("bounds", "Uses bounds −1 and 2", match_groups=[["-1", "−1"], ["2"], ["bound", "integral"]]),
            _point("area", "States area 9/2 or 4.5", match_any=["9/2", "4.5", "4.50"]),
        ]),
        "questions": [], "practice_questions": [],
    },
    {
        "id": "quad_l14",
        "title": "Exam Workflow, Precision Traps and Master Practice",
        "kind": "application",
        "visual_key": "quadratic_features",
        "skill_ids": ["exam_workflow", "algebraic_precision", "mixed_transfer"],
        "explanation": """
<h3>Method selection</h3>
<table><tr><th>Question asks…</th><th>Start with…</th><th>Then…</th></tr>
<tr><td>Vertex / min / max</td><td>Complete square or h = −b/(2a)</td><td>Find k; use sign of a</td></tr>
<tr><td>Line of symmetry</td><td>x = −b/(2a)</td><td>Check vertex x-coordinate</td></tr>
<tr><td>Sketch a quadratic</td><td>a, vertex, intercepts, roots</td><td>Add points using symmetry</td></tr>
<tr><td>Solve quadratic equation</td><td>Set expression = 0</td><td>Factor, complete square or formula</td></tr>
<tr><td>Quadratic inequality</td><td>Find roots</td><td>Sign chart and endpoint rules</td></tr>
<tr><td>Simultaneous solutions</td><td>Equate y-expressions</td><td>Solve x, find y, check both</td></tr>
<tr><td>Shade an inequality</td><td>Draw boundary</td><td>Solid/dashed, test point, shade</td></tr>
<tr><td>Area under/between curves</td><td>Find interval/intersections</td><td>Signed function or upper − lower</td></tr></table>
<h3>Precision traps</h3>
<ul><li>Keep the minus in h = −b/(2a) visible; bracket negative coefficients.</li><li>Axis of symmetry is x = h, not (h, k) and not y = h.</li><li>In a(x − h)² + k, read the bracket sign carefully.</li><li>Keep exact fractions/radicals until final rounding.</li><li>Roots are where y = 0; the vertex is the turning point.</li><li>Inclusive endpoints for ≥/≤; excluded endpoints for &gt;/&lt;.</li><li>Use a test point rather than assuming which side to shade.</li><li>An intersection answer needs an ordered pair; substitute to find y and check both equations.</li><li>For indefinite integrals include + C; for definite integrals compute F(upper) − F(lower).</li></ul>
<p><strong>Five-second audit:</strong> signs → correct form → boundary/endpoints → units/rounding → substitution check.</p>
<h3>Source alignment and final mental model</h3>
<p>The supplied note's running example, y = x² − 5x + 6, aligns with the school G9A Revision Practice Paper. Its completing-the-square sequence aligns with the PMT Education worksheet, <em>GCSE Maths – Algebra: Completing the Square (Higher Only)</em>. Integration is an explicitly added extension in the note, not a topic evidenced by those located source materials.</p>
<p><strong>Final mental model:</strong> the equation determines a parabola; completing the square exposes its symmetry; roots locate where y = 0; inequalities select intervals or regions; simultaneous equations locate shared points; integration measures signed accumulation and area.</p>
<p>Source reference: <a href="https://pmt.physicsandmathstutor.com/download/Maths/GCSE/Worksheets/Algebra/Graphs/c.%20Completing%20the%20Square%20%28H%29.pdf">PMT Education — Completing the Square (Higher Only)</a>.</p>
""",
        "worked_example": """
<h4>Apply the five-second audit to a sketch</h4>
<p>For y = x² − 4x + 3: y = (x − 2)² − 1 = (x − 1)(x − 3). It opens up; roots are (1, 0), (3, 0); y-intercept (0, 3); vertex (2, −1); axis x = 2. Check root midpoint: (1 + 3)/2 = 2.</p>
""",
        "interactive_question": _q("quad_l14_q1", "A learner says the vertex of y = −2(x + 1)² + 5 is (1, 5), and the symmetry line is y = −1. Correct both errors and explain the sign interpretation.", "Vertex (−1, 5), axis x = −1. The bracket is x − (−1), so h = −1; the axis is vertical.", "Read x + 1 as x − (−1), and remember the axis is x = h. Negative a opens the parabola down, making 5 a maximum.", "Exam error diagnosis", [
            _point("vertex", "Corrects vertex to (−1, 5)", match_any=["(-1,5)", "(−1,5)", "(-1, 5)"]),
            _point("axis", "Corrects line of symmetry to x = −1", match_any=["x=-1", "x=−1", "x = -1", "x = −1"]),
            _point("reason", "Explains sign inside bracket and downward opening", match_groups=[["x+1", "x − (−1)", "x-(-1)"], ["down", "negative", "maximum"]]),
        ]),
        "questions": [], "practice_questions": [],
    },
]


PRACTICE_SET = [
    _q("quad_master_q01", "For y = 2x² − 8x + 3, find the vertex, axis of symmetry and minimum/maximum value.", "y = 2(x − 2)² − 5; vertex (2, −5); axis x = 2; minimum −5.", "Complete the square or use h = 8/4 = 2 and substitute to get k = −5.", "Vertex and extrema", [
        _point("form", "Gives 2(x − 2)² − 5", match_any=["2(x-2)^2-5", "2(x-2)²-5"]),
        _point("vertex_axis", "Gives vertex (2, −5) and axis x = 2", match_groups=[["(2,-5)", "(2,−5)"], ["x=2", "x = 2"]]),
        _point("minimum", "Identifies minimum value −5", match_groups=[["minimum", "min"], ["-5", "−5"]]),
    ]),
    _q("quad_master_q02", "Complete the square for y = −2x² + 12x − 7 and state its vertex and opening.", "y = −2(x − 3)² + 11; vertex (3, 11); opens down.", "Factor −2, complete x² − 6x = (x − 3)² − 9, then simplify.", "Completing the square", [
        _point("form", "Gives −2(x − 3)² + 11", match_any=["-2(x-3)^2+11", "−2(x-3)^2+11"]),
        _point("vertex", "Gives vertex (3, 11)", match_any=["(3,11)", "(3, 11)"]),
        _point("opening", "States it opens down", match_any=["opens down", "downward", "maximum"]),
    ]),
    _q("quad_master_q03", "Find the x-intercepts of y = x² − 7x + 12. Then state where y ≤ 0.", "Roots 3 and 4; y ≤ 0 for 3 ≤ x ≤ 4.", "Factor (x − 3)(x − 4). The upward parabola is below/on the axis between roots.", "Roots and inequalities", [
        _point("roots", "Finds roots 3 and 4", match_groups=[["3"], ["4"], ["root"]]),
        _point("interval", "Gives 3 ≤ x ≤ 4", match_any=["3<=x<=4", "3≤x≤4", "3 <= x <= 4"]),
    ]),
    _q("quad_master_q04", "Use the discriminant to determine how many real roots x² + 4x + 8 = 0 has.", "D = −16 < 0; no real roots.", "D = 4² − 4(1)(8) = 16 − 32 = −16.", "Discriminant", [
        _point("value", "Calculates D = −16", match_any=["-16", "−16"]),
        _point("conclusion", "Concludes no real roots", match_groups=[["no real", "zero real"], ["root", "solution"]]),
    ]),
    _q("quad_master_q05", "Solve −x² + 4x − 3 > 0.", "1 < x < 3.", "Factor −(x − 1)(x − 3); the downward parabola is positive between roots, and strict > excludes endpoints.", "Quadratic inequalities", [
        _point("roots", "Finds roots 1 and 3", match_groups=[["1"], ["3"], ["root"]]),
        _point("interval", "Gives 1 < x < 3", match_any=["1<x<3", "1 < x < 3"]),
    ]),
    _q("quad_master_q06", "Find the intersection points of y = x² and y = 2x + 3.", "Points (3, 9) and (−1, 1).", "Equate to x² − 2x − 3 = 0 = (x − 3)(x + 1); substitute x = 3 and −1.", "Simultaneous equations", [
        _point("roots", "Finds x = 3 and x = −1", match_groups=[["3"], ["-1", "−1"]]),
        _point("points", "Gives both ordered pairs", match_groups=[["(3,9)", "(3, 9)"], ["(-1,1)", "(−1,1)", "(-1, 1)"]]),
    ]),
    _q("quad_master_q07", "Sketch y = x² − 4x + 3 and label its roots, y-intercept, vertex and axis.", "Opens up; roots (1, 0), (3, 0); y-intercept (0, 3); vertex (2, −1); axis x = 2.", "Write y = (x − 2)² − 1 = (x − 1)(x − 3), then mark intercepts and symmetry.", "Quadratic sketch", [
        _point("roots", "Gives roots (1, 0) and (3, 0)", match_groups=[["(1,0)", "(1, 0)"], ["(3,0)", "(3, 0)"]]),
        _point("yint", "Gives y-intercept (0, 3)", match_any=["(0,3)", "(0, 3)"]),
        _point("vertex_axis", "Gives vertex (2, −1) and axis x = 2", match_groups=[["(2,-1)", "(2,−1)", "(2, -1)"], ["x=2", "x = 2"]]),
        _point("opening", "States opens up", match_any=["opens up", "upward"]),
    ]),
    _q("quad_master_q08", "Find the intersection point of y = x + 1 and y = −2x + 7, then describe the region satisfying y ≥ x + 1 and y ≤ −2x + 7.", "Boundaries meet at (2, 3); region above/on the first line and below/on the second, with both boundaries included.", "Equate x + 1 = −2x + 7 to get x = 2 and y = 3; the feasible region is the overlap.", "Graphing inequalities", [
        _point("point", "Finds intersection (2, 3)", match_any=["(2,3)", "(2, 3)"]),
        _point("region", "Identifies above first and below second", match_groups=[["above"], ["below"]]),
        _point("boundary", "States both boundaries included", match_groups=[["both", "boundaries"], ["solid", "included"]]),
    ]),
    _q("quad_master_q09", "Extension: evaluate ∫₁³ (2x + 1) dx.", "10.", "An antiderivative is x² + x. Evaluate (9 + 3) − (1 + 1) = 10.", "Definite integration", [
        _point("anti", "Gives antiderivative x² + x", match_any=["x^2+x", "x²+x"]),
        _point("value", "Obtains 10", numeric_targets=[{"value": 10, "tolerance": 0}]),
    ]),
    _q("quad_master_q10", "Extension: find the area between y = x + 2 and y = x² from x = −1 to x = 2.", "9/2 square units.", "Area = ∫₋₁²(x + 2 − x²) dx = 9/2 because the line is the upper curve throughout the interval.", "Area between curves", [
        _point("integrand", "Uses upper − lower: x + 2 − x²", match_any=["x+2-x^2", "x+2−x²"]),
        _point("bounds", "Uses bounds −1 and 2", match_groups=[["-1", "−1"], ["2"], ["bound", "integral"]]),
        _point("area", "Obtains 9/2 or 4.5", match_any=["9/2", "4.5", "4.50"]),
    ]),
]

LESSONS[0]["diagnostic"] = COURSE_DIAGNOSTIC
LESSONS[-1]["practice_questions"] = PRACTICE_SET
LESSONS[-1]["interactive_question"] = PRACTICE_SET[0]
LESSONS[-1]["questions"] = PRACTICE_SET

# Explicit extra items keep practice tied to each lesson rather than reusing an unrelated model answer.
_EXTRA_PRACTICE = {
    "quad_l01": [
        _q("quad_l01_q2", "For y = 4x² + x − 1, give the y-intercept and second difference for unit x-steps.", "y-intercept (0, −1); second difference 8.", "Set x=0 for the intercept and use 2a=8.", "Quadratic patterns", [_point("int","Gives (0, −1)",match_any=["(0,-1)","(0, −1)"]),_point("diff","Gives second difference 8",match_groups=[["second difference"],["8"]])]),
        _q("quad_l01_q3", "Explain why y = 5x² + 3x + 1 is quadratic but y = 3x + 1 is linear.", "The first has highest power x² and a ≠ 0; the second has no x² term and is linear.", "The highest power is 2 only in the first expression.", "Quadratic definition", [_point("power","Identifies highest power x²",match_any=["highest power","power 2","x^2 term"]),_point("linear","Explains second expression has no x² term",match_groups=[["no x^2","no x²","without x^2"],["linear","power 1"]])]),
    ],
    "quad_l02": [
        _q("quad_l02_q2", "For y = 2(x + 1)² − 3, state the vertex, axis, opening and y-intercept.", "Vertex (−1, −3); axis x = −1; opens up; y-intercept (0, −1).", "Read vertex form directly; at x=0, y=2(1)−3=−1.", "Vertex form", [_point("vertex","Gives vertex (−1, −3)",match_any=["(-1,-3)","(−1, −3)"]),_point("axis","Gives x = −1",match_any=["x=-1","x=−1","x = −1"]),_point("opening","States opens up",match_any=["opens up","upward"]),_point("int","Gives y-intercept (0, −1)",match_any=["(0,-1)","(0, −1)"])]),
        _q("quad_l02_q3", "Write y = x² − 9 in factor form and state its roots.", "y = (x − 3)(x + 3); roots x = −3 and x = 3.", "Use difference of squares: x²−9=(x−3)(x+3).", "Factor form", [_point("factor","Gives (x − 3)(x + 3)",match_any=["(x-3)(x+3)","(x+3)(x-3)"]),_point("roots","States both roots −3 and 3",match_groups=[["-3","−3"],["3"]])]),
    ],
    "quad_l03": [
        _q("quad_l03_q2", "Describe the vertex and opening of y = −3(x − 2)² + 1, and compare its width with y = −(x − 2)² + 1.", "Vertex (2, 1); both open down; the coefficient −3 curve is narrower.", "Both coefficients are negative; |−3| is greater than 1, so the curve is narrower.", "Opening and width", [_point("vertex","Gives (2, 1)",match_any=["(2,1)","(2, 1)"]),_point("opening","States both open down",match_any=["both open down","both downward"]),_point("width","States coefficient magnitude 3 makes it narrower",match_groups=[["narrow"],["3","absolute value"]])]),
        _q("quad_l03_q3", "For y = 0.25x² − 4, state opening, vertex and y-intercept.", "Opens up; vertex (0, −4); y-intercept (0, −4); it is wider than y = x².", "The vertex form is 0.25(x−0)²−4; 0 < |a| < 1 makes it wider.", "Shape and intercept", [_point("opening","States opens up",match_any=["opens up","upward"]),_point("vertex","Gives vertex (0, −4)",match_any=["(0,-4)","(0, −4)"]),_point("width","States it is wider/flatter",match_any=["wider","flatter"])])
    ],
    "quad_l04": [
        _q("quad_l04_q2", "Complete the square for y = x² + 6x + 2 and state the vertex.", "y = (x + 3)² − 7; vertex (−3, −7).", "Half 6 to get 3: (x+3)²−9+2=(x+3)²−7.", "Completing the square", [_point("form","Gives (x + 3)² − 7",match_any=["(x+3)^2-7","(x+3)²-7"]),_point("vertex","Gives vertex (−3, −7)",match_any=["(-3,-7)","(−3, −7)"])]),
        _q("quad_l04_q3", "Complete the square for y = 2x² + 8x + 1.", "y = 2(x + 2)² − 7.", "Factor 2: 2(x²+4x)+1=2[(x+2)²−4]+1.", "General completing square", [_point("form","Gives 2(x + 2)² − 7",match_any=["2(x+2)^2-7","2(x+2)²-7"]),_point("method","Factors 2 before completing square",match_any=["factor 2","factor out 2","2(x^2+4x)","2(x²+4x)"])])
    ],
    "quad_l05": [
        _q("quad_l05_q2", "A parabola has axis x = 4. One point on a horizontal chord has x = 1. Find the other x-coordinate.", "x = 7.", "The axis is the midpoint: (1+x)/2=4, so x=7.", "Symmetric coordinates", [_point("partner","Gives x = 7",match_any=["x=7","x = 7"]),_point("reason","Uses midpoint or equal distance",match_any=["midpoint","equal distance","reflect"]) ]),
        _q("quad_l05_q3", "For y = 2(x − 3)² − 5, state the vertex, axis and minimum value.", "Vertex (3, −5); axis x = 3; minimum −5.", "The square is minimized at x=3 and coefficient 2 is positive.", "Vertex and minimum", [_point("vertex","Gives (3, −5)",match_any=["(3,-5)","(3, −5)"]),_point("axis","Gives x = 3",match_any=["x=3","x = 3"]),_point("minimum","States minimum −5",match_groups=[["minimum","min"],["-5","−5"]])])
    ],
    "quad_l06": [
        _q("quad_l06_q2", "Classify the number of real roots of x² − 6x + 9 = 0 using the discriminant.", "D = 36 − 36 = 0; one repeated root x = 3; the curve touches the x-axis.", "Zero discriminant means one repeated real root.", "Discriminant cases", [_point("D","Gives D = 0",match_any=["d=0","d = 0","discriminant is zero"]),_point("case","States one repeated root / tangent contact",match_any=["repeated root","one root","touches","tangent"]) ]),
        _q("quad_l06_q3", "For y = −x² + 2x + 8, find the y-intercept and discriminant.", "y-intercept (0, 8); D = 2² − 4(−1)(8) = 36 > 0, so two real roots.", "Set x=0 for the intercept; calculate D with a=−1, b=2, c=8.", "Roots and intercepts", [_point("int","Gives (0, 8)",match_any=["(0,8)","(0, 8)"]),_point("D","Gives D = 36",match_any=["36"]),_point("count","Concludes two real roots",match_any=["two real","2 real","two roots"])])
    ],
    "quad_l07": [
        _q("quad_l07_q2", "Solve x² + x − 6 = 0 by factorising.", "x = 2 or x = −3.", "Factor (x+3)(x−2)=0, then set each factor to zero.", "Factorising", [_point("factor","Gives (x + 3)(x − 2) = 0",match_any=["(x+3)(x-2)","(x-2)(x+3)"]),_point("roots","Gives roots 2 and −3",match_groups=[["2"],["-3","−3"]])]),
        _q("quad_l07_q3", "A height model is h = −5t² + 20t, where t is time in seconds. At what times is the height zero, and which root is the launch time?", "t = 0 and t = 4; t = 0 is launch, and t = 4 is the later return to ground.", "Factor h=−5t(t−4)=0. Interpret roots using the time domain.", "Contextual roots", [_point("roots","Finds t = 0 and t = 4",match_groups=[["t=0","t = 0"],["t=4","t = 4"]]),_point("context","Interprets t = 0 as launch and t = 4 as return",match_groups=[["launch","start"],["return","ground","lands"]])])
    ],
    "quad_l08": [
        _q("quad_l08_q2", "Solve x² − 5x + 6 < 0 and explain the endpoints.", "2 < x < 3; endpoints excluded because the inequality is strict.", "The upward parabola is negative between roots 2 and 3; strict < excludes equality.", "Sign charts", [_point("interval","Gives 2 < x < 3",match_any=["2<x<3","2 < x < 3"]),_point("endpoints","Excludes endpoints because inequality is strict",match_groups=[["exclude","open"],["strict","<"]])]),
        _q("quad_l08_q3", "Solve −x² + 4x − 3 ≥ 0.", "1 ≤ x ≤ 3.", "Roots are 1 and 3. The downward parabola lies above/on the axis between them; ≥ includes the roots.", "Downward quadratic inequality", [_point("roots","Finds roots 1 and 3",match_groups=[["1"],["3"],["root"]]),_point("interval","Gives 1 ≤ x ≤ 3",match_any=["1<=x<=3","1≤x≤3","1 <= x <= 3"])])
    ],
    "quad_l09": [
        _q("quad_l09_q2", "For y < 2x − 1, specify which side is shaded and how the boundary is drawn.", "Shade below y = 2x − 1; draw a dashed boundary.", "The inequality is strict and the y-coordinate must be below the line value.", "Boundary and shading", [_point("side","States shade below",match_any=["below","under"]),_point("style","States dashed boundary because < is strict",match_groups=[["dashed","broken"],["strict","<","not included"]])]),
        _q("quad_l09_q3", "Use (0, 0) as a test point for y ≥ 2x − 1. Does it satisfy the inequality, and which side should be shaded?", "0 ≥ −1 is true; shade the side containing (0, 0), above/on the boundary.", "Substitute x=0,y=0, giving 0≥−1.", "Test-point method", [_point("substitution","Checks 0 ≥ −1",match_any=["0>=-1","0 ≥ −1","0 >= -1"]),_point("side","Shades side containing origin, above/on line",match_groups=[["origin","(0,0)","(0, 0)"],["above","on"],["shade"]])])
    ],
    "quad_l10": [
        _q("quad_l10_q2", "Solve y = 2x + 1 and y = −x + 7 simultaneously.", "Intersection (2, 5).", "Equate: 2x+1=−x+7, so x=2 and y=5.", "Line–line systems", [_point("x","Finds x = 2",match_any=["x=2","x = 2"]),_point("y","Finds y = 5",match_any=["y=5","y = 5"]),_point("point","Gives (2, 5)",match_any=["(2,5)","(2, 5)"])]),
        _q("quad_l10_q3", "Do y = x² and y = x² + 2 intersect? Justify algebraically.", "No real intersections: x² = x² + 2 implies 0 = 2, impossible.", "Equating the equations cancels x² and leaves a contradiction.", "Intersection count", [_point("equation","Equates and cancels x² terms",match_any=["x^2=x^2+2","x²=x²+2","cancel"]),_point("conclusion","States no intersection/no solution",match_any=["no intersection","no solution","impossible"])])
    ],
    "quad_l11": [
        _q("quad_l11_q2", "If a parabola has roots 4 and 10, find the axis of symmetry and vertex x-coordinate.", "Axis x = 7; vertex x-coordinate 7.", "The axis is the midpoint (4+10)/2=7.", "Root midpoint", [_point("midpoint","Calculates (4 + 10)/2 = 7",match_any=["(4+10)/2","7"]),_point("axis","States x = 7",match_any=["x=7","x = 7"])]),
        _q("quad_l11_q3", "A parabola's axis is x = 2.5 and a point has x = 0.5. Find the symmetric point's x-coordinate and state the shared y-value relationship.", "Partner x = 4.5; the two points have equal y-values.", "Reflect across the axis: x_partner = 2(2.5)−0.5 = 4.5.", "Symmetry", [_point("partner","Finds 4.5",match_any=["4.5","4.50"]),_point("equal_y","States equal y-values",match_any=["same y","equal y","same output"])])
    ],
    "quad_l12": [
        _q("quad_l12_q2", "Find the indefinite integral ∫(3x² − 4x + 5) dx.", "x³ − 2x² + 5x + C.", "Integrate term by term: 3x²→x³, −4x→−2x², and 5→5x; add C.", "Power rule", [_point("terms","Integrates to x³ − 2x² + 5x",match_any=["x^3-2x^2+5x","x³-2x²+5x"]),_point("constant","Includes + C",match_any=["+c","+ c","constant of integration"]) ]),
        _q("quad_l12_q3", "Explain the difference between signed area and total geometric area when a curve lies below the x-axis.", "Signed area below the x-axis contributes negatively; total geometric area counts area as positive and may require splitting at roots.", "An integral adds signed contributions, while geometric area is non-negative.", "Signed area", [_point("sign","States below-axis contribution is negative",match_groups=[["below","under"],["negative","subtract"]]),_point("geometric","States geometric area is positive / split at roots",match_groups=[["geometric","total area"],["positive","root","split"]])])
    ],
    "quad_l13": [
        _q("quad_l13_q2", "State the five steps for finding area between two curves.", "Find intersections/bounds; identify upper curve; integrate upper minus lower; evaluate upper bound minus lower bound; check area is non-negative.", "The bounds come from intersections, and the integrand is upper−lower.", "Area workflow", [_point("bounds","Finds intersections/bounds first",match_any=["intersection","bounds"]),_point("upper_lower","Uses upper minus lower",match_any=["upper minus lower","upper-lower","upper−lower"]),_point("evaluate","Evaluates upper bound minus lower bound",match_groups=[["upper bound","upper"],["lower bound","lower"],["subtract","minus"]]),_point("check","Checks area is non-negative",match_any=["non-negative","nonnegative","positive area"]) ]),
        _q("quad_l13_q3", "Why should the interval be split when finding geometric area under a curve that crosses the x-axis?", "The signed integral changes sign at a root, but geometric area must remain positive, so split at each crossing root and add the absolute areas.", "The roots mark where the sign changes.", "Area and roots", [_point("root","Mentions splitting at roots/intercepts",match_any=["split at roots","crossing root","x-intercept"]),_point("sign","Distinguishes negative signed area from positive geometric area",match_groups=[["signed","integral"],["negative"],["geometric","total"],["positive","absolute"]]) ])
    ],
}

for _lesson in LESSONS:
    if _lesson["id"] in _EXTRA_PRACTICE:
        _lesson["practice_questions"] = [_lesson["interactive_question"]] + _EXTRA_PRACTICE[_lesson["id"]]
        _lesson["questions"] = _lesson["practice_questions"]

QUADRATICS_COURSE = {
    "id": "quadratics_graphs",
    "title": "Quadratics, Graphs & Integration",
    "short_description": (
        "Develop a visual, first-principles understanding of quadratic graphs, "
        "completing the square, roots, inequalities, simultaneous equations, and integration."
    ),
    "difficulty": "Intermediate",
    "topic_label": "Quadratics & Graphs",
    "category_id": "academics",
    "subject_id": "mathematics",
    "level": "Grade 9–10",
    "curriculum": "Cambridge-aligned mathematics; integration marked as extension",
    "course_version": "1.0.0",
    "lessons": LESSONS,
}
__all__ = ["QUADRATICS_COURSE", "LESSONS", "COURSE_DIAGNOSTIC", "PRACTICE_SET"]
