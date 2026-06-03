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
import argparse
import numpy as np

from wcdma_sync import generate_scrambling_code
from wcdma_pccpch import c_code_256_1, extract_frame_symbols
from wcdma_bch import col_perm_2nd, decode_viterbi, verify_crc16

def deinterleave_2nd_a(soft_bits):
    M = np.zeros((9, 30), dtype=soft_bits.dtype)
    for j in range(30):
        c = col_perm_2nd[j]
        M[:, c] = soft_bits[j*9 : (j+1)*9]
    return M.flatten()

def deinterleave_2nd_b(soft_bits):
    M = np.zeros((9, 30), dtype=soft_bits.dtype)
    for j in range(30):
        M[:, j] = soft_bits[col_perm_2nd[j]*9 : (col_perm_2nd[j]+1)*9]
    return M.flatten()

def deinterleave_1st(f0, f1, reverse_frames=False):
    M = np.zeros((270, 2), dtype=f0.dtype)
    if reverse_frames:
        M[:, 0] = f1
        M[:, 1] = f0
    else:
        M[:, 0] = f0
        M[:, 1] = f1
    return M.flatten()

def bits_to_hex(bits):
    byte_vals = []
    for i in range(0, len(bits), 8):
        byte_bits = bits[i:i+8]
        val = 0
        for b in byte_bits:
            val = (val << 1) | int(b)
        byte_vals.append(val)
    return "".join(f"{v:02X}" for v in byte_vals)

# Known correct receiver configuration resolved from TS 25.211/212/213 and empirical testing
DEFAULT_CONFIG = {
    "conj_mode": True,
    "deint2": "deinterleave_2nd_a",
    "reverse_frames": False,
    "swap_iq": False,
    "sign_i": 1.0,
    "sign_q": 1.0,
    "crc_init": 0x0000,
    "crc_reverse": True
}

def decode_single_config(f0_raw, f1_raw, H0, H1, config):
    """
    Decodes a frame pair with a single configuration.
    """
    conj_mode = config["conj_mode"]
    deint2_func = deinterleave_2nd_a if config["deint2"] == "deinterleave_2nd_a" else deinterleave_2nd_b
    reverse_frames = config["reverse_frames"]
    swap_iq = config["swap_iq"]
    sign_i = config["sign_i"]
    sign_q = config["sign_q"]
    
    f0_eq = f0_raw * (np.conj(H0) if conj_mode else H0)
    f1_eq = f1_raw * (np.conj(H1) if conj_mode else H1)
    
    f0_bits = np.zeros(270, dtype=np.float32)
    f1_bits = np.zeros(270, dtype=np.float32)
    if swap_iq:
        f0_bits[0::2] = sign_i * f0_eq.imag
        f0_bits[1::2] = sign_q * f0_eq.real
        f1_bits[0::2] = sign_i * f1_eq.imag
        f1_bits[1::2] = sign_q * f1_eq.real
    else:
        f0_bits[0::2] = sign_i * f0_eq.real
        f0_bits[1::2] = sign_q * f0_eq.imag
        f1_bits[0::2] = sign_i * f1_eq.real
        f1_bits[1::2] = sign_q * f1_eq.imag
        
    f0_deint = deint2_func(f0_bits)
    f1_deint = deint2_func(f1_bits)
    
    soft_bits = deinterleave_1st(f0_deint, f1_deint, reverse_frames)
    
    decoded = decode_viterbi(soft_bits)
    block_bits = decoded[:262]
    
    data = block_bits[:246]
    rx_crc = block_bits[246:]
    
    reg = config["crc_init"]
    for b in data:
        msb = (reg >> 15) & 1
        reg = (reg << 1) & 0xFFFF
        if msb ^ b:
            reg ^= 0x1021
            
    if config["crc_reverse"]:
        calc_crc = np.array([(reg >> i) & 1 for i in range(16)], dtype=np.int8)
    else:
        calc_crc = np.array([(reg >> (15 - i)) & 1 for i in range(16)], dtype=np.int8)
        
    if np.array_equal(rx_crc, calc_crc):
        return True, block_bits[:246]
        
    return False, None

