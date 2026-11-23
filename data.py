"""
data.py — Static dummy content for Vocogni Version 1.

This file holds all course/lesson/question content as plain data structures,
kept separate from UI code (see spec section 6: "Use dummy course data stored
separately from the UI where practical").

In a future version, COURSES could be loaded from a real database or CMS
instead of being hard-coded here — nothing outside this file needs to change
as long as the same shape (see the docstrings below) is preserved.

Question schema
----------------
Multiple choice:
    {
        "id": str,
        "type": "mc",
        "prompt": str,
        "options": list[str],
        "answer": str,           # must match one of "options" exactly
        "explanation": str,
        "mistake_tag": str,      # recorded when answered incorrectly
    }

Numeric:
    {
        "id": str,
        "type": "numeric",
        "prompt": str,
        "answer": float,
        "tolerance": float,      # allowed +/- error
        "whole_number": bool,    # controls input step/format
        "input_hint": str,
        "explanation": str,
        "mistake_tag": str,
    }

Lesson schema
-------------
{
    "id": str,
    "title": str,
    "kind": "standard" | "application",
    "explanation": str,          # teaching text, or challenge scenario text
    "questions": list[question],
}

Course schema
-------------
{
    "id": str,
    "title": str,
    "short_description": str,
    "difficulty": str,
    "topic_label": str,          # display name used on the Progress page
    "lessons": list[lesson],
}
"""

APPLICATION_MISTAKE_TAG = "Application / transfer error"


