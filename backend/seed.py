from flaskr.mongo import get_db


def seed_tags():
    tag_names = [
        "Work",
        "Study",
        "Free Time",
        "Exercise",
        "Health",
        "Travel",
        "Hobbies",
        "Shopping",
        "Finances",
        "Family",
        "Chores",
        "Friends",
        "Meetings",
        "Goals",
        "Projects",
        "Learning",
        "Entertainment",
        "Relaxation",
        "Urgent",
        "Miscellaneous",
    ]

    db = get_db()
    inserted = 0
    for name in tag_names:
        # Idempotent: don't insert duplicates
        if db.tags.find_one({"name": name}):
            continue
        db.tags.insert_one({"name": name})
        inserted += 1

    print(f"Inserted {inserted} new tags")


if __name__ == "__main__":
    seed_tags()
