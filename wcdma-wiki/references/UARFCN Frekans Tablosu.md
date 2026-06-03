---
title: UARFCN Frekans Tablosu
category: references
tags: [wcdma, references, uarfcn, frequency, turkey, operators]
aliases: [UARFCN Tablosu, Frekans Tablosu]
sources: [CLAUDE.md]
summary: Türkiye WCDMA (3G) şebekelerinde kullanılan UARFCN kodları, downlink/uplink frekansları ve operatör dağılım referans tablosu.
provenance:
  extracted: 0.98
  inferred: 0.02
  ambiguous: 0.00
base_confidence: 0.95
lifecycle: draft
lifecycle_changed: 2026-06-02
tier: supporting
created: 2026-06-02T16:16:00Z
updated: 2026-06-02T16:16:00Z
---

# UARFCN Frekans Tablosu (Türkiye Referansı)

Bu referans sayfası, Türkiye'de WCDMA (3G) lisansına sahip üç büyük GSM operatörünün (Turkcell, Vodafone, Türk Telekom) Band 1 (2100 MHz) ve Band 8 (900 MHz) frekanslarındaki nominal yayın parametrelerini içerir.

Bu tablo, SDR tarayıcısı programlanırken merkez frekans hedeflerini girmek ve yakalanan komşu hücre listelerinde çıkan UARFCN değerlerini anında operatör adına dönüştürmek için referans olarak kullanılacaktır.

---

## 3GPP Standart UARFCN Frekans Hesaplama Kuralları
* **Band 1 Downlink:** $F_{DL} \text{ (MHz)} = 0.2 \times N_{DL} \quad (10562 \le N_{DL} \le 10838)$
* **Band 8 Downlink:** $F_{DL} \text{ (MHz)} = 340.0 + 0.2 \times N_{DL} \quad (2937 \le N_{DL} \le 3088)$

---

## Operatör UARFCN ve Frekans Eşleştirme Tablosu

| Operatör | Frekans Bandı | Downlink UARFCN | Downlink Frekansı | Uplink UARFCN | Uplink Frekansı | Açıklama / Rolü |
|---|---|---|---|---|---|---|
| **Türk Telekom** | Band 1 (2100) | **10562** | 2112.4 MHz | 9612 | 1922.4 MHz | TT 3G Taşıyıcı 1 (Ana) |
| **Türk Telekom** | Band 1 (2100) | **10587** | 2117.4 MHz | 9637 | 1927.4 MHz | TT 3G Taşıyıcı 2 (Ek) |
| **Türk Telekom** | Band 8 (900) | **2988** | 937.6 MHz | 2763 | 892.6 MHz | TT Kırsal / Indoor 3G |
| **Vodafone** | Band 1 (2100) | **10638** | 2127.6 MHz | 9688 | 1937.6 MHz | VF 3G Taşıyıcı 1 (Ana) |
| **Vodafone** | Band 1 (2100) | **10662** | 2132.4 MHz | 9712 | 1942.4 MHz | VF 3G Taşıyıcı 2 (Ek) |
| **Vodafone** | Band 8 (900) | **3025** | 945.0 MHz | 2800 | 900.0 MHz | VF Kırsal / Indoor 3G |
| **Turkcell** | Band 1 (2100) | **10712** | 2142.4 MHz | 9762 | 1952.4 MHz | TCELL 3G Taşıyıcı 1 (Ana) |
| **Turkcell** | Band 1 (2100) | **10737** | 2147.4 MHz | 9787 | 1957.4 MHz | TCELL 3G Taşıyıcı 2 (Ek) |
| **Turkcell** | Band 8 (900) | **3062** | 952.4 MHz | 2837 | 907.4 MHz | TCELL Kırsal / Indoor 3G |

---

## Python Hızlı Arama Sözlüğü (Lookup Dictionary)
Tarayıcı analiz çıktısında operatör eşleştirmesi yapmak için kullanılabilecek örnek Python veri yapısı:

```python
TURKEY_WCDMA_LOOKUP = {
    # Band 1 (2100 MHz)
    10562: {"operator": "Turk Telekom", "band": 1, "freq_mhz": 2112.4},
    10587: {"operator": "Turk Telekom", "band": 1, "freq_mhz": 2117.4},
    10638: {"operator": "Vodafone",     "band": 1, "freq_mhz": 2127.6},
    10662: {"operator": "Vodafone",     "band": 1, "freq_mhz": 2132.4},
    10712: {"operator": "Turkcell",     "band": 1, "freq_mhz": 2142.4},
    10737: {"operator": "Turkcell",     "band": 1, "freq_mhz": 2147.4},
    
    # Band 8 (900 MHz)
    2988:  {"operator": "Turk Telekom", "band": 8, "freq_mhz": 937.6},
    3025:  {"operator": "Vodafone",     "band": 8, "freq_mhz": 945.0},
    3062:  {"operator": "Turkcell",     "band": 8, "freq_mhz": 952.4}
}
```

## İlgili Konular
* [[concepts/WCDMA ARFCN|WCDMA ARFCN (UARFCN)]]
* [[concepts/WCDMA Bandlar|WCDMA Bandlar]]
* [[synthesis/WCDMA Decode Zinciri|WCDMA Decode Zinciri]]
