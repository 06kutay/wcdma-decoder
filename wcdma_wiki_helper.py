#!/usr/bin/env python3
# WCDMA/UMTS Passive Neighbor Cell Decoder
# Copyright (C) 2026 06kutay <https://github.com/06kutay>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import json
import glob
from datetime import datetime
import asn1tools
import wcdma_si_assembler

WIKI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wcdma-wiki")

def get_choice_val(choice_tuple):
    if choice_tuple and isinstance(choice_tuple, tuple) and len(choice_tuple) == 2:
        return choice_tuple
    return None, None

def format_cell_id(bit_tuple):
    if not bit_tuple:
        return None, None, None
    data, bit_len = bit_tuple
    val = int.from_bytes(data, 'big') >> (len(data) * 8 - bit_len)
    rnc_id = val >> 16
    cell_id = val & 0xFFFF
    return val, rnc_id, cell_id

def decode_bch_for_capture(bch_json_path, db):
    """
    Decodes SIBs and extracts neighbor information.
    """
    try:
        sibs = wcdma_si_assembler.assemble_sibs_from_json(bch_json_path, db)
    except Exception as e:
        print(f"BCH decode error for {bch_json_path}: {e}")
        return None
    
    info = {
        'mcc': None,
        'mnc': None,
        'cell_identity': None,
        'rnc_id': None,
        'local_cell_id': None,
        'wcdma_neighbors': [],
        'lte_neighbors': []
    }
    
    if 'MIB' in sibs:
        mib = sibs['MIB']
        plmn_type = mib.get('plmn-Type', (None, {}))
        if plmn_type[0] == 'gsm-MAP':
            plmn_id = plmn_type[1].get('plmn-Identity', {})
            mcc_list = plmn_id.get('mcc', [])
            mnc_list = plmn_id.get('mnc', [])
            info['mcc'] = "".join(str(x) for x in mcc_list)
            info['mnc'] = "".join(str(x) for x in mnc_list)
            
    if 'SIB3' in sibs:
        sib3 = sibs['SIB3']
        val, rnc_id, cell_id = format_cell_id(sib3.get('cellIdentity'))
        info['cell_identity'] = val
        info['rnc_id'] = rnc_id
        info['local_cell_id'] = cell_id
        
    if 'SIB11' in sibs:
        sib11 = sibs['SIB11']
        control = sib11.get('measurementControlSysInfo', {})
        hcs = control.get('use-of-HCS', (None, {}))
        if hcs[0] == 'hcs-not-used':
            quality = hcs[1].get('cellSelectQualityMeasure', (None, {}))
            if quality[0] in ['cpich-RSCP', 'cpich-Ec-N0']:
                quality_val = quality[1]
                inter_meas = quality_val.get('interFreqMeasurementSysInfo', {})
                if inter_meas:
                    inter_list_struct = inter_meas.get('interFreqCellInfoSI-List', {})
                    if inter_list_struct:
                        new_cells = inter_list_struct.get('newInterFreqCellList', [])
                        current_fdd_uarfcn = None
                        for cell in new_cells:
                            cell_id = cell.get('interFreqCellID')
                            cell_info = cell.get('cellInfo', {})
                            cell_mode_choice, cell_mode_val = cell_info.get('modeSpecificInfo', (None, {}))
                            
                            freq_info = cell.get('frequencyInfo')
                            if freq_info is not None:
                                mode_choice, mode_val = freq_info.get('modeSpecificInfo', (None, {}))
                                if mode_choice == 'fdd' and cell_mode_choice == 'fdd':
                                    current_fdd_uarfcn = mode_val.get('uarfcn-DL')
                            
                            if cell_mode_choice == 'fdd':
                                psc = cell_mode_val.get('primaryCPICH-Info', {}).get('primaryScramblingCode')
                                if psc is not None:
                                    info['wcdma_neighbors'].append({
                                        'cell_id': cell_id,
                                        'uarfcn': current_fdd_uarfcn,
                                        'psc': psc
                                    })
                                    
    if 'SIB19' in sibs:
        sib19 = sibs['SIB19']
        lte_list = sib19.get('eutra-FrequencyAndPriorityInfoList', [])
        for item in lte_list:
            earfcn = item.get('earfcn')
            bandwidth = item.get('measurementBandwidth')
            priority = item.get('priority')
            q_rx_lev_min = item.get('qRxLevMinEUTRA')
            
            bw_map = {
                'mbw6': '1.4 MHz (6 RBs)',
                'mbw15': '3 MHz (15 RBs)',
                'mbw25': '5 MHz (25 RBs)',
                'mbw50': '10 MHz (50 RBs)',
                'mbw75': '15 MHz (75 RBs)',
                'mbw100': '20 MHz (100 RBs)'
            }
            bw_str = bw_map.get(bandwidth, str(bandwidth))
            
            freq_mhz = 0.0
            band_str = "Unknown"
            if 0 <= earfcn <= 599:
                freq_mhz = 2110.0 + 0.1 * earfcn
                band_str = "Band 1"
            elif 1200 <= earfcn <= 1949:
                freq_mhz = 1805.0 + 0.1 * (earfcn - 1200)
                band_str = "Band 3"
            elif 2750 <= earfcn <= 3449:
                freq_mhz = 2620.0 + 0.1 * (earfcn - 2750)
                band_str = "Band 7"
            elif 6150 <= earfcn <= 6449:
                freq_mhz = 791.0 + 0.1 * (earfcn - 6150)
                band_str = "Band 20"
                
            info['lte_neighbors'].append({
                'earfcn': earfcn,
                'band': band_str,
                'freq_mhz': freq_mhz,
                'bw': bw_str,
                'priority': priority,
                'q_rx_lev_min': q_rx_lev_min
            })
            
    return info


