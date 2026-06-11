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

import argparse
import os
import sys
import json
import subprocess
import time
import numpy as np
import glob
import wcdma_sync

def uarfcn_to_freq(uarfcn):
    """
    Converts WCDMA UARFCN to DL frequency in MHz.
    Band 1: 10562 - 10838 => 2110.0 + 0.2 * (uarfcn - 10562)
    Band 8: 2937 - 3088   => 925.0 + 0.2 * (uarfcn - 2937)
    """
    if 10562 <= uarfcn <= 10838:
        return 2110.0 + 0.2 * (uarfcn - 10562)
    elif 2937 <= uarfcn <= 3088:
        return 925.0 + 0.2 * (uarfcn - 2937)
    else:
        raise ValueError(f"Geçersiz UARFCN: {uarfcn}")

def run_cmd(cmd, check_exit_code=True):
    """
    Helper to run subprocess commands and print output.
    """
    print(f"\033[94m[CMD] Running: {' '.join(cmd)}\033[0m")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        if check_exit_code:
            print(f"\033[91m[CMD ERROR] Command failed with code {res.returncode}\n{res.stderr}\033[0m")
        return False
    print(res.stdout)
    return True

def scan_cfile(cfile_path, uarfcn=None, no_wiki=False):
    """
    Scans a single complex64 .cfile.
    """
    if not os.path.exists(cfile_path):
        print(f"\033[91m[-] Hata: Dosya bulunamadı: {cfile_path}\033[0m")
        return False
        
    print(f"\033[96m[CELL SEARCH] {cfile_path} analiz ediliyor...\033[0m")
    
    # Try to load metadata
    meta_path = cfile_path + ".json"
    freq_mhz = 0.0
    sample_rate = 7.68e6
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r") as f:
                meta = json.load(f)
            if uarfcn is None:
                uarfcn = meta.get("uarfcn")
            freq_mhz = meta.get("frequency_mhz", 0.0)
            sample_rate = meta.get("sample_rate_hz", 7.68e6)
        except Exception as e:
            print(f"\033[93m[!] Metadata okunamadı: {e}\033[0m")
            
    if uarfcn is not None and freq_mhz == 0.0:
        try:
            freq_mhz = uarfcn_to_freq(uarfcn)
        except ValueError:
            pass

    # Read binary float32 complex values
    try:
        iq_data = np.fromfile(cfile_path, dtype=np.complex64)
    except Exception as e:
        print(f"\033[91m[-] Hata: IQ dosyası okunamadı: {e}\033[0m")
        return False
        
    if len(iq_data) < 76800:
        print("\033[91m[-] Hata: IQ verisi çok kısa!\033[0m")
        return False
        
    # Perform multi-cell search
    try:
        cells = wcdma_sync.perform_multi_cell_search(iq_data, sample_rate=sample_rate)
    except Exception as e:
        print(f"\033[91m[-] Multi-cell search hatası: {e}\033[0m")
        return False
        
    results = {
        "uarfcn": uarfcn,
        "frequency_mhz": freq_mhz,
        "cells": cells
    }
    
    results_path = cfile_path + ".results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\033[92m[+] Cell search sonuçları kaydedildi: {results_path}\033[0m")
    
    # Decode BCH for the top cells (up to 3 cells max to avoid interference decoding issues)
    # Zayıf hücreleri decode etmeden sadece listele
    decoded_any = False
    for idx, cell in enumerate(cells):
        sc = cell["scrambling_code"]
        timing = cell["frame_timing_sample"]
        cfo = cell["frequency_correction_hz"]
        ecno = cell["cpich_ecno_db"]
        
        if idx >= 3:
            print(f"\033[93m[BCH] SC {sc} ({ecno:.1f} dB) zayıf/limit dışı -> Decode edilmedi (Sadece tespit edildi)\033[0m")
            continue
            
        print(f"\033[96m[BCH] SC {sc} ({ecno:.1f} dB) BCH çözümleniyor...\033[0m")
        out_bch_path = cfile_path.replace(".cfile", f"_sc{sc}.bch.json") if cfile_path.endswith(".cfile") else f"{cfile_path}_sc{sc}.bch.json"
        
        # Call wcdma_bch_decode.py
        bch_cmd = [
            sys.executable, "wcdma_bch_decode.py",
            "--input", cfile_path,
            "--sc", str(sc),
            "--timing", str(timing),
            "--cfo", str(cfo),
            "--output", out_bch_path
        ]
        
        success = run_cmd(bch_cmd, check_exit_code=False)
        if success:
            decoded_any = True
            print(f"\033[92m[+] SC {sc} SIB verileri başarıyla çözümlendi -> {out_bch_path}\033[0m")
        else:
            print(f"\033[91m[-] SC {sc} BCH kod çözme başarısız oldu!\033[0m")
            
    return True