COURSES = {
    "fractions": {
        "id": "fractions",
        "title": "Simple Fractions",
        "short_description": "Understand how fractions represent parts of a whole, then compare and calculate with them in everyday contexts.",
        "difficulty": "Beginner",
        "topic_label": "Fractions",
        "lessons": [
            {
                "id": "fractions_l1",
                "title": "Understanding Fractions",
                "kind": "standard",
                "explanation": (
                    "A fraction represents an amount relative to one whole (or a group treated as the whole). "
                    "It has two parts:\n\n"
                    "**Numerator (top):** how many equal parts are being counted.\n"
                    "**Denominator (bottom):** how many equal parts make one whole.\n\n"
                    "The parts must be equal-sized. If one pizza is split into 4 equal slices and 3 are counted, "
                    "the amount is **3/4**. The denominator 4 describes the partition of that one pizza; it does not mean "
                    "there are four pizzas.\n\n"
                    "A fraction can also be greater than 1. For example, **7/5** means seven fifths: "
                    "five fifths make one whole, with two fifths left, so 7/5 = 1 2/5.\n\n"
                    "Different fractions can represent the same amount. **3/4** and **6/8** are equivalent because "
                    "the second uses twice as many parts, each half as large."
                ),
                "worked_example": (
                    "**Example 1: reading 3/5**\n"
                    "1. Treat the rectangle as one whole.\n"
                    "2. Divide it into 5 equal-sized sections; unequal sections would not represent fifths.\n"
                    "3. Count 3 sections. The numerator is 3 because 3 sections are selected.\n"
                    "4. The denominator is 5 because the whole is partitioned into 5 equal sections.\n"
                    "So the selected amount is **3/5**.\n\n"
                    "**Example 2: a fraction greater than one**\n"
                    "For **7/5**, count seven fifth-sized parts. Five fifths equal one whole, leaving two fifths: "
                    "7/5 = 5/5 + 2/5 = **1 2/5**. A numerator can be greater than the denominator when the amount "
                    "includes more than one whole.\n\n"
                    "**Example 3: equivalent fractions**\n"
                    "For **3/4** and **6/8**, imagine the same whole:\n"
                    "1. Divide it into 4 equal parts and count 3: 3/4.\n"
                    "2. Divide each of those 4 parts in half, making 8 equal parts in total.\n"
                    "3. The counted amount is now 6 of those 8 parts: 6/8.\n"
                    "The whole amount did not change, so **3/4 = 6/8**. Both numerator and denominator were multiplied by 2.\n\n"
                    "**Common mistake:** changing only one part of the fraction changes the amount. For example, 3/4 is not equal to 3/8 because the whole is divided into smaller parts while the counted number stays 3."
                ),
                "interactive_question": {
                    "id": "fractions_l1_screen3",
                    "type": "mc",
                    "prompt": "A pizza is split into 8 equal slices and you eat 5. Which fraction represents the slices eaten?",
                    "options": ["5/8", "8/5", "3/8", "5/5"],
                    "answer": "5/8",
                    "explanation": "Five slices were eaten out of eight equal slices, so the fraction is 5/8.",
                    "mistake_tag": "Representing fractions",
                },
                "diagnostic": {
                    "version": 1,
                    "questions": [
                        {
                            "id": "fractions_l1_d1",
                            "type": "mc",
                            "stage": "prerequisite",
                            "skill_tag": "Meaning of the denominator",
                            "prompt": "If a whole is divided into 4 parts to represent fourths, what must be true about those parts?",
                            "options": [
                                "All 4 parts must be equal-sized",
                                "One part must be larger than the other 3",
                                "The parts can be any sizes as long as there are 4",
                                "Each part must be a separate whole"
                            ],
                            "answer": "All 4 parts must be equal-sized",
                            "explanation": "A denominator of 4 means the whole is partitioned into 4 equal-sized parts. If the parts are unequal, they cannot all represent fourths, even if there are 4 pieces.",
                            "mistake_tag": "Meaning of the denominator"
                        },
                        {
                            "id": "fractions_l1_d2",
                            "type": "mc",
                            "stage": "level_1",
                            "skill_tag": "Representing fractions",
                            "prompt": "A shape is divided into 5 equal parts. You are counting 3 of those parts. Which fraction describes the amount counted?",
                            "options": [
                                "3/5",
                                "5/3",
                                "3/3",
                                "2/5"
                            ],
                            "answer": "3/5",
                            "explanation": "The numerator counts the parts considered; the denominator counts all equal parts.",
                            "mistake_tag": "Representing fractions"
                        },
                        {
                            "id": "fractions_l1_d3",
                            "type": "mc",
                            "stage": "level_2",
                            "skill_tag": "Equivalent fractions",
                            "prompt": "Which fraction is equivalent to 2/3?",
                            "options": [
                                "4/6",
                                "2/6",
                                "3/4",
                                "4/5"
                            ],
                            "answer": "4/6",
                            "explanation": "2/3 and 4/6 describe the same amount. Multiplying both the numerator and denominator by 2 makes twice as many parts, each half the original size, so the total amount stays unchanged.",
                            "mistake_tag": "Equivalent fractions"
                        },
                        {
                            "id": "fractions_l1_d4",
                            "type": "mc",
                            "stage": "level_3",
                            "skill_tag": "Comparing fractions",
                            "prompt": "Which fraction is greatest?",
                            "options": [
                                "3/5",
                                "5/8",
                                "2/3",
                                "1/2"
                            ],
                            "answer": "2/3",
                            "explanation": "Use denominator 120 to compare: 3/5 = 72/120, 5/8 = 75/120, 2/3 = 80/120, and 1/2 = 60/120. Therefore 2/3 is greatest. This checks the comparison using equal-sized parts rather than guessing from the numerators.",
                            "mistake_tag": "Comparing fractions"
                        },
                        {
                            "id": "fractions_l1_d5",
                            "type": "mc",
                            "stage": "project",
                            "skill_tag": "Applying fractions in context",
                            "prompt": "A recipe uses 3/4 cup of milk for 2 portions. How much milk is needed for 4 portions?",
                            "options": [
                                "1 1/2 cups",
                                "3/8 cup",
                                "3/4 cup",
                                "2 1/4 cups"
                            ],
                            "answer": "1 1/2 cups",
                            "explanation": "The portions double, so double 3/4: 3/4 × 2 = 1 1/2 cups.",
                            "mistake_tag": "Applying fractions in context"
                        }
                    ],
                    "prerequisite_review": "A fraction describes a portion of one whole or group. The numerator counts the parts being considered; the denominator tells how many equal-sized parts make one whole. The parts must be equal-sized. For example, 3/5 means 3 of the 5 equal parts—not 3 objects out of 5 unrelated objects unless the group is being treated as the whole.",
                    "pathways": {
                        "level_2": {
                            "questions": [
                                {
                                    "id": "fractions_l1_l2_q1",
                                    "type": "mc",
                                    "stage": "practice",
                                    "skill_tag": "Adding fractions",
                                    "prompt": "What is 1/4 + 2/4?",
                                    "options": [
                                        "3/4",
                                        "3/8",
                                        "2/4",
                                        "1/2"
                                    ],
                                    "answer": "3/4",
                                    "explanation": "The denominators match, so add the numerators and keep the denominator: 3/4.",
                                    "mistake_tag": "Adding fractions"
                                },
                                {
                                    "id": "fractions_l1_l2_q2",
                                    "type": "mc",
                                    "stage": "practice",
                                    "skill_tag": "Comparing fractions",
                                    "prompt": "Which fraction is larger?",
                                    "options": [
                                        "5/6",
                                        "7/9",
                                        "They are equal",
                                        "Not enough information"
                                    ],
                                    "answer": "5/6",
                                    "explanation": "5/6 is about 0.833 and 7/9 is about 0.778, so 5/6 is larger.",
                                    "mistake_tag": "Comparing fractions"
                                }
                            ]
                        },
                        "level_3": {
                            "questions": [
                                {
                                    "id": "fractions_l1_l3_q1",
                                    "type": "mc",
                                    "stage": "practice",
                                    "skill_tag": "Ordering fractions",
                                    "prompt": "Which list orders the fractions from smallest to largest?",
                                    "options": [
                                        "3/5, 5/8, 2/3",
                                        "2/3, 5/8, 3/5",
                                        "5/8, 3/5, 2/3",
                                        "3/5, 2/3, 5/8"
                                    ],
                                    "answer": "3/5, 5/8, 2/3",
                                    "explanation": "Their decimal values are 0.6, 0.625, and about 0.667.",
                                    "mistake_tag": "Ordering fractions"
                                },
                                {
                                    "id": "fractions_l1_l3_q2",
                                    "type": "mc",
                                    "stage": "practice",
                                    "skill_tag": "Subtracting unlike fractions",
                                    "prompt": "A ribbon is 3/4 m long. You use 2/5 m. How much remains?",
                                    "options": [
                                        "7/20 m",
                                        "1/20 m",
                                        "1/2 m",
                                        "1/3 m"
                                    ],
                                    "answer": "7/20 m",
                                    "explanation": "3/4 − 2/5 = 15/20 − 8/20 = 7/20.",
                                    "mistake_tag": "Subtracting unlike fractions"
                                }
                            ]
                        },
                        "project": {
                            "intro": "Project task: calculate ingredients for multiple batches. Show that you can transfer fraction reasoning to a practical planning problem.",
                            "questions": [
                                {
                                    "id": "fractions_l1_project_q1",
                                    "type": "numeric",
                                    "stage": "project",
                                    "skill_tag": "Scaling a recipe",
                                    "prompt": "One batch uses 2/3 cup of oats. How many cups are needed for 3 batches?",
                                    "answer": 2,
                                    "tolerance": 0.01,
                                    "whole_number": True,
                                    "input_hint": "Enter the number of cups.",
                                    "explanation": "2/3 × 3 = 2 cups.",
                                    "mistake_tag": "Scaling a recipe"
                                }
                            ]
                        }
                    }
                },
"questions": [
                    {
                        "id": "fractions_l1_q1",
                        "type": "mc",
                        "prompt": "Which fraction represents 3 out of 4 equal parts?",
                        "options": ["3/4", "4/3", "1/3", "3/3"],
                        "answer": "3/4",
                        "explanation": (
                            "3 out of 4 equal parts is written with 3 as the "
                            "numerator (parts you have) and 4 as the denominator "
                            "(total equal parts): 3/4."
                        ),
                        "mistake_tag": "Denominator confusion",
                    },
                    {
                        "id": "fractions_l1_q2",
                        "type": "mc",
                        "prompt": "In the fraction 5/8, what is the denominator?",
                        "options": ["5", "8", "3", "13"],
                        "answer": "8",
                        "explanation": (
                            "The denominator is the bottom number. In 5/8, that "
                            "number is 8 — it tells you the whole is split into 8 "
                            "equal parts."
                        ),
                        "mistake_tag": "Denominator confusion",
                    },
                    {
                        "id": "fractions_l1_q3",
                        "type": "mc",
                        "prompt": "What does 7/5 represent?",
                        "options": ["7 wholes", "2/5 of a whole", "1 whole and 2/5 more", "1/7 of a whole"],
                        "answer": "1 whole and 2/5 more",
                        "explanation": "Five fifths make one whole. The remaining two fifths give 7/5 = 5/5 + 2/5 = 1 2/5.",
                        "mistake_tag": "Fractions greater than one",
                    },
                ],
            },
            {
                "id": "fractions_l2",
                "title": "Adding Fractions",
                "kind": "standard",
                "explanation": (
                    "This lesson adds fractions that have the same denominator (the same-sized parts). "
                    "The denominator tells us the size of each part, so it stays the same when we combine "
                    "parts of that size. The numerator tells us how many parts we have, so we add the "
                    "numerators.\n\n"
                    "Rule: a/b + c/b = (a + c)/b, when the denominators are equal.\n\n"
                    "Example: 2/7 + 3/7 means 2 sevenths plus 3 sevenths. That is 5 sevenths, or 5/7. "
                    "Do not add the denominators: 7 still describes the size of each part.\n\n"
                    "This rule applies when the denominators match. If they are different, first rewrite "
                    "the fractions as equivalent fractions with a common denominator."
                ),
                "worked_example": (
                    "**Example 1: 2/7 + 3/7**\n"
                    "1. Check the denominators: both are 7, so the parts are the same size.\n"
                    "2. Add the numerators: 2 + 3 = 5.\n"
                    "3. Keep the denominator 7.\n"
                    "Answer: 5/7.\n\n"
                    "**Example 2: 1/4 + 1/4**\n"
                    "1. The denominators match, so add the numerators: 1 + 1 = 2.\n"
                    "2. Keep the denominator: 2/4.\n"
                    "3. Simplify by dividing both numbers by 2: 2/4 = 1/2.\n"
                    "Answer: 1/2."
                ),
                "interactive_question": {
                    "id": "fractions_l2_screen3",
                    "type": "mc",
                    "prompt": "What is 1/6 + 3/6?",
                    "options": ["4/6", "4/12", "3/6", "1/3"],
                    "answer": "4/6",
                    "explanation": (
                        "The denominators are both 6, so add only the numerators: 1 + 3 = 4. "
                        "Keep 6 as the denominator to get 4/6. This can then simplify to 2/3."
                    ),
                    "mistake_tag": "Addition error",
                },
                "questions": [
                    {
                        "id": "fractions_l2_q1",
                        "type": "numeric",
                        "prompt": "What is 1/4 + 1/4? Enter your answer as a decimal.",
                        "answer": 0.5,
                        "tolerance": 0.01,
                        "whole_number": False,
                        "input_hint": "e.g. 0.5",
                        "explanation": (
                            "Add the numerators because both fractions are quarters: 1 + 1 = 2, so the result is 2/4. "
                            "Simplify 2/4 to 1/2, which is 0.5."
                        ),
                        "mistake_tag": "Addition error",
                    },
                    {
                        "id": "fractions_l2_q2",
                        "type": "numeric",
                        "prompt": "What is 1/5 + 2/5? Enter your answer as a decimal.",
                        "answer": 0.6,
                        "tolerance": 0.01,
                        "whole_number": False,
                        "input_hint": "e.g. 0.6",
                        "explanation": (
                            "Add the numerators: 1 + 2 = 3. Keep the denominator 5 to get 3/5. "
                            "Convert 3/5 to a decimal: 3 ÷ 5 = 0.6."
                        ),
                        "mistake_tag": "Addition error",
                    },
                ],
                "diagnostic": {
                    "version": 1,
                    "questions": [
                        {
                            "id": "fractions_l2_d1",
                            "type": "mc",
                            "stage": "prerequisite",
                            "skill_tag": "Understanding equal-sized fractional parts",
                            "prompt": "Why can 2/9 + 4/9 be added by combining the numerators?",
                            "options": [
                                "Both fractions count parts of the same size",
                                "The denominator is always added after the numerator",
                                "The numerators and denominators are interchangeable",
                                "Adding fractions always makes the denominator smaller"
                            ],
                            "answer": "Both fractions count parts of the same size",
                            "explanation": "Both fractions use ninths, so each counted part is the same size. The total can be found by combining the number of ninths.",
                            "mistake_tag": "Understanding equal-sized fractional parts"
                        },
                        {
                            "id": "fractions_l2_d2",
                            "type": "mc",
                            "stage": "level_1",
                            "skill_tag": "Adding same-denominator fractions",
                            "prompt": "What is 3/8 + 2/8?",
                            "options": ["5/8", "5/16", "6/8", "1/8"],
                            "answer": "5/8",
                            "explanation": "There are 3 eighths and 2 more eighths: 3 + 2 = 5 eighths. Keep the denominator 8.",
                            "mistake_tag": "Adding same-denominator fractions"
                        },
                        {
                            "id": "fractions_l2_d3",
                            "type": "mc",
                            "stage": "level_2",
                            "skill_tag": "Preserving the denominator",
                            "prompt": "A learner calculates 2/7 + 3/7 = 5/14. Which correction explains the error?",
                            "options": [
                                "Add the numerators but keep 7 because the parts are still sevenths",
                                "Add both numerators and both denominators to make 5/14",
                                "Subtract the numerators and keep 7",
                                "Multiply the numerators and keep 14"
                            ],
                            "answer": "Add the numerators but keep 7 because the parts are still sevenths",
                            "explanation": "The denominator describes the size of each part. Combining sevenths gives five sevenths, not fourteen parts.",
                            "mistake_tag": "Preserving the denominator"
                        },
                        {
                            "id": "fractions_l2_d4",
                            "type": "mc",
                            "stage": "level_3",
                            "skill_tag": "Simplifying a sum",
                            "prompt": "Calculate 3/10 + 5/10, then choose the answer in simplest form.",
                            "options": ["4/5", "8/20", "7/10", "3/5"],
                            "answer": "4/5",
                            "explanation": "Add the numerators to get 8/10. Divide numerator and denominator by 2 to simplify to 4/5.",
                            "mistake_tag": "Simplifying a sum"
                        },
                        {
                            "id": "fractions_l2_d5",
                            "type": "mc",
                            "stage": "project",
                            "skill_tag": "Adding fractions in a measurement context",
                            "prompt": "A student walks 2/8 km, then another 3/8 km. What total distance did they walk?",
                            "options": ["5/8 km", "5/16 km", "1/8 km", "6/8 km"],
                            "answer": "5/8 km",
                            "explanation": "The distances are both measured in eighths of a kilometre. Add 2 eighths and 3 eighths to get 5/8 km.",
                            "mistake_tag": "Adding fractions in a measurement context"
                        }
                    ],
                    "prerequisite_review": "Fraction addition with equal denominators works because the parts are the same size. Combine the numerators, keep the denominator, then simplify the result if possible.",
                    "pathways": {
                        "level_2": {
                            "questions": [
                                {
                                    "id": "fractions_l2_dpath_m1",
                                    "type": "mc",
                                    "stage": "practice",
                                    "skill_tag": "Adding same-denominator fractions",
                                    "prompt": "What is 4/9 + 2/9?",
                                    "options": ["6/9", "6/18", "2/9", "8/9"],
                                    "answer": "6/9",
                                    "explanation": "Add the numerators, 4 + 2 = 6, and keep the denominator 9.",
                                    "mistake_tag": "Adding same-denominator fractions"
                                }
                            ]
                        },
                        "level_3": {
                            "questions": [
                                {
                                    "id": "fractions_l2_dpath_h1",
                                    "type": "mc",
                                    "stage": "practice",
                                    "skill_tag": "Simplifying fraction sums",
                                    "prompt": "What is 5/12 + 7/12 in simplest form?",
                                    "options": ["1", "12/24", "11/12", "5/6"],
                                    "answer": "1",
                                    "explanation": "5/12 + 7/12 = 12/12 = 1 whole.",
                                    "mistake_tag": "Simplifying fraction sums"
                                }
                            ]
                        },
                        "project": {
                            "intro": "Apply addition of like-denominator fractions to a simple measurement situation.",
                            "questions": [
                                {
                                    "id": "fractions_l2_dpath_p1",
                                    "type": "mc",
                                    "stage": "project",
                                    "skill_tag": "Adding fractional measurements",
                                    "prompt": "A ribbon is 3/10 m long and another piece is 4/10 m. What is their combined length?",
                                    "options": ["7/10 m", "7/20 m", "1/10 m", "3/10 m"],
                                    "answer": "7/10 m",
                                    "explanation": "Both lengths are tenths, so add 3 tenths and 4 tenths to get 7/10 m.",
                                    "mistake_tag": "Adding fractional measurements"
                                }
                            ]
                        }
                    }
                },
            },
            {
                "id": "fractions_l3",
                "title": "Simplifying Fractions",
                "kind": "standard",
                "explanation": (
                    "Simplifying a fraction means writing an equivalent fraction with smaller numbers. "
                    "You must divide the numerator AND denominator by the same non-zero number, because "
                    "this keeps the fraction's value unchanged.\\n\\n"
                    "A common factor is a number that divides both parts exactly. Keep simplifying while "
                    "a common factor greater than 1 remains; the fraction is in simplest form when the "
                    "numerator and denominator have no common factor other than 1.\\n\\n"
                    "You can divide by the greatest common factor in one step, or by smaller common "
                    "factors in several steps."
                ),
                "worked_example": (
                    "**Simplify 12/18**\\n"
                    "1. Find a common factor of 12 and 18. Their greatest common factor is 6.\\n"
                    "2. Divide both by 6: 12 ÷ 6 = 2 and 18 ÷ 6 = 3.\\n"
                    "3. Write the equivalent fraction: 12/18 = 2/3.\\n"
                    "4. Check: 2 and 3 have no common factor greater than 1, so 2/3 is simplest.\\n\\n"
                    "You could also divide both numbers by 2 first (12/18 = 6/9), then by 3 (6/9 = 2/3)."
                ),
                "interactive_question": {
                    "id": "fractions_l3_screen3",
                    "type": "mc",
                    "prompt": "What is 8/12 in its simplest form?",
                    "options": ["2/3", "4/6", "1/3", "8/6"],
                    "answer": "2/3",
                    "explanation": (
                        "Divide both parts by the same common factor, 4: 8 ÷ 4 = 2 and 12 ÷ 4 = 3. "
                        "So 8/12 = 2/3. 4/6 is equivalent, but it can still be simplified."
                    ),
                    "mistake_tag": "Incorrect simplification",
                },
                "questions": [
                    {
                        "id": "fractions_l3_q1",
                        "type": "mc",
                        "prompt": "What is 4/8 simplified?",
                        "options": ["1/2", "2/4", "1/4", "4/8"],
                        "answer": "1/2",
                        "explanation": (
                            "Divide both 4 and 8 by 4. This gives 1/2. "
                            "2/4 is equivalent, but it is not yet in simplest form."
                        ),
                        "mistake_tag": "Incorrect simplification",
                    },
                    {
                        "id": "fractions_l3_q2",
                        "type": "numeric",
                        "prompt": "Simplify 6/9. What is the denominator of the simplified fraction?",
                        "answer": 3,
                        "tolerance": 0.01,
                        "whole_number": True,
                        "input_hint": "whole number",
                        "explanation": (
                            "Divide numerator and denominator by their common factor, 3: "
                            "6 ÷ 3 = 2 and 9 ÷ 3 = 3. The simplest fraction is 2/3, so its denominator is 3."
                        ),
                        "mistake_tag": "Incorrect simplification",
                    },
                ],
                "diagnostic": {
                    "version": 1,
                    "questions": [
                        {
                            "id": "fractions_l3_d1",
                            "type": "mc",
                            "stage": "prerequisite",
                            "skill_tag": "Equivalent fractions",
                            "prompt": "Why does dividing both the numerator and denominator by the same non-zero factor keep a fraction's value unchanged?",
                            "options": [
                                "It changes the number of parts and their size proportionally",
                                "It only changes the numerator",
                                "It makes every fraction equal to 1",
                                "It changes the whole being described"
                            ],
                            "answer": "It changes the number of parts and their size proportionally",
                            "explanation": "Dividing both terms by the same factor describes the same amount using fewer, proportionally larger parts.",
                            "mistake_tag": "Equivalent fractions"
                        },
                        {
                            "id": "fractions_l3_d2",
                            "type": "mc",
                            "stage": "level_1",
                            "skill_tag": "Simplifying by a common factor",
                            "prompt": "Simplify 15/20 to its simplest form.",
                            "options": ["3/4", "5/10", "3/5", "15/5"],
                            "answer": "3/4",
                            "explanation": "Divide both numerator and denominator by 5: 15/20 = 3/4. The simplified numerator and denominator have no common factor greater than 1.",
                            "mistake_tag": "Incomplete simplification"
                        },
                        {
                            "id": "fractions_l3_d3",
                            "type": "mc",
                            "stage": "level_2",
                            "skill_tag": "Applying the same divisor",
                            "prompt": "A student simplifies 18/24 to 9/12 by dividing the numerator by 2 and the denominator by 2. What is the next valid simplification?",
                            "options": ["3/4, divide both by 3", "9/24, divide only the numerator", "9/6, divide numerator and denominator by different numbers", "18/12, divide only the denominator"],
                            "answer": "3/4, divide both by 3",
                            "explanation": "9 and 12 share the factor 3. Dividing both by 3 gives 3/4. Dividing only one term or using different divisors would change the fraction's value.",
                            "mistake_tag": "Unequal division"
                        },
                        {
                            "id": "fractions_l3_d4",
                            "type": "mc",
                            "stage": "level_3",
                            "skill_tag": "Finding simplest form",
                            "prompt": "What is the simplest form of 42/56?",
                            "options": ["3/4", "6/8", "21/28", "7/8"],
                            "answer": "3/4",
                            "explanation": "The greatest common factor of 42 and 56 is 14. Divide both by 14 to obtain 3/4; no common factor greater than 1 remains.",
                            "mistake_tag": "Not fully simplified"
                        },
                        {
                            "id": "fractions_l3_d5",
                            "type": "mc",
                            "stage": "project",
                            "skill_tag": "Simplifying a contextual fraction",
                            "prompt": "A class has used 24 of 36 identical tickets. Which fraction represents the used tickets in simplest form?",
                            "options": ["2/3", "3/4", "12/18", "24/12"],
                            "answer": "2/3",
                            "explanation": "The used portion is 24/36. Divide both terms by 12 to simplify it to 2/3.",
                            "mistake_tag": "Applying simplification"
                        }
                    ],
                    "prerequisite_review": "Equivalent fractions describe the same amount. To simplify, divide the numerator and denominator by the same common factor greater than 1. Continue until they have no common factor greater than 1; the greatest common factor can simplify the fraction in one step.",
                    "pathways": {
                        "level_2": {
                            "questions": [
                                {
                                    "id": "fractions_l3_l2_q1",
                                    "type": "mc",
                                    "stage": "practice",
                                    "skill_tag": "Simplifying by a common factor",
                                    "prompt": "Simplify 16/24.",
                                    "options": ["2/3", "4/6", "1/3", "8/24"],
                                    "answer": "2/3",
                                    "explanation": "Divide both by 8 to get 2/3.",
                                    "mistake_tag": "Incomplete simplification"
                                }
                            ]
                        },
                        "level_3": {
                            "questions": [
                                {
                                    "id": "fractions_l3_l3_q1",
                                    "type": "mc",
                                    "stage": "practice",
                                    "skill_tag": "Finding simplest form",
                                    "prompt": "Simplify 63/81 fully.",
                                    "options": ["7/9", "21/27", "9/12", "3/9"],
                                    "answer": "7/9",
                                    "explanation": "Divide both numerator and denominator by 9 to get 7/9.",
                                    "mistake_tag": "Not fully simplified"
                                }
                            ]
                        },
                        "project": {
                            "questions": [
                                {
                                    "id": "fractions_l3_project_q1",
                                    "type": "mc",
                                    "stage": "practice",
                                    "skill_tag": "Simplifying a contextual fraction",
                                    "prompt": "A garden has 30 of its 45 plants flowering. What fraction of the plants are flowering in simplest form?",
                                    "options": ["2/3", "3/5", "5/6", "30/15"],
                                    "answer": "2/3",
                                    "explanation": "30/45 is simplified by dividing both terms by 15, giving 2/3.",
                                    "mistake_tag": "Applying simplification"
                                }
                            ]
                        }
                    }
                },
            },
            {
                "id": "fractions_l4",
                "title": "Real-World Challenge: Scaling a Recipe",
                "kind": "application",
                "explanation": (
                    "Scaling a recipe means changing the amount of food while keeping the same proportions. "
                    "Use one scale factor for every ingredient: scale factor = new servings ÷ original servings. "
                    "Multiply each original ingredient amount by this factor. If the servings are halved, the factor is 1/2; "
                    "if they are tripled, the factor is 3. Do not add the difference in servings to the ingredient amounts—"
                    "scaling is multiplication, not addition.\n\n"
                    "Fraction reminder: multiply a fraction by a whole-number scale factor by multiplying its numerator "
                    "by that factor (or multiply by the factor written as a fraction). Simplify the result if needed."
                ),
                "worked_example": (
                    "A recipe uses 3/4 cup of sugar for 4 servings. How much is needed for 8 servings?\n"
                    "1. Scale factor = new servings ÷ original servings = 8 ÷ 4 = 2.\n"
                    "2. Multiply the ingredient amount by 2: 3/4 × 2 = 6/4.\n"
                    "3. Simplify 6/4 = 3/2 = 1 1/2.\n"
                    "So use 1 1/2 cups of sugar. Check: servings doubled, so every ingredient must double."
                ),
                "interactive_question": {
                    "id": "fractions_l4_screen3",
                    "type": "numeric",
                    "prompt": "A recipe needs 2/3 cup of oats for 2 servings. How many cups are needed for 6 servings? Enter a decimal.",
                    "answer": 2,
                    "tolerance": 0.01,
                    "whole_number": False,
                    "input_hint": "e.g. 2",
                    "explanation": (
                        "Scale factor = 6 ÷ 2 = 3. Multiply the original amount by 3: "
                        "2/3 × 3 = 6/3 = 2 cups. The amount triples because the servings triple."
                    ),
                    "mistake_tag": APPLICATION_MISTAKE_TAG,
                },
                "questions": [
                    {
                        "id": "fractions_l4_q1",
                        "type": "numeric",
                        "prompt": "Cups of sugar needed for 8 servings:",
                        "answer": 1.5,
                        "tolerance": 0.01,
                        "whole_number": False,
                        "input_hint": "e.g. 1.5",
                        "explanation": (
                            "The original recipe uses 3/4 cup for 4 servings. The scale factor is 8 ÷ 4 = 2, "
                            "so multiply the sugar by 2: 3/4 × 2 = 6/4 = 1.5 cups. "
                            "All other ingredients must also be doubled."
                        ),
                        "mistake_tag": APPLICATION_MISTAKE_TAG,
                    }
                ],            },
        ],
    },
    "algebra": {
        "id": "algebra",
        "title": "Algebra Basics",
        "short_description": "Build fluency with variables, expressions, and simple equations—from translating symbols to solving for an unknown.",
        "difficulty": "Beginner",
        "topic_label": "Algebra",
        "lessons": [
            {
                "id": "algebra_l1",
                "title": "What Is a Variable?",
                "kind": "standard",
                "explanation": (
                    "A variable is a letter that stands in for a number we don't "
                    "know yet, usually written as x, y, or n. Algebra is largely "
                    "about finding what number a variable represents.\n\n"
                    "For example, in x + 5 = 12, x is the unknown value we solve for."
                ),
                "worked_example": (
                    "In x + 5 = 12, x stands for the unknown number. The equation is true when x = 7, "
                    "because 7 + 5 = 12."
                ),
                "interactive_question": {
                    "id": "algebra_l1_screen3",
                    "type": "mc",
                    "prompt": "Let n stand for the number of stickers you start with. Which expression means 3 more stickers?",
                    "options": ["n + 3", "3n", "n - 3", "3 - n"],
                    "answer": "n + 3",
                    "explanation": "The letter n represents the starting amount. Three more means add 3: n + 3.",
                    "mistake_tag": "Meaning of a variable",
                },
                "diagnostic": {
                    "version": 1,
                    "questions": [
                        {
                            "id": "algebra_l1_d1",
                            "type": "mc",
                            "stage": "prerequisite",
                            "skill_tag": "Basic arithmetic",
                            "prompt": "What is 8 + 7?",
                            "options": [
                                "15",
                                "14",
                                "16",
                                "13"
                            ],
                            "answer": "15",
                            "explanation": "Basic arithmetic supports later work with unknown values.",
                            "mistake_tag": "Basic arithmetic"
                        },
                        {
                            "id": "algebra_l1_d2",
                            "type": "mc",
                            "stage": "level_1",
                            "skill_tag": "Meaning of a variable",
                            "prompt": "In x + 5 = 11, what does x represent?",
                            "options": [
                                "An unknown number we need to find",
                                "The plus sign",
                                "Always the number 5",
                                "The number 11"
                            ],
                            "answer": "An unknown number we need to find",
                            "explanation": "A variable is a symbol that represents a value that may be unknown.",
                            "mistake_tag": "Meaning of a variable"
                        },
                        {
                            "id": "algebra_l1_d3",
                            "type": "mc",
                            "stage": "level_2",
                            "skill_tag": "Solving a one-step equation",
                            "prompt": "Solve x + 7 = 15.",
                            "options": [
                                "8",
                                "7",
                                "22",
                                "−8"
                            ],
                            "answer": "8",
                            "explanation": "Subtract 7 from both sides: x = 15 − 7 = 8.",
                            "mistake_tag": "Solving a one-step equation"
                        },
                        {
                            "id": "algebra_l1_d4",
                            "type": "mc",
                            "stage": "level_3",
                            "skill_tag": "Solving equations with brackets",
                            "prompt": "Solve 2(x + 3) = 18.",
                            "options": [
                                "6",
                                "9",
                                "12",
                                "3"
                            ],
                            "answer": "6",
                            "explanation": "Divide both sides by 2 to get x + 3 = 9, then subtract 3.",
                            "mistake_tag": "Solving equations with brackets"
                        },
                        {
                            "id": "algebra_l1_d5",
                            "type": "mc",
                            "stage": "project",
                            "skill_tag": "Applying algebra to pricing",
                            "prompt": "A product costs Rp40,000 to make. The seller adds a profit equal to 30% of the cost. What is the selling price?",
                            "options": [
                                "Rp52,000",
                                "Rp43,000",
                                "Rp70,000",
                                "Rp28,000"
                            ],
                            "answer": "Rp52,000",
                            "explanation": "30% of Rp40,000 is Rp12,000; Rp40,000 + Rp12,000 = Rp52,000.",
                            "mistake_tag": "Applying algebra to pricing"
                        }
                    ],
                    "prerequisite_review": "Before using variables, be comfortable with addition, subtraction, multiplication, and division. An equation states that two expressions have equal value. To keep an equation balanced, apply the same operation to both sides.",
                    "pathways": {
                        "level_2": {
                            "questions": [
                                {
                                    "id": "algebra_l1_l2_q1",
                                    "type": "mc",
                                    "stage": "practice",
                                    "skill_tag": "Two-step equations",
                                    "prompt": "Solve 3x + 2 = 17.",
                                    "options": [
                                        "5",
                                        "7",
                                        "19",
                                        "3"
                                    ],
                                    "answer": "5",
                                    "explanation": "Subtract 2 to get 3x = 15, then divide by 3.",
                                    "mistake_tag": "Two-step equations"
                                },
                                {
                                    "id": "algebra_l1_l2_q2",
                                    "type": "mc",
                                    "stage": "practice",
                                    "skill_tag": "Inverse operations",
                                    "prompt": "Solve 2x − 4 = 10.",
                                    "options": [
                                        "7",
                                        "3",
                                        "12",
                                        "14"
                                    ],
                                    "answer": "7",
                                    "explanation": "Add 4 to get 2x = 14, then divide by 2.",
                                    "mistake_tag": "Inverse operations"
                                }
                            ]
                        },
                        "level_3": {
                            "questions": [
                                {
                                    "id": "algebra_l1_l3_q1",
                                    "type": "mc",
                                    "stage": "practice",
                                    "skill_tag": "Equations with brackets",
                                    "prompt": "Solve 5(x − 2) = 30.",
                                    "options": [
                                        "8",
                                        "4",
                                        "6",
                                        "10"
                                    ],
                                    "answer": "8",
                                    "explanation": "Divide by 5 to get x − 2 = 6, then add 2.",
                                    "mistake_tag": "Equations with brackets"
                                },
                                {
                                    "id": "algebra_l1_l3_q2",
                                    "type": "mc",
                                    "stage": "practice",
                                    "skill_tag": "Equations on both sides",
                                    "prompt": "Solve 3x + 5 = 2x + 12.",
                                    "options": [
                                        "7",
                                        "17",
                                        "−7",
                                        "6"
                                    ],
                                    "answer": "7",
                                    "explanation": "Subtract 2x from both sides, then subtract 5: x = 7.",
                                    "mistake_tag": "Equations on both sides"
                                }
                            ]
                        },
                        "project": {
                            "intro": "Project task: use a simple cost model to make a constrained business decision.",
                            "questions": [
                                {
                                    "id": "algebra_l1_project_q1",
                                    "type": "numeric",
                                    "stage": "project",
                                    "skill_tag": "Budget and break-even reasoning",
                                    "prompt": "An event costs Rp25,000 as a fixed fee plus Rp6,000 per participant. With a Rp100,000 budget, what is the maximum number of participants?",
                                    "answer": 12,
                                    "tolerance": 0.01,
                                    "whole_number": True,
                                    "input_hint": "Enter a whole number of participants.",
                                    "explanation": "Rp100,000 − Rp25,000 = Rp75,000 available for participants. Rp75,000 ÷ Rp6,000 allows 12 whole participants.",
                                    "mistake_tag": "Budget and break-even reasoning"
                                }
                            ]
                        }
                    }
                },
"questions": [
                    {
                        "id": "algebra_l1_q1",
                        "type": "mc",
                        "prompt": "In the equation x + 5 = 12, what does x represent?",
                        "options": [
                            "An unknown number we need to find",
                            "A fixed constant",
                            "The answer 5",
                            "The answer 12",
                        ],
                        "answer": "An unknown number we need to find",
                        "explanation": (
                            "x is a placeholder for the number that makes the "
                            "equation true — that's what solving for x means."
                        ),
                        "mistake_tag": "Variable misunderstanding",
                    },
                    {
                        "id": "algebra_l1_q2",
                        "type": "mc",
                        "prompt": "Which of these is a variable?",
                        "options": ["x", "7", "+", "="],
                        "answer": "x",
                        "explanation": (
                            "x is a letter standing in for an unknown number. "
                            "7, +, and = are a fixed number and operators, not "
                            "variables."
                        ),
                        "mistake_tag": "Variable misunderstanding",
                    },
                ],
            },
            {
                "id": "algebra_l2",
                "title": "Solving Simple Equations",
                "kind": "standard",
                "explanation": (
                    "To solve for a variable, do the same operation to both sides "
                    "of the equation until the variable is alone.\n\n"
                    "For example: x + 7 = 15. Subtract 7 from both sides: "
                    "x = 15 - 7 = 8."
                ),
                "worked_example": (
                    "Solve x + 7 = 15. Subtract 7 from both sides so the equation stays balanced: "
                    "x = 15 − 7 = 8. Check: 8 + 7 = 15."
                ),
                "interactive_question": {
                    "id": "algebra_l2_screen3",
                    "type": "numeric",
                    "prompt": "Solve 3x = 24. What is x?",
                    "answer": 8,
                    "tolerance": 0.01,
                    "whole_number": True,
                    "input_hint": "Enter a whole number.",
                    "explanation": "Divide both sides by 3: x = 24 ÷ 3 = 8.",
                    "mistake_tag": "Incorrect inverse operation",
                },
                "questions": [
                    {
                        "id": "algebra_l2_q1",
                        "type": "numeric",
                        "prompt": "Solve for x: x + 7 = 15",
                        "answer": 8,
                        "tolerance": 0.01,
                        "whole_number": True,
                        "input_hint": "whole number",
                        "explanation": "Subtract 7 from both sides: x = 15 - 7 = 8.",
                        "mistake_tag": "Incorrect inverse operation",
                    },
                    {
                        "id": "algebra_l2_q2",
                        "type": "numeric",
                        "prompt": "Solve for x: 3x = 21",
                        "answer": 7,
                        "tolerance": 0.01,
                        "whole_number": True,
                        "input_hint": "whole number",
                        "explanation": "Divide both sides by 3: x = 21 / 3 = 7.",
                        "mistake_tag": "Incorrect inverse operation",
                    },
                ],
            },
            {
                "id": "algebra_l3",
                "title": "Working with Negative Numbers",
                "kind": "standard",
                "explanation": (
                    "Watch the sign carefully when an equation involves negative "
                    "numbers. Subtracting a negative is the same as adding, and "
                    "dividing by a negative flips the sign of the answer.\n\n"
                    "For example: x - 5 = -2, so x = -2 + 5 = 3."
                ),
                "worked_example": (
                    "Solve x − 5 = −2. Add 5 to both sides: x = −2 + 5 = 3. "
                    "For −2x = 10, divide by −2, giving x = −5."
                ),
                "interactive_question": {
                    "id": "algebra_l3_screen3",
                    "type": "mc",
                    "prompt": "Solve −3x = 12. What is x?",
                    "options": ["−4", "4", "9", "−9"],
                    "answer": "−4",
                    "explanation": "Divide both sides by −3: x = 12 ÷ (−3) = −4.",
                    "mistake_tag": "Sign errors",
                },
                "questions": [
                    {
                        "id": "algebra_l3_q1",
                        "type": "mc",
                        "prompt": "Solve for x: x - 5 = -2. What is x?",
                        "options": ["3", "-7", "7", "-3"],
                        "answer": "3",
                        "explanation": "Add 5 to both sides: x = -2 + 5 = 3.",
                        "mistake_tag": "Sign errors",
                    },
                    {
                        "id": "algebra_l3_q2",
                        "type": "numeric",
                        "prompt": "Solve for x: -2x = 10",
                        "answer": -5,
                        "tolerance": 0.01,
                        "whole_number": True,
                        "input_hint": "can be negative",
                        "explanation": "Divide both sides by -2: x = 10 / -2 = -5.",
                        "mistake_tag": "Sign errors",
                    },
                ],
            },
            {
                "id": "algebra_l4",
                "title": "Real-World Challenge: Pricing a Product",
                "kind": "application",
                "explanation": (
                    "A selling price can be modeled as production cost plus profit. "
                    "When profit is a percentage of cost, calculate that percentage of the cost first, "
                    "then add it to the original cost."
                ),
                "worked_example": (
                    "A product costs Rp60,000 to make. A 25% profit on cost is 0.25 × Rp60,000 = Rp15,000. "
                    "Add the profit to the cost: Rp60,000 + Rp15,000 = Rp75,000."
                ),
                "interactive_question": {
                    "id": "algebra_l4_screen3",
                    "type": "numeric",
                    "prompt": "A product costs Rp80,000 to make. The seller adds a profit of 20% of the cost. What is the selling price in rupiah?",
                    "answer": 96000,
                    "tolerance": 0.01,
                    "whole_number": True,
                    "input_hint": "e.g. 96000",
                    "explanation": "20% of Rp80,000 is Rp16,000. Add it to the cost: Rp80,000 + Rp16,000 = Rp96,000.",
                    "mistake_tag": APPLICATION_MISTAKE_TAG,
                },
                "questions": [
                    {
                        "id": "algebra_l4_q1",
                        "type": "numeric",
                        "prompt": "Selling price (Rp):",
                        "answer": 75000,
                        "tolerance": 1,
                        "whole_number": True,
                        "input_hint": "e.g. 75000",
                        "explanation": (
                            "A 25% profit means adding 25% of the cost on top: "
                            "60,000 + (0.25 x 60,000) = 60,000 + 15,000 = 75,000."
                        ),
                        "mistake_tag": APPLICATION_MISTAKE_TAG,
                    }
                ],
            },
        ],
    },
    "word_problems": {
        "id": "word_problems",
        "title": "Word Problems",
        "short_description": "Turn written situations into mathematical expressions, identify relevant information, and interpret results in context.",
        "difficulty": "Beginner",
        "topic_label": "Word Problems",
        "lessons": [
            {
                "id": "wp_l1",
                "title": "Translating Words into Math",
                "kind": "standard",
                "explanation": (
                    "Word problems use everyday language to describe a "
                    "mathematical relationship. Certain words are clues to which "
                    "operation to use: 'total' or 'combined' often means "
                    "addition; 'times as many' means multiplication.\n\n"
                    "Spotting these clues is the first step to setting up the "
                    "right equation."
                ),
                "worked_example": (
                    "Maya has x stickers. Four more stickers are added. Translate the relationship: "
                    "the starting amount is x and the extra amount is 4, so the total is x + 4. "
                    "For comparison, '4 less than x' is x - 4, not 4 - x."
                ),
                "interactive_question": {
                    "id": "wp_l1_screen3",
                    "type": "mc",
                    "prompt": "Ben has x cards and receives 4 more. Which expression represents his new total?",
                    "options": ["x + 4", "4x", "x - 4", "4 - x"],
                    "answer": "x + 4",
                    "explanation": "Receiving 4 more means add 4 to the starting amount x, giving x + 4.",
                    "mistake_tag": "Translating key words",
                },
                "diagnostic": {
                    "version": 1,
                    "questions": [
                        {
                            "id": "wp_l1_d1",
                            "type": "mc",
                            "stage": "prerequisite",
                            "skill_tag": "Choosing a basic operation",
                            "prompt": "A box contains 6 red pencils and 4 blue pencils. Which operation finds the total number of pencils?",
                            "options": [
                                "Addition",
                                "Subtraction",
                                "Division",
                                "Multiplication"
                            ],
                            "answer": "Addition",
                            "explanation": "Finding a total means combining the amounts.",
                            "mistake_tag": "Choosing a basic operation"
                        },
                        {
                            "id": "wp_l1_d2",
                            "type": "mc",
                            "stage": "level_1",
                            "skill_tag": "Translating key words",
                            "prompt": "Which operation does the word “total” usually suggest?",
                            "options": [
                                "Addition",
                                "Subtraction",
                                "Multiplication",
                                "Division"
                            ],
                            "answer": "Addition",
                            "explanation": "“Total” generally means combining amounts, which is addition.",
                            "mistake_tag": "Translating key words"
                        },
                        {
                            "id": "wp_l1_d3",
                            "type": "mc",
                            "stage": "level_2",
                            "skill_tag": "Translating relationships",
                            "prompt": "Tom has x stickers. Sara has 3 times as many stickers, plus 2 more. Which expression represents Sara’s stickers?",
                            "options": [
                                "3x + 2",
                                "x + 3",
                                "3(x + 2)",
                                "x/3 + 2"
                            ],
                            "answer": "3x + 2",
                            "explanation": "“Three times as many” is 3x; “plus 2 more” gives 3x + 2.",
                            "mistake_tag": "Translating relationships"
                        },
                        {
                            "id": "wp_l1_d4",
                            "type": "mc",
                            "stage": "level_3",
                            "skill_tag": "Selecting relevant information",
                            "prompt": "Three notebooks cost Rp12,000 each. The shop gives a Rp5,000 discount on the total. How much is paid?",
                            "options": [
                                "Rp31,000",
                                "Rp36,000",
                                "Rp19,000",
                                "Rp41,000"
                            ],
                            "answer": "Rp31,000",
                            "explanation": "3 × Rp12,000 = Rp36,000; subtract the Rp5,000 discount.",
                            "mistake_tag": "Selecting relevant information"
                        },
                        {
                            "id": "wp_l1_d5",
                            "type": "mc",
                            "stage": "project",
                            "skill_tag": "Building a cost model",
                            "prompt": "A school activity has a fixed room cost of Rp30,000 plus Rp5,000 per student. If 18 students attend, what is the total cost?",
                            "options": [
                                "Rp120,000",
                                "Rp90,000",
                                "Rp33,000",
                                "Rp150,000"
                            ],
                            "answer": "Rp120,000",
                            "explanation": "Rp30,000 + (18 × Rp5,000) = Rp120,000.",
                            "mistake_tag": "Building a cost model"
                        }
                    ],
                    "prerequisite_review": "Start by identifying what the question asks for. Then identify quantities, units, and relationships. Words can be clues, but they are not rules: check the full meaning of the sentence before choosing an operation.",
                    "pathways": {
                        "level_2": {
                            "questions": [
                                {
                                    "id": "wp_l1_l2_q1",
                                    "type": "mc",
                                    "stage": "practice",
                                    "skill_tag": "Forming an equation",
                                    "prompt": "There are 3 boxes with x notebooks in each box and 5 extra notebooks. There are 23 notebooks altogether. Which equation models this?",
                                    "options": [
                                        "3x + 5 = 23",
                                        "3 + x + 5 = 23",
                                        "3(x + 5) = 23",
                                        "x + 5 = 23"
                                    ],
                                    "answer": "3x + 5 = 23",
                                    "explanation": "Three equal groups give 3x, then add the 5 extra notebooks.",
                                    "mistake_tag": "Forming an equation"
                                },
                                {
                                    "id": "wp_l1_l2_q2",
                                    "type": "mc",
                                    "stage": "practice",
                                    "skill_tag": "Multi-step calculation",
                                    "prompt": "Four tickets cost Rp25,000 each. A Rp10,000 discount applies to the total. How much is paid?",
                                    "options": [
                                        "Rp90,000",
                                        "Rp100,000",
                                        "Rp75,000",
                                        "Rp110,000"
                                    ],
                                    "answer": "Rp90,000",
                                    "explanation": "4 × Rp25,000 = Rp100,000; subtract Rp10,000.",
                                    "mistake_tag": "Multi-step calculation"
                                }
                            ]
                        },
                        "level_3": {
                            "questions": [
                                {
                                    "id": "wp_l1_l3_q1",
                                    "type": "mc",
                                    "stage": "practice",
                                    "skill_tag": "Sharing a multi-step cost",
                                    "prompt": "A ride costs Rp10,000 plus Rp2,000 per kilometre. Two people share the cost of an 8 km ride equally. How much does each pay?",
                                    "options": [
                                        "Rp13,000",
                                        "Rp26,000",
                                        "Rp16,000",
                                        "Rp12,000"
                                    ],
                                    "answer": "Rp13,000",
                                    "explanation": "The total is Rp10,000 + (8 × Rp2,000) = Rp26,000. Half is Rp13,000.",
                                    "mistake_tag": "Sharing a multi-step cost"
                                },
                                {
                                    "id": "wp_l1_l3_q2",
                                    "type": "mc",
                                    "stage": "practice",
                                    "skill_tag": "Working backward from a budget",
                                    "prompt": "A class has Rp150,000. Equipment costs Rp30,000 and refreshments cost Rp5,000 per student. What is the maximum number of students who can be covered?",
                                    "options": [
                                        "24",
                                        "30",
                                        "25",
                                        "20"
                                    ],
                                    "answer": "24",
                                    "explanation": "Rp120,000 remains after equipment. Rp120,000 ÷ Rp5,000 = 24.",
                                    "mistake_tag": "Working backward from a budget"
                                }
                            ]
                        },
                        "project": {
                            "intro": "Project task: use a cost model and a fixed budget to make a practical planning decision.",
                            "questions": [
                                {
                                    "id": "wp_l1_project_q1",
                                    "type": "numeric",
                                    "stage": "project",
                                    "skill_tag": "Budget-constrained planning",
                                    "prompt": "A school fair has a fixed setup cost of Rp40,000 and costs Rp7,000 per booth. With Rp130,000 available, what is the maximum number of whole booths that can be funded?",
                                    "answer": 12,
                                    "tolerance": 0.01,
                                    "whole_number": True,
                                    "input_hint": "Enter a whole number of booths.",
                                    "explanation": "Rp130,000 − Rp40,000 = Rp90,000. Twelve booths cost Rp84,000; thirteen would cost Rp91,000, exceeding the budget.",
                                    "mistake_tag": "Budget-constrained planning"
                                }
                            ]
                        }
                    }
                },
"questions": [
                    {
                        "id": "wp_l1_q1",
                        "type": "mc",
                        "prompt": "Which operation does the word 'total' usually suggest?",
                        "options": ["Addition", "Subtraction", "Multiplication", "Division"],
                        "answer": "Addition",
                        "explanation": (
                            "'Total' usually means combining amounts together, "
                            "which is addition."
                        ),
                        "mistake_tag": "Misidentifying the operation",
                    },
                    {
                        "id": "wp_l1_q2",
                        "type": "mc",
                        "prompt": (
                            "Sarah has 3 times as many apples as Tom. If Tom has "
                            "x apples, how would you write Sarah's apples?"
                        ),
                        "options": ["3x", "x/3", "x + 3", "x - 3"],
                        "answer": "3x",
                        "explanation": (
                            "'3 times as many' means multiplying Tom's amount by "
                            "3, so Sarah has 3x apples."
                        ),
                        "mistake_tag": "Misidentifying the operation",
                    },
                ],
            },
            {
                "id": "wp_l2",
                "title": "Multi-Step Problems",
                "kind": "standard",
                "explanation": (
                    "A multi-step word problem requires a sequence of operations. "
                    "Identify the relationship at each stage, calculate the first result, "
                    "and use that result in the next step. Keep track of units and apply "
                    "discounts after finding the subtotal."
                ),
                "worked_example": (
                    "Three notebooks cost Rp12,000 each and the shop gives Rp5,000 off the total. "
                    "First multiply: 3 × Rp12,000 = Rp36,000. Then subtract the discount: "
                    "Rp36,000 − Rp5,000 = Rp31,000."
                ),
                "interactive_question": {
                    "id": "wp_l2_screen3",
                    "type": "numeric",
                    "prompt": "Four tickets cost Rp15,000 each. You receive Rp10,000 off the total. How much do you pay in rupiah?",
                    "answer": 50000,
                    "tolerance": 0.01,
                    "whole_number": True,
                    "input_hint": "e.g. 50000",
                    "explanation": "4 × Rp15,000 = Rp60,000; subtract Rp10,000 to get Rp50,000.",
                    "mistake_tag": "Multi-step setup error",
                },
                "questions": [
                    {
                        "id": "wp_l2_q1",
                        "type": "numeric",
                        "prompt": (
                            "A notebook costs Rp12,000. You buy 3 and receive a Rp5,000 "
                            "discount on the total. How much do you pay in rupiah?"
                        ),
                        "answer": 31000,
                        "tolerance": 0.01,
                        "whole_number": True,
                        "input_hint": "e.g. 31000",
                        "explanation": "3 × Rp12,000 = Rp36,000; subtract Rp5,000 = Rp31,000.",
                        "mistake_tag": "Multi-step setup error",
                    },
                    {
                        "id": "wp_l2_q2",
                        "type": "numeric",
                        "prompt": (
                            "You save Rp15,000 per week. How many rupiah will you have "
                            "saved after 6 weeks?"
                        ),
                        "answer": 90000,
                        "tolerance": 0.01,
                        "whole_number": True,
                        "input_hint": "e.g. 90000",
                        "explanation": "Rp15,000 × 6 weeks = Rp90,000.",
                        "mistake_tag": "Multi-step setup error",
                    },
                ],
            },
            {
                "id": "wp_l3",
                "title": "Identifying Key Information",
                "kind": "standard",
                "explanation": (
                    "Word problems sometimes include extra details that aren't "
                    "needed to solve them. Before calculating, identify exactly "
                    "which numbers and relationships actually matter."
                ),
                "worked_example": (
                    "A notebook costs Rp8,000 and you buy 3. The shop has 100 notebooks left in stock, "
                    "but that detail is irrelevant to your cost. Use only the needed values: "
                    "3 × Rp8,000 = Rp24,000."
                ),
                "interactive_question": {
                    "id": "wp_l3_screen3",
                    "type": "numeric",
                    "prompt": "Five students each buy a ticket for Rp20,000. The hall has 200 seats. What is the total ticket cost in rupiah?",
                    "answer": 100000,
                    "tolerance": 0.01,
                    "whole_number": True,
                    "input_hint": "e.g. 100000",
                    "explanation": "Use the number of tickets and the price per ticket: 5 × Rp20,000 = Rp100,000. The hall capacity is not needed.",
                    "mistake_tag": "Missed key information",
                },
                "questions": [
                    {
                        "id": "wp_l3_q1",
                        "type": "mc",
                        "prompt": (
                            "A train travels 60 km in 1 hour. Which piece of "
                            "information helps you find its speed?"
                        ),
                        "options": [
                            "Distance and time",
                            "Only the distance",
                            "Only the time",
                            "Neither value",
                        ],
                        "answer": "Distance and time",
                        "explanation": (
                            "Speed is distance divided by time, so you need both "
                            "values: 60 km / 1 hour = 60 km/h."
                        ),
                        "mistake_tag": "Missed key information",
                    },
                    {
                        "id": "wp_l3_q2",
                        "type": "mc",
                        "prompt": (
                            "A store sells pens for Rp2,000 each. Maria buys 4 pens. The "
                            "store also has 100 pens in stock. How many pens did "
                            "Maria buy?"
                        ),
                        "options": ["4", "2", "100", "8"],
                        "answer": "4",
                        "explanation": (
                            "The '100 pens in stock' detail doesn't affect how "
                            "many Maria bought — that's stated directly as 4."
                        ),
                        "mistake_tag": "Missed key information",
                    },
                ],
            },
            {
                "id": "wp_l4",
                "title": "Real-World Challenge: Planning a Class Trip",
                "kind": "application",
                "explanation": (
                    "Some real-world costs combine a fixed fee and a variable cost. "
                    "The model is: total cost = fixed fee + (cost per person × number of people)."
                ),
                "worked_example": (
                    "A school club pays a fixed room fee of Rp100,000 plus Rp5,000 for each of 12 attendees. "
                    "Variable cost: Rp5,000 × 12 = Rp60,000. Total: Rp100,000 + Rp60,000 = Rp160,000."
                ),
                "interactive_question": {
                    "id": "wp_l4_screen3",
                    "type": "numeric",
                    "prompt": "A class trip bus costs a fixed Rp150,000 plus Rp8,000 per student. If 20 students go, what is the total bus cost in rupiah?",
                    "answer": 310000,
                    "tolerance": 0.01,
                    "whole_number": True,
                    "input_hint": "e.g. 310000",
                    "explanation": "Calculate the student cost first: Rp8,000 × 20 = Rp160,000. Add the fixed Rp150,000 fee: Rp150,000 + Rp160,000 = Rp310,000.",
                    "mistake_tag": APPLICATION_MISTAKE_TAG,
                },
                "questions": [
                    {
                        "id": "wp_l4_q1",
                        "type": "numeric",
                        "prompt": "Total bus cost (Rp):",
                        "answer": 310000,
                        "tolerance": 0.01,
                        "whole_number": True,
                        "input_hint": "e.g. 310000",
                        "explanation": (
                            "Rp150,000 flat fee + (Rp8,000 × 20 students) = Rp150,000 + Rp160,000 = Rp310,000."
                        ),
                        "mistake_tag": APPLICATION_MISTAKE_TAG,
                    }
                ],
            },
        ],
    },
}


