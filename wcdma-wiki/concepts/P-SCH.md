---
title: P-SCH
category: concepts
tags: [wcdma, physical-layer, p-sch, synchronization, golay]
aliases: [Primary Synchronization Channel, PSC]
sources: [CLAUDE.md]
summary: Primary Synchronization Channel (P-SCH) yapısı, Primary Synchronization Code (PSC) matematiksel üretimi ve slot senkronizasyonundaki rolü.
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

# P-SCH (Primary Synchronization Channel)

**P-SCH (Primary Synchronization Channel - Birincil Senkronizasyon Kanalı)**, WCDMA downlink sisteminde cihazların (UE) hücre ile ilk slot seviyesinde senkronize olabilmesi için kullanılan, sadece fiziksel katmanda tanımlı özel bir downlink kanalıdır.

## Temel Görevi ve Özellikleri
* **Slot Senkronizasyonu:** P-SCH'in temel görevi, alıcı cihaza 0.667 ms'lik slot sınırlarını bildirmektir.
* **Global Tasarım:** P-SCH üzerinde iletilen **Primary Synchronization Code (PSC)**, dünyadaki tüm WCDMA/UMTS baz istasyonlarında (NodeB) **birebir aynıdır**. Hücreye veya operatöre göre değişmez.
* **Aralıklı İletim:** Sürekli yayın yapmaz. Her slotun **ilk 256 çiplik** (toplam 2560 çiplik slotun %10'u) diliminde yüksek güçle iletilir. Geri kalan 2304 çip boyunca P-SCH tamamen kapalıdır.
* **Scrambling Yoktur:** P-SCH, hücrenin scrambling kodu ([[concepts/Scrambling Code|Scrambling Code]]) ile çırpılmaz. Sinyal havada "yalın" olarak bulunur, böylece cihaz henüz scrambling kodunu bilmeden bu sinyali doğrudan yakalayabilir.

## PSC ($C_{psc}$) Matematiksel Üretimi (3GPP TS 25.213)
PSC, **genelleştirilmiş hiyerarşik Golay dizisi (Generalized Hierarchical Golay Sequence)** yapısında tasarlanmıştır. Bu özel matematiksel yapı, mükemmel aperiodic autocorrelation (öz-ilişkilendirme) özellikleri sunar ve alıcı tarafta tek bir eşleştirilmiş filtre (matched filter) yardımıyla çok düşük işlem yükü ile tespit edilebilir.

### 1. Temel Dizi $a$ (Boyut: 16 çip)
Öncelikle 16 elemanlı bir temel Golay dizisi tanımlanır:
$$a = \langle 1, 1, 1, 1, 1, 1, -1, -1, 1, -1, 1, -1, 1, -1, -1, 1 \rangle$$

### 2. Genişletme ve Kompleks Yapı
256 elemanlı PSC dizisi ($C_{psc}$), $a$ dizisinin belirli işaretlerle 16 kez tekrarlanması ve kompleks düzleme taşınması ile üretilir:
$$C_{psc} = (1 + j) \times \langle a, a, a, -a, -a, a, -a, -a, a, a, a, -a, a, -a, a, a \rangle$$

Burada:
* Eleman bazında çarpma yapıldığında toplam uzunluk $16 \times 16 = 256$ çiptir.
* $(1 + j)$ katsayısı sinyalin In-phase (I) ve Quadrature (Q) bileşenlerinin genliğini eşitleyerek alıcıda tespiti kolaylaştırır.
* PSC'nin ikili (binary) karşılığı kodlama ve işlem kolaylığı açısından $\pm 1$ dizisi olarak hafızada tutulur.

## Alıcıda Eşleştirilmiş Filtre (Matched Filter) Uygulaması
Alıcı cihaz (SDR), havadan sürekli IQ verisi kaydederken aradığı slot sınırlarını bulmak için gelen sinyal ile bilinen $C_{psc}$ dizisi arasında **Cross-Correlation (çapraz ilinti)** işlemi yapar.
* Sinyal her slot başlangıcına (PSC iletim anı) denk geldiğinde, Golay dizisinin aperiodic korelasyon özelliğinden dolayı korelasyon çıktısında çok keskin ve yüksek bir **tepe noktası (peak)** oluşur.
* Slot başına 2560 çip olduğu için, bu korelasyon işlemi 2560 çip kaydırılarak tekrarlanır ve tepe noktalarının her 2560 çipte bir periyodik olarak tekrarladığı doğrulanır.
* Bu işlemin sonucunda slot sınırı kesin olarak bulunmuş olur.

```
Korelasyon Çıktısı (Slot Sync):
Genlik
 ^
 |         |                        |                        |
 |         |                        |                        |
 |         |                        |                        |
 |________/ \______________________/ \______________________/ \______
 +---------+------------------------+------------------------+-----> Zaman
 0      2560                     5120                     7680 (Chips)
      Slot Sınırı              Slot Sınırı              Slot Sınırı
```

## İlgili Konular
* [[concepts/WCDMA Frame Yapisi|WCDMA Frame Yapısı]]
* [[concepts/S-SCH|S-SCH]]
* [[concepts/WCDMA Cell Search|WCDMA Cell Search]]
