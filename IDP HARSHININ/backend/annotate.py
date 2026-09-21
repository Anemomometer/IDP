import json
import os
import sys


# -----------------------------------------
# INPUT / OUTPUT FILES
# -----------------------------------------

if len(sys.argv) > 1:
    input_file = sys.argv[1]
else:
    input_file = "data/abstracts.json"

if len(sys.argv) > 2:
    output_file = sys.argv[2]
else:
    output_file = "data/annotated_data.json"


# -----------------------------------------
# LOAD DATA
# -----------------------------------------

with open(input_file, "r", encoding="utf-8") as file:
    abstracts = json.load(file)

print(f"\nLoaded {len(abstracts)} abstracts.")
print(f"Input file: {input_file}")
print(f"Output file: {output_file}")


# -----------------------------------------
# LABELS
# -----------------------------------------

labels = [
    "DISEASE",
    "DRUG",
    "SAMPLE_SIZE",
    "ENDPOINT"
]


# -----------------------------------------
# ANNOTATION
# -----------------------------------------

annotated_data = []

for index, abstract in enumerate(abstracts):

    text = abstract["text"]

    print("\n" + "=" * 70)
    print(f"ABSTRACT {index + 1}/{len(abstracts)}")
    print("=" * 70)

    print("\nPMID:", abstract.get("pmid", "Unknown"))

    print("\nTEXT:")
    print(text)

    entities = []

    for label in labels:

        print("\n" + "-" * 50)
        print(f"Find entities for: {label}")
        print("-" * 50)

        while True:

            entity_text = input(
                f"Enter {label} (press Enter to finish): "
            ).strip()

            if entity_text == "":
                break

            # Find all occurrences
            positions = []
            start = 0

            while True:

                position = text.lower().find(
                    entity_text.lower(),
                    start
                )

                if position == -1:
                    break

                positions.append(position)
                start = position + 1

            if not positions:
                print("❌ Entity not found in text.")
                print("Please enter the text exactly as it appears.")
                continue

            # If multiple occurrences exist
            if len(positions) > 1:

                print("\nMultiple occurrences found:")

                for i, position in enumerate(positions):
                    print(
                        f"{i + 1}. "
                        f"{text[position:position + len(entity_text)]}"
                        f" (position {position})"
                    )

                choice = input(
                    "Choose occurrence number: "
                ).strip()

                try:
                    choice = int(choice)

                    if choice < 1 or choice > len(positions):
                        print("Invalid choice.")
                        continue

                    start_pos = positions[choice - 1]

                except ValueError:
                    print("Please enter a valid number.")
                    continue

            else:
                start_pos = positions[0]

            end_pos = start_pos + len(entity_text)

            entities.append({
                "text": text[start_pos:end_pos],
                "label": label,
                "start": start_pos,
                "end": end_pos
            })

            print(
                f"✅ Added: "
                f"{text[start_pos:end_pos]} → {label}"
            )

    annotated_data.append({
        "pmid": abstract.get("pmid", ""),
        "text": text,
        "entities": entities
    })


# -----------------------------------------
# SAVE
# -----------------------------------------

os.makedirs(
    os.path.dirname(output_file) or ".",
    exist_ok=True
)

with open(
    output_file,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        annotated_data,
        file,
        indent=2,
        ensure_ascii=False
    )


print("\n" + "=" * 70)
print("ANNOTATION COMPLETED!")
print("=" * 70)

print(f"\nSaved annotated data to:")
print(output_file)