COURSE_ORDER = ["fractions", "algebra", "word_problems"]

# Shared catalogue taxonomy: every course uses the same category/subject fields.
COURSE_CATEGORIES = [
    {"id": "academics", "label": "Academics"},
]
COURSE_SUBJECTS = [
    {"id": "mathematics", "label": "Mathematics"},
    {"id": "chemistry", "label": "Chemistry"},
    {"id": "physics", "label": "Physics"},
    {"id": "biology", "label": "Biology"},
    {"id": "english", "label": "English"},
    {"id": "computer_science", "label": "Computer Science"},
    {"id": "other", "label": "Other"},
]

# Chemistry content is authored separately from UI and registered here so
# every existing data.get_course / logic / progress consumer sees it.
from chemistry_course import CHEMISTRY_COURSE
from quadratics_course import QUADRATICS_COURSE
from geometry_course import GEOMETRY_COURSE
from clock_course import ANALOG_CLOCKS_COURSE

COURSES[CHEMISTRY_COURSE["id"]] = CHEMISTRY_COURSE
COURSE_ORDER.append(CHEMISTRY_COURSE["id"])
COURSES[QUADRATICS_COURSE["id"]] = QUADRATICS_COURSE
COURSE_ORDER.append(QUADRATICS_COURSE["id"])
COURSES[GEOMETRY_COURSE["id"]] = GEOMETRY_COURSE
COURSE_ORDER.append(GEOMETRY_COURSE["id"])
COURSES[ANALOG_CLOCKS_COURSE["id"]] = ANALOG_CLOCKS_COURSE
COURSE_ORDER.append(ANALOG_CLOCKS_COURSE["id"])

