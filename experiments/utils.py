import pathlib
import json
import csv
from slugify import slugify


def get_sample():
    sample_path = pathlib.Path("../resources/sample.json")
    with sample_path.open() as sample_file:
        reader = json.load(sample_file)
        sample = {}
        for entry in reader:
            entry_id = entry.pop("codigo")  # Remove "ID" and use it as the key
            sample[entry_id] = entry
    return sample


def get_ground_truth():
    ground_truth_path = pathlib.Path("../resources/ground_truth.csv")
    ground_truth = {}
    with ground_truth_path.open() as ground_truth_file:
        reader = csv.DictReader(ground_truth_file)
        fieldnames = []
        for header in reader.fieldnames:
            header = slugify(header, separator="_")
            if header == "datahoradom":
                header = "data"
            if header == "categoriadom":
                header = "categoria"
            fieldnames.append(header)
        reader.fieldnames = fieldnames
        for row in reader:
            row = {key: (value if value != "NULL" else None) for key, value in row.items()}
            row_id = row.pop("codigo")  # remove 'ID' and use it as a key
            ground_truth[row_id] = row
    return ground_truth


def calculate_null_of_consistent_values(sample, ground_truth):
    dom_values = [
        "titulo",
        "data",
        "cod_registro_info_sfinge",
        "municipio",
        "entidade",
        "categoria",
    ]
    cod_registro_info_sfinge_null_amount = 0
    cod_municipio_null_amount = 0
    for codigo in sample:
        if ground_truth[codigo]["cod_registro_info_sfinge"] is None:
            cod_registro_info_sfinge_null_amount += 1
        if ground_truth[codigo]["municipio"] is None:
            cod_municipio_null_amount += 1
