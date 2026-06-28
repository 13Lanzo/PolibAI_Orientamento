from pathlib import Path
import sys


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from kpi_data import COURSE_KPI  # noqa: E402


SUSPICIOUS_LEGACY_VALUES = {
    "100%",
    "Positivo",
    "Giudizi rilevati",
    "Dato parziale",
    "Punto di attenzione",
}

IIA_CARICO_PARAMETRO = "Il carico di studio dell'insegnamento è proporzionato ai crediti assegnati?"


def fail(errors):
    print("OPIS KPI check FAILED")
    for error in errors:
        print(f"- {error}")
    return 1


def main():
    errors = []
    courses_without_opis = []
    indicator_count = 0

    for course_id, data in COURSE_KPI.items():
        for item in data.get("recensioni", []) or []:
            value = str(item.get("valore", "")).strip()
            if value in SUSPICIOUS_LEGACY_VALUES:
                errors.append(f"{course_id}: legacy recensioni contiene valore sospetto {value!r}")

        opis = data.get("opis") or {}
        indicatori = opis.get("indicatori") or []
        numeric_indicatori = [
            item for item in indicatori
            if item.get("giudizi_positivi") is not None or item.get("giudizi_negativi") is not None
        ]
        indicator_count += len(numeric_indicatori)
        if not numeric_indicatori:
            courses_without_opis.append(course_id)

        for item in numeric_indicatori:
            for key in ("giudizi_positivi", "giudizi_negativi"):
                value = item.get(key)
                if value is not None and not isinstance(value, (int, float)):
                    errors.append(f"{course_id}: {key} non numerico per {item.get('parametro')!r}")

    iia_opis = COURSE_KPI["IIA"]["opis"]["indicatori"]
    iia_carico = next((item for item in iia_opis if item["parametro"] == IIA_CARICO_PARAMETRO), None)
    if not iia_carico:
        errors.append("IIA: indicatore carico di studio mancante")
    else:
        if iia_carico.get("giudizi_positivi") != 79.92:
            errors.append(f"IIA: carico giudizi_positivi atteso 79.92, trovato {iia_carico.get('giudizi_positivi')}")
        if iia_carico.get("giudizi_negativi") != 20.08:
            errors.append(f"IIA: carico giudizi_negativi atteso 20.08, trovato {iia_carico.get('giudizi_negativi')}")
        if iia_carico.get("giudizi_positivi") == 100 or iia_carico.get("giudizi_negativi") == 100:
            errors.append("IIA: carico di studio è tornato a 100")

    if errors:
        return fail(errors)

    print("OPIS KPI check OK")
    print(f"- Corsi controllati: {len(COURSE_KPI)}")
    print(f"- Indicatori OPIS numerici: {indicator_count}")
    if courses_without_opis:
        print(f"- Corsi senza OPIS numerico disponibile: {', '.join(courses_without_opis)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
