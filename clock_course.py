"""Analog Clock Foundations — a visual, misconception-led Vocogni course."""

from __future__ import annotations

from copy import deepcopy


def _mc(qid, prompt, options, answer, explanation, skill):
    return {
        "id": qid,
        "type": "mc",
        "prompt": prompt,
        "options": list(options),
        "answer": answer,
        "explanation": explanation,
        "skill_tag": skill,
        "mistake_tag": skill,
    }


def _num(qid, prompt, answer, explanation, skill):
    return {
        "id": qid,
        "type": "numeric",
        "prompt": prompt,
        "answer": answer,
        "tolerance": 0.01,
        "whole_number": True,
        "input_hint": "Enter the number only.",
        "explanation": explanation,
        "skill_tag": skill,
        "mistake_tag": skill,
    }


def _lesson(number, title, visual_key, explanation, worked_example, questions, *, kind="standard"):
    lesson = {
        "id": f"clock_l{number}",
        "title": title,
        "kind": kind,
        "visual_key": visual_key,
        "explanation": explanation,
        "worked_example": worked_example,
        "practice_questions": questions,
        "interactive_question": deepcopy(questions[0]),
    }
    return lesson


LESSONS = [
    _lesson(
        1,
        "Meet the Two Hands",
        "clock_foundation",
        (
            "<h4>Start with what each hand measures</h4>"
            "<p>A standard analog clock has two main hands. The <strong>longer hand is the minute hand</strong>. "
            "It measures minutes. The <strong>shorter hand is the hour hand</strong>. It tells which hour is in progress.</p>"
            "<ul>"
            "<li>The minute hand makes one full turn in <strong>60 minutes</strong>.</li>"
            "<li>Each time the minute hand completes one turn, the hour hand moves forward by one hour.</li>"
            "<li>The hands move clockwise: from 12, past 1, 2, 3, and onward.</li>"
            "</ul>"
            "<h4>Do not memorise two disconnected shapes</h4>"
            "<p>Think of a team: the long hand counts the minutes inside the current hour; the short hand shows "
            "which hour those minutes belong to. They move together.</p>"
            "<p><strong>Check yourself:</strong> point to each hand and say its job before reading any time.</p>"
        ),
        (
            "At 3:00, the minute hand points to 12 and the hour hand points to 3. "
            "After 30 minutes, the minute hand has travelled halfway around the clock. "
            "The hour hand has also moved halfway from 3 toward 4. The time is 3:30, not 4:30."
        ),
        [
            _mc(
                "clock_l1_q1",
                "Which hand tells you the minutes on a standard analog clock?",
                ["The longer hand", "The shorter hand", "Both hands equally", "The hand nearest 12"],
                "The longer hand",
                "The longer hand is the minute hand. It makes one complete turn every 60 minutes.",
                "Clock hand roles",
            ),
            _num(
                "clock_l1_q2",
                "The minute hand makes one complete turn. How many minutes have passed?",
                60,
                "One complete turn of the minute hand represents 60 minutes, or one hour.",
                "Clock hand roles",
            ),
            _mc(
                "clock_l1_q3",
                "At 5:00, the minute hand is at 12. After one full minute-hand turn, where will the hour hand point?",
                ["6", "5", "12", "11"],
                "6",
                "A full minute-hand turn is 60 minutes. During that hour, the hour hand advances from 5 to 6.",
                "Clock hand roles",
            ),
        ],
    ),
    _lesson(
        2,
        "Count the Minutes — Fives, Then Ones",
        "clock_minute_counting",
        (
            "<h4>The numbers are shortcuts, not minute labels</h4>"
            "<p>For the <strong>minute hand</strong>, each large number marks another group of five minutes:</p>"
            "<p><strong>1 = 5, 2 = 10, 3 = 15, 4 = 20, …, 11 = 55, 12 = 60 (or 00).</strong></p>"
            "<p>There are also four small marks between each pair of numbers. Each small mark is <strong>one minute</strong>.</p>"
            "<h4>Use the same two-step count every time</h4>"
            "<ol>"
            "<li>Count the groups of five to the number the minute hand points at.</li>"
            "<li>Count the extra small marks after that number, one by one.</li>"
            "</ol>"
            "<p>Never read the number 4 as four minutes when you are reading the <strong>minute hand</strong>. "
            "It means 20 minutes because 4 groups of 5 make 20.</p>"
        ),
        (
            "The minute hand points to 4, then sits two small marks beyond it. "
            "Number 4 means 4 × 5 = 20 minutes. Add the two extra marks: 20 + 2 = 22 minutes. "
            "The minute value is 22, not 4 or 42."
        ),
        [
            _num(
                "clock_l2_q1",
                "The minute hand points exactly to 7. How many minutes past the hour is it?",
                35,
                "Each number is five minutes for the minute hand: 7 × 5 = 35 minutes.",
                "Counting minute groups of five",
            ),
            _num(
                "clock_l2_q2",
                "The minute hand points to 4 and then sits two small marks beyond it. How many minutes past the hour?",
                22,
                "Number 4 gives 4 × 5 = 20 minutes. Two extra marks give 20 + 2 = 22 minutes.",
                "Counting individual minute ticks",
            ),
            _num(
                "clock_l2_q3",
                "The minute hand points exactly to 11. How many minutes past the hour is it?",
                55,
                "Eleven groups of five minutes give 11 × 5 = 55 minutes.",
                "Counting minute groups of five",
            ),
            _num(
                "clock_l2_q4",
                "The minute hand points to 2 and then passes six small marks. How many minutes past the hour?",
                16,
                "Number 2 means 10 minutes. Add six individual minute marks: 10 + 6 = 16.",
                "Counting individual minute ticks",
            ),
        ],
    ),
    _lesson(
        3,
        "The Hour Hand Moves Between Numbers",
        "clock_hour_position",
        (
            "<h4>The short hand does not jump from one number to the next</h4>"
            "<p>The hour hand moves <strong>continuously</strong> as the minutes pass. It starts at an hour number "
            "and gradually travels toward the next number.</p>"
            "<ul>"
            "<li>At 3:00, it points to 3.</li>"
            "<li>At 3:15, it is a little past 3.</li>"
            "<li>At 3:30, it is halfway between 3 and 4.</li>"
            "<li>At 3:55, it is very close to 4, but it is still in the 3 o'clock hour.</li>"
            "<li>Only at 4:00 does it reach 4.</li>"
            "</ul>"
            "<p><strong>Reliable rule:</strong> identify the last hour number the short hand has passed. "
            "Do not choose the number it is closest to.</p>"
        ),
        (
            "The minute hand is at 11, so it shows 55 minutes. The short hand is between 7 and 8, very close to 8. "
            "It has passed 7 but has not reached 8. Read the time as 7:55, not 8:55."
        ),
        [
            _mc(
                "clock_l3_q1",
                "At 3:40, the short hour hand is between 3 and 4. Which hour is currently in progress?",
                ["3 o'clock", "4 o'clock", "40 o'clock", "The nearest hour, 4"],
                "3 o'clock",
                "The short hand has passed 3 but has not reached 4. The current hour is still 3.",
                "Hour hand position",
            ),
            _mc(
                "clock_l3_q2",
                "At 7:55, where should the short hour hand be?",
                [
                    "Between 7 and 8, very close to 8",
                    "Exactly on 7",
                    "Exactly on 8",
                    "Halfway between 7 and 8",
                ],
                "Between 7 and 8, very close to 8",
                "The hour hand moves gradually. At 55 minutes past 7, it is near 8 but has not arrived there.",
                "Hour hand position",
            ),
            _mc(
                "clock_l3_q3",
                "The short hand is halfway between 5 and 6, and the long hand points to 6. What time is shown?",
                ["5:30", "6:30", "5:06", "6:05"],
                "5:30",
                "The long hand at 6 means 30 minutes. The short hand halfway from 5 to 6 means the 5 o'clock hour is halfway through.",
                "Hour hand position",
            ),
        ],
    ),
    _lesson(
        4,
        "Read the Whole Clock — One Method, Every Time",
        "clock_reading",
        (
            "<h4>Use this order; do not guess from the shape</h4>"
            "<ol>"
            "<li><strong>Read the long minute hand.</strong> Count by fives, then add the extra small ticks.</li>"
            "<li><strong>Read the short hour hand.</strong> Find the last hour number it has passed.</li>"
            "<li><strong>Join them.</strong> Write hour:minutes, using two digits for minutes (for example, 7:05).</li>"
            "<li><strong>Say the time.</strong> Use 'past' for minutes 1–30 and 'to' for minutes 31–59 if that wording is used.</li>"
            "</ol>"
            "<h4>Four language anchors</h4>"
            "<ul><li>15 minutes = quarter past.</li><li>30 minutes = half past.</li>"
            "<li>45 minutes = quarter to the next hour.</li><li>00 minutes = o'clock.</li></ul>"
            "<p>For 2:45, the long hand shows 45 minutes and the short hand is between 2 and 3. "
            "That is 2:45, also called quarter to 3. It is not 3:45.</p>"
        ),
        (
            "The long hand is on 5: 5 × 5 = 25 minutes. The short hand is just past 9, so the hour is 9. "
            "Combine the readings: 9:25. In words, this is 25 minutes past 9."
        ),
        [
            _mc(
                "clock_l4_q1",
                "The long hand points to 5 and the short hand is just past 9. What time is shown?",
                ["9:25", "5:09", "9:05", "10:25"],
                "9:25",
                "The long hand at 5 means 25 minutes. The short hand has passed 9, so the time is 9:25.",
                "Combining hour and minute hands",
            ),
            _mc(
                "clock_l4_q2",
                "What digital time means 'quarter to 3'?",
                ["2:45", "3:15", "2:15", "3:45"],
                "2:45",
                "A quarter hour is 15 minutes. Quarter to 3 means 15 minutes before 3:00, which is 2:45.",
                "Reading past and to language",
            ),
            _mc(
                "clock_l4_q3",
                "The minute hand shows 52 minutes and the short hand is close to 9 but has not reached it. What time is shown?",
                ["8:52", "9:52", "8:12", "9:08"],
                "8:52",
                "The minute hand gives 52. The short hand has passed 8 and is approaching 9, so it is still 8:52.",
                "Combining hour and minute hands",
            ),
            _mc(
                "clock_l4_q4",
                "Which digital time is 'quarter past 10'?",
                ["10:15", "10:45", "9:45", "11:15"],
                "10:15",
                "Quarter past means 15 minutes after the hour: 10:15.",
                "Reading past and to language",
            ),
        ],
    ),
    _lesson(
        5,
        "Elapsed Time — Move Forward, Do Not Restart",
        "clock_elapsed",
        (
            "<h4>Elapsed time asks how long passed</h4>"
            "<p>Elapsed time is the amount of time between a start and an end. You are not reading one clock; "
            "you are measuring the movement from the first time to the second.</p>"
            "<h4>The jump-to-the-next-hour method</h4>"
            "<ol>"
            "<li>Count from the start time to the next exact hour.</li>"
            "<li>Count from that hour to the end time.</li>"
            "<li>Add the two jumps.</li>"
            "</ol>"
            "<p>Example: 2:47 to 3:18. From 2:47 to 3:00 is 13 minutes. From 3:00 to 3:18 is 18 minutes. "
            "Total elapsed time = 13 + 18 = 31 minutes.</p>"
            "<p>For longer intervals, continue adding full hours and remaining minutes. Keep a timeline so you "
            "do not confuse the clock's hand position with the amount of time that has passed.</p>"
        ),
        (
            "A lesson starts at 9:50 and ends at 10:15. First jump to 10:00: 10 minutes. "
            "Then count 15 more minutes to 10:15. Total = 10 + 15 = 25 minutes."
        ),
        [
            _num(
                "clock_l5_q1",
                "How many minutes pass from 2:47 to 3:18?",
                31,
                "2:47 to 3:00 is 13 minutes. 3:00 to 3:18 is 18 minutes. Total: 13 + 18 = 31 minutes.",
                "Elapsed time across an hour",
            ),
            _num(
                "clock_l5_q2",
                "How many minutes pass from 9:50 to 10:15?",
                25,
                "9:50 to 10:00 is 10 minutes. Add 15 minutes to reach 10:15. Total: 25 minutes.",
                "Elapsed time across an hour",
            ),
            _mc(
                "clock_l5_q3",
                "A film starts at 16:35 and lasts 1 hour 25 minutes. When does it finish?",
                ["18:00", "17:50", "18:10", "19:00"],
                "18:00",
                "16:35 + 1 hour = 17:35. Add 25 minutes to reach 18:00.",
                "Time in a real schedule",
            ),
            _num(
                "clock_l5_q4",
                "A club meeting begins at 4:20 and lasts 45 minutes. At what minute of the next hour does it end? Enter the minute number only.",
                5,
                "4:20 + 40 minutes = 5:00; five more minutes gives 5:05. The minute number is 5.",
                "Time in a real schedule",
            ),
        ],
    ),
    _lesson(
        6,
        "Final Check — Read, Explain, and Apply",
        "clock_final",
        (
            "<p>This check mixes hand identification, minute counting, hour-hand position, complete time reading, "
            "and elapsed time. Work independently and write down the two hand readings before combining them.</p>"
            "<p>When you make an error, classify it: <strong>hand role</strong>, <strong>minute count</strong>, "
            "<strong>hour position</strong>, <strong>combining the hands</strong>, or <strong>elapsed time</strong>. "
            "Then return to the lesson that teaches that exact step.</p>"
        ),
        (
            "This is a cumulative assessment. Use the method from the lessons, but do not open the worked examples "
            "while answering. The purpose is to see whether you can transfer the method to new times and contexts."
        ),
        [
            _mc(
                "clock_l6_q1",
                "The minute hand points to 10 and the short hand is between 5 and 6. What time is shown?",
                ["5:50", "6:50", "5:10", "10:05"],
                "5:50",
                "Number 10 on the minute dial means 50 minutes. The short hand has passed 5 but not 6: 5:50.",
                "Complete analog time reading",
            ),
            _mc(
                "clock_l6_q2",
                "The minute hand points to 4 and then passes three small marks. How many minutes past the hour?",
                ["23", "20", "43", "7"],
                "23",
                "Number 4 gives 20 minutes; three extra marks give 20 + 3 = 23 minutes.",
                "Minute counting transfer",
            ),
            _mc(
                "clock_l6_q3",
                "At 11:45, the short hand is closest to 12. Which hour is still in progress?",
                ["11", "12", "45", "1"],
                "11",
                "The short hand has passed 11 but has not reached 12. The time is still in the 11 o'clock hour.",
                "Hour-hand position transfer",
            ),
            _mc(
                "clock_l6_q4",
                "What digital time means 'quarter to 7'?",
                ["6:45", "7:15", "6:15", "7:45"],
                "6:45",
                "Quarter to 7 is 15 minutes before 7:00, so it is 6:45.",
                "Past and to language transfer",
            ),
            _num(
                "clock_l6_q5",
                "How many minutes pass from 3:38 to 4:12?",
                34,
                "3:38 to 4:00 is 22 minutes. Add 12 minutes: 22 + 12 = 34 minutes.",
                "Elapsed time transfer",
            ),
            _mc(
                "clock_l6_q6",
                "A bus leaves at 07:48 and the trip lasts 1 hour 35 minutes. At what time does it arrive?",
                ["09:23", "09:13", "08:83", "10:23"],
                "09:23",
                "07:48 + 1 hour = 08:48. Add 35 minutes: 08:48 to 09:00 is 12 minutes, then 23 more gives 09:23.",
                "Real-schedule transfer",
            ),
        ],
        kind="assessment",
    ),
]


