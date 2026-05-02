"""
PDF Intervention Report Parser – Sogetrel Belgium

Purpose:
- Extract unstructured data from technician-generated PDF reports
- Normalize intervention data (dates, times, status, tests, equipment)
- Output clean datasets for operational analytics and Power BI

Input:
- Folder of PDF files named InterventionReport_*.pdf

Output:
- CSV and Excel files ready for BI consumption

Author: (Youssef JAHAZ)
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import sys
from datetime import datetime
import pandas as pd
import fitz  # PyMuPDF

# ============== PARAMÈTRES ==============
DIR_INPUT = "rest"
RECURSIVE = True
PATTERN_PREFIX = "InterventionReport_"
CSV_NAME = "interventions_parsed.csv"
XLSX_NAME = "interventions_parsed.xlsx"
# =======================================

def find_first(patterns, text, flags=re.IGNORECASE):
    """Retourne la 1re capture regex trouvée parmi une liste de motifs."""
    if isinstance(patterns, str):
        patterns = [patterns]
    for pat in patterns:
        m = re.search(pat, text, flags)
        if m:
            g = m.groups()
            return g[-1].strip() if g else m.group(0).strip()
    return None

def extract_field_advanced(text, field_names, max_lines_after=3):
    """
    Extrait un champ en cherchant parmi plusieurs noms possibles
    et en regardant les lignes suivantes si nécessaire.
    """
    if isinstance(field_names, str):
        field_names = [field_names]

    lines = text.split('\n')

    for i, line in enumerate(lines):
        for field_name in field_names:
            if re.search(field_name, line, re.IGNORECASE):
                # Essayer d'extraire de la même ligne d'abord
                same_line_pattern = field_name + r"\s*[:]?\s*([^\n]+)"
                m = re.search(same_line_pattern, line, re.IGNORECASE)
                if m:
                    value = m.group(1).strip()
                    if value:  # Ne pas retourner si vide
                        return value

                # Regarder 
                for j in range(i+1, min(i+max_lines_after+1, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and not re.search(r'^\s*$', next_line):
                        # Vérifier que ce n'est pas un autre label
                        if not re.search(r'[a-zA-Z]+\s*:', next_line) and not re.search(r'\b(?:Statut|Numéro|Nom|Adresse|Email|Date|Heure|Type|Service|Raison|Installateur)\b', next_line, re.IGNORECASE):
                            return next_line.strip()
    return None

def find_materials(text):
    """Détecte des mots-clés matériels (normalisés) présents dans le texte."""
    keywords = [
        r"livebox", r"modem", r"d[ée]codeur", r"coupleur", r"rg11", r"moca", r"cpl",
        r"airbox", r"wifi comfort", r"veex", r"cx310", r"webtv", r"tv", r"internet"
    ]
    found = set()
    for kw in keywords:
        if re.search(kw, text, re.IGNORECASE):
            label = kw.replace("d[ée]codeur", "decodeur").upper()
            if label == 'CX310':
                found.add('VEEX CX310')
            elif label == 'TV' and re.search(r"webtv", text, re.IGNORECASE):
                found.add('WEBTV')
            else:
                found.add(label)
    return sorted(found)

def find_metric_near(text, label_regex):
    """Récupère un nombre proche d'un libellé (Descendant Mbps, Ping ms...)."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.search(label_regex, line, re.IGNORECASE):
            m = re.search(r"([0-9]+(?:[.,][0-9]+)?)", line)
            if m:
                return m.group(1).replace(',', '.')
            for j in range(max(0, i - 2), i):
                m2 = re.search(r"([0-9]+(?:[.,][0-9]+)?)", lines[j])
                if m2:
                    return m2.group(1).replace(',', '.')
    return None

DT_FORMATS = ["%d/%m/%Y %H:%M", "%d-%m-%Y %H:%M", "%Y/%m/%d %H:%M"]

def parse_dt(s):
    if not s:
        return None
    for fmt in DT_FORMATS:
        try:
            return datetime.strptime(s.strip(), fmt)
        except Exception:
            continue
    return None

def extract_datetime_field(text, field_names, reference_date=None):
    """
    Extrait un champ datetime avec gestion robuste.
    Si seule l'heure est trouvée et qu'une date de référence est fournie, complète avec la date.
    """
    value = extract_field_advanced(text, field_names, 2)

    if value:
        # Si on a déjà une date complète, la retourner
        if re.search(r'\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\s+\d{1,2}:\d{2}', value):
            return value

        # Si on a seulement l'heure, essayer de compléter avec la date de référence
        time_match = re.search(r'(\d{1,2}:\d{2})', value)
        if time_match and reference_date:
            return f"{reference_date} {time_match.group(1)}"

    return value

