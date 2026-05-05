import json

recensioni_map = {
    'IIA': [{'parametro': 'Il carico di studio dell\'insegnamento è proporzionato ai crediti assegnati?', 'valore': '79.92%'}, {'parametro': 'Le modalità di esame sono state definite in modo chiaro?', 'valore': '83.46%'}],
    'ICD': [{'parametro': 'Il carico di studio dell\'insegnamento è proporzionato ai crediti assegnati?', 'valore': '100%'}, {'parametro': 'Le modalità di esame sono state definite in modo chiaro?', 'valore': '80%'}],
    'IEDILE': [{'parametro': 'I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all\'apprendimento della materia?', 'valore': '80.42%'}, {'parametro': 'L\'insegnamento è stato svolto in maniera coerente con quanto dichiarato sul sito Web?', 'valore': '35.25%'}],
    'IELE': [{'parametro': 'Il docente è reperibile per chiarimenti e spiegazioni?', 'valore': 'Positivo'}],
    'IETI': [{'parametro': 'Le modalità di esame sono state definite in modo chiaro?', 'valore': 'Positivo'}, {'parametro': 'È interessato/a agli argomenti trattati nell\'insegnamento?', 'valore': '82.16%'}],
    'IGEST': [{'parametro': 'I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all\'apprendimento della materia?', 'valore': '84.25%'}, {'parametro': 'Il materiale didattico (indicato e disponibile) è adeguato per lo studio della materia?', 'valore': '79.21%'}],
    'INAVAL': [{'parametro': 'I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all\'apprendimento della materia?', 'valore': '100%'}, {'parametro': 'Gli orari di svolgimento di lezioni, esercitazioni e altre eventuali attività sono rispettati?', 'valore': '93.69%'}],
    'ICIVAMB': [{'parametro': 'Il docente è reperibile per chiarimenti e spiegazioni?', 'valore': '87.04%'}, {'parametro': 'Le modalità di esame sono state definite in modo chiaro?', 'valore': '77.97%'}],
    'IAERO': [{'parametro': 'Le modalità di esame sono state definite in modo chiaro?', 'valore': 'Positivo'}, {'parametro': 'Gli orari di svolgimento di lezioni, esercitazioni e altre eventuali attività sono rispettati?', 'valore': 'Positivo'}],
    'LDES': [{'parametro': 'La modalità di erogazione a distanza consente di seguire le attività integrative in maniera appropriata ed efficace?', 'valore': '83.33%'}, {'parametro': 'I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all\'apprendimento della materia?', 'valore': '85.71%'}],
    'LPOL': [{'parametro': 'Il carico di studio dell\'insegnamento è proporzionato ai crediti assegnati?', 'valore': 'Positivo'}, {'parametro': 'Le modalità di esame sono state definite in modo chiaro?', 'valore': 'Positivo'}],
    'IMEC': [{'parametro': 'Ritiene che contenuti e metodi didattici del corso utilizzati dal docente siano adeguati alla modalità di erogazione della didattica a distanza?', 'valore': '85.98%'}, {'parametro': 'Si ritiene complessivamente soddisfatto dell\'organizzazione del servizio di erogazione on-line della didattica?', 'valore': '86.12%'}],
    'IMED': [{'parametro': 'È interessato/a agli argomenti trattati nell\'insegnamento?', 'valore': '87.27%'}, {'parametro': 'Le conoscenze preliminari possedute sono risultate sufficienti per la comprensione degli argomenti previsti nel programma d\'esame?', 'valore': '85.37%'}]
}

def update_kpi_data():
    file_path = r"c:\Users\Lanzo\OneDrive\Desktop\progetto_sw\backend\kpi_data.py"
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    out_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        out_lines.append(line)
        
        # Check if we hit a course key block
        for course_id, recensioni in recensioni_map.items():
            if f'"{course_id}": {{' in line:
                # Now read lines until we find "note":
                j = i + 1
                while j < len(lines):
                    sub_line = lines[j]
                    if '"note":' in sub_line:
                        # Found it! Insert recensioni before note
                        rec_str = json.dumps(recensioni, ensure_ascii=False)
                        out_lines.append(f'        "recensioni": {rec_str},\n')
                        break
                    out_lines.append(sub_line)
                    j += 1
                i = j - 1
                break
        i += 1

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(out_lines)
    print("Done")

if __name__ == "__main__":
    update_kpi_data()
