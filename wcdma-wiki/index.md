---
title: WCDMA Komşu Hücre Analiz Sistemi Wiki Index
category: index
tags: [wcdma, index, home]
sources: [CLAUDE.md]
summary: WCDMA/UMTS Komşu Hücre Analiz Sistemi için bilgi tabanı ana indeksi.
provenance:
  extracted: 1.00
  inferred: 0.00
  ambiguous: 0.00
base_confidence: 1.00
lifecycle: seed
lifecycle_changed: 2026-06-02
tier: core
created: 2026-06-02T16:10:00Z
updated: 2026-06-02T16:16:00Z
---

# WCDMA Komşu Hücre Analiz Sistemi Bilgi Tabanı

Bu bilgi tabanı, SDR tabanlı **WCDMA/UMTS Komşu Hücre Analiz Sistemi** için fiziksel katmandan RRC katmanına kadar olan teorik temelleri, yazılım mimarisini ve referans standartları içermektedir. Karpathy LLM Wiki 3-katmanlı mimarisine göre organize edilmiştir.

## 📚 WCDMA Teorik Kavramlar (Concepts)

* **Genel:** [[concepts/WCDMA Genel|WCDMA Genel Bakış]] — CDMA, Chip Rate, FDD yapısı.
* **Zamanlama:** [[concepts/WCDMA Frame Yapisi|WCDMA Frame Yapısı]] — Slot, Radio Frame, Superframe, SFN.
* **Kanallar:** [[concepts/WCDMA Fiziksel Kanallar|WCDMA Fiziksel Kanallar]] — P-SCH, S-SCH, CPICH, P-CCPCH, S-CCPCH.
* **Senkronizasyon (Adım 1 & 2):**
  * [[concepts/P-SCH|P-SCH & PSC]] — Primary Sync Channel, Golay dizisi üretimi ve slot senkronizasyonu.
  * [[concepts/S-SCH|S-SCH & SSC]] — Secondary Sync Channel, Comma-Free kodlama ve frame senkronizasyonu.
* **Kanal Tahmini ve Ölçüm (Adım 3):**
  * [[concepts/CPICH|CPICH]] — Ortak Pilot Kanalı, Scrambling tespiti, RSCP ve Ec/No ölçümleri.
* **Veri Taşıma ve Kod Çözme:**
  * [[concepts/P-CCPCH|P-CCPCH]] — Sistem bilgi verisini taşıyan fiziksel kanal ve slot yapısı.
  * [[concepts/BCH|BCH]] — Transport kanalı, 20 ms TTI, 1/2 Convolutional Viterbi çözme, CRC16.
* **Kodlama Matematiği:**
  * [[concepts/Scrambling Code|Scrambling Code]] — 512 Gold kodu, 18-dereceli LFSR m-dizileri polinomları ve descrambling.
  * [[concepts/Channelization Code|Channelization Code (OVSF)]] — Ortogonal yayma kodları, OVSF kod ağacı üretimi ve despreading.
* **Arama Algoritması:** [[concepts/WCDMA Cell Search|WCDMA Cell Search]] — 3 adımlı hücre arama şeması.
* **Sistem Bilgileri (SIB):**
  * [[concepts/WCDMA SIB Genel|WCDMA SIB Genel]] — BCCH mantıksal kanalı, segmentasyon ve birleştirme.
  * [[concepts/WCDMA SIB3|WCDMA SIB3]] — Serving hücre kimlik bilgileri: Cell Identity (CID), LAC ve hücre seçim kriterleri.
  * [[concepts/WCDMA SIB11|WCDMA SIB11]] — Intra-frequency ve Inter-frequency komşu listeleri (PSC + UARFCN).
  * [[concepts/WCDMA SIB11bis|WCDMA SIB11bis]] — SIB11 boyut sınırını aşan ek komşu hücre listesi.
  * [[concepts/WCDMA SIB19|WCDMA SIB19]] — Inter-RAT komşu listeleri (LTE EARFCN, GSM ARFCN) ve öncelikler.
* **Frekans Planlama:**
  * [[concepts/WCDMA ARFCN|WCDMA ARFCN (UARFCN)]] — 200 kHz raster yapısı, Band 1 ve Band 8 frekans formülleri.
  * [[concepts/WCDMA Bandlar|WCDMA Bandlar]] — Türkiye'deki 3G band dağılımları, operatör spektrumları ve SDR LNAH/LNAW port eşleştirmeleri.

## 🔗 Sistem Mimarisi ve Sentez (Synthesis)

* [[synthesis/WCDMA Decode Zinciri|WCDMA Decode Zinciri]] — SDR ham IQ örneğinden komşu hücre listesine giden uçtan uca offline pipeline akış şeması.
* [[synthesis/Sistem Mimarisi|Sistem Mimarisi]] — Offline yürütme modeli, LimeSDR mini entegrasyonu, veri yakalama parametreleri ve modüler yazılım yapısı.

## 📋 Teknik Referanslar (References)

* [[references/UARFCN Frekans Tablosu|UARFCN Frekans Tablosu]] — Turkcell, Vodafone, Türk Telekom Band 1/8 nominal UARFCN, DL/UL frekans kod tablosu ve Python hızlı arama sözlüğü.
* [[references/3GPP WCDMA Standartlari|3GPP WCDMA Standartları]] — Projede temel alınan TS 25.213, TS 25.211, TS 25.212, TS 25.331 ve TS 25.101 standart haritası.
* [[references/WCDMA Komşu Haritası|WCDMA Komşu Haritası]] — Hücreler arası komşuluk ilişkilerini ve yön durumlarını (tek/çift yönlü) gösteren topolojik matris.

### Aktif WCDMA Hücre Listesi (Phase 2 & 4)