def run_decode_grid_search(frame0_raw, frame1_raw, H0, H1):
    """
    Tries 64 configurations of:
      - equalization conjugation direction (True/False)
      - QPSK bit mapping (I/Q swap, signs)
      - 2nd deinterleaver type (direct vs inverse)
      - frame combining order (normal vs reversed)
    Returns:
      (success, decoded_bits, config_dict)
    """
    for conj_mode in [True, False]:
        if conj_mode:
            f0_eq = frame0_raw * np.conj(H0)
            f1_eq = frame1_raw * np.conj(H1)
        else:
            f0_eq = frame0_raw * H0
            f1_eq = frame1_raw * H1
            
        for swap_iq in [False, True]:
            for sign_i in [1.0, -1.0]:
                for sign_q in [1.0, -1.0]:
                    f0_bits = np.zeros(270, dtype=np.float32)
                    f1_bits = np.zeros(270, dtype=np.float32)
                    
                    if swap_iq:
                        f0_bits[0::2] = sign_i * f0_eq.imag
                        f0_bits[1::2] = sign_q * f0_eq.real
                        f1_bits[0::2] = sign_i * f1_eq.imag
                        f1_bits[1::2] = sign_q * f1_eq.real
                    else:
                        f0_bits[0::2] = sign_i * f0_eq.real
                        f0_bits[1::2] = sign_q * f0_eq.imag
                        f1_bits[0::2] = sign_i * f1_eq.real
                        f1_bits[1::2] = sign_q * f1_eq.imag
                        
                    for deint2_func in [deinterleave_2nd_a, deinterleave_2nd_b]:
                        f0_deint2 = deint2_func(f0_bits)
                        f1_deint2 = deint2_func(f1_bits)
                        
                        for reverse_frames in [False, True]:
                            soft_bits = deinterleave_1st(f0_deint2, f1_deint2, reverse_frames)
                            
                            decoded = decode_viterbi(soft_bits)
                            block_bits = decoded[:262]
                            
                            success, rx_crc, calc_crc, crc_config = verify_crc16(block_bits)
                            if success:
                                config_dict = {
                                    "conj_mode": conj_mode,
                                    "deint2": "deinterleave_2nd_a" if deint2_func == deinterleave_2nd_a else "deinterleave_2nd_b",
                                    "reverse_frames": reverse_frames,
                                    "swap_iq": swap_iq,
                                    "sign_i": sign_i,
                                    "sign_q": sign_q,
                                    "crc_config": crc_config
                                }
                                return True, block_bits[:246], config_dict
                                
    return False, None, None

