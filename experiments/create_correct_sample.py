import csv
import json

# Paths to your input files
csv_path = "../resources/ground_truth_100.csv"
json_path = "../resources/sample_150.json"
output_json_path = "../resources/sample_100.json"

# Read codes from CSV
codes_set = set()

with open(csv_path, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        codes_set.add(row["Código"])

print(f"Total codes read from CSV: {len(codes_set)}")

# Read JSON data
with open(json_path, encoding="utf-8") as jsonfile:
    json_data = json.load(jsonfile)

# Filter JSON based on codes from CSV
filtered_data = [item for item in json_data if item["codigo"] in codes_set]

print(f"Total items matched from JSON: {len(filtered_data)}")

# Save filtered data to new JSON file
with open(output_json_path, "w", encoding="utf-8") as outfile:
    json.dump(filtered_data, outfile, ensure_ascii=False, indent=4)

print(f"Filtered JSON saved to {output_json_path}")
