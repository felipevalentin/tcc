import json

from openpyxl import Workbook

# Define the header columns for the Excel file
headers = [
    "Código",
    "Título",
    "NrProLicitatório",
    "DataHoraDOM",
    "cod_registro_info_sfinge",
    "Município",
    "Entidade",
    "CategoriaDOM",
    "Modalidade",
    "Formato",
    "NrModalidade",
    "Objeto",
    "Justificativa",
    "Data Abertura Normalizada",
    "Informacoes",
    "Signatário",
    "Cargo do Signatário",
]

# Create a new workbook and select the active worksheet
wb = Workbook()
ws = wb.active
ws.title = "Dados"

# Append the header row
ws.append(headers)

# Load the JSON data from a file named 'data.json'
with open(
    "/resources/sample_150.json",
    "r",
    encoding="utf-8",
) as f:
    data = json.load(f)

# Loop through each JSON item and append a row to the Excel sheet
for item in data:
    row = [
        item.get("codigo", ""),  # Código
        item.get("titulo", ""),  # Título
        "",  # NrProLicitatório (empty)
        item.get("data", ""),  # DataHoraDOM
        item.get("cod_registro_info_sfinge", ""),  # cod_registro_info_sfinge
        item.get("municipio", ""),  # Município
        item.get("entidade", ""),  # Entidade
        item.get("categoria", ""),  # CategoriaDOM
        "",  # Modalidade
        "",  # Formato
        "",  # NrModalidade
        "",  # Objeto
        "",  # Justificativa
        "",  # Data Abertura Normalizada
        "",  # Informacoes
        "",  # Signatário
        "",  # Cargo do Signatário
    ]
    ws.append(row)

# Save the workbook to an Excel file on your computer
wb.save("output.xlsx")
print("Excel file 'output.xlsx' has been created successfully!")
