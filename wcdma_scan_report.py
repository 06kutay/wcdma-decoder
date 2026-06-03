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
import sys
import glob
import json
import asn1tools
from datetime import datetime
import wcdma_si_assembler

def uarfcn_to_freq(uarfcn):
    if 10562 <= uarfcn <= 10838:
        return 2110.0 + 0.2 * (uarfcn - 10562)
    elif 2937 <= uarfcn <= 3088:
        return 925.0 + 0.2 * (uarfcn - 2937)
    else:
        return 0.0

def earfcn_to_freq_band(earfcn):
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
    return freq_mhz, band_str

def format_cell_id(bit_tuple):
    if not bit_tuple:
        return None, None, None
    data, bit_len = bit_tuple
    val = int.from_bytes(data, 'big') >> (len(data) * 8 - bit_len)
    rnc_id = val >> 16
    cell_id = val & 0xFFFF
    return val, rnc_id, cell_id

def decode_sib_data(bch_json_path, db):
    """
    Decodes SIBs from a given BCH json file.
    """
    try:
        sibs = wcdma_si_assembler.assemble_sibs_from_json(bch_json_path, db)
    except Exception as e:
        print(f"[-] SIB birleştirme hatası ({bch_json_path}): {e}")
        return None
        
    info = {
        "mcc": "N/A",
        "mnc": "N/A",
        "cell_id": "N/A",
        "rnc_id": "N/A",
        "local_cell_id": "N/A",
        "wcdma_neighbors": [],
        "lte_neighbors": [],
        "gsm_neighbors": []
    }
    
    if 'MIB' in sibs:
        mib = sibs['MIB']
        plmn_type = mib.get('plmn-Type', (None, {}))
        if plmn_type[0] == 'gsm-MAP':
            plmn_id = plmn_type[1].get('plmn-Identity', {})
            mcc_list = plmn_id.get('mcc', [])
            mnc_list = plmn_id.get('mnc', [])
            info["mcc"] = "".join(str(x) for x in mcc_list)
            info["mnc"] = "".join(str(x) for x in mnc_list)
            
    if 'SIB3' in sibs:
        sib3 = sibs['SIB3']
        val, rnc_id, cell_id = format_cell_id(sib3.get('cellIdentity'))
        if val is not None:
            info["cell_id"] = str(val)
            info["rnc_id"] = str(rnc_id)
            info["local_cell_id"] = str(cell_id)
            
    if 'SIB11' in sibs:
        sib11 = sibs['SIB11']
        control = sib11.get('measurementControlSysInfo', {})
        hcs = control.get('use-of-HCS', (None, {}))
        if hcs[0] == 'hcs-not-used':
            quality = hcs[1].get('cellSelectQualityMeasure', (None, {}))
            if quality[0] in ['cpich-RSCP', 'cpich-Ec-N0']:
                quality_val = quality[1]
                
                # WCDMA inter-frequency neighbors
                inter_meas = quality_val.get('interFreqMeasurementSysInfo', {})
                if inter_meas:
                    inter_list_struct = inter_meas.get('interFreqCellInfoSI-List', {})
                    if inter_list_struct:
                        new_cells = inter_list_struct.get('newInterFreqCellList', [])
                        current_fdd_uarfcn = None
                        for cell in new_cells:
                            cell_id_val = cell.get('interFreqCellID')
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
                                    info["wcdma_neighbors"].append({
                                        "cell_id": cell_id_val,
                                        "uarfcn": current_fdd_uarfcn,
                                        "psc": psc
                                    })
                                    
                # GSM inter-RAT neighbors
                inter_rat_meas = quality_val.get('interRATMeasurementSysInfo', {})
                if inter_rat_meas:
                    inter_rat_list = inter_rat_meas.get('interRATCellInfoList', {})
                    if inter_rat_list:
                        new_rat_cells = inter_rat_list.get('newInterRATCellList', [])
                        for cell in new_rat_cells:
                            cell_id_val = cell.get('interRATCellID')
                            tech_choice, tech_val = cell.get('technologySpecificInfo', (None, {}))
                            if tech_choice == 'gsm':
                                bsic_dict = tech_val.get('bsic', {})
                                ncc = bsic_dict.get('ncc')
                                bcc = bsic_dict.get('bcc')
                                bsic_str = f"{ncc}{bcc}" if ncc is not None and bcc is not None else "N/A"
                                freq_band = tech_val.get('frequency-band', "Unknown")
                                bcch_arfcn = tech_val.get('bcch-ARFCN')
                                info["gsm_neighbors"].append({
                                    "cell_id": cell_id_val,
                                    "arfcn": bcch_arfcn,
                                    "bsic": bsic_str,
                                    "band": str(freq_band)
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
                'mbw6': '1.4 MHz',
                'mbw15': '3 MHz',
                'mbw25': '5 MHz',
                'mbw50': '10 MHz',
                'mbw75': '15 MHz',
                'mbw100': '20 MHz'
            }
            bw_str = bw_map.get(bandwidth, str(bandwidth))
            
            freq_mhz, band_str = earfcn_to_freq_band(earfcn)
            
            info["lte_neighbors"].append({
                "earfcn": earfcn,
                "band": band_str,
                "freq_mhz": freq_mhz,
                "bw": bw_str,
                "priority": priority,
                "q_rx_lev_min": q_rx_lev_min
            })
            
    return info

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Birleşik Tarama Raporu Oluşturucu")
    parser.add_argument("--uarfcns", type=int, nargs="+", help="Sadece bu UARFCN'lerin sonuçlarını raporla")
    args = parser.parse_args()

    print("[*] Birleşik Tarama Raporu Oluşturucu")
    
    # Compile ASN.1
    asn_files = [
        "wcdma_rrc_asn1/Constant-definitions.asn",
        "wcdma_rrc_asn1/Class-definitions.asn",
        "wcdma_rrc_asn1/InformationElements.asn",
        "wcdma_rrc_asn1/PDU-definitions.asn",
        "wcdma_rrc_asn1/Internode-definitions.asn"
    ]
    try:
        db = asn1tools.compile_files(asn_files, 'uper')
    except Exception as e:
        print(f"[-] ASN.1 derleme hatası: {e}")
        sys.exit(1)
        
    results_files = glob.glob("captures/*.results.json")
    
    # Filter by uarfcns if specified
    if args.uarfcns:
        filtered_files = []
        for rf in results_files:
            try:
                with open(rf, "r") as f:
                    data = json.load(f)
                uarfcn = data.get("uarfcn")
                if uarfcn in args.uarfcns:
                    filtered_files.append(rf)
            except Exception:
                pass
        results_files = filtered_files

    if not results_files:
        print("[-] Raporlanacak aktif results.json dosyası bulunamadı!")
        sys.exit(1)
        
    scanned_cells = []
    wcdma_neighbors_all = []
    lte_neighbors_all = []
    gsm_neighbors_all = []
    scanned_uarfcns = set()
    
    for rf in results_files:
        with open(rf, "r") as f:
            data = json.load(f)
            
        uarfcn = data.get("uarfcn")
        if uarfcn:
            scanned_uarfcns.add(int(uarfcn))
            
        freq_mhz = data.get("frequency_mhz", 0.0)
        
        prefix = rf.replace(".results.json", "")
        
        for cell in data.get("cells", []):
            sc = cell["scrambling_code"]
            ecno = cell["cpich_ecno_db"]
            rscp = cell["cpich_rscp_dbm"]
            grp = cell["code_group"]
            timing = cell["frame_timing_sample"]
            cfo = cell["frequency_correction_hz"]
            
            # Check for bch file
            bch_filename = prefix.replace(".cfile", f"_sc{sc}.bch.json")
            if not os.path.exists(bch_filename):
                bch_filename = prefix + f"_sc{sc}.bch.json"
            if not os.path.exists(bch_filename):
                bch_filename = rf.replace(".results.json", f"_sc{sc}.bch.json")
            if not os.path.exists(bch_filename):
                # Fallback to general .bch.json
                bch_filename = rf.replace(".results.json", ".bch.json")
                
            sib_info = None
            if os.path.exists(bch_filename):
                # Only use if this bch file belongs to the current cell or is legacy general
                # We assume wcdma_scan.py writes cell-specific bch files correctly
                sib_info = decode_sib_data(bch_filename, db)
                
            cell_summary = {
                "uarfcn": uarfcn,
                "freq_mhz": freq_mhz,
                "sc": sc,
                "grp": grp,
                "ecno": ecno,
                "rscp": rscp,
                "timing": timing,
                "cfo": cfo,
                "bch_status": "Çözüldü" if sib_info else "Çözülmedi",
                "mcc": sib_info["mcc"] if sib_info else "N/A",
                "mnc": sib_info["mnc"] if sib_info else "N/A",
                "cell_id": sib_info["cell_id"] if sib_info else "N/A",
                "rnc_id": sib_info["rnc_id"] if sib_info else "N/A",
                "local_cell_id": sib_info["local_cell_id"] if sib_info else "N/A"
            }
            scanned_cells.append(cell_summary)
            
            if sib_info:
                # Add to neighbor list collections
                for n in sib_info["wcdma_neighbors"]:
                    wcdma_neighbors_all.append({
                        "serving_sc": sc,
                        "cell_id": n["cell_id"],
                        "uarfcn": n["uarfcn"],
                        "psc": n["psc"]
                    })
                for n in sib_info["lte_neighbors"]:
                    lte_neighbors_all.append({
                        "serving_sc": sc,
                        "earfcn": n["earfcn"],
                        "band": n["band"],
                        "freq_mhz": n["freq_mhz"],
                        "bw": n["bw"],
                        "priority": n["priority"],
                        "q_rx_lev_min": n["q_rx_lev_min"]
                    })
                for n in sib_info["gsm_neighbors"]:
                    gsm_neighbors_all.append({
                        "serving_sc": sc,
                        "cell_id": n["cell_id"],
                        "arfcn": n["arfcn"],
                        "bsic": n["bsic"],
                        "band": n["band"]
                    })

    # Find discovered but not scanned UARFCNs
    discovered_uarfcns = set()
    for n in wcdma_neighbors_all:
        if n["uarfcn"]:
            discovered_uarfcns.add(int(n["uarfcn"]))
            
    unscanned_uarfcns = discovered_uarfcns - scanned_uarfcns
    
    # Sort tables
    scanned_cells = sorted(scanned_cells, key=lambda x: (x["uarfcn"], -x["ecno"]))
    
    # Generate Output File
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"captures/wcdma_scan_report_{now_str}.txt"
    
    report = []
    report.append("==================================================================================")
    report.append(f"               WCDMA/UMTS TEK KOMUTLU SAHA TARAMA BİRLEŞİK RAPORU")
    report.append(f"               Rapor Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("==================================================================================")
    report.append("")
    
    # Table 1: Detected Cells
    report.append("TABLO 1: TESPİT EDİLEN HÜCRELER (SERVING & DETECTED)")
    report.append("-" * 115)
    report.append(f"| {'UARFCN':6s} | {'Frekans':8s} | {'PSC':3s} | {'Ec/N0':6s} | {'RSCP':8s} | {'BCH':8s} | {'PLMN':7s} | {'Cell ID':8s} | {'RNC ID':6s} | {'L-Cell ID':9s} |")
    report.append("-" * 115)
    for c in scanned_cells:
        plmn = f"{c['mcc']}-{c['mnc']}" if c['mcc'] != "N/A" else "N/A"
        report.append(f"| {c['uarfcn']:6} | {c['freq_mhz']:6.1f} MHz | {c['sc']:3d} | {c['ecno']:5.1f}dB | {c['rscp']:6.1f}dBm | {c['bch_status']:8s} | {plmn:7s} | {c['cell_id']:8s} | {c['rnc_id']:6s} | {c['local_cell_id']:9s} |")
    report.append("-" * 115)
    report.append("")
    
    # Table 2: WCDMA Neighbors (SIB11)
    report.append("TABLO 2: WCDMA SIB11 INTER-FREQUENCY KOMŞULAR")
    report.append("-" * 85)
    report.append(f"| {'Serving PSC':11s} | {'Neighbor ID':11s} | {'UARFCN':6s} | {'DL Frequency':13s} | {'Neighbor PSC':12s} |")
    report.append("-" * 85)
    if wcdma_neighbors_all:
        for n in wcdma_neighbors_all:
            cell_id_str = str(n['cell_id']) if n['cell_id'] is not None else "N/A"
            u_val = n['uarfcn']
            freq_mhz = uarfcn_to_freq(u_val)
            report.append(f"| {n['serving_sc']:11d} | {cell_id_str:>11s} | {u_val:6d} | {freq_mhz:8.1f} MHz   | {n['psc']:12d} |")
    else:
        report.append(f"| {'-':11s} | {'-':11s} | {'-':6s} | {'-':13s} | {'-':12s} |")
    report.append("-" * 85)
    report.append("")
    
    # Table 3: LTE Neighbors (SIB19)
    report.append("TABLO 3: LTE SIB19 NEIGHBOR FREQUENCIES (E-UTRA)")
    report.append("-" * 95)
    report.append(f"| {'Serving PSC':11s} | {'EARFCN':6s} | {'Band':7s} | {'Frequency':10s} | {'Bandwidth':10s} | {'Priority':8s} | {'Min Rx':6s} |")
    report.append("-" * 95)
    if lte_neighbors_all:
        for n in lte_neighbors_all:
            report.append(f"| {n['serving_sc']:11d} | {n['earfcn']:6d} | {n['band']:7s} | {n['freq_mhz']:6.1f} MHz | {n['bw']:10s} | {n['priority']:8d} | {n['q_rx_lev_min']:4d}dB |")
    else:
        report.append(f"| {'-':11s} | {'-':6s} | {'-':7s} | {'-':10s} | {'-':10s} | {'-':8s} | {'-':6s} |")
    report.append("-" * 95)
    report.append("")
    
    # Table 4: GSM Neighbors (SIB11)
    report.append("TABLO 4: GSM SIB11 INTER-RAT KOMŞULAR")
    report.append("-" * 65)
    report.append(f"| {'Serving PSC':11s} | {'ARFCN':5s} | {'BSIC':4s} | {'Frequency Band':20s} |")
    report.append("-" * 65)
    if gsm_neighbors_all:
        for n in gsm_neighbors_all:
            report.append(f"| {n['serving_sc']:11d} | {n['arfcn']:5d} | {n['bsic']:4s} | {n['band']:20s} |")
    else:
        report.append(f"| {'-':11s} | {'-':5s} | {'-':4s} | {'-':20s} |")
    report.append("-" * 65)
    report.append("")
    
    # Table 5: Discovery Summary
    report.append("TABLO 5: KEŞİF VE RESCAN ÖNERİLERİ (SIB11'den Çıkan Taranmamış UARFCN'ler)")
    report.append("-" * 80)
    report.append(f"| {'UARFCN':6s} | {'DL Frequency':13s} | {'Önerilen Tarama Komutu':55s} |")
    report.append("-" * 80)
    if unscanned_uarfcns:
        for u in sorted(unscanned_uarfcns):
            freq_mhz = uarfcn_to_freq(u)
            cmd_suggestion = f"python3 wcdma_scan.py --uarfcn {u}"
            report.append(f"| {u:6d} | {freq_mhz:8.1f} MHz   | {cmd_suggestion:55s} |")
    else:
        report.append(f"| {'-':6s} | {'-':13s} | {'Tüm komşu taşıyıcılar taranmış durumda.':55s} |")
    report.append("-" * 80)
    report.append("")
    
    # Write report to text file
    report_content = "\n".join(report)
    with open(report_filename, "w") as f:
        f.write(report_content)
        
    print(f"\033[92m[+] Birleşik metin raporu başarıyla yazıldı: {report_filename}\033[0m")
    
    # Print the same report in colored format to terminal
    print("\n" + report_content.replace("TABLO 1", "\033[96mTABLO 1\033[0m")
                              .replace("TABLO 2", "\033[96mTABLO 2\033[0m")
                              .replace("TABLO 3", "\033[96mTABLO 3\033[0m")
                              .replace("TABLO 4", "\033[96mTABLO 4\033[0m")
                              .replace("TABLO 5", "\033[93mTABLO 5\033[0m"))

if __name__ == "__main__":
    main()
