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
                    "REAL-WORLD CHALLENGE\n\n"
                    "You are scaling a recipe. The original recipe needs 3/4 cup "
                    "of sugar for 4 servings. You want to make 8 servings.\n\n"
                    "How many cups of sugar do you need?"
                ),
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
                    "REAL-WORLD CHALLENGE\n\n"
                    "You are pricing a product for a small business.\n\n"
                    "The product costs Rp60,000 to produce. You want a 25% profit.\n\n"
                    "What should the selling price be?"
                ),
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
                    "Some word problems need more than one calculation. Break "
                    "the problem into smaller steps, solve each one in order, "
                    "and use the result of one step in the next.\n\n"
                    "For example: 3 books at $12 each, minus a $5 discount: "
                    "(3 x 12) - 5 = 36 - 5 = 31."
                ),
                "questions": [
                    {
                        "id": "wp_l2_q1",
                        "type": "numeric",
                        "prompt": (
                            "A book costs $12. You buy 3 books and get a $5 "
                            "discount on the total. How much do you pay?"
                        ),
                        "answer": 31,
                        "tolerance": 0.01,
                        "whole_number": True,
                        "input_hint": "e.g. 31",
                        "explanation": "(3 x $12) - $5 = $36 - $5 = $31.",
                        "mistake_tag": "Multi-step setup error",
                    },
                    {
                        "id": "wp_l2_q2",
                        "type": "numeric",
                        "prompt": (
                            "You save $15 per week. How many dollars will you have "
                            "saved after 6 weeks?"
                        ),
                        "answer": 90,
                        "tolerance": 0.01,
                        "whole_number": True,
                        "input_hint": "e.g. 90",
                        "explanation": "$15 x 6 weeks = $90.",
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
                            "A store sells pens for $2 each. Maria buys 4 pens. The "
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
                    "REAL-WORLD CHALLENGE\n\n"
                    "You are planning a class trip. Bus rental costs a $150 flat "
                    "fee plus $8 per student. There are 20 students going.\n\n"
                    "What is the total cost of the bus?"
                ),
                "questions": [
                    {
                        "id": "wp_l4_q1",
                        "type": "numeric",
                        "prompt": "Total bus cost ($):",
                        "answer": 310,
                        "tolerance": 0.01,
                        "whole_number": True,
                        "input_hint": "e.g. 310",
                        "explanation": (
                            "$150 flat fee + ($8 x 20 students) = $150 + $160 = $310."
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