import random


DICE_ART = {
    1: (
        "┌─────────┐",
        "│         │",
        "│    ●    │",
        "│         │",
        "└─────────┘",
    ),
    2: (
        "┌─────────┐",
        "│  ●      │",
        "│         │",
        "│      ●  │",
        "└─────────┘",
    ),
    3: (
        "┌─────────┐",
        "│  ●      │",
        "│    ●    │",
        "│      ●  │",
        "└─────────┘",
    ),
    4: (
        "┌─────────┐",
        "│  ●   ●  │",
        "│         │",
        "│  ●   ●  │",
        "└─────────┘",
    ),
    5: (
        "┌─────────┐",
        "│  ●   ●  │",
        "│    ●    │",
        "│  ●   ●  │",
        "└─────────┘",
    ),
    6: (
        "┌─────────┐",
        "│  ●   ●  │",
        "│  ●   ●  │",
        "│  ●   ●  │",
        "└─────────┘",
    )
}
DIE_HEIGHT = len(DICE_ART[1])
DIE_WIDTH = len(DICE_ART[1][0])
DIE_FACE_SEPARATOR = " "


def generate_dice_face_diagram(dice_values):
    dice_faces = []
    for value in dice_values:
        dice_faces.append(DICE_ART[value])

    # Generate list containing dice face rows
    dice_face_rows = []
    for rows_idx in range(DIE_HEIGHT):
        row_component = []
        for die in dice_faces:
            row_component.append(die[rows_idx])
        row_string = DIE_FACE_SEPARATOR.join(row_component)
        dice_face_rows.append(row_string)

    # Header with "RESULTS" in center
    width = len(dice_face_rows[0])
    header = "RESULT".center(width, "~")
    dice_face_diagram = "\n".join([header] + dice_face_rows)
    return dice_face_diagram


def parse_input(user_input):
    """
    Check and Return input string as an integer btw 1-6
    """
    if user_input.strip() in {"1", "2", "3", "4", "5", "6"}:
        return int(user_input)
    else:
        print("Please only input from 1 to 6")
        return SystemExit(1)


def roll_dice(num_dice):
    """Return a list of integers with length `num_dice`.
    Each integer in the returned list is a random number between
    1 and 6, inclusive
    """
    roll_result = []
    for _ in range(num_dice):
        rolls = random.randint(1, 6)
        roll_result.append(rolls)
    return roll_result


# GET AND VALIDATE USER INPUT
dice_num_input = input("How many dices you want to roll? [1-6] ")
num_dice = parse_input(dice_num_input)
# ROLL DICE
roll_results = roll_dice(num_dice)
dice_face_diagram = generate_dice_face_diagram(roll_results)
print(f"\n{dice_face_diagram}")