def main():
    parser = argparse.ArgumentParser(description="Uçtan Uca Tek Komutlu WCDMA Tarama CLI")
    parser.add_argument("--uarfcn", type=str, help="Tarama yapılacak UARFCN listesi (örn: '10813 2997')")
    parser.add_argument("--input", type=str, help="Yeniden capture yapmadan taranacak ham IQ .cfile dosyası")
    parser.add_argument("--duration", type=float, default=3.0, help="SDR kayıt süresi (saniye, varsayılan: 3.0)")
    parser.add_argument("--gain", type=float, default=40.0, help="SDR RX Kazancı (dB, varsayılan: 40)")
    parser.add_argument("--serial", type=str, help="SDR cihaz seri numarası")
    parser.add_argument("--sdr", type=str, choices=["limesdr", "usrp", "auto"], default="auto", help="Kullanılacak SDR donanımı (varsayılan: auto)")
    parser.add_argument("--no-wiki", action="store_true", help="Obsidian wiki güncellemelerini devre dışı bırak")
    parser.add_argument("--keep-captures", action="store_true", help="Tarama sonrasında ham .cfile dosyalarını silme")
    
    args = parser.parse_args()
    
    if args.input:
        # Clean up old results and BCH files for this input UARFCN
        import re
        m = re.search(r"uarfcn_(\d+)", args.input)
        if m:
            u = int(m.group(1))
            stale_files = glob.glob(f"captures/*{u}*")
            for sf in stale_files:
                if sf != args.input:
                    try:
                        os.remove(sf)
                    except Exception:
                        pass
        else:
            # Fallback to prefix matching if no UARFCN in name
            prefix = args.input.replace(".cfile", "")
            stale_files = glob.glob(prefix + ".cfile*") + glob.glob(prefix + "_*")
            for sf in stale_files:
                if sf != args.input:
                    try:
                        os.remove(sf)
                    except Exception:
                        pass
                    
        # Scan a single existing cfile
        success = scan_cfile(args.input, no_wiki=args.no_wiki)
        if not success:
            sys.exit(1)
            
    elif args.uarfcn:
        # Parse UARFCN list
        uarfcns = []
        for x in args.uarfcn.strip().split():
            try:
                uarfcns.append(int(x))
            except ValueError:
                print(f"\033[91m[-] Hata: Geçersiz UARFCN numarası: {x}\033[0m")
                sys.exit(1)
                
        print(f"\033[95m[*] WCDMA Tarama işlemi başlatılıyor. Taşıyıcılar: {uarfcns}\033[0m")
        
        captured_files = []
        for u in uarfcns:
            # Clean up all old capture, results, metadata, bch, and reports containing this UARFCN
            stale_files = glob.glob(f"captures/*{u}*")
            for sf in stale_files:
                try:
                    os.remove(sf)
                except Exception:
                    pass

            try:
                freq_mhz = uarfcn_to_freq(u)
            except ValueError as e:
                print(f"\033[91m[-] Hata: {e}\033[0m")
                continue
                
            cfile_name = f"captures/uarfcn_{u}.cfile"
            print(f"\n\033[94m[CAPTURE] UARFCN {u} ({freq_mhz:.1f} MHz) kaydediliyor...\033[0m")
            
            capture_cmd = [
                sys.executable, "wcdma_capture.py",
                "--uarfcn", str(u),
                "--duration", str(args.duration),
                "--gain", str(args.gain),
                "--sdr", args.sdr,
                "--output", cfile_name
            ]
            if args.serial:
                capture_cmd.extend(["--serial", args.serial])
                
            # Run capture
            success = run_cmd(capture_cmd)
            if not success:
                print(f"\033[91m[-] UARFCN {u} capture hatası, atlanıyor.\033[0m")
                continue
                
            captured_files.append((u, cfile_name))
            
            # Scan the captured file
            scan_cfile(cfile_name, uarfcn=u, no_wiki=args.no_wiki)
            
            # Optionally clean up the captured .cfile
            if not args.keep_captures:
                print(f"\033[93m[CLEANUP] Ham IQ dosyası siliniyor: {cfile_name}\033[0m")
                try:
                    os.remove(cfile_name)
                except Exception as e:
                    print(f"Silme hatası: {e}")
                    
        if not captured_files:
            print("\033[91m[-] Hiçbir taşıyıcı başarıyla taranamadı!\033[0m")
            sys.exit(1)
            
    else:
        print("\033[91m[-] Hata: --uarfcn veya --input parametrelerinden biri belirtilmelidir!\033[0m")
        parser.print_help()
        sys.exit(1)
        
    # Generate the Unified Scan Report
    print("\n\033[95m[*] Birleşik tarama raporu oluşturuluyor...\033[0m")
    report_cmd = [sys.executable, "wcdma_scan_report.py"]
    if uarfcns:
        report_cmd.extend(["--uarfcns"] + [str(u) for u in uarfcns])
    run_cmd(report_cmd)
    
    # Ingest to Wiki if requested
    if not args.no_wiki:
        print("\n\033[95m[*] Obsidian Wiki entegrasyonu başlatılıyor...\033[0m")
        wiki_cmd = [sys.executable, "wcdma_wiki_helper.py"]
        if uarfcns:
            wiki_cmd.extend(["--uarfcns"] + [str(u) for u in uarfcns])
        run_cmd(wiki_cmd)
        
    print("\n\033[92m[+] Tüm tarama ve entegrasyon işlemleri başarıyla tamamlandı!\033[0m")

if __name__ == "__main__":
    main()