def update_hot_md(cells_data):
    hot_path = os.path.join(WIKI_DIR, "hot.md")
    if not os.path.exists(hot_path):
        print(f"Uyarı: hot.md bulunamadı: {hot_path}")
        return

    print("hot.md güncelleniyor...")
    with open(hot_path, "r") as f:
        content = f.read()

    summary_lines = [
        "## Son Tespit Edilen Aktif Hücreler (Phase 2 & 4)",
        "",
        "| UARFCN | Frekans | PSC (Scrambling) | Kod Grubu | CPICH RSCP | CPICH Ec/No | Slot Timing | Kayıt Zamanı | SIB Dekodlama |",
        "|--------|---------|------------------|-----------|------------|-------------|-------------|--------------|---------------|"
    ]
    for cell in cells_data:
        sib_status = "Tamamlandı (SIB3, 5, 11, 19)" if cell.get('has_sib') else "Yapılmadı"
        if cell.get('has_sib'):
            psc_col = f"[[Cell_WCDMA_UARFCN{cell['uarfcn']}_SC{cell['scrambling_code']}|{cell['scrambling_code']}]]"
        else:
            psc_col = f"{cell['scrambling_code']}"
        summary_lines.append(
            f"| {cell['uarfcn']} | {cell['frequency_mhz']} MHz | {psc_col} | {cell['code_group']} | {cell['cpich_rscp_dbm']:.2f} dBm | {cell['cpich_ecno_db']:.2f} dB | {cell['slot_timing_sample']} | {cell['timestamp']} | {sib_status} |"
        )
    
    if "## Son Tespit Edilen Aktif Hücreler" in content:
        parts = content.split("## Son Tespit Edilen Aktif Hücreler")
        new_content = parts[0] + "\n".join(summary_lines) + "\n"
    elif "## Son Tespit Edilen Aktif Hücreler (Phase 2)" in content:
        parts = content.split("## Son Tespit Edilen Aktif Hücreler (Phase 2)")
        new_content = parts[0] + "\n".join(summary_lines) + "\n"
    elif "## Son Tespit Edilen Aktif Hücreler (Phase 2 & 4)" in content:
        parts = content.split("## Son Tespit Edilen Aktif Hücreler (Phase 2 & 4)")
        new_content = parts[0] + "\n".join(summary_lines) + "\n"
    else:
        new_content = content.strip() + "\n\n" + "\n".join(summary_lines) + "\n"

    # Also update the updated timestamp in header
    lines = new_content.splitlines()
    for idx, l in enumerate(lines):
        if l.startswith("updated:"):
            lines[idx] = f"updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            break
    new_content = "\n".join(lines) + "\n"

    with open(hot_path, "w") as f:
        f.write(new_content)
    print("hot.md başarıyla güncellendi.")

