import json
import sys

# Force UTF-8 output
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def safe_print(s):
    try:
        print(s)
    except UnicodeEncodeError:
        print(s.encode('ascii', 'replace').decode('ascii'))

try:
    with open('e:/Acollage/projectco/heart_disease_model.ipynb', 'r', encoding='utf-8') as f:
        nb = json.load(f)

    print(f"Total cells: {len(nb.get('cells', []))}")
        if cell.get('cell_type') == 'code' and 'source' in cell:
            for line in cell['source']:
                if 'import ' in line or 'from ' in line:
                    safe_print(f"IMPORT CHECK: {line.strip()}")
except Exception as e:
    safe_print(f"Error reading notebook: {e}")
