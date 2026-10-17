"""
data.py — Static dummy content for VOCogni Version 1.

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
        "short_description": "Learn fraction fundamentals and basic operations.",
        "difficulty": "Beginner",
        "topic_label": "Fractions",
        "lessons": [
            {
                "id": "fractions_l1",
                "title": "Understanding Fractions",
                "kind": "standard",
                "explanation": (
                    "A fraction describes part of a whole. It is written as two "
                    "numbers separated by a line: the <strong>numerator</strong> "
                    "(top) tells you how many parts you have, and the "
                    "<strong>denominator</strong> (bottom) tells you how many "
                    "equal parts the whole is divided into.\n\n"
                    "For example, in the fraction 3/4, the whole is split into 4 "
                    "equal parts, and you have 3 of them."
                ),
                "worked_example": (
                    "A chocolate bar is divided into 4 equal pieces. If you eat 3 pieces, "
                    "you have eaten 3/4: the numerator is 3 pieces and the denominator is 4 equal pieces."
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
                            "prompt": "In 1/2, what does the bottom number 2 tell you?",
                            "options": [
                                "The whole is divided into 2 equal parts",
                                "You have 2 whole objects",
                                "The top number is 2",
                                "There are 2 different wholes"
                            ],
                            "answer": "The whole is divided into 2 equal parts",
                            "explanation": "The denominator tells how many equal parts make up one whole.",
                            "mistake_tag": "Meaning of the denominator"
                        },
                        {
                            "id": "fractions_l1_d2",
                            "type": "mc",
                            "stage": "level_1",
                            "skill_tag": "Representing fractions",
                            "prompt": "Which fraction represents 3 parts out of 5 equal parts?",
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
                            "explanation": "Multiplying numerator and denominator by 2 gives 4/6.",
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
                            "explanation": "2/3 is about 0.667, greater than 5/8 (0.625), 3/5 (0.6), and 1/2 (0.5).",
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
                    "prerequisite_review": "A fraction names equal parts of one whole. The numerator is the top number and counts the parts being considered. The denominator is the bottom number and tells how many equal parts make up the whole. Make sure the parts are equal before naming a fraction.",
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
                ],
            },
            {
                "id": "fractions_l2",
                "title": "Adding Fractions",
                "kind": "standard",
                "explanation": (
                    "When two fractions share the same denominator, you can add "
                    "them by adding the numerators and keeping the denominator the "
                    "same.\n\n"
                    "For example: 1/5 + 2/5 = (1 + 2)/5 = 3/5."
                ),
                "worked_example": (
                    "For 2/7 + 3/7, the denominators are equal. Add the numerators and keep the denominator: "
                    "2/7 + 3/7 = 5/7. Do not add the denominators."
                ),
                "interactive_question": {
                    "id": "fractions_l2_screen3",
                    "type": "mc",
                    "prompt": "What is 1/6 + 3/6?",
                    "options": ["4/6", "4/12", "3/6", "1/3"],
                    "answer": "4/6",
                    "explanation": "The denominators match, so add the numerators: 1 + 3 = 4, giving 4/6 (which can simplify to 2/3).",
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
                        "explanation": "1/4 + 1/4 = 2/4 = 0.5.",
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
                        "explanation": "1/5 + 2/5 = 3/5 = 0.6.",
                        "mistake_tag": "Addition error",
                    },
                ],
            },
            {
                "id": "fractions_l3",
                "title": "Simplifying Fractions",
                "kind": "standard",
                "explanation": (
                    "Simplifying a fraction means dividing the numerator and "
                    "denominator by the same number until they share no common "
                    "factor other than 1.\n\n"
                    "For example: 4/8 — both divide evenly by 4 — simplifies to 1/2."
                ),
                "worked_example": (
                    "To simplify 12/18, divide both numbers by their greatest common factor, 6: "
                    "12 ÷ 6 = 2 and 18 ÷ 6 = 3, so 12/18 = 2/3."
                ),
                "interactive_question": {
                    "id": "fractions_l3_screen3",
                    "type": "mc",
                    "prompt": "What is 8/12 in its simplest form?",
                    "options": ["2/3", "4/6", "1/3", "8/6"],
                    "answer": "2/3",
                    "explanation": "Divide numerator and denominator by 4: 8/12 = 2/3. The fraction 4/6 can be simplified again.",
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
                            "4 and 8 share a common factor of 4. Dividing both by "
                            "4 gives 1/2."
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
                            "6 and 9 share a common factor of 3. Dividing both by "
                            "3 gives 2/3, so the new denominator is 3."
                        ),
                        "mistake_tag": "Incorrect simplification",
                    },
                ],
            },
            {
                "id": "fractions_l4",
                "title": "Real-World Challenge: Scaling a Recipe",
                "kind": "application",
                "explanation": (
                    "Recipe scaling keeps ingredient amounts proportional to serving counts. "
                    "Find the scale factor by dividing the new number of servings by the original "
                    "number of servings, then multiply every ingredient by that factor."
                ),
                "worked_example": (
                    "A recipe uses 3/4 cup of sugar for 4 servings. For 8 servings, the scale factor is 8 ÷ 4 = 2, "
                    "so use 3/4 × 2 = 6/4 = 1 1/2 cups."
                ),
                "interactive_question": {
                    "id": "fractions_l4_screen3",
                    "type": "numeric",
                    "prompt": "A recipe needs 2/3 cup of oats for 2 servings. How many cups are needed for 6 servings? Enter a decimal.",
                    "answer": 2,
                    "tolerance": 0.01,
                    "whole_number": False,
                    "input_hint": "e.g. 2",
                    "explanation": "The number of servings triples (6 ÷ 2 = 3), so multiply 2/3 × 3 = 2 cups.",
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
                            "Doubling the servings (4 to 8) means doubling every "
                            "ingredient: 3/4 cup x 2 = 1.5 cups of sugar."
                        ),
                        "mistake_tag": APPLICATION_MISTAKE_TAG,
                    }
                ],
            },
        ],
    },
    "algebra": {
        "id": "algebra",
        "title": "Algebra Basics",
        "short_description": "Understand variables and solve simple equations.",
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
        "short_description": "Learn how to translate real-world problems into mathematical operations.",
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