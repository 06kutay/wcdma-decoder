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
import numpy as np
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import wcdma_sync

def test_hadamard_orthogonality():
    print("Testing Hadamard orthogonality...")
    H = wcdma_sync.generate_hadamard_matrix(8)
    assert H.shape == (256, 256), "Hadamard matrix size must be 256x256"
    
    # Check that rows are orthogonal
    # H_i . H_j = 0 for i != j
    # H_i . H_i = 256
    row0 = H[0].astype(np.int32)
    row1 = H[1].astype(np.int32)
    dot_product = np.dot(row0, row1)
    assert dot_product == 0, f"Hadamard rows must be orthogonal, got {dot_product}"
    
    dot_self = np.dot(row0, row0)
    assert dot_self == 256, f"Hadamard row self product must be 256, got {dot_self}"
    print("  -> Hadamard orthogonality test PASSED!")

def test_psc_properties():
    print("Testing PSC properties...")
    C_psc = wcdma_sync.generate_psc()
    assert C_psc.shape == (256,), "PSC must be 256 elements"
    
    # Check that values are ±1 ± j
    for val in C_psc[:5]:
        assert abs(val.real) == 1.0 and abs(val.imag) == 1.0, f"PSC chips must be (1+j) or (-1-j) modulated, got {val}"
        
    # Check correlation properties (autocorrelation peak at lag 0)
    auto_corr = np.correlate(C_psc, C_psc, mode='full')
    peak_idx = len(C_psc) - 1
    assert np.argmax(np.abs(auto_corr)) == peak_idx, "Autocorrelation peak must be at lag 0"
    print("  -> PSC properties test PASSED!")

def test_ssc_orthogonal():
    print("Testing SSC properties...")
    ssc1 = wcdma_sync.generate_ssc(1)
    ssc2 = wcdma_sync.generate_ssc(2)
    assert ssc1.shape == (256,), "SSC must be 256 elements"
    
    # SSCs should be orthogonal
    dot_prod = np.dot(ssc1, ssc2.conj())
    assert np.abs(dot_prod) < 1e-5, f"SSCs must be orthogonal, got dot product: {dot_prod}"
    print("  -> SSC orthogonality test PASSED!")

def test_gold_code():
    print("Testing Gold code generation...")
    gold0 = wcdma_sync.generate_scrambling_code(0, length=100)
    assert gold0.shape == (100,), "Gold sequence length should match parameter"
    
    # Real and imaginary components should be ±1
    for val in gold0[:5]:
        assert abs(val.real) == 1.0 and abs(val.imag) == 1.0, f"Gold code symbols must be QPSK (real/imag in ±1), got {val}"
    print("  -> Gold code test PASSED!")

if __name__ == "__main__":
    test_hadamard_orthogonality()
    test_psc_properties()
    test_ssc_orthogonal()
    test_gold_code()
    print("\nALL WCDMA GENERATOR TESTS PASSED SUCCESSFULLY!")
