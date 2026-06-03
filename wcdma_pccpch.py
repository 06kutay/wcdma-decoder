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

import numpy as np
from wcdma_sync import generate_scrambling_code

# OVSF codes definitions
# Cch,256,0 is all ones
c_code_256_0 = np.ones(256, dtype=np.int8)

# Cch,256,1 is 128 ones followed by 128 minus ones
c_code_256_1 = np.concatenate([np.ones(128, dtype=np.int8), -np.ones(128, dtype=np.int8)])

def extract_frame_symbols(iq_data, resolved_sc, frame_start_idx, frequency_correction_hz, sample_rate=7.68e6):
    """
    Extracts, descrambles, and despreads one WCDMA frame (10ms = 76800 samples) starting at frame_start_idx.
    Applies coherent CPICH-based channel estimation and equalization.
    Returns:
        pccpch_symbols: np.array of 135 complex symbols (9 symbols per slot * 15 slots)
        cpich_symbols: np.array of 150 complex symbols (10 symbols per slot * 15 slots)
    """
    # 1. Apply carrier frequency correction to the entire frame duration
    t = (frame_start_idx + np.arange(76800)) / sample_rate
    correction = np.exp(-1j * 2 * np.pi * frequency_correction_hz * t)
    frame_iq = iq_data[frame_start_idx : frame_start_idx + 76800] * correction
    
    # 2. Generate and upsample scrambling code (38400 chips => 76800 samples)
    gold_seq = generate_scrambling_code(resolved_sc, length=38400)
    gold_upsampled = np.repeat(gold_seq, 2)
    
    # 3. Descramble the frame
    descrambled = frame_iq * gold_upsampled.conj()
    
    # 4. Process slot-by-slot (15 slots)
    pccpch_symbols = []
    cpich_symbols_all = []
    
    # Pre-upsample P-CCPCH channelization code (SF=256 => 512 samples)
    c_code_256_1_upsampled = np.repeat(c_code_256_1, 2)
    
    for slot_idx in range(15):
        slot_seg = descrambled[slot_idx * 5120 : (slot_idx + 1) * 5120]
        
        # A. CPICH despreading (SF=256, code 0) - 10 symbols per slot
        slot_cpich = []
        for n in range(10):
            sym_seg = slot_seg[n * 512 : (n + 1) * 512]
            # Since Cch,256,0 is all 1s, we just sum
            slot_cpich.append(np.sum(sym_seg))
        
        slot_cpich = np.array(slot_cpich, dtype=np.complex128)
        cpich_symbols_all.extend(slot_cpich)
        
        # B. Channel Estimation from CPICH
        # CPICH pilot symbols are all constant A * (1 + j)
        # So we divide by (1 + 1j) to get the complex channel estimate H
        H = np.mean(slot_cpich) / (1.0 + 1.0j)
        
        # C. P-CCPCH despreading (SF=256, code 1) - 9 symbols per slot
        # Skip the first symbol (first 256 chips = 512 samples) which is SCH
        slot_pccpch_raw = []
        for m in range(9):
            sym_seg = slot_seg[512 + m * 512 : 512 + (m + 1) * 512]
            sym_val = np.sum(sym_seg * c_code_256_1_upsampled)
            slot_pccpch_raw.append(sym_val)
            
        slot_pccpch_raw = np.array(slot_pccpch_raw, dtype=np.complex128)
        
        # D. Coherent equalization
        # Coherent equalization rotates the raw symbols using H*
        # We also normalise by |H|^2 to scale, but for Viterbi soft bits, 
        # multiplying by conj(H) is optimal as it implements MRC weighting.
        # We can implement configurable conj(H) direction as suggested by user.
        slot_pccpch_equalized = slot_pccpch_raw * np.conj(H)
        pccpch_symbols.extend(slot_pccpch_equalized)
        
    return np.array(pccpch_symbols), np.array(cpich_symbols_all)
