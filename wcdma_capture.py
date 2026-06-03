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
import time
import os
import json
import numpy as np

def uarfcn_to_freq(uarfcn):
    """
    Converts 3GPP UARFCN to DL Frequency in MHz.
    Band 1: 10562 - 10838 => 2110.0 + 0.2 * (uarfcn - 10562)
    Band 8: 2937 - 3088   => 925.0 + 0.2 * (uarfcn - 2937)
    """
    if 10562 <= uarfcn <= 10838:
        # Band 1 DL
        return 2110.0 + 0.2 * (uarfcn - 10562)
    elif 2937 <= uarfcn <= 3088:
        # Band 8 DL
        return 925.0 + 0.2 * (uarfcn - 2937)
    else:
        # Custom mapping fallback
        raise ValueError(f"Geçersiz UARFCN: {uarfcn}. Desteklenen bantlar: Band 1 (10562-10838) ve Band 8 (2937-3088)")

def main():
    parser = argparse.ArgumentParser(description="LimeSDR Mini WCDMA IQ Capture Script")
    parser.add_argument("--uarfcn", type=int, help="3GPP UARFCN Kanal Numarası (Band 1 veya Band 8)")
    parser.add_argument("--freq", type=float, help="Doğrudan hedef frekans (MHz)")
    parser.add_argument("--duration", type=float, default=0.5, help="Capture süresi (saniye, varsayılan: 0.5)")
    parser.add_argument("--gain", type=float, default=40.0, help="SDR RX Kazancı (dB, varsayılan: 40)")
    parser.add_argument("--samp-rate", type=float, default=7.68e6, help="Örnekleme hızı (Hz, varsayılan: 7.68e6)")
    parser.add_argument("--serial", type=str, help="LimeSDR Mini cihaz seri numarası (belirtilmezse ilk aygıt seçilir)")
    parser.add_argument("--output", type=str, required=True, help="Çıktı .cfile yolu (örn: captures/uarfcn_2997.cfile)")
    
    args = parser.parse_args()
    
    # 1. Determine frequency
    if args.freq is not None:
        freq_mhz = args.freq
        print(f"Frekans doğrudan belirtildi: {freq_mhz} MHz")
    elif args.uarfcn is not None:
        try:
            freq_mhz = uarfcn_to_freq(args.uarfcn)
            print(f"UARFCN {args.uarfcn} -> Hesaplanan Frekans: {freq_mhz} MHz")
        except ValueError as e:
            print(f"Hata: {e}")
            return
    else:
        print("Hata: --uarfcn veya --freq parametrelerinden en az biri belirtilmelidir!")
        return

    freq_hz = freq_mhz * 1e6
    
    # 2. Determine RF Port / Antenna
    if freq_mhz >= 1500.0:
        antenna = "LNAH"
    else:
        antenna = "LNAW"
    print(f"RF Port / Anten seçimi: {antenna} (Frekans: {freq_mhz} MHz)")

    # 3. Initialize SoapySDR
    try:
        import SoapySDR
    except ImportError:
        print("Hata: SoapySDR modülü import edilemedi! Sanal ortam yapılandırmasını kontrol edin.")
        return

    # Check connected devices
    results = SoapySDR.Device.enumerate()
    if not results:
        print("Hata: Hiçbir SDR cihazı bulunamadı!")
        return

    # Device selection arguments
    args_dict = {}
    if args.serial:
        args_dict["serial"] = args.serial
        print(f"Seçilen seri numarası: {args.serial}")
    else:
        # Select first available device
        print(f"Bulunan ilk cihaz seçiliyor: {results[0]['label']}")
        args_dict = results[0]

    # Try to open SDR device
    sdr = None
    try:
        sdr = SoapySDR.Device(args_dict)
    except Exception as e:
        print(f"\nHata: LimeSDR aygıtı açılamadı! Aygıt başka bir işlem tarafından kilitlenmiş veya meşgul olabilir.")
        print(f"Sistem Hatası: {e}")
        return

    try:
        # 4. Configure SDR Channel Parameters
        channel = 0
        sdr.setSampleRate(SoapySDR.SOAPY_SDR_RX, channel, args.samp_rate)
        sdr.setFrequency(SoapySDR.SOAPY_SDR_RX, channel, freq_hz)
        sdr.setGain(SoapySDR.SOAPY_SDR_RX, channel, args.gain)
        sdr.setAntenna(SoapySDR.SOAPY_SDR_RX, channel, antenna)
        
        # Enable automatic DC offset calibration if supported
        try:
            sdr.setDCOffsetMode(SoapySDR.SOAPY_SDR_RX, channel, True)
        except Exception:
            pass

        print(f"SDR Ayarları uygulandı:")
        print(f"  -> Sample Rate: {sdr.getSampleRate(SoapySDR.SOAPY_SDR_RX, channel) / 1e6:.3f} Msps")
        print(f"  -> Center Freq: {sdr.getFrequency(SoapySDR.SOAPY_SDR_RX, channel) / 1e6:.3f} MHz")
        print(f"  -> RX Gain: {sdr.getGain(SoapySDR.SOAPY_SDR_RX, channel):.1f} dB")
        print(f"  -> Antenna Port: {sdr.getAntenna(SoapySDR.SOAPY_SDR_RX, channel)}")

        # 5. Prepare Buffer & Stream
        # Calculate samples to capture
        num_samples = int(args.samp_rate * args.duration)
        print(f"Toplam capture süresi: {args.duration} sn, Örnek sayısı: {num_samples}")

        # Setup RX stream
        rx_stream = sdr.setupStream(SoapySDR.SOAPY_SDR_RX, SoapySDR.SOAPY_SDR_CF32, [channel])
        
        # Flush output directory
        out_dir = os.path.dirname(args.output)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)

        # Allocate memory for storing captured data
        captured_data = np.zeros(num_samples, dtype=np.complex64)
        
        # Buffer size matching hardware MTU
        mtu = sdr.getStreamMTU(rx_stream)
        buff = np.zeros(mtu, dtype=np.complex64)

        # Start streaming
        sdr.activateStream(rx_stream)
        print("Alıcı akışı aktif edildi, IQ kaydı yapılıyor...")

        # Capture loop
        samples_received = 0
        overruns = 0
        
        start_time = time.time()
        
        while samples_received < num_samples:
            # Calculate remaining samples to capture
            rem = num_samples - samples_received
            read_size = min(mtu, rem)
            
            # Read from stream
            sr = sdr.readStream(rx_stream, [buff], read_size, timeoutUs=1000000)
            
            if sr.ret < 0:
                # Handle error
                if sr.ret == SoapySDR.SOAPY_SDR_OVERFLOW:
                    # Overflow occurred (buffer overrun), continue reading but count it
                    overruns += 1
                    continue
                else:
                    print(f"Hata: SDR akışı okuma hatası! Kod: {sr.ret}")
                    break
            
            # Copy to global buffer
            captured_data[samples_received : samples_received + sr.ret] = buff[:sr.ret]
            samples_received += sr.ret

        # Stop streaming
        sdr.deactivateStream(rx_stream)
        sdr.closeStream(rx_stream)
        
        capture_duration = time.time() - start_time
        print(f"Kayıt tamamlandı. Gerçekleşen Süre: {capture_duration:.3f} saniye")
        print(f"  -> Alınan örnek sayısı: {samples_received}")
        print(f"  -> Karşılaşılan Buffer Overrun sayısı: {overruns}")

        # 6. Write complex64 binary .cfile
        print(f"IQ verisi ikili (binary) formatta yazılıyor: {args.output}")
        captured_data.tofile(args.output)
        
        # 7. Write metadata JSON
        meta_path = args.output + ".json"
        metadata = {
            "uarfcn": args.uarfcn,
            "frequency_mhz": freq_mhz,
            "sample_rate_hz": args.samp_rate,
            "duration_seconds": args.duration,
            "gain_db": args.gain,
            "antenna_port": antenna,
            "samples_captured": samples_received,
            "overruns": overruns,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "sdr_serial": dict(sdr.getHardwareInfo()).get("serial", "unknown"),
            "sdr_label": dict(sdr.getHardwareInfo()).get("label", "unknown")
        }
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)
        print(f"Metadata JSON dosyası kaydedildi: {meta_path}")

    finally:
        if sdr is not None:
            # Clean up device allocation
            del sdr
            print("LimeSDR Mini bağlantısı güvenli bir şekilde kapatıldı.")

if __name__ == "__main__":
    main()
