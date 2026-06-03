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

import json
import asn1tools
import sys

def get_sib_type_by_sfn(sfn_prime):
    m = sfn_prime % 32
    if 2 <= m <= 9:
        return 'systemInformationBlockType5'
    elif 11 <= m <= 13:
        return 'extensionType'  # SIB19 is transmitted as extensionType
    elif 14 <= m <= 30:
        return 'systemInformationBlockType11'
    return 'unknown'

def concatenate_bits(segments):
    """
    Concatenates segments which are lists/tuples of (bytes, bit_length).
    Returns a bytes object.
    """
    all_bits = ""
    for data, bit_length in segments:
        bits = "".join(f"{b:08b}" for b in data)[:bit_length]
        all_bits += bits
    
    byte_list = []
    for i in range(0, len(all_bits), 8):
        chunk = all_bits[i:i+8]
        if len(chunk) < 8:
            chunk = chunk + '0' * (8 - len(chunk))
        byte_list.append(int(chunk, 2))
    return bytes(byte_list)

def assemble_sibs_from_json(bch_json_path, db):
    """
    Reads BCH transport blocks from JSON, reassembles segmented SIBs,
    and returns a dictionary of successfully decoded SIB structures.
    """
    with open(bch_json_path, "r") as f:
        bch_data = json.load(f)

    decoded_sibs = {}
    
    # Store segments for each segmented SIB type
    # Structure: { sib_type: { segment_index: (bytes, bit_length) } }
    sib_segments = {
        'systemInformationBlockType5': {},
        'extensionType': {},  # SIB19
        'systemInformationBlockType11': {}
    }
    
    # Expected segment counts
    expected_counts = {
        'systemInformationBlockType5': 3,
        'extensionType': 2,
        'systemInformationBlockType11': 11
    }

    # First pass: decode complete SIBs and collect segments
    for frame_idx, info in sorted(bch_data.items(), key=lambda x: int(x[0])):
        hex_str = info["hex"]
        raw_bytes = bytes.fromhex(hex_str)
        try:
            decoded = db.decode('SystemInformation-BCH', raw_bytes)
            payload_type = decoded['payload'][0]
            payload_val = decoded['payload'][1]
            sfn_prime = decoded['sfn-Prime']
            
            if not payload_val:
                continue
                
            if payload_type == 'completeSIB-List':
                # completeSIB-List contains multiple complete SIBs
                for item in payload_val:
                    sib_type = item['sib-Type']
                    sib_data_val = item.get('sib-Data-fixed') or item.get('sib-Data-variable')
                    if not sib_data_val:
                        continue
                    sib_data, bit_len = sib_data_val
                    
                    # Decode complete SIB immediately
                    try:
                        if sib_type == 'masterInformationBlock':
                            decoded_sibs['MIB'] = db.decode('MasterInformationBlock', sib_data)
                        elif sib_type == 'systemInformationBlockType1':
                            decoded_sibs['SIB1'] = db.decode('SysInfoType1', sib_data)
                        elif sib_type == 'systemInformationBlockType2':
                            decoded_sibs['SIB2'] = db.decode('SysInfoType2', sib_data)
                        elif sib_type == 'systemInformationBlockType3':
                            decoded_sibs['SIB3'] = db.decode('SysInfoType3', sib_data)
                        elif sib_type == 'systemInformationBlockType4':
                            decoded_sibs['SIB4'] = db.decode('SysInfoType4', sib_data)
                        elif sib_type == 'systemInformationBlockType7':
                            decoded_sibs['SIB7'] = db.decode('SysInfoType7', sib_data)
                        elif sib_type == 'systemInformationBlockTypeSB1':
                            decoded_sibs['SB1'] = db.decode('SysInfoTypeSB1', sib_data)
                    except Exception as e:
                        print(f"Error decoding complete SIB {sib_type} in frame {frame_idx}: {e}")
                        
            elif payload_type in ['firstSegment', 'subsequentSegment', 'lastSegmentShort', 'lastSegmentLong']:
                # Determine SIB type of the segment
                sib_type = get_sib_type_by_sfn(sfn_prime)
                if sib_type == 'unknown':
                    continue
                    
                seg_idx = None
                bit_data = None
                
                if payload_type == 'firstSegment':
                    seg_idx = 0
                    bit_data = payload_val['sib-Data-fixed']
                    expected_counts[sib_type] = payload_val['seg-Count']
                elif payload_type == 'subsequentSegment':
                    seg_idx = payload_val['segmentIndex']
                    bit_data = payload_val['sib-Data-fixed']
                elif payload_type in ['lastSegmentShort', 'lastSegmentLong']:
                    seg_idx = payload_val['segmentIndex']
                    bit_data = payload_val['sib-Data-variable']
                    
                if seg_idx is not None and bit_data is not None:
                    sib_segments[sib_type][seg_idx] = bit_data
                    
        except Exception as e:
            # print(f"Warning: Failed to decode BCH payload in frame {frame_idx}: {e}")
            continue

    # Second pass: Reassemble and decode segmented SIBs
    for sib_type, segments in sib_segments.items():
        count = expected_counts[sib_type]
        missing = [idx for idx in range(count) if idx not in segments]
        
        friendly_name = {
            'systemInformationBlockType5': 'SIB5',
            'extensionType': 'SIB19',
            'systemInformationBlockType11': 'SIB11'
        }[sib_type]
        
        if not missing:
            print(f"[+] All {count} segments present for {friendly_name}. Reassembling...")
            ordered_segments = [segments[idx] for idx in range(count)]
            assembled_bytes = concatenate_bits(ordered_segments)
            
            try:
                if sib_type == 'systemInformationBlockType5':
                    decoded_sibs['SIB5'] = db.decode('SysInfoType5', assembled_bytes)
                elif sib_type == 'extensionType':
                    decoded_sibs['SIB19'] = db.decode('SysInfoType19', assembled_bytes)
                elif sib_type == 'systemInformationBlockType11':
                    decoded_sibs['SIB11'] = db.decode('SysInfoType11', assembled_bytes)
                print(f"[+] Successfully decoded {friendly_name}!")
            except Exception as e:
                print(f"[-] Failed to decode reassembled {friendly_name}: {e}")
        else:
            print(f"[-] {friendly_name} is incomplete: missing segments {missing}")

    return decoded_sibs
