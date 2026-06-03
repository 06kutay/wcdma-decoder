---
title: WCDMA Frame Yapısı
category: concepts
tags: [wcdma, physical-layer, frame-structure, timing]
aliases: [WCDMA Frame Structure, Superframe]
sources: [CLAUDE.md]
summary: WCDMA sistemindeki 10 ms radyo çerçevesi, slot yapısı, çip zamanlamaları ve superframe organizasyonunun incelenmesi.
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

# WCDMA Frame Yapısı

WCDMA downlink ve uplink fiziksel katman iletimleri, zaman ekseninde belirli bir hiyerarşik çerçeve (frame) yapısına göre düzenlenmiştir. Tüm zamanlama birimleri, sistemin sabit çip hızı olan **3.84 Mcps** üzerinden tanımlanır.

## Temel Zamanlama Birimleri

* **1 Chip Zamanı ($T_c$):** 
  $$T_c = \frac{1}{3.84 \text{ Mcps}} \approx 260.42 \text{ ns}$$
* **Slot (Zaman Dilimi):** 1 radyo çerçevesi içerisinde **15 adet slot** bulunur.
  * 1 Slot süresi: **0.667 ms** (tam olarak $2/3\text{ ms}$).
  * 1 Slot uzunluğu: **2560 chip** ($2560 \times T_c$).
* **Radio Frame (Radyo Çerçevesi):** Temel fiziksel katman iletim birimidir.
  * 1 Çerçeve süresi: **10 ms**.
  * 1 Çerçeve uzunluğu: **38,400 chip** ($15 \text{ slot} \times 2560 \text{ chip}$).
* **Superframe:** 72 adet radyo çerçevesinden oluşur.
  * 1 Superframe süresi: **720 ms** ($72 \times 10\text{ ms}$).

```
WCDMA Zamanlama Hiyerarşisi:
+-----------------------------------------------------------------------------------+
|                                  SUPERFRAME (720 ms)                              |
+-----------------------------------------------------------------------------------+
|  Frame 0  |  Frame 1  |  Frame 2  |  ...                                | Frame 71|
+-----------+-----------+-----------+-------------------------------------+---------+
|                                10 ms RADIO FRAME                                  |
+-----------------------------------------------------------------------------------+
| Slot 0 | Slot 1 | Slot 2 | Slot 3 | ...                                  | Slot 14|
+--------+--------+--------+--------+--------------------------------------+--------+
|                            0.667 ms SLOT (2560 Chips)                             |
+-----------------------------------------------------------------------------------+
```

## System Frame Number (SFN)
Sistemdeki çerçevelerin kimliğini belirlemek için **SFN (System Frame Number)** kullanılır.
* SFN değeri **0 ile 4095** arasında değişir (12-bit).
* 4096 radyo çerçevelik periyot (40.96 saniye) **SFN Cycle** olarak adlandırılır.
* SFN bilgisi, fiziksel katmandaki BCH ([[concepts/BCH|BCH]]) transport kanalı üzerinden yayınlanan Master Information Block (MIB) ve Scheduling Block'ların zamanlamasında kritik rol oynar.

## Slot Seviyesinde Yapı
Slot içerisindeki çip dağılımı fiziksel kanala göre değişir. Örneğin:
* **Primary Common Control Physical Channel ([[concepts/P-CCPCH|P-CCPCH]]):** Slot başına 2560 chip taşır. Ancak ilk 256 çiplik dilimde fiziksel olarak veri iletilmez, bu alan boş bırakılarak senkronizasyon kanalları ([[concepts/P-SCH|P-SCH]] ve [[concepts/S-SCH|S-SCH]]) ile zaman çoklamalı (time-multiplexed) olarak paylaşılır.
* **Common Pilot Channel ([[concepts/CPICH|CPICH]]):** Slot boyunca sabit pilot sembolleri iletir ve OVSF kodu $C_{ch,256,0}$ ([[concepts/Channelization Code|Channelization Code]]) ile yayılır.

## SDR Veri Yakalama Parametreleri
Matematiksel olarak bir slot 2560 çipten oluştuğu için, saniyede 3.84 Mcps hızında örnekleme yapıldığında (örnekleme oranı = 3.84 Msps, Nyquist sınırında minimum):
* 1 Frame = 38,400 IQ Örneği
* 1 Slot = 2,560 IQ Örneği

Ancak pratikte frekans kaymalarını ve çok yollu yayılımı (multipath) telafi etmek için örnekleme hızı en az 2 katı (**7.68 Msps**) seçilmelidir. Bu durumda:
* 1 Frame = 76,800 IQ Örneği (Oversampling Factor = 2) ^[inferred]
* 1 Slot = 5,120 IQ Örneği

## İlgili Konular
* [[concepts/WCDMA Genel|WCDMA Genel]]
* [[concepts/P-CCPCH|P-CCPCH]]
* [[concepts/WCDMA Cell Search|WCDMA Cell Search]]
