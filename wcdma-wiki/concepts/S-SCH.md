---
title: S-SCH
category: concepts
tags: [wcdma, physical-layer, s-sch, synchronization, hadamard]
aliases: [Secondary Synchronization Channel, SSC]
sources: [CLAUDE.md]
summary: Secondary Synchronization Channel (S-SCH) yapısı, 16 adet Secondary Synchronization Code (SSC) üretimi, comma-free kodlama ve frame senkronizasyonundaki rolü.
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

# S-SCH (Secondary Synchronization Channel)

**S-SCH (Secondary Synchronization Channel - İkincil Senkronizasyon Kanalı)**, WCDMA downlink sisteminde cihazların (UE) **frame (çerçeve) senkronizasyonunu** sağlamak ve hücrenin ait olduğu **scrambling kod grubunu** tespit etmek için kullanılan, sadece fiziksel katmanda tanımlı özel bir downlink kanalıdır.

## Temel Görevi ve Özellikleri
* **Frame Senkronizasyonu:** P-SCH ([[concepts/P-SCH|P-SCH]]) ile slot sınırları bulunmuştur, ancak slotun 15 slotluk çerçevenin (10 ms frame) kaçıncı slotu olduğu henüz bilinmemektedir. S-SCH bu başlangıç noktasını (Frame Boundary) bulur.
* **Kod Grubu Tespiti:** WCDMA'deki 512 birincil scrambling kodu, 64 gruba ayrılmıştır. S-SCH, hücrenin bu **64 gruptan hangisine** ait olduğunu bildirir.
* **Zaman Çoklaması:** P-SCH gibi, her slotun sadece **ilk 256 çiplik** diliminde yüksek güçle iletilir. Geri kalan kısımda kapalıdır.
* **Scrambling Yoktur:** Hücrenin scrambling kodu ile çırpılmaz.

## SSC ($C_{ssc,k}$) Matematiksel Üretimi (3GPP TS 25.213)
S-SCH üzerinde her slotta 16 farklı **Secondary Synchronization Code (SSC)** dizisinden biri iletilir. Bu 16 dizi ($C_{ssc,1}$ ila $C_{ssc,16}$), Hadamard matrisi satırları ile bir temel dizinin eleman eleman çarpılmasıyla (modülasyonuyla) oluşturulur.

### 1. Temel Dizi $z$ (Boyut: 256 çip)
Öncelikle PSC üretiminde kullanılan temel $Golay$ dizisi $b = a$ (bkz. [[concepts/P-SCH|P-SCH]]) ve bir işaret katsayıları dizisi $K$ kullanılarak 256 çiplik $z$ dizisi oluşturulur:
$$K = \langle 1, 1, 1, -1, 1, 1, -1, -1, 1, -1, 1, -1, -1, -1, -1, -1 \rangle$$
$$z(i) = b(i \bmod 16) \times K(i \text{ div } 16), \quad i = 0, \dots, 255$$
Burada $b$ dizisi, $K$ dizisinin elemanları ile modüle edilerek 256 çiplik gürültü benzeri bir temel dizi üretilmiş olur.

### 2. Hadamard Matrisi ve SSC Dizileri
16 adet SSC dizisi ($C_{ssc,k}$, $k=1, \dots, 16$), $H_{256}$ Hadamard matrisinin $m = 16 \times (k-1)$ indexli satırları ($h_m$) ile temel dizi $z$'nin çarpımı ve kompleks düzleme taşınması ile elde edilir:
$$C_{ssc,k}(i) = (1 + j) \times h_{16(k-1)}(i) \times z(i), \quad i = 0, \dots, 255$$

Hadamard matrisi $H_{256}$ satırları birbirine dik (orthogonal) olduğu için, üretilen 16 adet SSC dizisi de birbirine tamamen diktir. Alıcı cihaz, gelen 256 çiplik sinyali 16 paralel correlator (veya Fast Hadamard Transform - FHT) üzerinden geçirerek hangi SSC'nin iletildiğini tek seferde bulabilir.

## Comma-Free Kodlama Yapısı
S-SCH üzerinde bir radyo çerçevesi (15 slot) boyunca iletilen 15 adet SSC'nin sırası rastgele değildir. 3GPP TS 25.213 Table 4'te tanımlanan **64 adet Comma-Free Kod Kelimesi (Codeword)** arasından seçilir.

* Her scrambling kod grubu (0-63) için 15 slot boyunca iletilecek SSC indeksleri sabittir.
* **Örnek Kod Kelimesi:** Grup 0 için slot örüntüsü: $\langle 1, 1, 2, 8, 9, 10, 15, 8, 10, 16, 2, 7, 15, 7, 16 \rangle$ (buradaki rakamlar SSC indeksleridir).
* **Comma-Free Özelliği:** Bu 64 kod kelimesinin hiçbirinin döngüsel kaydırılmış (cyclic shift) hali:
  1. Başka bir kod kelimesine eşit olamaz.
  2. Kendisinin başka bir döngüsel kaymasına eşit olamaz.

### Alıcıda Frame Sınırı ve Kod Grubu Analizi
1. Cihaz, bir frame (15 slot) boyunca her slotun başında iletilen SSC'yi paralel olarak korele eder ve 15 slotluk bir SSC dizisi elde eder (Örn. $\langle 8, 9, 10, 15, 8, 10, 16, 2, 7, 15, 7, 16, 1, 1, 2 \rangle$).
2. Elde edilen bu 15'li dizi, 64 kod kelimesinin tüm döngüsel kaymalarıyla (toplam $64 \times 15 = 960$ olasılık) karşılaştırılır.
3. Eşleşme sağlandığında:
   * Eşleşen kod kelimesinin satır numarası (0-63), hücrenin **Scrambling Kod Grubu**'nu verir.
   * Eşleşmenin sağlandığı kayma miktarı (shift), frame başlangıcını (**Frame Boundary**) yani 1. slotun nerede olduğunu tam olarak belirtir.

## İlgili Konular
* [[concepts/P-SCH|P-SCH]]
* [[concepts/Scrambling Code|Scrambling Code]]
* [[concepts/WCDMA Cell Search|WCDMA Cell Search]]
