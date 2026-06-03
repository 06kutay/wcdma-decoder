---
title: P-CCPCH
category: concepts
tags: [wcdma, physical-layer, p-ccpch, bch, channels]
aliases: [Primary Common Control Physical Channel]
sources: [CLAUDE.md]
summary: Primary Common Control Physical Channel (P-CCPCH) özellikleri, $C_{ch,256,1}$ OVSF kodu kullanımı, SCH kanalları ile zaman çoklaması yapısı.
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

# P-CCPCH (Primary Common Control Physical Channel)

**P-CCPCH (Primary Common Control Physical Channel - Birincil Ortak Kontrol Fiziksel Kanalı)**, WCDMA sisteminde hücreye ait temel sistem bilgilerini içeren **[[concepts/BCH|BCH (Broadcast Channel)]]** taşıma kanalını havadan fiziksel olarak iletmekle görevli downlink fiziksel kanalıdır.

## Temel Görevi ve Özellikleri
* **Sistem Bilgileri İletimi:** Baz istasyonuna ait kimlik bilgileri, frekanslar, komşu hücreler gibi tüm kritik RRC parametreleri bu kanal üzerinden taşınır.
* **Sabit Spreading Kodu:** P-CCPCH her zaman **$C_{ch,256,1}$** OVSF kodu ile yayılır. Bu kod, CPICH'ten ($C_{ch,256,0}$) sonraki ilk koddur ve $\langle 1, 1, -1, -1, 1, 1, -1, -1, \dots \rangle$ örüntüsüne sahiptir.
* **Sabit Spreading Factor:** Spreading factor (yayma faktörü) **$SF = 256$** olarak sabittir.
* **Bant Genişliği:** 3.84 Mcps çip hızında SF 256 kullanıldığında sembol hızı:
  $$\text{Sembol Hızı} = \frac{3.84 \text{ Mcps}}{256} = 15 \text{ ksps}$$
  QPSK modülasyonu uygulandığı için her sembol 2 bit taşır ve ham kanal veri hızı 30 kbps olur.

## Zaman Çoklamalı (Time-Multiplexed) Yapı
P-CCPCH, senkronizasyon kanalları ([[concepts/P-SCH|P-SCH]] ve [[concepts/S-SCH|S-SCH]]) ile **zaman çoklamalı** olarak paylaşılır.
* **İlk 256 Chip:** Slot başlangıcındaki ilk 256 chip süresince (0 ila 66.7 $\mu$s arası) P-CCPCH verici tarafında kapatılır (gücü sıfırdır). Bu sırada P-SCH ve S-SCH kanalları yüksek güçle yayınlanır.
* **Kalan 2304 Chip:** Slotun 256. çipinden 2560. çipine kadar olan kısmında P-CCPCH aktif hale gelir ve BCH verisini QPSK sembolleri olarak iletir.
* **Sembol Sayısı:** Slot başına iletilen sembol sayısı:
  $$\text{Sembol Sayısı} = \frac{2304 \text{ chips}}{SF=256} = 9 \text{ sembol}$$
  QPSK ile her sembol 2 bit taşıdığından slot başına $9 \times 2 = 18$ ham bit, frame (15 slot) başına ise $18 \times 15 = 270$ ham bit iletilir.

```
Slot Seviyesinde P-CCPCH İletimi:
+-------------------+---------------------------------------------------+
| 0                 | 256                                           2560|
+-------------------+---------------------------------------------------+
|  SCH İletimi      |              P-CCPCH Verisi (9 Sembol, 18 Bit)    |
|  (P-CCPCH Kapalı) |              (OVSF Code: C_ch,256,1)              |
+-------------------+---------------------------------------------------+
```

## Alıcıda Despreading ve İşleme Adımları
Senkronizasyon adımları tamamlandıktan sonra, BCH sistem bilgilerini okumak için alıcı cihaz (SDR / Python) şu adımları izler:
1. Yakalanan IQ verisi frame sınırına göre hizalanır.
2. Her slotun ilk 256 çipi atlanır (SCH kanallarının etkisi temizlenir).
3. Kalan 2304 çip, hücreye özgü **Primary Scrambling Code**'un ilgili slot bölümü ile çarpılarak descramble edilir.
4. Çıkan sinyal, $C_{ch,256,1}$ OVSF kodu ile çarpılıp sembol entegrasyonu yapılarak despread edilir.
5. Elde edilen 270 ham bit, BCH çözücüye ([[concepts/BCH|BCH]]) gönderilir.

## İlgili Konular
* [[concepts/BCH|BCH]]
* [[concepts/Channelization Code|Channelization Code (OVSF)]]
* [[concepts/WCDMA Cell Search|WCDMA Cell Search]]