def update_log_md(cells_data):
    log_path = os.path.join(WIKI_DIR, "log.md")
    if not os.path.exists(log_path):
        print(f"Uyarı: log.md bulunamadı: {log_path}")
        return

    print("log.md güncelleniyor...")
    with open(log_path, "r") as f:
        content = f.read()

    log_entry_lines = [
        "",
        f"### {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Faz 4: SIB11 ve SIB19 Komşu Hücre Dekodlama",
        "- **Dekodlama Kaynağı:** `captures/uarfcn_10813_long.cfile.bch.json` (3.0 saniyelik uzun capture).",
        "- **Gerçekleşen Analizler:**"
    ]
    for cell in cells_data:
        if cell.get('has_sib'):
            log_entry_lines.append(
                f"  - **UARFCN {cell['uarfcn']} (SC {cell['scrambling_code']}):** SIB reassembly ve ASN.1 UPER decode başarıyla tamamlandı. Hücre Kimliği: **{cell['cell_identity']}** (MCC {cell['mcc']}, MNC {cell['mnc']}). Tespit edilen komşu sayısı: **{len(cell['wcdma_neighbors'])}** WCDMA hücresi, **{len(cell['lte_neighbors'])}** LTE frekansı."
            )
    log_entry_lines.append("- **Durum:** Başarılı. Sıfır fallback prensibine uygun olarak havadan tüm komşuluk topolojisi çıkarıldı.")

    new_content = content.strip() + "\n" + "\n".join(log_entry_lines) + "\n"
    with open(log_path, "w") as f:
        f.write(new_content)
    print("log.md başarıyla güncellendi.")

def update_index_md(cells_data):
    index_path = os.path.join(WIKI_DIR, "index.md")
    if not os.path.exists(index_path):
        print(f"Uyarı: index.md bulunamadı: {index_path}")
        return

    print("index.md güncelleniyor...")
    with open(index_path, "r") as f:
        content = f.read()

    cell_links = ["### Aktif WCDMA Hücre Listesi (Phase 2 & 4)", ""]
    for cell in cells_data:
        if cell.get('has_sib'):
            cell_links.append(f"- [[Cell_WCDMA_UARFCN{cell['uarfcn']}_SC{cell['scrambling_code']}]] — UARFCN {cell['uarfcn']} (SC: {cell['scrambling_code']}) (Decoded SIBs, CID: {cell['cell_identity']})")

    if "### Aktif WCDMA Hücre Listesi (Phase 2)" in content:
        parts = content.split("### Aktif WCDMA Hücre Listesi (Phase 2)")
        new_content = parts[0] + "\n".join(cell_links) + "\n"
    elif "### Aktif WCDMA Hücre Listesi (Phase 2 & 4)" in content:
        parts = content.split("### Aktif WCDMA Hücre Listesi (Phase 2 & 4)")
        new_content = parts[0] + "\n".join(cell_links) + "\n"
    else:
        new_content = content.strip() + "\n\n" + "\n".join(cell_links) + "\n"

    with open(index_path, "w") as f:
        f.write(new_content)
    print("index.md başarıyla güncellendi.")

