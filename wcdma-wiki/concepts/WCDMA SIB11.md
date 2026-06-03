---
title: WCDMA SIB11
category: concepts
tags: [wcdma, rrc, sib, sib11, neighbor-list, measurements]
aliases: [SIB11]
sources: [CLAUDE.md]
summary: WCDMA RRC SIB11 (System Information Block 11) detayları, Intra-Frequency ve Inter-Frequency komşu hücre listeleri ve ASN.1 yapısı.
provenance:
  extracted: 0.95
  inferred: 0.05
  ambiguous: 0.00
base_confidence: 0.90
lifecycle: draft
lifecycle_changed: 2026-06-02
tier: core
created: 2026-06-02T16:16:00Z
updated: 2026-06-02T16:16:00Z
---

# WCDMA SIB11 (System Information Block 11)

**WCDMA SIB11 (System Information Block 11 - Sistem Bilgi Bloğu 11)**, RRC katmanında yayınlanan, WCDMA Komşu Hücre Analiz Projesi'nin **en önemli veri kaynağıdır**. 

Hizmet veren hücre, kapsama alanındaki mobil cihazların hangi komşu hücreleri ölçmesi gerektiğini (Measurement Control) ve bu hücrelere ait fiziksel parametreleri SIB11 aracılığıyla bildirir.

## Temel Görevleri
* **Komşu Hücre Listesi Sağlama:** Cihazların arama yapmasına gerek kalmadan çevredeki aktif hücrelerin listesini doğrudan verir.
* **Ölçüm Parametreleri:** Cihazın hangi kriterlere göre (RSCP veya $E_c/N_0$) ölçüm yapacağını ve bu ölçüm raporlarını ne zaman baz istasyonuna göndereceğini tanımlar.

## Komşu Hücre Listesi Türleri (Neighbor Cell Lists)
SIB11 çözüldüğünde temel olarak iki farklı komşu hücre listesi elde edilir:

### 1. Intra-Frequency Neighbor List (Aynı Frekanstaki Komşular)
* **Açıklama:** Hizmet veren hücre ile **birebir aynı frekansta (aynı UARFCN üzerinde)** çalışan komşu hücrelerin listesidir.
* **Parametreler:** Sadece **[[concepts/Scrambling Code|Primary Scrambling Code]] (PSC)** değerlerini içerir (0 ila 511 arası tamsayı). Frekans aynı olduğu için UARFCN bilgisi tekrar gönderilmez, cihaz aynı frekansta bu scrambling kodlarını tarar.
* **Önemi:** WCDMA'de en sık gerçekleştirilen **Soft Handover (Yumuşak Geçiş)** işlemleri bu listedeki hücreler arasında yapılır.

### 2. Inter-Frequency Neighbor List (Farklı Frekanstaki Komşular)
* **Açıklama:** Farklı WCDMA frekanslarında (operatörün diğer 3G taşıyıcılarında veya diğer bantlarında) çalışan komşu hücrelerin listesidir.
* **Parametreler:** Her komşu hücre için iki parametre iletilir:
  1. **UARFCN ([[concepts/WCDMA ARFCN|UARFCN]]):** Hücrenin çalıştığı merkez frekans kodu.
  2. **Primary Scrambling Code (PSC):** Hücrenin scrambling kodu.
* **Önemi:** Cihazın kendi frekansındaki kapasite yetersiz kaldığında veya sinyal zayıfladığında diğer frekans taşıyıcılarına (Hard Handover) geçmesini sağlar. ^[inferred]

## SIB11 ASN.1 Yapısı ve Parametre Haritası (3GPP TS 25.331)
SIB11 ASN.1 tanımında komşu hücre bilgileri `MeasurementControlSysInfo` yapısı altında, `intraFreqCellInfoList` ve `interFreqCellInfoList` dizilerinde taşınır.

### Örnek ASN.1 Decode Çıktısı (UPER Çözümünden Sonra)
```json
{
  "sib11": {
    "intraFreqCellInfoList": {
      "newIntraFreqCellList": [
        { "primaryScramblingCode": 104 },
        { "primaryScramblingCode": 215 },
        { "primaryScramblingCode": 48 }
      ]
    },
    "interFreqCellInfoList": {
      "newInterFreqCellList": [
        {
          "frequencyInfo": { "uarfcn-DL": 10587 },
          "primaryScramblingCode": 12 },
        {
          "frequencyInfo": { "uarfcn-DL": 10587 },
          "primaryScramblingCode": 244 },
        {
          "frequencyInfo": { "uarfcn-DL": 10612 },
          "primaryScramblingCode": 305 }
      ]
    }
  }
}
```

## SIB11 Boyut Sınırı ve SIB11bis İlişkisi
BCH taşıma kanalının kapasite sınırları nedeniyle SIB11 bloğunun maksimum boyutu sınırlıdır. Çevrede çok fazla komşu hücre varsa ve tüm liste SIB11 içine sığmıyorsa:
* Ana liste SIB11 içinde gönderilir.
* Kalan komşu hücreler ek olarak **[[concepts/WCDMA SIB11bis|SIB11bis]]** bloğu içerisinde yayınlanır.

## İlgili Konular
* [[concepts/WCDMA SIB Genel|WCDMA SIB Genel]]
* [[concepts/WCDMA SIB11bis|WCDMA SIB11bis]]
* [[concepts/WCDMA SIB19|WCDMA SIB19]]
* [[concepts/Scrambling Code|Scrambling Code]]
* [[concepts/WCDMA ARFCN|WCDMA ARFCN]]
