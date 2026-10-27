"""Book plan: one book per grade, each unit follows the 20-section ROXY template."""

BOOKS = {
    2: {
        "level": "Grade 2 – Beginner",
        "color": "#ff7a59",
        "reading_words": (60, 85, 130),
        "notes": (
            "Learners are 7 years old and beginners. Use very short, concrete sentences, "
            "present simple only, high-frequency words, lots of repetition. Questions must be "
            "answerable straight from the text."
        ),
        "units": [
            ("My School", "School Life"),
            ("My Family", "Family & Love"),
            ("My Body", "Me & My Body"),
            ("Colours and Shapes", "The World Around Me"),
            ("My Toys", "Play Time"),
            ("Animals at the Zoo", "Animals"),
            ("Food and Drinks", "Healthy Eating"),
            ("My House", "Home Sweet Home"),
            ("My Clothes", "Everyday Life"),
            ("Weather and Seasons", "Nature"),
        ],
    },
    3: {
        "level": "Grade 3 – Elementary",
        "color": "#2bb3a3",
        "reading_words": (85, 120, 170),
        "notes": (
            "Learners are 8 years old. Use present simple, present continuous for actions "
            "happening now, can/can't, have got, simple wh-questions. Sentences may join with "
            "and/but/because."
        ),
        "units": [
            ("Me and My Friends", "Friendship"),
            ("My School Things", "School Life"),
            ("My Hobbies", "Free Time"),
            ("My Day", "Daily Routines & Time"),
            ("Rooms in My Home", "Home"),
            ("My Pets", "Animals & Care"),
            ("Jobs People Do", "Community"),
            ("Sports and Games", "Healthy Body"),
            ("At the Park", "Outdoor Fun"),
            ("Food I Like", "Healthy Eating"),
        ],
    },
    4: {
        "level": "Grade 4 – Pre-Intermediate",
        "color": "#6c63ff",
        "reading_words": (110, 150, 210),
        "notes": (
            "Learners are 9 years old. Use present simple, present continuous, can/could for "
            "ability, past simple of be and common regular/irregular verbs, will for plans, "
            "comparatives in simple form. Readings can have 2–3 short paragraphs."
        ),
        "units": [
            ("Countries and Nationalities", "Around the World"),
            ("My Week and Timetable", "School Life"),
            ("Birthdays and Months", "Celebrations"),
            ("What I Can Do", "Abilities & Talents"),
            ("Places in My Town", "My Community"),
            ("Tet and Festivals", "Culture"),
            ("Healthy Habits", "Health"),
            ("Going Shopping", "Money & Shopping"),
            ("Wild Animals", "Nature & Environment"),
            ("My Summer Holiday", "Travel & Memories"),
        ],
    },
}
