from datetime import datetime

# ----------------------------------
# DAILY WORKOUT (USED IN DASHBOARD)
# ----------------------------------
def get_today_workout():
    day = datetime.now().strftime("%A")

    daily_plan = {
        "Monday": {
            "muscle": "Chest + Triceps",
            "exercises": [
                "Bench Press",
                "Incline Dumbbell Press",
                "Chest Fly",
                "Tricep Pushdown",
                "Overhead Tricep Extension"
            ]
        },
        "Tuesday": {
            "muscle": "Back + Biceps",
            "exercises": [
                "Pull-ups",
                "Lat Pulldown",
                "Seated Row",
                "Barbell Curl",
                "Hammer Curl"
            ]
        },
        "Wednesday": {
            "muscle": "Legs + Shoulders",
            "exercises": [
                "Squats",
                "Leg Press",
                "Lunges",
                "Shoulder Press",
                "Lateral Raises"
            ]
        },
        "Thursday": {
            "muscle": "Chest + Triceps",
            "exercises": [
                "Flat Dumbbell Press",
                "Incline Bench Press",
                "Cable Fly",
                "Skull Crushers",
                "Tricep Dips"
            ]
        },
        "Friday": {
            "muscle": "Back + Biceps",
            "exercises": [
                "Deadlift",
                "T-Bar Row",
                "Lat Pulldown",
                "Preacher Curl",
                "Concentration Curl"
            ]
        },
        "Saturday": {
            "muscle": "Legs + Shoulders",
            "exercises": [
                "Leg Curl",
                "Leg Extension",
                "Calf Raises",
                "Arnold Press",
                "Front Raises"
            ]
        },
        "Sunday": {
            "muscle": "Rest Day",
            "exercises": [
                "Stretching",
                "Walking",
                "Recovery"
            ]
        }
    }

    return day, daily_plan.get(day, daily_plan["Sunday"])


# ----------------------------------
# WEEKLY WORKOUT (USED IN WEEKLY PLAN PAGE & DOWNLOAD)
# ----------------------------------
WEEKLY_PLAN = {
    "Monday": (
        "Chest",
        [
            "Bench Press",
            "Push-ups",
            "Chest Fly"
        ]
    ),
    "Tuesday": (
        "Back",
        [
            "Pull-ups",
            "Deadlift",
            "Rows"
        ]
    ),
    "Wednesday": (
        "Legs",
        [
            "Squats",
            "Leg Press",
            "Lunges"
        ]
    ),
    "Thursday": (
        "Shoulders",
        [
            "Overhead Press",
            "Lateral Raises"
        ]
    ),
    "Friday": (
        "Arms",
        [
            "Biceps Curls",
            "Triceps Dips"
        ]
    ),
    "Saturday": (
        "Core + Cardio",
        [
            "Plank",
            "Crunches",
            "Running"
        ]
    ),
    "Sunday": (
        "Rest",
        [
            "Stretching",
            "Light walk"
        ]
    )
}
