def calculate_accuracy(correct, total):

    if total == 0:
        return 0

    return round((correct / total) * 100, 2)


def calculate_wpm(total_characters, minutes):

    if minutes == 0:
        return 0

    words = total_characters / 5

    return round(words / minutes, 2)