def main():
    parser = argparse.ArgumentParser(description="WCDMA BCH Transport Channel Decoder")
    parser.add_argument("--input", type=str, required=True, help="Path to complex64 IQ capture file")
    parser.add_argument("--sc", type=int, default=None, help="Primary Scrambling Code (0-511)")
    parser.add_argument("--timing", type=int, default=None, help="Frame start timing in samples")
    parser.add_argument("--cfo", type=float, default=None, help="CFO correction frequency in Hz")
    parser.add_argument("--force-search", action="store_true", help="Force full grid search instead of using default configuration")
    parser.add_argument("--output", type=str, default=None, help="Path to write decoded BCH blocks JSON")
    args = parser.parse_args()
    
    sc = args.sc
    timing = args.timing
    cfo = args.cfo
    
    if sc is None or timing is None or cfo is None:
        json_path = args.input + ".results.json"
        if os.path.exists(json_path):
            print(f"Reading parameters from metadata file: {json_path}")
            with open(json_path, 'r') as f:
                meta = json.load(f)
            if "cells" in meta and len(meta["cells"]) > 0:
                cell = meta["cells"][0]
                if sc is None: sc = cell["scrambling_code"]
                if timing is None: timing = cell["frame_timing_sample"]
                if cfo is None: cfo = cell["frequency_correction_hz"]
            else:
                print("Error: No cell information found in results JSON.")
                sys.exit(1)
        else:
            print(f"Error: Missing parameters and no results JSON found at {json_path}")
            sys.exit(1)
            
    print(f"Using parameters: SC={sc}, Frame Timing={timing}, CFO={cfo:.1f} Hz")
    
    print(f"Loading IQ data from {args.input}...")
    iq_data = np.fromfile(args.input, dtype=np.complex64)
    print(f"Loaded {len(iq_data)} samples ({len(iq_data)/7.68e6:.3f} seconds)")
    
    num_frames = (len(iq_data) - timing) // 76800
    print(f"Extracting {num_frames} frames from capture...")
    
    frame_pccpch_raw = []
    frame_H_all = []
    
    c_code_256_1_upsampled = np.repeat(c_code_256_1, 2)
    
    print("Performing digital downconversion & frequency correction...")
    t = np.arange(len(iq_data)) / 7.68e6
    iq_rotated = iq_data * np.exp(-1j * 2 * np.pi * cfo * t)
    
    gold_seq = generate_scrambling_code(sc, length=38400)
    gold_upsampled = np.repeat(gold_seq, 2)
    
    # Timing tracking loop initialization
    current_timing = timing
    print("Extracting frames with active Timing Tracking Loop (TTL)...")
    
    for f in range(num_frames):
        best_energy = -1
        best_delay = 0
        best_H_slots = None
        best_pccpch_raw = None
        
        # Search window: -8 to +8 samples around tracked timing
        for delay in range(-8, 9):
            start_idx = current_timing + delay
            if start_idx < 0 or start_idx + 76800 > len(iq_rotated):
                continue
            frame_iq = iq_rotated[start_idx : start_idx + 76800]
            descrambled = frame_iq * gold_upsampled.conj()
            
            pccpch_raw = []
            H_slots = []
            energy = 0.0
            
            for slot_idx in range(15):
                slot_seg = descrambled[slot_idx * 5120 : (slot_idx + 1) * 5120]
                
                slot_cpich = []
                for n in range(10):
                    slot_cpich.append(np.sum(slot_seg[n * 512 : (n + 1) * 512]))
                H = np.mean(slot_cpich) / (1.0 + 1.0j)
                H_slots.append(H)
                energy += np.sum(np.abs(slot_cpich)**2)
                
                for m in range(9):
                    sym_seg = slot_seg[512 + m * 512 : 512 + (m + 1) * 512]
                    sym_val = np.sum(sym_seg * c_code_256_1_upsampled)
                    pccpch_raw.append(sym_val)
                    
            if energy > best_energy:
                best_energy = energy
                best_delay = delay
                best_H_slots = H_slots
                best_pccpch_raw = pccpch_raw
                
        # Update tracked timing
        current_timing += best_delay
        timing_offset = current_timing - (timing + f * 76800)
        
        frame_pccpch_raw.append(np.array(best_pccpch_raw))
        H_symbols = np.repeat(best_H_slots, 9)
        frame_H_all.append(H_symbols)
        
        # Advance by 1 frame
        current_timing += 76800
        
    print("Frame extraction and despreading complete. Decoding...")
    
    decoded_blocks = {}
    success_count = 0
    
    if not args.force_search:
        print("Decoding using standard WCDMA configuration...")
        for f in range(num_frames - 1):
            f0_raw = frame_pccpch_raw[f]
            f1_raw = frame_pccpch_raw[f+1]
            H0 = frame_H_all[f]
            H1 = frame_H_all[f+1]
            
            success, data_bits = decode_single_config(f0_raw, f1_raw, H0, H1, DEFAULT_CONFIG)
            if success:
                hex_str = bits_to_hex(data_bits)
                print(f"[+] Decoded block at frame pair ({f}, {f+1}) SFN-like counter: {hex_str[2:4]} (Hex: {hex_str[:16]}...)")
                success_count += 1
                decoded_blocks[f] = {
                    "hex": hex_str,
                    "config": DEFAULT_CONFIG
                }
                
    if success_count == 0 or args.force_search:
        if not args.force_search:
            print("\n[-] Standard configuration failed. Falling back to full grid search...")
        else:
            print("\n[!] Forcing full grid search over 64 combinations...")
            
        decoded_blocks = {}
        success_count = 0
        
        for f in range(num_frames - 1):
            f0_raw = frame_pccpch_raw[f]
            f1_raw = frame_pccpch_raw[f+1]
            H0 = frame_H_all[f]
            H1 = frame_H_all[f+1]
            
            success, data_bits, config = run_decode_grid_search(f0_raw, f1_raw, H0, H1)
            if success:
                hex_str = bits_to_hex(data_bits)
                print(f"[+] SUCCESS! Frame pair ({f}, {f+1}) decoded with config: {config}")
                print(f"    Hex: {hex_str}")
                success_count += 1
                decoded_blocks[f] = {
                    "hex": hex_str,
                    "config": config
                }
                
    if success_count > 0:
        print(f"\n[+] Decoded {success_count} BCH transport blocks successfully!")
        out_json_path = args.output if args.output is not None else args.input + ".bch.json"
        with open(out_json_path, 'w') as f:
            json.dump(decoded_blocks, f, indent=2)
        print(f"Results written to {out_json_path}")
    else:
        print("\n[-] BCH decoding failed. No blocks passed the CRC16 check.")
        sys.exit(1)

if __name__ == "__main__":
    main()
