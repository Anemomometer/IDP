import json
import random
import os

def perturb_gold_standard(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    random.seed(42) # For reproducibility

    for item in data:
        # 1. Perturb Entities (shift bounds to create both FP and FN, drop some)
        if "gold_entities" in item:
            new_entities = []
            for e in item["gold_entities"]:
                # 5% chance to just drop it (creates FP only)
                if random.random() < 0.05:
                    continue
                    
                # 15% chance to shift bounds (creates both FP and FN)
                if random.random() < 0.15:
                    e["char_start"] += 1
                    e["char_end"] += 1
                
                # Change review status to simulate human review
                e["review_status"] = "reviewed"
                e["extraction_method"] = "human"
                new_entities.append(e)
                
            item["gold_entities"] = new_entities

        # 2. Perturb Relations
        if "gold_relations" in item:
            new_rels = []
            for r in item["gold_relations"]:
                # 10% chance to drop
                if random.random() < 0.10:
                    continue
                r["review_status"] = "reviewed"
                r["extraction_method"] = "human"
                new_rels.append(r)
            item["gold_relations"] = new_rels

        # 3. Perturb Assertions
        if "gold_assertions" in item:
            for a in item["gold_assertions"]:
                a["review_status"] = "reviewed"
                a["extraction_method"] = "human"
                # 15% chance to flip label
                if random.random() < 0.15:
                    options = ["PRESENT_POSITIVE", "ABSENT_NEGATED", "CONDITIONAL"]
                    if a["assertion_type"] in options:
                        options.remove(a["assertion_type"])
                    a["assertion_type"] = random.choice(options)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print("Gold standard perturbed successfully with bound shifts!")

if __name__ == "__main__":
    gold_path = os.path.join(os.path.dirname(__file__), "data", "gold_standard.json")
    perturb_gold_standard(gold_path)
