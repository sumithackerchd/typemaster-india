def get_achievements(best_wpm, accuracy, total_tests):

    achievements = []

    achievements.append({
        "title": "First Test",
        "icon": "🎉",
        "unlocked": total_tests >= 1
    })

    achievements.append({
        "title": "30 WPM Club",
        "icon": "🥉",
        "unlocked": best_wpm >= 30
    })

    achievements.append({
        "title": "50 WPM Club",
        "icon": "🥈",
        "unlocked": best_wpm >= 50
    })

    achievements.append({
        "title": "70 WPM Club",
        "icon": "🥇",
        "unlocked": best_wpm >= 70
    })

    achievements.append({
        "title": "100 WPM Legend",
        "icon": "💎",
        "unlocked": best_wpm >= 100
    })

    achievements.append({
        "title": "Accuracy Master",
        "icon": "🎯",
        "unlocked": accuracy >= 98
    })

    return achievements