import json
import pandas as pd
from tabulate import tabulate 

"""
program that runs a menu to help test the backend of the database/hierachy
"""


# Load 
with open("discoveries_with_friendly_topics.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

topics = sorted(df["topic_label"].unique())
topics = [t for t in topics if t != "Unclustered"]

# Extract top-level categories from the hierarchy
top_levels = sorted(set(cat[0] for cat in df["topic_hierarchy"] if cat and cat[0] != "Uncategorized"))

def main_menu():
    while True:
        print("\n Explore Discoveries")
        print("----------------------------")
        print("1. Search by Topic")
        print("2. Search by Year")
        print("3. Search by Top-Level Category")
        print("4. Exit")
        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            choose_topic()
        elif choice == "2":
            search_by_year()
        elif choice == "3":
            search_by_top_level()
        elif choice == "4":
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

def choose_topic():
    print("\n Available Topics:")
    for i, topic in enumerate(topics):
        print(f"{i + 1}. {topic}")

    selection = input("Enter the topic number you want to explore: ").strip()

    if not selection.isdigit():
        print("Please enter a valid number (e.g. 1, 2, 3...)")
        return

    selection = int(selection) - 1
    if 0 <= selection < len(topics):
        label = topics[selection]
        results = df[df["topic_label"] == label][["name", "year", "topic_hierarchy"]]
        print(f"\n Discoveries in '{label}':")
        print(tabulate(results, headers="keys", tablefmt="simple", showindex=False))

    else:
        print(f"Number out of range. Please choose between 1 and {len(topics)}.")

def search_by_year():
    year = input("Enter a year (e.g., 1950): ").strip()

    if not year.isdigit():
        print("That doesn't look like a valid year. Try entering something like 1925 or 2003.")
        return 

    results = df[df["year"] == year][["name", "topic_label", "topic_hierarchy"]]
    if results.empty:
        print(f" No discoveries found for year {year}. Tip: You can try another nearby year.")
    else:
        print(f"\n Discoveries from {year} :")
        print(tabulate(results, headers="keys", tablefmt="simple", showindex=False))


def search_by_top_level():
    print("\n Top-Level Categories:")
    for i, cat in enumerate(top_levels):
        print(f"{i + 1}. {cat}")

    selection = input("Enter the category number to explore: ").strip()

    if not selection.isdigit():
        print("Please enter a valid number.")
        return

    selection = int(selection) - 1
    if 0 <= selection < len(top_levels):
        top_category = top_levels[selection]
        results = df[df["topic_hierarchy"].apply(lambda x: x[0] == top_category)][["name", "year", "topic_label"]]
        print(f"\n Discoveries under '{top_category}':")
        print(tabulate(results, headers="keys", tablefmt="simple", showindex=False))
    else:
        print(f"Number out of range. Please choose between 1 and {len(top_levels)}.")

main_menu()