_SUBJECT_BY_COURSE = {
    "fractions": "mathematics",
    "algebra": "mathematics",
    "word_problems": "mathematics",
    "chemistry_9701": "chemistry",
    "quadratics_graphs": "mathematics",
    "basic_geometry": "mathematics",
    "analog_clocks": "mathematics",
}
_CATEGORY_LABELS = {item["id"]: item["label"] for item in COURSE_CATEGORIES}
_SUBJECT_LABELS = {item["id"]: item["label"] for item in COURSE_SUBJECTS}

# Backfill metadata for all current courses without changing their IDs or
# lesson/progress structures. Lesson count is always derived from published data.
for _course in COURSES.values():
    _course.setdefault("category_id", "academics")
    _course.setdefault("subject_id", _SUBJECT_BY_COURSE.get(_course["id"], "other"))
    _course["category_label"] = _CATEGORY_LABELS.get(_course["category_id"], "Other")
    _course["subject_label"] = _SUBJECT_LABELS.get(_course["subject_id"], "Other")
    _course["lesson_count"] = len(_course.get("lessons", []))
    _course.setdefault("level", "Not specified")
    _course.setdefault("curriculum", "General")

SUBJECT_OPTIONS = [
    "Math", "Science", "Language Arts", "History", "Art", "Music",
    "Computer Science", "Physical Education", "Other",
]