COURSE_ENTRY_DIAGNOSTIC = {
    "version": 1,
    "prerequisite_review": (
        "Start with the physical roles of the two hands. The longer hand counts minutes; "
        "the shorter hand shows the hour already passed. Count minute groups in fives, then "
        "extra ticks one by one. The hour hand moves continuously, so use the last hour number "
        "it has passed. For elapsed time, move forward to the next hour and add the remaining minutes."
    ),
    "questions": [
        {
            "id": "clock_entry_d1",
            "type": "mc",
            "stage": "prerequisite",
            "skill_tag": "Clock hand roles",
            "prompt": "On a standard analog clock, which hand shows the minutes?",
            "options": ["The longer hand", "The shorter hand", "The hand nearest 12", "Both hands equally"],
            "answer": "The longer hand",
            "explanation": "The longer hand is the minute hand. It completes one full turn in 60 minutes.",
            "mistake_tag": "Clock hand roles",
        },
        {
            "id": "clock_entry_d2",
            "type": "mc",
            "stage": "level_1",
            "skill_tag": "Counting minute groups of five",
            "prompt": "The minute hand points to 8. How many minutes past the hour is it?",
            "options": ["40", "8", "45", "50"],
            "answer": "40",
            "explanation": "The minute hand counts in fives: 8 × 5 = 40 minutes.",
            "mistake_tag": "Counting minute groups of five",
        },
        {
            "id": "clock_entry_d3",
            "type": "mc",
            "stage": "level_2",
            "skill_tag": "Hour hand position",
            "prompt": "At 6:50, where is the short hour hand?",
            "options": [
                "Between 6 and 7, close to 7",
                "Exactly on 7",
                "Exactly on 6",
                "Between 5 and 6",
            ],
            "answer": "Between 6 and 7, close to 7",
            "explanation": "The hour hand moves continuously. At 50 minutes past 6 it is close to 7, but has not reached it.",
            "mistake_tag": "Hour hand position",
        },
        {
            "id": "clock_entry_d4",
            "type": "mc",
            "stage": "level_3",
            "skill_tag": "Combining both hands",
            "prompt": "The minute hand points to 6 and the short hand is halfway between 4 and 5. What time is shown?",
            "options": ["4:30", "5:30", "4:06", "6:04"],
            "answer": "4:30",
            "explanation": "The minute hand at 6 means 30 minutes. The hour hand is halfway from 4 to 5, so it is 4:30.",
            "mistake_tag": "Combining both hands",
        },
        {
            "id": "clock_entry_d5",
            "type": "mc",
            "stage": "project",
            "skill_tag": "Elapsed time",
            "prompt": "A class starts at 2:40 and ends at 3:05. How long does it last?",
            "options": ["25 minutes", "15 minutes", "35 minutes", "65 minutes"],
            "answer": "25 minutes",
            "explanation": "2:40 to 3:00 is 20 minutes; add 5 minutes to reach 3:05. Total: 25 minutes.",
            "mistake_tag": "Elapsed time",
        },
    ],
}

LESSONS[0]["diagnostic"] = COURSE_ENTRY_DIAGNOSTIC

ANALOG_CLOCKS_COURSE = {
    "id": "analog_clocks",
    "title": "Analog Clock Foundations",
    "short_description": (
        "Learn to read an analog clock by understanding how its two hands move, "
        "counting minutes accurately, reading the hour hand between numbers, and "
        "calculating elapsed time in real schedules."
    ),
    "difficulty": "Beginner",
    "topic_label": "Analog Clocks",
    "category_id": "academics",
    "subject_id": "mathematics",
    "level": "Foundational numeracy · flexible catch-up",
    "curriculum": "General foundational mathematics",
    "course_version": "1.0.0",
    "lessons": LESSONS,
}

__all__ = ["ANALOG_CLOCKS_COURSE", "LESSONS", "COURSE_ENTRY_DIAGNOSTIC"]
