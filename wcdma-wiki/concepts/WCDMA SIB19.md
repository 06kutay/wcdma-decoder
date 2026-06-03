---
title: WCDMA SIB19
category: concepts
tags: [wcdma, rrc, sib, sib19, inter-rat, neighbor-list]
aliases: [SIB19]
sources: [CLAUDE.md]
summary: WCDMA RRC katmanındaki SIB19 (System Information Block 19) işlevi, LTE EARFCN ve GSM ARFCN komşu hücre bilgileri taşıyan Inter-RAT geçiş mekanizması.
provenance:
  extracted: 0.95
  inferred: 0.05
  ambiguous: 0.00
base_confidence: 0.90
lifecycle: draft
lifecycle_changed: 2026-06-02
tier: supporting
created: 2026-06-02T16:16:00Z
updated: 2026-06-02T16:16:00Z
---

# WCDMA SIB19 (System Information Block 19)

**WCDMA SIB19 (System Information Block 19 - Sistem Bilgi Bloğu 19)**, RRC katmanında yayınlanan ve cihazın WCDMA (3G) ağından diğer radyo erişim teknolojilerine (GSM-2G veya LTE-4G) geçiş yapabilmesi için gereken **Inter-RAT (Radio Access Technology) komşu hücre listelerini** ve öncelik parametrelerini taşıyan kritik bir bloktur.

3G standardının geç dönem sürümlerinde (Release 8 ve sonrası) LTE entegrasyonu ile birlikte tanımlanmıştır.

## Temel Görevleri
* **Teknolojiler Arası Geçiş (Inter-RAT Handover):** 3G sinyali zayıfladığında veya veri hızı ihtiyacı arttığında cihazın otomatik olarak 4G (LTE) veya 2G (GSM) şebekelerine geçmesini (cell reselection / handover) tetikler.
* **4G Kapsama Alanı Tanımlama:** Çevredeki 4G baz istasyonlarının frekanslarını (EARFCN) cihaza bildirerek arka planda hızlı tarama yapmasını sağlar.

## SIB19 İçeriğindeki Komşu Bilgileri
SIB19 çözüldüğünde elde edilen komşu listeleri şunlardır:

### 1. LTE Neighbor List (E-UTRA / 4G Komşuları)
* **EARFCN (E-UTRA Absolute Radio Frequency Channel Number):** Komşu LTE hücrelerinin merkez downlink frekans kodudur.
* **Measurement Bandwidth:** Ölçüm yapılacak LTE kanal genişliği (Örn. 5, 10, 15, 20 MHz).
* **Blacklisted Cells:** Cihazın bağlanmaması gereken hatalı/yasaklı LTE fiziksel hücre kimliklerinin (PCI) listesi.
* **Priority (Öncelik):** LTE şebekesinin 3G'ye göre öncelik değeridir (Genellikle LTE önceliği 3G'den yüksek set edilir, böylece cihaz 4G bulduğu an oraya geçiş yapar). ^[inferred]

### 2. GSM Neighbor List (GERAN / 2G Komşuları)
* **ARFCN (Absolute Radio Frequency Channel Number):** Komşu GSM frekans kanalları.
* **Band Indicator:** GSM 900, DCS 1800 vb. band belirteçleri.
* *Not:* Bazı eski şebekelerde GSM komşuları SIB11 veya SIB12 içinde de taşınabilir, ancak modern WCDMA konfigürasyonlarında hiyerarşik yapı SIB19 üzerinde toplanmıştır.

## ASN.1 Yapısı ve Çözümlemedeki Yeri
SIB19, `SystemInformationBlockType19` ASN.1 yapısını kullanır. İçerisinde `earfcn` dizileri ve `geran-PriorityInfoList` gibi yapılar bulunur.

### Örnek SIB19 Decode Çıktısı (UPER)
```json
{
  "sib19": {
    "utran-PriorityInfoList": {
      "priority": 3
    },
    "eutra-FrequencyAndPriorityInfoList": [
      {
        "earfcn": 1600,   # LTE Band 3 (1800 MHz) frekansı
        "priority": 6,
        "measurementBandwidth": "mbw50"  # 10 MHz (50 PRB)
      },
      {
        "earfcn": 3000,   # LTE Band 7 (2600 MHz) frekansı
        "priority": 7,
        "measurementBandwidth": "mbw100" # 20 MHz (100 PRB)
      }
    ]
  }
}
```

## Komşu Analiz Sistemindeki Önemi
WCDMA komşu analizörünün amacı sadece 3G ağını haritalamak değil, aynı zamanda şebekeler arası geçiş topolojisini de yakalamaktır. **SIB19 decode edilerek**, operatörün 3G kapsama alanından hangi 4G (LTE) frekanslarına geçiş yolları tanımladığını (şebeke planlama stratejisini) doğrudan görebiliriz.

## İlgili Konular
* [[concepts/WCDMA SIB Genel|WCDMA SIB Genel]]
* [[concepts/WCDMA SIB11|WCDMA SIB11]]
* [[concepts/WCDMA ARFCN|WCDMA ARFCN]]