def extract_from_pdf(path):
    """Ouvre un PDF et extrait les champs structurés pour Power BI."""
    doc = fitz.open(path)
    full_text = "\n".join([page.get_text("text") for page in doc])

    # Champs principaux 
    statut = find_first([r"Statut\s+de\s+l[’']?intervention:\s*([\w\-\sÀ-ÿ]+)"], full_text)
    if not statut:
        statut = extract_field_advanced(full_text, [r"Statut\s+de\s+l[’']?intervention"])

    num_client = find_first([r"Num[é|e]ro\s+de\s+client\s*([0-9\.]+)",
                             r"Client\s*N[°o]\s*:?\s*([0-9\.]+)"], full_text)
    if not num_client:
        num_client = extract_field_advanced(full_text, [r"Num[ée]ro\s+de\s+client", r"Client\s*N[°o]"])

    nom_client = find_first([r"Nom\s*\n?\s*([A-Za-zÀ-ÿ'\-\s]+)\n?Adresse",
                             r"Client\s*-\s*Nom:\s*([A-Za-zÀ-ÿ'\-\s]+)"], full_text)
    if not nom_client:
        nom_client = extract_field_advanced(full_text, [r"^Nom", r"Client\s*-\s*Nom"])

    adresse = find_first([r"Adresse\s*\n?\s*([A-Za-z0-9À-ÿ'\-\s\(\)]+)\n?Email"], full_text)
    if not adresse:
        adresse = extract_field_advanced(full_text, [r"Adresse"])

    email = find_first([r"Email\s*\n?\s*([\w\.-]+@[\w\.-]+)"], full_text)
    if not email:
        email = extract_field_advanced(full_text, [r"Email"])

    # Extraction robuste de la date d'intervention avec créneau
    date_interv = None
    slot_start = None
    slot_end = None

    # Méthode 1: 
    mslot = re.search(
        r"Date\s*d['']?intervention\s*([0-9/\-]{8,10})\s*\[\s*([0-9]{2}:[0-9]{2})\s*-\s*([0-9]{2}:[0-9]{2})\s*\]",
        full_text, re.IGNORECASE
    )

    if mslot:
        date_interv = mslot.group(1)
        slot_start = mslot.group(2)
        slot_end = mslot.group(3)
    else:
        # Méthode 2: 
        date_interv = extract_field_advanced(full_text, [r"Date\s*d['']?intervention"], 3)

        # Chercher le créneau horaire près de la date
        if date_interv:
            # Trouver la ligne avec la date
            lines = full_text.split('\n')
            for i, line in enumerate(lines):
                if re.search(r"Date\s*d['']?intervention", line, re.IGNORECASE) or (date_interv and date_interv in line):
                    # Chercher le créneau dans les 3 lignes suivantes
                    for j in range(i, min(i+4, len(lines))):
                        slot_match = re.search(r"\[\s*([0-9]{2}:[0-9]{2})\s*-\s*([0-9]{2}:[0-9]{2})\s*\]", lines[j])
                        if slot_match:
                            slot_start = slot_match.group(1)
                            slot_end = slot_match.group(2)
                            break
                    break

    # Extraction ROBUSTE des heures d'arrivée et de départ
    heure_arrivee = None
    heure_depart = None

    # Méthode 1: Pattern traditionnel (votre méthode originale)
    heure_arrivee_match = find_first([r"Heure d'arriv[ée]e\s*\n?\s*([0-9/\-]{8,10}\s+[0-9]{2}:[0-9]{2})"], full_text)
    if heure_arrivee_match:
        heure_arrivee = heure_arrivee_match
    else:
        # Méthode 2: Approche robuste avec extraction avancée
        heure_arrivee = extract_datetime_field(full_text, [r"Heure\s*d['']?arriv[ée]e"], date_interv)

        # Méthode 3: Recherche de pattern alternatif
        if not heure_arrivee:
            arrivee_alt = re.search(r"Arriv[ée]e?\s*:?\s*([0-9/\-]{8,10}\s+[0-9]{1,2}:[0-9]{2})", full_text, re.IGNORECASE)
            if arrivee_alt:
                heure_arrivee = arrivee_alt.group(1)

    # Même approche pour l'heure de départ
    heure_depart_match = find_first([r"Heure de d[ée]part\s*\n?\s*([0-9/\-]{8,10}\s+[0-9]{2}:[0-9]{2})"], full_text)
    if heure_depart_match:
        heure_depart = heure_depart_match
    else:
        heure_depart = extract_datetime_field(full_text, [r"Heure\s*de\s*d[ée]part"], date_interv)

        if not heure_depart:
            depart_alt = re.search(r"D[ée]part?\s*:?\s*([0-9/\-]{8,10}\s+[0-9]{1,2}:[0-9]{2})", full_text, re.IGNORECASE)
            if depart_alt:
                heure_depart = depart_alt.group(1)

    # Calcul du temps passé
    dt_arr = parse_dt(heure_arrivee) if heure_arrivee else None
    dt_dep = parse_dt(heure_depart) if heure_depart else None
    temps_passe_min = int((dt_dep - dt_arr).total_seconds() // 60) if (dt_arr and dt_dep) else None

    # Autres champs
    type_interv = find_first([r"Type d'intervention:\s*([A-Za-zÀ-ÿ \-]+)"], full_text)
    if not type_interv:
        type_interv = extract_field_advanced(full_text, [r"Type\s*d['']?intervention"])

    services = find_first([
        r"Service\(s\) Demand[ée] \(s\):\s*([A-Za-zÀ-ÿ \+]+)",
        r"Service\(s\) Demand[ée]s:\s*([A-Za-zÀ-ÿ \+]+)",
        r"Service\(s\) Demand[é|e]\(s\):\s*([A-Za-zÀ-ÿ \+]+)"
    ], full_text)
    if not services:
        services = extract_field_advanced(full_text, [r"Service\(s\)\s*Demand[ée]s?"])

    # Matériel / équipements
    equipements = []
    eq_block_match = re.search(r"Equipment\s*\(s\)\s*:\s*([\s\S]{0,200})\n", full_text, re.IGNORECASE)
    if eq_block_match:
        eq_block = eq_block_match.group(1)
        for line in re.split(r"[\n\u2022\-]", eq_block):
            t = line.strip(" :•-\n\t")
            if t:
                equipements.append(t)

    for m in find_materials(full_text):
        if m not in equipements:
            equipements.append(m)
    equipements_str = "; ".join(sorted(set(equipements)))

    # Commentaires et raison d'annulation
    commentaires_match = re.search(
        r"Remarques du client et\/ou de l'installateur:\s*([\s\S]{0,600}?)(?:\nP:|\nJ'autorise|\nClient|\nPhotos|$)",
        full_text, re.IGNORECASE
    )
    commentaires = re.sub(r"\s+", " ", commentaires_match.group(1)).strip() if commentaires_match else ''

    raison_annulation = find_first([r"Raison d'annulation:\s*([\s\S]{0,120}?)\n"], full_text)
    if not raison_annulation:
        raison_annulation = extract_field_advanced(full_text, [r"Raison\s*d['']?annulation"])

    # Technicien
    technicien = find_first([r"Installateur\s*-\s*Nom:\s*([A-Za-zÀ-ÿ'\-\s]+)"], full_text)
    if not technicien:
        technicien = extract_field_advanced(full_text, [r"Installateur\s*-\s*Nom"])

    # WiFi
    wifi_ssid = find_first([r"Nom du r[ée]seau WIFI:\s*([A-Za-z0-9_\-]+)"], full_text)
    if not wifi_ssid:
        wifi_ssid = extract_field_advanced(full_text, [r"Nom\s*du\s*r[ée]seau\s*WIFI"])

    wifi_pwd = find_first([r"Mot de passe WIFI:\s*([A-Za-z0-9]+)"], full_text)
    if not wifi_pwd:
        wifi_pwd = extract_field_advanced(full_text, [r"Mot\s*de\s*passe\s*WIFI"])

    # Speedtest
    down_mbps = find_metric_near(full_text, r"Descendant\s*Mbps")
    up_mbps = find_metric_near(full_text, r"Ascendant\s*Mbps")
    ping_ms = find_metric_near(full_text, r"Ping\s*ms")
    jitter_ms = find_metric_near(full_text, r"Gigue\s*ms")

    # Drapeaux
    test_ok = bool(re.search(r"\bTEST\s*OK\b|SIGNAL\s*OK|MODEM\s*OK|NOTCH\s*OK", full_text, re.IGNORECASE))
    client_absent = bool(re.search(r"client\s*absent", full_text, re.IGNORECASE))

    # Références
    base = os.path.basename(path)
    rid_match = re.search(r"InterventionReport_(.*?)\.pdf$", base, re.IGNORECASE)
    report_id = rid_match.group(1) if rid_match else base

    return {
        'ReportFile': base,
        'ReportID': report_id,
        'StatutIntervention': statut.strip() if statut else '',
        'NumeroClient': num_client if num_client else '',
        'NomClient': nom_client.strip() if nom_client else '',
        'Adresse': adresse.strip() if adresse else '',
        'Email': email if email else '',
        'DateIntervention': date_interv if date_interv else '',
        'TimeSlotStart': slot_start if slot_start else '',
        'TimeSlotEnd': slot_end if slot_end else '',
        'HeureArrivee': heure_arrivee if heure_arrivee else '',
        'HeureDepart': heure_depart if heure_depart else '',
        'TempsPasseMinutes': temps_passe_min,
        'TypeIntervention': type_interv.strip() if type_interv else '',
        'ServicesDemandes': services.strip() if services else '',
        'Equipements': equipements_str,
        'Commentaires': commentaires,
        'RaisonAnnulation': raison_annulation if raison_annulation else '',
        'Technicien': technicien.strip() if technicien else '',
        'WiFi_SSID': wifi_ssid if wifi_ssid else '',
        'WiFi_Password': wifi_pwd if wifi_pwd else '',
        'Test_Down_Mbps': float(down_mbps) if down_mbps else None,
        'Test_Up_Mbps': float(up_mbps) if up_mbps else None,
        'Test_Ping_ms': float(ping_ms) if ping_ms else None,
        'Test_Jitter_ms': float(jitter_ms) if jitter_ms else None,
        'Test_OK_Flag': test_ok,
        'ClientAbsent_Flag': client_absent,
        'FullPath': path
    }

def collect_pdf_files(root_dir, recursive=True, prefix="InterventionReport_"):
    pdfs = []
    if recursive:
        for r, _, files in os.walk(root_dir):
            for f in files:
                if f.lower().endswith(".pdf") and f.startswith(prefix):
                    pdfs.append(os.path.join(r, f))
    else:
        for f in os.listdir(root_dir):
            if f.lower().endswith(".pdf") and f.startswith(prefix):
                pdfs.append(os.path.join(root_dir, f))
    return sorted(pdfs)

def main():
    if not os.path.isdir(DIR_INPUT):
        print(f"❌ Dossier introuvable : {DIR_INPUT}")
        sys.exit(1)

    pdf_files = collect_pdf_files(DIR_INPUT, RECURSIVE, PATTERN_PREFIX)
    if not pdf_files:
        print(f"⚠️ Aucun PDF '{PATTERN_PREFIX}*.pdf' trouvé dans {DIR_INPUT}")
        sys.exit(0)

    records = []
    for pdf in pdf_files:
        try:
            records.append(extract_from_pdf(pdf))
        except Exception as e:
            print(f"❌ Erreur avec {pdf}: {str(e)}")
            rec = {'ReportFile': os.path.basename(pdf), 'FullPath': pdf, 'Error': str(e)}
            for k in ['ReportID','StatutIntervention','NumeroClient','NomClient','Adresse','Email',
                      'DateIntervention','TimeSlotStart','TimeSlotEnd','HeureArrivee','HeureDepart',
                      'TempsPasseMinutes','TypeIntervention','ServicesDemandes','Equipements',
                      'Commentaires','RaisonAnnulation','Technicien','WiFi_SSID','WiFi_Password',
                      'Test_Down_Mbps','Test_Up_Mbps','Test_Ping_ms','Test_Jitter_ms',
                      'Test_OK_Flag','ClientAbsent_Flag']:
                rec.setdefault(k, None)
            records.append(rec)

    df = pd.DataFrame(records)
    for col in ['DateIntervention', 'ReportFile']:
        if col not in df.columns:
            df[col] = None
    df.sort_values(by=['DateIntervention', 'ReportFile'], inplace=True, na_position='last')

    out_csv = os.path.join(DIR_INPUT, CSV_NAME)
    out_xlsx = os.path.join(DIR_INPUT, XLSX_NAME)
    df.to_csv(out_csv, index=False)
    df.to_excel(out_xlsx, index=False, engine='openpyxl')

    print(f"✅ {len(df)} rapports traités")
    print(f"→ CSV :  {out_csv}")
    print(f"→ Excel: {out_xlsx}")

    # Afficher 
    print("\n📊 Échantillon des données extraites:")
    print(df[['ReportFile', 'DateIntervention', 'HeureArrivee', 'HeureDepart', 'TempsPasseMinutes']].head(10))

if __name__ == '__main__':
    main()