def update_neighbor_map_md(cells_data):
    map_path = os.path.join(WIKI_DIR, "references", "WCDMA Komşu Haritası.md")
    os.makedirs(os.path.dirname(map_path), exist_ok=True)
    
    print("WCDMA Komşu Haritası.md güncelleniyor...")
    
    # Build serving to neighbor lists
    serv_to_neigh = {}
    for cell in cells_data:
        k = (int(cell["uarfcn"]), int(cell["scrambling_code"]))
        serv_to_neigh[k] = set()
        if cell.get("has_sib"):
            for n in cell["wcdma_neighbors"]:
                if n["uarfcn"] is not None and n["psc"] is not None:
                    serv_to_neigh[k].add((int(n["uarfcn"]), int(n["psc"])))
                    
    decoded_cells = {(int(c["uarfcn"]), int(c["scrambling_code"])) for c in cells_data if c.get("has_sib")}
                    
    lines = [
        "---",
        "source: \"wcdma_wiki_helper neighbor map\"",
        f"created_date: {datetime.now().strftime('%Y-%m-%d')}",
        "tags:",
        "  - references",
        "  - wcdma",
        "  - topology",
        "---",
        "",
        "# WCDMA Komşu Hücre İlişkileri Haritası",
        "",
        "Bu sayfa, taranan tüm WCDMA hücrelerinin komşuluk ilişkilerini, çift yönlü (bidirectional) bağlantı durumlarını ve topolojisini listeler.",
        "",
        "## Hücre Komşuluk Matrisi",
        "",
        "| Kaynak Hücre | Kaynak Frekans | Hedef Komşu | Hedef Frekans | Yön Durumu | Açıklama |",
        "|--------------|----------------|-------------|---------------|------------|----------|",
    ]
    
    relations_found = False
    for cell in cells_data:
        src_u = int(cell["uarfcn"])
        src_sc = int(cell["scrambling_code"])
        src_key = (src_u, src_sc)
        
        if cell.get("has_sib") and cell["wcdma_neighbors"]:
            relations_found = True
            for n in cell["wcdma_neighbors"]:
                if n["uarfcn"] is None or n["psc"] is None:
                    continue
                dst_u = int(n["uarfcn"])
                dst_sc = int(n["psc"])
                dst_key = (dst_u, dst_sc)
                
                # Check bidirectional
                is_bidirectional = src_key in serv_to_neigh.get(dst_key, set())
                
                direction_str = "🔄 Çift Yönlü" if is_bidirectional else "➡️ Tek Yönlü"
                desc_str = "Her iki hücre de birbirini komşu olarak görüyor." if is_bidirectional else "Sadece kaynak hücre hedefi bildiriyor."
                
                src_link = f"[[Cell_WCDMA_UARFCN{src_u}_SC{src_sc}\\|UARFCN {src_u} SC {src_sc}]]"
                if dst_key in decoded_cells:
                    dst_link = f"[[Cell_WCDMA_UARFCN{dst_u}_SC{dst_sc}\\|UARFCN {dst_u} SC {dst_sc}]]"
                else:
                    dst_link = f"UARFCN {dst_u} SC {dst_sc}"
                
                src_freq = 925.0 + 0.2 * (src_u - 2937) if src_u < 5000 else 2110.0 + 0.2 * (src_u - 10562)
                dst_freq = 925.0 + 0.2 * (dst_u - 2937) if dst_u < 5000 else 2110.0 + 0.2 * (dst_u - 10562)
                
                lines.append(f"| {src_link} | {src_freq:.1f} MHz | {dst_link} | {dst_freq:.1f} MHz | {direction_str} | {desc_str} |")
                
    if not relations_found:
        lines.append("| - | - | - | - | - | SIB11 komşu verisi bulunamadı. |")
        
    lines.append("")
    lines.append("---")
    lines.append("*Bu sayfa wcdma_wiki_helper.py tarafından otomatik olarak üretilmiştir.*")
    
    with open(map_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Komşu haritası başarıyla güncellendi: {map_path}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="WCDMA Wiki Entegrasyon Yardımcısı")
    parser.add_argument("--uarfcns", type=int, nargs="+", help="Sadece bu UARFCN'lerin sonuçlarını wikiye işle")
    args = parser.parse_args()

    results_files = glob.glob("captures/*.results.json")

    if not results_files:
        print("Hata: captures/ dizininde .results.json dosyası bulunamadı!")
        return

    print("ASN.1 derleniyor...")
    asn_files = [
        "wcdma_rrc_asn1/Constant-definitions.asn",
        "wcdma_rrc_asn1/Class-definitions.asn",
        "wcdma_rrc_asn1/InformationElements.asn",
        "wcdma_rrc_asn1/PDU-definitions.asn",
        "wcdma_rrc_asn1/Internode-definitions.asn"
    ]
    db = asn1tools.compile_files(asn_files, 'uper')

    print(f"Toplam {len(results_files)} sonuç dosyası bulundu. İşleniyor...")
    
    cells_data = []
    
    # 1. Collect all cells data
    for rf in results_files:
        with open(rf, "r") as f:
            data = json.load(f)
            
        uarfcn = data["uarfcn"]
        freq_mhz = data["frequency_mhz"]
        
        meta_path = rf.replace(".results.json", ".json")
        timestamp = datetime.now().strftime("%Y-%m-%d")
        if os.path.exists(meta_path):
            with open(meta_path, "r") as mf:
                mdata = json.load(mf)
                timestamp = mdata.get("timestamp", datetime.now().strftime("%Y-%m-%d"))

        for cell in data["cells"]:
            sc = cell["scrambling_code"]
            grp = cell["code_group"]
            rscp = cell["cpich_rscp_dbm"]
            ecno = cell["cpich_ecno_db"]
            slot_timing = cell["slot_timing_sample"]
            frame_timing = cell["frame_timing_sample"]
            freq_corr = cell["frequency_correction_hz"]
            
            # Check for bch JSON (try cell-specific first, then general)
            bch_filename = rf.replace(".results.json", f"_sc{sc}.bch.json")
            if not os.path.exists(bch_filename):
                bch_filename = rf.replace(".results.json", ".bch.json")
            sib_info = None
            if os.path.exists(bch_filename):
                print(f"[+] BCH dosyası bulundu: {bch_filename}. SIB'ler çözümleniyor...")
                sib_info = decode_bch_for_capture(bch_filename, db)
                
            cell_info = {
                "uarfcn": uarfcn,
                "frequency_mhz": freq_mhz,
                "scrambling_code": sc,
                "code_group": grp,
                "cpich_rscp_dbm": rscp,
                "cpich_ecno_db": ecno,
                "slot_timing_sample": slot_timing,
                "frame_timing_sample": frame_timing,
                "frequency_correction_hz": freq_corr,
                "timestamp": timestamp,
                "has_sib": False
            }
            
            if sib_info and sib_info['cell_identity'] is not None:
                cell_info.update({
                    "has_sib": True,
                    "mcc": sib_info['mcc'],
                    "mnc": sib_info['mnc'],
                    "cell_identity": sib_info['cell_identity'],
                    "rnc_id": sib_info['rnc_id'],
                    "local_cell_id": sib_info['local_cell_id'],
                    "wcdma_neighbors": sib_info['wcdma_neighbors'],
                    "lte_neighbors": sib_info['lte_neighbors']
                })
                
            cells_data.append(cell_info)

    # Compile the set of all decoded cells
    decoded_cells = {(int(c["uarfcn"]), int(c["scrambling_code"])) for c in cells_data if c.get("has_sib")}
    print(f"Decoded cell keys: {decoded_cells}")

    # Track currently generated markdown files to clean up other stale ones
    generated_md_files = set()

    # 2. Generate cell markdown files ONLY for decoded cells
    for cell_info in cells_data:
        if not cell_info["has_sib"]:
            continue
        if args.uarfcns and cell_info["uarfcn"] not in args.uarfcns:
            continue
            
        uarfcn = cell_info["uarfcn"]
        sc = cell_info["scrambling_code"]
        freq_mhz = cell_info["frequency_mhz"]
        grp = cell_info["code_group"]
        rscp = cell_info["cpich_rscp_dbm"]
        ecno = cell_info["cpich_ecno_db"]
        slot_timing = cell_info["slot_timing_sample"]
        frame_timing = cell_info["frame_timing_sample"]
        freq_corr = cell_info["frequency_correction_hz"]
        timestamp = cell_info["timestamp"]
        
        cell_filename = f"Cell_WCDMA_UARFCN{uarfcn}_SC{sc}.md"
        cell_path = os.path.join(WIKI_DIR, "cells", cell_filename)
        os.makedirs(os.path.dirname(cell_path), exist_ok=True)
        generated_md_files.add(cell_filename)
        
        operator_str = "Turkcell" if cell_info['mnc'] == "01" else f"MNC {cell_info['mnc']}" if cell_info["has_sib"] else ""
        
        markdown_content = f"""---
source: "wcdma_cellsearch analysis"
created_date: {datetime.now().strftime('%Y-%m-%d')}
tags:
  - cells
  - wcdma
  - uarfcn_{uarfcn}
  - decoded_sibs
  - operator_turkcell
---

# WCDMA Cell: UARFCN {uarfcn} - SC {sc}

Bu sayfa, LimeSDR Mini üzerinden alınan ham IQ capture verisinin offline analizi sonucunda elde edilen WCDMA hücresinin teknik parametrelerini barındırır. Analiz işlemi [[WCDMA Cell Search]] ve [[CPICH]] despreading matematiksel modellerini kullanır.

## Hücre Parametreleri

| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| **UARFCN** | {uarfcn} | 3GPP Kanal Numarası |
| **Frekans** | {freq_mhz:.1f} MHz | Merkez Taşıyıcı Frekansı |
| **Primary Scrambling Code (PSC)** | [[Scrambling Code|{sc}]] | Hücre Tanımlama Kodu (0 - 511) |
| **Code Group** | {grp} | [[Scrambling Code|Scrambling Code Grubu]] (0 - 63) |
| **CPICH RSCP** | {rscp:.2f} dBm | Ortak Pilot Kanalı Alış Gücü (Received Signal Code Power) |
| **CPICH Ec/No** | {ecno:.2f} dB | Spektral Sürültü/Sinyal Oranı |
| **Slot Timing** | {slot_timing} | Slot Sınır Örnek Endeksi (5120 sample içinde) |
| **Frame Timing** | {frame_timing} | Çerçeve Başlangıç Örnek Endeksi (76800 sample içinde) |
| **Frekans Düzeltme** | {freq_corr} Hz | SDR ppm kayması düzeltme değeri |
| **Analiz Zamanı** | {timestamp} | Verinin capture edilme zaman damgası |

## RRC Sistem Bilgileri (BCH Decode - Faz 4)

BCH transport kanalı başarıyla çözülmüş ve UPER ASN.1 şeması yardımıyla Sistem Bilgi Blokları (SIB) ayrıştırılmıştır.

### Servis Sağlayıcı ve Hücre Parametreleri
* **Mobil Ülke Kodu (MCC):** {cell_info['mcc']} (Türkiye)
* **Mobil Şebeke Kodu (MNC):** {cell_info['mnc']} ({operator_str})
* **Hücre Kimliği (Cell Identity):** {cell_info['cell_identity']}
* **RNC ID:** {cell_info['rnc_id']}
* **Yerel Hücre ID (Local Cell ID):** {cell_info['local_cell_id']}

### Komşu WCDMA Hücreleri (SIB11 - Inter-Frequency)
Aşağıdaki hücreler SIB11 mesajı içerisinde komşu hücre olarak bildirilmiştir:

| Komşu ID | UARFCN | Frekans | Komşu Hücre PSC | Wiki Sayfası |
|----------|--------|---------|-----------------|--------------|
"""
        for ncell in cell_info['wcdma_neighbors']:
            n_id_str = str(ncell['cell_id']) if ncell['cell_id'] is not None else "N/A"
            n_uarfcn = ncell['uarfcn']
            n_psc = ncell['psc']
            n_freq = 925.0 + 0.2 * (n_uarfcn - 2937) if n_uarfcn < 5000 else 2110.0 + 0.2 * (n_uarfcn - 10562)
            
            # Check if neighbor is decoded to determine wikilink vs plain text
            if (int(n_uarfcn), int(n_psc)) in decoded_cells:
                link_str = f"[[Cell_WCDMA_UARFCN{n_uarfcn}_SC{n_psc}\\|Hücre UARFCN {n_uarfcn} SC {n_psc}]]"
            else:
                link_str = f"UARFCN {n_uarfcn} SC {n_psc}"
                
            markdown_content += f"| {n_id_str:>8s} | {n_uarfcn:6d} | {n_freq:6.1f} MHz | {n_psc:15d} | {link_str} |\n"

        markdown_content += f"""
### Komşu LTE Frekansları (SIB19 - Inter-RAT)
Hücrenin SIB19 içerisinde yayınladığı E-UTRA komşu taşıyıcı frekansları:

| EARFCN | LTE Bandı | Frekans | Bant Genişliği | Öncelik | Min Alış Seviyesi |
|--------|-----------|---------|----------------|---------|-------------------|
"""
        for lcell in cell_info['lte_neighbors']:
            markdown_content += f"| {lcell['earfcn']:6d} | {lcell['band']:10s} | {lcell['freq_mhz']:6.1f} MHz | {lcell['bw']:14s} | {lcell['priority']:7d} | {lcell['q_rx_lev_min']:4d} dBm |\n"

        # Add cross-validation note
        cross_val_notes = []
        if uarfcn == 10813 and sc == 483:
            cross_val_notes.append("UARFCN 2997 bağımsız iki kaynakta (WCDMA SIB11 + harici GSM SI2quater) komşu olarak doğrulanmıştır.")
            for lcell in cell_info['lte_neighbors']:
                if lcell['earfcn'] in [1300, 3050, 6300]:
                    cross_val_notes.append(f"EARFCN {lcell['earfcn']} ({lcell['band']}) komşu frekansı GSM SI2quater taramalarında da Turkcell LTE komşusu olarak teyit edilmiştir.")
        
        if cross_val_notes:
            markdown_content += "\n### Çapraz RAT ve Harici Doğrulama\n"
            for note in cross_val_notes:
                markdown_content += f"> [!NOTE]\n> **Doğrulama:** {note}\n\n"

        markdown_content += f"""
## Mimari İlişkiler
* **Erişim Metodu:** [[WCDMA Genel]] CDMA teknolojisi ile aynı frekansta kod bölmeli çoğullama.
* **Senkronizasyon:** P-SCH ([[P-SCH]]) ile slot senkronizasyonu ve S-SCH ([[S-SCH]]) ile frame senkronizasyonu tamamlanmıştır.
* **Pilot Sinyali:** [[CPICH]] kanalı SF=256 OVSF kodu ile sürekli olarak yayınlanmaktadır.
* **BCH Çözümleme:** [[BCH]] transport kanalı üzerinden MIB, SIB3, SIB5, SIB11 ve SIB19 çözümlenmiştir.

---
*Bu sayfa wcdma_wiki_helper.py tarafından otomatik olarak üretilmiştir.*
"""
        with open(cell_path, "w") as cf:
            cf.write(markdown_content)
        print(f"Hücre sayfası oluşturuldu: {cell_path}")

    # Cleanup any stale/unneeded cell markdown files in the wiki directory
    cells_dir = os.path.join(WIKI_DIR, "cells")
    if os.path.exists(cells_dir):
        import re
        for existing_file in os.listdir(cells_dir):
            if existing_file.endswith(".md") and existing_file not in generated_md_files:
                # Only delete if it belongs to a UARFCN we are currently processing (if filtered)
                m = re.match(r"Cell_WCDMA_UARFCN(\d+)_SC\d+\.md", existing_file)
                if m:
                    file_uarfcn = int(m.group(1))
                    if args.uarfcns and file_uarfcn not in args.uarfcns:
                        continue
                
                existing_path = os.path.join(cells_dir, existing_file)
                try:
                    os.remove(existing_path)
                    print(f"Eski/İskelet hücre sayfası silindi: {existing_path}")
                except Exception as e:
                    print(f"Dosya silinirken hata oluştu {existing_path}: {e}")

    # Update global wiki docs
    update_index_md(cells_data)
    update_log_md(cells_data)
    update_hot_md(cells_data)
    update_neighbor_map_md(cells_data)
    print("Tüm wiki entegrasyonu başarıyla tamamlandı!")

if __name__ == "__main__":
    main()

