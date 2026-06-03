---
title: WCDMA Genel
category: concepts
tags: [wcdma, umts, physical-layer, fundamentals]
aliases: [W-CDMA, UMTS, Wideband CDMA]
sources: [CLAUDE.md]
summary: WCDMA/UMTS standardının temel çalışma prensipleri, CDMA erişim tekniği, GSM/LTE ile karşılaştırması ve FDD yapısının incelenmesi.
provenance:
  extracted: 0.90
  inferred: 0.10
  ambiguous: 0.00
base_confidence: 0.85
lifecycle: draft
lifecycle_changed: 2026-06-02
tier: core
created: 2026-06-02T16:16:00Z
updated: 2026-06-02T16:16:00Z
---

# WCDMA Genel

**WCDMA (Wideband Code Division Multiple Access - Geniş Bant Kod Bölmeli Çoklu Erişim)**, 3G (Üçüncü Nesil) mobil iletişim standardı olan **UMTS (Universal Mobile Telecommunications System)** sisteminin hava arayüzü (Air Interface) teknolojisidir. 

## CDMA Tabanlı Çoklu Erişim
GSM (2G) teknolojisinde kullanılan frekans bölmeli (FDMA) ve zaman bölmeli (TDMA) çoklu erişim yöntemlerinden farklı olarak WCDMA, tüm kullanıcıların **aynı frekans bandını** ve **aynı zaman dilimini** paylaştığı **CDMA** tekniğini kullanır.
* **Kodla Ayrıştırma:** Her kullanıcıya ve her kanala benzersiz bir matematiksel kod tanımlanır. Alıcı taraf, bu özel kodu kullanarak geniş bantlı gürültü benzeri sinyal içerisinden sadece ilgili veriyi süzüp çıkarır.
* **Geniş Bant Sinyali:** Dar bantlı veri sinyali, yüksek hızlı bir kod dizisiyle (Spreading Code) çarpılarak geniş bir frekans bandına yayılır.

## Temel Fiziksel Parametreler
* **Chip Rate (Çip Hızı):** WCDMA'in çip hızı sabit **3.84 Mcps (Megachips per second)** değerindedir. Bu, saniyede 3.84 milyon adet "çip" (kod biti) iletildiği anlamına gelir.
* **Kanal Bant Genişliği:** Taşıyıcı kanal genişliği nominal olarak **5 MHz**'dir. Bu bant genişliği, 3.84 Mcps çip hızı ve koruma bantları ile tam uyumludur.
* **FDD Yapısı (Frequency Division Duplex):** WCDMA yaygın olarak FDD modunda çalışır. Uplink (cihazdan baz istasyonuna) ve Downlink (baz istasyonundan cihaza) yönündeki iletimler farklı frekans kanalları üzerinden eşzamanlı olarak gerçekleştirilir (Örn. Band 1 için UL: 1920-1980 MHz, DL: 2110-2170 MHz).

## GSM ve LTE ile Karşılaştırma

| Özellik | GSM (2G) | WCDMA (3G) | LTE (4G) |
|---|---|---|---|
| **Erişim Yöntemi** | FDMA + TDMA | CDMA | OFDMA (DL) / SC-FDMA (UL) |
| **Bant Genişliği** | 200 kHz | 5 MHz | 1.4 MHz - 20 MHz (Esnek) |
| **Modülasyon** | GMSK | QPSK (DL/UL), 16QAM (HSPA) | QPSK, 16QAM, 64QAM, 256QAM |
| **Kanal Paylaşımı** | Zaman ve Frekans Slotu | Benzersiz Kodlar | Frekans Alt Taşıyıcıları ve Zaman (PRB) |
| **Hücre Geçişi (Handover)**| Hard Handover (Kes-Bağlan) | Soft / Softer Handover (Aynı anda çoklu hücre bağlantısı) ^[inferred] | Hard Handover |

## Spreading ve Despreading Mantığı
WCDMA veri iletiminde iki aşamalı kodlama uygulanır:
1. **Spreading (Kanal Yayma):** OVSF ([[concepts/Channelization Code|Channelization Code]]) kodları kullanılarak dar bantlı veri sembolleri 3.84 Mcps çip hızına yükseltilir. Bu işlem kanalları birbirinden ayırır.
2. **Scrambling (Çırpma):** Hücreye özgü [[concepts/Scrambling Code|Scrambling Code]] kullanılarak yayılan sinyal çırpılır. Bu işlem hücreleri birbirinden ayırır ve sinyalin spektral olarak gürültüye benzemesini sağlar.

Alıcı tarafta **Despreading (Geri Yayma)** işlemi gerçekleştirilir. Alıcı sinyali, verici ile birebir senkronize edilmiş aynı OVSF koduyla çarptığında sinyal tekrar orijinal dar bant genişliğine daralır (Processing Gain elde edilir) ve gürültü seviyesinin üzerine çıkar. Yanlış kodla yapılan despreading işlemi ise sinyali gürültü olarak bırakır.

## İlgili Konular
* [[concepts/WCDMA Frame Yapisi|WCDMA Frame Yapısı]]
* [[concepts/WCDMA Fiziksel Kanallar|WCDMA Fiziksel Kanallar]]
* [[concepts/Channelization Code|Channelization Code (OVSF)]]
* [[concepts/Scrambling Code|Scrambling Code]]
