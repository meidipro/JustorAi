import os
import subprocess
import time

files = [
    'code_of_civil_procedure_1908_sections.json',
    'contract_act_1872_sections.json',
    'NI_act_1881_sections.json',
    'ICT_Act_2006_Bangladesh.json',
    'hindu_law_inheritance_amendment_1929_sections.json',
    'hindu_married_womens_right_1946_sections.json',
    'pdr_1913_sections.json'
]

for file in files:
    print(f"Starting ingestion for {file}...")
    success = False
    retries = 3
    while not success and retries > 0:
        result = subprocess.run(['.venv_ragas\\Scripts\\python.exe', 'ingest_one.py', file])
        if result.returncode == 0:
            success = True
            print(f"Successfully finished {file}.")
        else:
            retries -= 1
            print(f"Failed to ingest {file}. Retrying ({retries} left) in 30s...")
            time.sleep(30)
            
    if not success:
        print(f"CRITICAL FAILURE: Could not ingest {file} after retries.")
