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
import json
import asn1tools
import wcdma_si_assembler
from datetime import datetime

def format_cell_id(bit_tuple):
    # bit_tuple is (bytes, bit_length)
    if not bit_tuple:
        return "N/A"
    data, bit_len = bit_tuple
    val = int.from_bytes(data, 'big') >> (len(data) * 8 - bit_len)
    rnc_id = val >> 16
    cell_id = val & 0xFFFF
    return f"{val} (RNC: {rnc_id}, Cell: {cell_id})"

def main():
    print("[*] WCDMA Neighbor List Reporter")
    
    bch_json = "captures/uarfcn_10813_long.cfile.bch.json"
    if not os.path.exists(bch_json):
        print(f"[-] Error: BCH JSON file not found: {bch_json}")
        sys.exit(1)
        
    print("[*] Compiling ASN.1 files...")
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
        print(f"[-] Failed to compile ASN.1: {e}")
        sys.exit(1)
        
    print("[*] Reassembling and decoding SIBs...")
    sibs = wcdma_si_assembler.assemble_sibs_from_json(bch_json, db)
    
    # Serving Cell Info
    mcc, mnc = "N/A", "N/A"
    cell_identity_str = "N/A"
    
    if 'MIB' in sibs:
        mib = sibs['MIB']
        plmn_type = mib.get('plmn-Type', (None, {}))
        if plmn_type[0] == 'gsm-MAP':
            plmn_id = plmn_type[1].get('plmn-Identity', {})
            mcc_list = plmn_id.get('mcc', [])
            mnc_list = plmn_id.get('mnc', [])
            mcc = "".join(str(x) for x in mcc_list)
            mnc = "".join(f"{x}" for x in mnc_list)
            
    if 'SIB3' in sibs:
        sib3 = sibs['SIB3']
        cell_identity_str = format_cell_id(sib3.get('cellIdentity'))
        
    report = []
    report.append("# WCDMA Neighbor Cell Topology Report")
    report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    report.append("## Serving Cell Information")
    report.append(f"- **Mobile Country Code (MCC):** {mcc}")
    report.append(f"- **Mobile Network Code (MNC):** {mnc} (Turkcell)" if mnc == "01" else f"- **Mobile Network Code (MNC):** {mnc}")
    report.append(f"- **Cell Identity:** {cell_identity_str}")
    report.append(f"- **Source Capture:** `captures/uarfcn_10813_long.cfile` (UARFCN 10813, SC 483)")
    report.append("")
    
    # WCDMA Neighbor list (SIB11)
    report.append("## WCDMA Inter-Frequency Neighbors (SIB11)")
    wcdma_neighbors = []
    
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
                                    wcdma_neighbors.append({
                                        'cell_id': cell_id,
                                        'uarfcn': current_fdd_uarfcn,
                                        'psc': psc
                                    })
                                    
    if wcdma_neighbors:
        report.append("| Neighbor ID | UARFCN | Downlink Frequency | Primary Scrambling Code (PSC) |")
        report.append("|-------------|--------|-------------------|--------------------------------|")
        for cell in wcdma_neighbors:
            cell_id_str = str(cell['cell_id']) if cell['cell_id'] is not None else "N/A"
            # Calculate freq
            freq_mhz = 925.0 + 0.2 * (cell['uarfcn'] - 2937) if cell['uarfcn'] < 5000 else 2110.0 + 0.2 * (cell['uarfcn'] - 10562)
            report.append(f"| {cell_id_str:>11s} | {cell['uarfcn']:6d} | {freq_mhz:8.1f} MHz | {cell['psc']:30d} |")
    else:
        report.append("*No WCDMA Inter-Frequency neighbors found in SIB11.*")
        
    report.append("")
    
    # LTE Neighbor list (SIB19)
    report.append("## LTE Neighbor Frequencies (SIB19)")
    lte_neighbors = []
    
    if 'SIB19' in sibs:
        sib19 = sibs['SIB19']
        lte_list = sib19.get('eutra-FrequencyAndPriorityInfoList', [])
        for item in lte_list:
            earfcn = item.get('earfcn')
            bandwidth = item.get('measurementBandwidth')
            priority = item.get('priority')
            q_rx_lev_min = item.get('qRxLevMinEUTRA')
            
            # Map bandwidth enum to text
            bw_map = {
                'mbw6': '1.4 MHz (6 RBs)',
                'mbw15': '3 MHz (15 RBs)',
                'mbw25': '5 MHz (25 RBs)',
                'mbw50': '10 MHz (50 RBs)',
                'mbw75': '15 MHz (75 RBs)',
                'mbw100': '20 MHz (100 RBs)'
            }
            bw_str = bw_map.get(bandwidth, str(bandwidth))
            
            # Calculate frequency
            # E-UTRA Band 1: EARFCN 0-599
            # E-UTRA Band 3: EARFCN 1200-1949
            # E-UTRA Band 7: EARFCN 2750-3449
            # E-UTRA Band 20: EARFCN 6150-6449
            freq_mhz = 0.0
            band_str = "Unknown"
            if 0 <= earfcn <= 599:
                freq_mhz = 2110.0 + 0.1 * earfcn
                band_str = "Band 1 (2100 MHz)"
            elif 1200 <= earfcn <= 1949:
                freq_mhz = 1805.0 + 0.1 * (earfcn - 1200)
                band_str = "Band 3 (1800 MHz)"
            elif 2750 <= earfcn <= 3449:
                freq_mhz = 2620.0 + 0.1 * (earfcn - 2750)
                band_str = "Band 7 (2600 MHz)"
            elif 6150 <= earfcn <= 6449:
                freq_mhz = 791.0 + 0.1 * (earfcn - 6150)
                band_str = "Band 20 (800 MHz)"
                
            lte_neighbors.append({
                'earfcn': earfcn,
                'band': band_str,
                'freq_mhz': freq_mhz,
                'bw': bw_str,
                'priority': priority,
                'q_rx_lev_min': q_rx_lev_min
            })
            
    if lte_neighbors:
        report.append("| EARFCN | LTE Band | Downlink Frequency | Measurement Bandwidth | Priority | Min Rx Level |")
        report.append("|--------|----------|-------------------|-----------------------|----------|--------------|")
        for item in lte_neighbors:
            report.append(f"| {item['earfcn']:6d} | {item['band']:10s} | {item['freq_mhz']:8.1f} MHz | {item['bw']:21s} | {item['priority']:8d} | {item['q_rx_lev_min']:4d} dBm |")
    else:
        report.append("*No LTE neighbor frequencies found in SIB19.*")
        
    report_content = "\n".join(report)
    print("\n" + report_content)
    
    report_path = "captures/uarfcn_10813_neighbor_report.md"
    with open(report_path, "w") as f:
        f.write(report_content)
    print(f"\n[+] Neighbor report written to {report_path}")

if __name__ == "__main__":
    main()
