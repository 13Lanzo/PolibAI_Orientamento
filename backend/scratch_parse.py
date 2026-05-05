import os
import re

def extract_positives(filepath):
    positives = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Giudizi Positivi:' in line or 'Giudizi Positivi rilevati' in line:
                # E.g.: |  | Il materiale didattico... | Giudizi Positivi: **80.42%** |
                parts = line.split('|')
                if len(parts) >= 4:
                    param = parts[2].strip()
                    val_str = parts[3].strip()
                    
                    match = re.search(r'Giudizi Positivi:\s*\*\*([0-9.]+%)\*\*', val_str)
                    if match:
                        positives.append({"parametro": param, "valore": match.group(1)})
                    elif 'rilevati' in val_str.lower():
                        positives.append({"parametro": param, "valore": "Positivo"})
    
    # Ordina i positivi (se ci sono % sort by that)
    def parse_pct(v):
        try:
            return float(v.replace('%', ''))
        except:
            return 0
    
    positives.sort(key=lambda x: parse_pct(x['valore']) if '%' in x['valore'] else 0, reverse=True)
    return positives[:3] # Top 3

def main():
    base_dir = r"c:\Users\Lanzo\OneDrive\Desktop\progetto_sw\backend\knowledge\Recensioni Studenti"
    tri_dir = os.path.join(base_dir, "triennale")
    mag_dir = os.path.join(base_dir, "magistrale")
    
    results = {}
    
    for d in [tri_dir, mag_dir]:
        if not os.path.exists(d): continue
        for fname in os.listdir(d):
            if fname.endswith(".md"):
                course_name = fname.replace("Rapporto OPIS 2024 - ", "").replace("Rapporto OPIS 2022 - ", "").replace("Rapporto OPIS 2023 - ", "").replace(".md", "")
                results[course_name] = extract_positives(os.path.join(d, fname))
                
    import pprint
    pprint.pprint(results)

if __name__ == "__main__":
    main()
