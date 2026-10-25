"""Stable skill taxonomy for the initial Grade 7–9 mathematics VQE pilot.

Grade bands express intended lower-secondary use, including prerequisite
review. They are product-level planning tags, not official curriculum codes.
Curriculum mappings must be reviewed before any external alignment claim.
"""

SKILLS = {
    "math.number.fraction_representation": {
        "label": "Fraction representation and equivalence",
        "strand": "Number",
        "grade_bands": [7, 8, 9],
        "prerequisites": [],
        "learning_objectives": [
            "Interpret numerator and denominator",
            "Represent parts of an equal whole",
            "Recognise equivalent fractions",
        ],
        "common_misconceptions": [
            "Reversing numerator and denominator",
            "Treating the denominator as the number of parts held",
        ],
        "curriculum_alignment": "Provisional lower-secondary mapping; not an official curriculum code",
    },
    "math.number.fraction_operations": {
        "label": "Fraction operations",
        "strand": "Number",
        "grade_bands": [7, 8, 9],
        "prerequisites": ["math.number.fraction_representation"],
        "learning_objectives": [
            "Add fractions with like denominators",
            "Represent fraction sums using equivalent values",
            "Subtract fractions using a common denominator",
        ],
        "common_misconceptions": [
            "Adding or subtracting denominators directly",
            "Failing to use a common denominator",
        ],
        "curriculum_alignment": "Provisional lower-secondary mapping; not an official curriculum code",
    },
    "math.algebra.variables_expressions": {
        "label": "Variables and expressions",
        "strand": "Algebra",
        "grade_bands": [7, 8, 9],
        "prerequisites": [],
        "learning_objectives": [
            "Interpret a letter as a variable",
            "Distinguish variables from constants and operators",
            "Translate simple verbal relationships into expressions",
        ],
        "common_misconceptions": [
            "Treating a variable as a fixed label",
            "Confusing addition with multiplication in expressions",
        ],
        "curriculum_alignment": "Provisional lower-secondary mapping; not an official curriculum code",
    },
    "math.algebra.linear_equations": {
        "label": "Linear equations",
        "strand": "Algebra",
        "grade_bands": [7, 8, 9],
        "prerequisites": ["math.algebra.variables_expressions"],
        "learning_objectives": [
            "Solve one-step equations using inverse operations",
            "Solve simple multi-step linear equations",
            "Check a solution by substitution",
        ],
        "common_misconceptions": [
            "Applying an operation to only one side",
            "Choosing the wrong inverse operation",
            "Losing signs when rearranging",
        ],
        "curriculum_alignment": "Provisional lower-secondary mapping; not an official curriculum code",
    },
    "math.problem_solving.expression_translation": {
        "label": "Translating words into expressions",
        "strand": "Problem-solving",
        "grade_bands": [7, 8, 9],
        "prerequisites": ["math.algebra.variables_expressions"],
        "learning_objectives": [
            "Identify quantities and relationships in a short word problem",
            "Translate verbal relationships into mathematical expressions",
            "Explain why an operation matches the situation",
        ],
        "common_misconceptions": [
            "Choosing an operation from a keyword without checking meaning",
            "Reversing the order in expressions such as 'less than'",
        ],
        "curriculum_alignment": "Provisional lower-secondary mapping; not an official curriculum code",
    },
    "math.geometry.angle_facts": {
        "label": "Angle facts",
        "strand": "Geometry and Measure",
        "grade_bands": [7, 8, 9],
        "prerequisites": [],
        "learning_objectives": [
            "Use angles on a straight line",
            "Use angles around a point",
            "Use vertically opposite angles",
            "Use the interior angle sum of a triangle",
        ],
        "common_misconceptions": [
            "Using 360 degrees instead of 180 degrees, or vice versa",
            "Assuming vertically opposite angles add to 180 degrees",
        ],
        "curriculum_alignment": "Provisional lower-secondary mapping; not an official curriculum code",
    },
    "math.problem_solving.linear_cost_models": {
        "label": "Linear cost models",
        "strand": "Problem-solving",
        "grade_bands": [7, 8, 9],
        "prerequisites": [
            "math.algebra.variables_expressions",
            "math.problem_solving.expression_translation",
        ],
        "learning_objectives": [
            "Represent a fixed fee plus a per-unit cost",
            "Calculate a multi-step cost",
            "Work within a whole-number budget constraint",
        ],
        "common_misconceptions": [
            "Applying a fixed fee per unit",
            "Ignoring a constraint after calculating a ratio",
        ],
        "curriculum_alignment": "Provisional lower-secondary mapping; not an official curriculum code",
    },
}