LEARNING_STYLE_OPTIONS = [
    "Prefer not to say", "Visual", "Auditory", "Reading / writing", "Hands-on", "Mixed",
]

DIFFICULTY_OPTIONS = ["Adaptive", "Easy", "Medium", "Hard"]

SESSION_LENGTH_OPTIONS = [
    "Prefer not to say", "5-10 minutes", "10-20 minutes", "20-30 minutes", "30+ minutes",
]

FEEDBACK_STYLE_OPTIONS = [
    "Prefer not to say", "Encouraging", "Direct and brief", "Detailed explanations",
]

LANGUAGE_OPTIONS = [
    "Prefer not to say", "English", "Bahasa Indonesia", "Spanish", "Mandarin", "French", "Other",
]

GENDER_OPTIONS = [
    "Male",
    "Female",
    "Prefer not to say / others",
]

GRADE_OPTIONS = [
    "Prefer not to say", "Grade 6", "Grade 7", "Grade 8", "Grade 9",
    "Grade 10", "Grade 11", "Grade 12", "Other",
]

TIMEZONE_OPTIONS = [
    "Prefer not to say", "UTC-8", "UTC-7", "UTC-6", "UTC-5", "UTC-4",
    "UTC+0", "UTC+1", "UTC+2", "UTC+3", "UTC+5:30", "UTC+7", "UTC+8",
    "UTC+9", "UTC+10", "UTC+12",
]


def get_course(course_id):
    """Return a course dict by id, or None if it doesn't exist."""
    return COURSES.get(course_id)


def get_lesson(course_id, lesson_id):
    """Return a (lesson, lesson_index) tuple for a course, or (None, -1)."""
    course = get_course(course_id)
    if not course:
        return None, -1
    for idx, lesson in enumerate(course["lessons"]):
        if lesson["id"] == lesson_id:
            return lesson, idx
    return None, -1


def all_courses_in_order():
    """Return course dicts in the fixed Version 1 order."""
    return [COURSES[cid] for cid in COURSE_ORDER]