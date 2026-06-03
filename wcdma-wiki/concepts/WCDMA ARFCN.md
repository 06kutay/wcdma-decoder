---
title: WCDMA ARFCN
category: concepts
tags: [wcdma, physical-layer, frequency, uarfcn, bands]
aliases: [UARFCN, WCDMA Frequency, ARFCN]
sources: [CLAUDE.md]
summary: WCDMA taşıyıcı frekanslarını temsil eden UARFCN mantığı, Band 1 ve Band 8 downlink/uplink frekans hesaplama formülleri ve raster yapısı.
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

# WCDMA ARFCN (UARFCN)

WCDMA sisteminde taşıyıcı frekanslarını belirtmek için doğrudan MHz cinsinden değerler yerine, standartlaştırılmış tam sayı kodları olan **UARFCN (UTRA Absolute Radio Frequency Channel Number - UTRA Mutlak Radyo Frekansı Kanal Numarası)** kullanılır.

## UARFCN Raster Yapısı
WCDMA taşıyıcı frekansları, **200 kHz (0.2 MHz) kanal adım aralığına (channel raster)** sahiptir. Bu, merkez frekanslarının her zaman 200 kHz'in katlarında yer alabileceği anlamına gelir. 

UARFCN değeri ile MHz cinsinden frekans arasındaki matematiksel ilişki, bulunulan frekans bandına göre standart (3GPP TS 25.101) tarafından tanımlanmış formüllere dayanır.

---

## Band 1 (IMT 2100 MHz) Frekans Hesaplamaları
Band 1, Türkiye ve Avrupa genelinde WCDMA (3G) hizmeti için tahsis edilmiş ana frekans bandıdır.

### Downlink (DL) Frekans Formülü
Band 1 DL merkez frekansı ($F_{DL}$), $10562$ ila $10838$ aralığındaki UARFCN değerleri ($N_{DL}$) için şöyle hesaplanır:
$$F_{DL} \text{ (MHz)} = 0.2 \times N_{DL}$$

* **UARFCN Sınırları:** $10562 \le N_{DL} \le 10838$
* **Frekans Sınırları:** $2112.4 \text{ MHz} \le F_{DL} \le 2167.6 \text{ MHz}$
* *Örnek:* Turkcell Band 1 UARFCN $10712$ için:
  $$F_{DL} = 0.2 \times 10712 = 2142.4 \text{ MHz}$$

### Uplink (UL) Frekans Formülü
Band 1 UL merkez frekansı ($F_{UL}$), $9612$ ila $9888$ aralığındaki UARFCN değerleri ($N_{UL}$) için hesaplanır:
$$F_{UL} \text{ (MHz)} = 0.2 \times N_{UL}$$

* **UARFCN Sınırları:** $9612 \le N_{UL} \le 9888$
* **Frekans Sınırları:** $1922.4 \text{ MHz} \le F_{UL} \le 1977.6 \text{ MHz}$
* **Duplex Shift (Farkı):** Band 1 için DL ve UL frekansları arasındaki fark sabit **190 MHz**'dir ($F_{DL} - F_{UL} = 190 \text{ MHz}$).

---

## Band 8 (EGSM 900 MHz) Frekans Hesaplamaları
Band 8, genellikle kırsal alanlarda geniş kapsama alanı ve binaların içine nüfuz etme kabiliyeti sağlamak amacıyla kullanılan 900 MHz bandıdır.

### Downlink (DL) Frekans Formülü
Band 8 DL merkez frekansı ($F_{DL}$), $2937$ ila $3088$ aralığındaki UARFCN değerleri ($N_{DL}$) için şöyle hesaplanır:
$$F_{DL} \text{ (MHz)} = 340.0 + 0.2 \times N_{DL}$$

* **UARFCN Sınırları:** $2937 \le N_{DL} \le 3088$
* **Frekans Sınırları:** $927.4 \text{ MHz} \le F_{DL} \le 957.6 \text{ MHz}$
* *Örnek:* Vodafone Band 8 UARFCN $3025$ için:
  $$F_{DL} = 340.0 + 0.2 \times 3025 = 945.0 \text{ MHz}$$

### Uplink (UL) Frekans Formülü
Band 8 UL merkez frekansı ($F_{UL}$), $2712$ ila $2863$ aralığındaki UARFCN değerleri ($N_{UL}$) için hesaplanır:
$$F_{UL} \text{ (MHz)} = 340.0 + 0.2 \times N_{UL}$$

* **UARFCN Sınırları:** $2712 \le N_{UL} \le 2863$
* **Frekans Sınırları:** $882.4 \text{ MHz} \le F_{UL} \le 912.6 \text{ MHz}$
* **Duplex Shift (Farkı):** Band 8 için DL ve UL frekansları arasındaki fark sabit **45 MHz**'dir ($F_{DL} - F_{UL} = 45 \text{ MHz}$).

---

## Alıcıda UARFCN Dönüşüm Tablosu (Python Örneği)
SDR tarayıcı kodunda kullanılacak pratik dönüşüm fonksiyonu taslağı şöyledir:

```python
def uarfcn_to_frequency_dl(uarfcn):
    # Band 1 Downlink
    if 10562 <= uarfcn <= 10838:
        band = 1
        freq = 0.2 * uarfcn
    # Band 8 Downlink
    elif 2937 <= uarfcn <= 3088:
        band = 8
        freq = 340.0 + (0.2 * uarfcn)
    else:
        raise ValueError(f"Desteklenmeyen UARFCN: {uarfcn}")
        
    return freq, band
```

## İlgili Konular
* [[concepts/WCDMA Bandlar|WCDMA Bandlar]]
* [[references/UARFCN Frekans Tablosu|UARFCN Frekans Tablosu]]
* [[concepts/WCDMA SIB11|WCDMA SIB11]]
