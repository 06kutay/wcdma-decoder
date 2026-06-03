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

# 2nd Deinterleaver Column Permutation Pattern (TS 25.212 Table 7)
col_perm_2nd = [0, 20, 10, 5, 15, 25, 3, 13, 23, 8, 18, 28, 1, 11, 21, 6, 16, 26, 4, 14, 24, 19, 9, 29, 12, 2, 7, 22, 27, 17]

def deinterleave_2nd(soft_bits):
    """
    Intra-frame deinterleaving for one 10ms radio frame (270 bits).
    Matrix: 9 rows, 30 columns.
    """
    assert len(soft_bits) == 270, f"Expected 270 bits, got {len(soft_bits)}"
    M = np.zeros((9, 30), dtype=soft_bits.dtype)
    for j in range(30):
        c = col_perm_2nd[j]
        M[:, c] = soft_bits[j*9 : (j+1)*9]
    return M.flatten()

def deinterleave_1st_tti20(frame0_bits, frame1_bits):
    """
    Inter-frame deinterleaving for BCH with TTI = 20ms (2 frames).
    Matrix: 270 rows, 2 columns.
    Permutation pattern for TTI=20ms: [0, 1]
    """
    assert len(frame0_bits) == 270 and len(frame1_bits) == 270
    M = np.zeros((270, 2), dtype=frame0_bits.dtype)
    M[:, 0] = frame0_bits
    M[:, 1] = frame1_bits
    return M.flatten()

# Precompute tables for Viterbi Decoder
NEXT_STATES = np.zeros((256, 2), dtype=np.int16)
OUTPUTS = np.zeros((256, 2, 2), dtype=np.int8)
PREV_STATES = np.zeros((256, 2), dtype=np.int16)

for s in range(256):
    for u in [0, 1]:
        ns = (u << 7) | (s >> 1)
        NEXT_STATES[s, u] = ns
        
        # Polynomials:
        # G0 = 561 octal = 101110001 binary
        # G1 = 753 octal = 111101011 binary
        x_i_1 = (s >> 7) & 1
        x_i_2 = (s >> 6) & 1
        x_i_3 = (s >> 5) & 1
        x_i_4 = (s >> 4) & 1
        x_i_5 = (s >> 3) & 1
        x_i_6 = (s >> 2) & 1
        x_i_7 = (s >> 1) & 1
        x_i_8 = s & 1
        
        v0 = u ^ x_i_2 ^ x_i_3 ^ x_i_4 ^ x_i_8
        v1 = u ^ x_i_1 ^ x_i_2 ^ x_i_3 ^ x_i_5 ^ x_i_7 ^ x_i_8
        
        OUTPUTS[s, u] = [v0, v1]

for ns in range(256):
    PREV_STATES[ns, 0] = (ns & 0x7F) << 1
    PREV_STATES[ns, 1] = ((ns & 0x7F) << 1) | 1

def decode_viterbi(soft_bits):
    """
    256-state Viterbi decoder for WCDMA Rate 1/2 Convolutional Code (K=9).
    Generator polynomials: G0 = 561 (octal), G1 = 753 (octal).
    Input:
        soft_bits: numpy array of floats (real, imag, real, imag, ...)
                   where positive maps to bit 0, negative maps to bit 1.
    Returns:
        decoded_bits: numpy array of 270 bits (including tail bits)
    """
    n_symbols = len(soft_bits) // 2
    
    # Path metrics initialized to infinity except state 0
    path_metrics = np.full(256, np.inf)
    path_metrics[0] = 0.0
    
    tb_paths = np.zeros((n_symbols, 256), dtype=np.int16)
    
    for k in range(n_symbols):
        r0 = soft_bits[2*k]
        r1 = soft_bits[2*k+1]
        
        new_path_metrics = np.full(256, np.inf)
        
        for ns in range(256):
            u = ns >> 7
            ps0 = PREV_STATES[ns, 0]
            ps1 = PREV_STATES[ns, 1]
            
            # Outputs for transition from ps0 -> ns
            v0_0, v0_1 = OUTPUTS[ps0, u]
            # Outputs for transition from ps1 -> ns
            v1_0, v1_1 = OUTPUTS[ps1, u]
            
            # Map expected binary [0, 1] to BPSK [+1, -1]
            exp0_0 = 1.0 - 2.0 * v0_0
            exp0_1 = 1.0 - 2.0 * v0_1
            exp1_0 = 1.0 - 2.0 * v1_0
            exp1_1 = 1.0 - 2.0 * v1_1
            
            m0 = path_metrics[ps0] + (r0 - exp0_0)**2 + (r1 - exp0_1)**2
            m1 = path_metrics[ps1] + (r0 - exp1_0)**2 + (r1 - exp1_1)**2
            
            if m0 < m1:
                new_path_metrics[ns] = m0
                tb_paths[k, ns] = ps0
            else:
                new_path_metrics[ns] = m1
                tb_paths[k, ns] = ps1
                
        path_metrics = new_path_metrics
        
    # Traceback from state 0 (encoder is terminated to state 0 by 8 tail bits)
    best_state = 0
    decoded_bits = []
    
    for k in range(n_symbols - 1, -1, -1):
        prev_state = tb_paths[k, best_state]
        u = best_state >> 7
        decoded_bits.append(u)
        best_state = prev_state
        
    decoded_bits.reverse()
    return np.array(decoded_bits, dtype=np.int8)

def verify_crc16(bits):
    """
    Robust CRC16 check for the 262-bit block (246 data bits + 16 CRC bits).
    Polynomial: D^16 + D^12 + D^5 + 1 (0x1021).
    Tests both:
      - Initial state: 0x0000 and 0xFFFF
      - CRC bit order: direct (MSB-first) and reversed (LSB-first)
    Returns:
      (success, rx_crc, expected_crc, config_str)
    """
    assert len(bits) == 262, f"Expected 262 bits, got {len(bits)}"
    data = bits[:246]
    rx_crc = bits[246:]
    
    # Try all configurations
    for init_val in [0x0000, 0xFFFF]:
        for reverse_out in [True, False]:
            reg = init_val
            for b in data:
                msb = (reg >> 15) & 1
                reg = (reg << 1) & 0xFFFF
                if msb ^ b:
                    reg ^= 0x1021
            
            if reverse_out:
                calc_crc = np.array([(reg >> i) & 1 for i in range(16)], dtype=np.int8)
            else:
                calc_crc = np.array([(reg >> (15 - i)) & 1 for i in range(16)], dtype=np.int8)
                
            if np.array_equal(rx_crc, calc_crc):
                config_str = f"init={hex(init_val)}, reverse={reverse_out}"
                return True, rx_crc, calc_crc, config_str
                
    # If no configuration matches, calculate with standard init=0, reverse=True (TS 25.212 spec)
    reg = 0
    for b in data:
        msb = (reg >> 15) & 1
        reg = (reg << 1) & 0xFFFF
        if msb ^ b:
            reg ^= 0x1021
    calc_crc_default = np.array([(reg >> i) & 1 for i in range(16)], dtype=np.int8)
    return False, rx_crc, calc_crc_default, "failed"
