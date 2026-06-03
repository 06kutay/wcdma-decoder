---
title: WCDMA Cell Search
category: concepts
tags: [wcdma, physical-layer, cell-search, synchronization]
aliases: [Cell Search, 3-Step Cell Search]
sources: [CLAUDE.md]
summary: WCDMA alıcılarında kullanılan 3 adımlı hücre arama (Cell Search) algoritması: slot senkronizasyonu, frame senkronizasyonu ve scrambling code tespiti aşamaları.
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

# WCDMA Cell Search (Hücre Arama)

**WCDMA Cell Search (Hücre Arama)**, mobil cihazın (UE) veya tarayıcının (SDR) açık alanda tarama yaparken, ortamdaki WCDMA baz istasyonlarının sinyallerini yakalayıp, zamanlama sınırlarını bulup, veri kanalını decode edebilmek için uyguladığı **3 adımlı senkronizasyon algoritmasıdır**.

Aşağıdaki şemada, 3 adımlı hücre arama sürecinin girdileri, işlemleri ve çıktıları uçtan uca gösterilmiştir:

```
Hücre Arama Akış Şeması:
+--------------------------------------------------------------------------+
| Girdi: Sürekli IQ Sinyali (SDR Örnekleri)                                |
+--------------------------------------------------------------------------+
                                    |
                                    v
+--------------------------------------------------------------------------+
| ADIM 1: Slot Senkronizasyonu (PSC Eşleştirilmiş Filtre)                  |
| - Gelen sinyal ile bilinen PSC (C_psc) çapraz korelasyona sokulur.       |
| - 2560 çiplik periyotlardaki korelasyon pikleri doğrulanır.              |
+--------------------------------------------------------------------------+
                                    |
                                    v
  [Çıktı 1: Slot Başlangıç Zamanlaması (0.667 ms Sınırları)]
                                    |
                                    v
+--------------------------------------------------------------------------+
| ADIM 2: Frame Senkronizasyonu & Kod Grubu Tespiti (SSC Korelasyonu)     |
| - Her slot başında 16 dikgen SSC kodu paralel olarak korele edilir.      |
| - 15 slot boyunca elde edilen SSC dizisi 64 kod kelimesiyle eşleştirilir.|
+--------------------------------------------------------------------------+
                                    |
                                    v
  [Çıktı 2: Frame Başlangıç Zamanlaması (10 ms Sınırı) & Scrambling Grubu]
                                    |
                                    v
+--------------------------------------------------------------------------+
| ADIM 3: Scrambling Code Tespiti (CPICH Pilot Korelasyonu)                |
| - Tespit edilen gruptaki 8 olası Scrambling Kodu sinyale sırayla uygulanır.|
| - CPICH OVSF kodu (C_ch,256,0) ile despreading yapılarak güç ölçülür.   |
+--------------------------------------------------------------------------+
                                    |
                                    v
  [Çıktı 3: Hücreye Özgü Primary Scrambling Code (0-511) & Tam Hizalama]
                                    |
                                    v
+--------------------------------------------------------------------------+
| Çözüm: P-CCPCH kanalı despread edilir ve BCH sistem bilgileri okunur.    |
+--------------------------------------------------------------------------+
```

---

## Adım Adım Hücre Arama Detayları

### Adım 1: Slot Senkronizasyonu (Slot Synchronization)
* **Yöntem:** Alıcı, aralıksız olarak gelen ham IQ verisini dünyadaki tüm WCDMA hücrelerinde ortak olan **PSC (Primary Synchronization Code)** ile çapraz ilintiye (cross-correlation) sokar.
* **Matematik:** $C_{psc}$ dizisi ile veri arasındaki matched filter korelasyon tepe noktaları aranır.
* **Gereklilik:** Bu adımda scrambling kodu veya frame yapısı bilgisine ihtiyaç duyulmaz.
* **Çıktı:** **Slot sınırları (Slot Timing).** Cihaz artık her bir 2560 çiplik zaman diliminin tam olarak nerede başlayıp bittiğini bilmektedir.

### Adım 2: Frame Senkronizasyonu ve Kod Grubu Tespiti
* **Yöntem:** Slot sınırları bilindiği için, alıcı her slotun ilk 256 çiplik kısmına odaklanır. Bu kısım, **S-SCH (Secondary Synchronization Channel)** üzerinden gönderilen 16 adet dikgen SSC kodundan biri ile modüle edilmiştir. Cihaz 16 paralel korelatör kullanarak her slotta iletilen SSC indeksini bulur.
* **Matematik:** 15 ardışık slot boyunca toplanan SSC örüntüsü, standardın Comma-Free Kod tablosundaki 64 benzersiz kod kelimesiyle döngüsel olarak eşleştirilir.
* **Çıktı:** 
  1. **Frame Sınırı (Frame Boundary):** 10 ms'lik radyo çerçevesinin başlangıç noktası (yani 1. slotun yeri).
  2. **Scrambling Kod Grubu:** Hücrenin kullandığı birincil scrambling kodunun ait olduğu grup numarası ($g \in [0, 63]$).

### Adım 3: Scrambling Code Tespiti
* **Yöntem:** Kod grubu $g$ bilindiği için, hücrenin kullandığı gerçek kod bu gruptaki 8 olası primary scrambling kodundan biridir ($8g$ ila $8g+7$). Cihaz, IQ verisini bu 8 scrambling kodu ile sırayla descramble eder ve ardından her zaman $C_{ch,256,0}$ (CPICH OVSF kodu) ile yayılan pilot kanalı arar.
* **Matematik:** Descramble edilmiş verinin CPICH ile despread edilmesiyle elde edilen sinyal gücü ölçülür:
  $$E_{cpich}(n) = \left| \sum_{i=0}^{255} (r_{descramble, n}(i) \times C_{ch,256,0}(i)) \right|^2$$
* **Karar:** En yüksek enerjiyi ($E_{cpich}$) veren $n$ kodu, hücrenin birincil scrambling kodu olarak kabul edilir.
* **Çıktı:** Hücreye özgü **Primary Scrambling Code (PSC)**.

## Hücre Aramadan Sonrası: Sistem Bilgilerinin Decode Edilmesi
3 adım başarıyla tamamlandıktan sonra cihaz hücreye tamamen senkronize olmuştur.
1. Hücrenin Primary Scrambling Code'u kullanılarak veri kanalları descramble edilir.
2. Sabit $C_{ch,256,1}$ OVSF kodu kullanılarak **[[concepts/P-CCPCH|P-CCPCH]]** kanalı despread edilir.
3. Çıkan veriler **[[concepts/BCH|BCH]]** çözücüye gönderilerek hücrenin **MIB** ve **SIB11** gibi sistem bilgileri decode edilir.

## İlgili Konular
* [[concepts/P-SCH|P-SCH]]
* [[concepts/S-SCH|S-SCH]]
* [[concepts/CPICH|CPICH]]
* [[concepts/Scrambling Code|Scrambling Code]]
* [[concepts/P-CCPCH|P-CCPCH]]
