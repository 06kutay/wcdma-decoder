---
title: BCH
category: concepts
tags: [wcdma, physical-layer, bch, transport-channel, viterbi, crc]
aliases: [Broadcast Channel]
sources: [CLAUDE.md]
summary: Broadcast Channel (BCH) taşıma kanalı yapısı, 20 ms TTI zamanlaması, 1/2 rate evrişimsel kodlama, CRC16 hata denetimi ve SIB taşıma mekanizması.
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

# BCH (Broadcast Channel)

**BCH (Broadcast Channel - Yayın Kanalı)**, WCDMA sisteminde en üst katmandaki RRC sistem bilgilerini (MIB, SIB) fiziksel katmana taşıyan **downlink yönündeki taşıma kanalıdır (Transport Channel)**. BCH verileri fiziksel katmanda [[concepts/P-CCPCH|P-CCPCH]] kanalı üzerinde taşınır.

## Temel Görevi ve Yapısı
BCH, hücrenin yaydığı tüm sistem parametrelerini paketler ve fiziksel katmanın hata koruma (Channel Coding) aşamalarından geçirir. 

* **Sabit TTI (Transmission Time Interval):** BCH kanalı için TTI süresi her zaman **20 ms**'dir. Bu, her bir BCH veri bloğunun **2 ardışık radyo çerçevesine (20 ms / 2 frame)** yayılarak iletildiği anlamına gelir.
* **Hata Algılama (CRC):** Her BCH bloğuna hata algılama amacıyla **16-bit CRC** (Cyclic Redundancy Check) eklenir.
* **Hata Düzeltme (Channel Coding):** Çok yollu sönümlenme ve gürültüye karşı koruma sağlamak için **$R=1/2$ oranında Convolutional Coding (Evrişimsel Kodlama)** uygulanır.

## BCH Fiziksel Katman İşleme Zinciri (3GPP TS 25.212)

Yukarıdan gelen RRC sistem veri blokları, fiziksel katmanda sırasıyla aşağıdaki işlemlerden geçer:

```
BCH İşleme Akışı:
+---------------------------------------+
|  RRC Sistem Bilgisi (Örn. 246 Bit)    |
+---------------------------------------+
                   |
                   v
+---------------------------------------+
|  1. CRC16 Ekleme (246 + 16 = 262 Bit) |
+---------------------------------------+
                   |
                   v
+---------------------------------------+
|  2. Tail Bit Ekleme (262 + 8 = 270)   |
+---------------------------------------+
                   |
                   v
+---------------------------------------+
|  3. 1/2 Convolutional Coding (540 Bit)|
+---------------------------------------+
                   |
                   v
+---------------------------------------+
|  4. Interleaving (20 ms TTI)          |
+---------------------------------------+
                   |
                   v
+---------------------------------------+
|  5. Frame Segmentation (2x270 Bit)    |
+---------------------------------------+
                   |
                   v
+---------------------------------------+
|  6. P-CCPCH Downlink Fiziksel Kanalı  |
|     (Frame 1: 270 Bit / Frame 2: 270) |
+---------------------------------------+
```

### 1. Evrişimsel Kodlama (Convolutional Coding)
* Kodlama Oranı: $R = 1/2$
* Constraint Length (Bellek Boyu): $K = 9$ (8 adet geciktirme elemanı)
* Generator Polynomials: 
  * $G_0 = 561$ (oktal) $\rightarrow 101110001_2$
  * $G_1 = 753$ (oktal) $\rightarrow 111101011_2$
* Kodlayıcıya giren 270 bit (262 bilgi + 8 kuyruk/tail biti), çıkışta tam olarak **540 kodlu bit** üretir.

### 2. Kanal Matrisli Serpiştirme (1st Interleaving)
540 kodlu bit, çoklu bit hatalarını (burst error) önlemek için 20 ms'lik TTI boyunca zamana yayılır (serpiştirilir). 20 sütunlu bir matrise satır satır yazılarak sütun bazında karıştırılır ve sütun sütun okunur.

### 3. Çerçeve Segmentasyonu (Frame Segmentation)
Serpiştirilen 540 bit, her biri 270 bitlik iki alt bloğa bölünür.
* 1. Blok $\rightarrow$ TTI'ın ilk 10 ms'lik çerçevesinde (Frame 1) P-CCPCH ile iletilir.
* 2. Blok $\rightarrow$ TTI'ın ikinci 10 ms'lik çerçevesinde (Frame 2) P-CCPCH ile iletilir.

## Alıcıda BCH Decode (Viterbi Çözücü)
SDR üzerinden kaydedilen sinyal P-CCPCH despread aşamasından geçirildikten sonra alıcı şu adımları uygular:
1. İki ardışık radyo çerçevesinden gelen 270'er bit toplanarak 540 bitlik TTI paketi birleştirilir.
2. Serpiştirme işlemi tersine çevrilir (De-interleaving).
3. **Viterbi Algoritması** kullanılarak 1/2 rate evrişimsel kod çözülür ve orijinal 270 bit (kuyruk bitleri dahil) elde edilir.
4. Son 8 bit (tail) atılır, geriye kalan 262 bitin ilk 246 biti üzerinde CRC16 hesaplanır.
5. Hesaplanan CRC, paketin sonundaki 16-bit CRC ile karşılaştırılır. **CRC geçerli ise (hata yoksa)** elde edilen veri RRC katmanına aktarılarak SIB ([[concepts/WCDMA SIB Genel|SIB]]) birleştirme ünitesine gönderilir. ^[inferred]

## İlgili Konular
* [[concepts/P-CCPCH|P-CCPCH]]
* [[concepts/WCDMA SIB Genel|WCDMA SIB Genel]]
