---
title: Sistem Mimarisi
category: synthesis
tags: [wcdma, architecture, offline, python, SoapySDR, LimeSDR]
aliases: [System Architecture, Sistem Mimarisi]
sources: [CLAUDE.md]
summary: WCDMA Komşu Hücre Analizörü yazılım mimarisi, offline işlem modeli, LimeSDR SoapySDR entegrasyonu ve modüler tasarım prensipleri.
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

# Sistem Mimarisi (Offline İşlem Modeli)

WCDMA Komşu Hücre Analizörü projesi, yüksek hızlı radyo frekansı (RF) sinyali yakalama (IQ capture) süreci ile karmaşık sayısal sinyal işleme (DSP/Decoding) süreçlerini birbirinden tamamen ayıran **Offline Yürütme Modeline** dayanmaktadır.

Bu mimari tasarım, GNU Radio veya harici ağır SDR framework'lerine bağımlı olmadan, **saf Python (numpy/scipy)** kütüphaneleri ile taşınabilir, yüksek performanslı ve hata ayıklaması kolay bir offline analiz sistemi sunar.

---

## 1. Donanım ve Yazılım Katmanları (Modüler Mimari)

Sistem, fiziksel donanımdan RRC katmanı çıktısına kadar 4 bağımsız katmana ayrılmıştır:

```
+-------------------------------------------------------------+
| RRC KATMANI (UPER ASN.1 Çözücü - python-asn1tools)          |
| - SIB3 (Hücre ID), SIB11 (Komşular), SIB19 (LTE/GSM)        |
+-------------------------------------------------------------+
                              ^
                              | (Birleştirilmiş SIB Bit Dizisi)
+-------------------------------------------------------------+
| L2 / HATA DÜZELTME KATMANI (Saf Python / Numpy)              |
| - BCH Segment Birleştirici, CRC16, Viterbi 1/2 Rate Çözücü  |
+-------------------------------------------------------------+
                              ^
                              | (Descramble/Despread Sembolleri)
+-------------------------------------------------------------+
| L1 / DSP KATMANI (Saf Python - numpy, scipy, matplotlib)    |
| - P-SCH (Slot Sync), S-SCH (Frame Sync), CPICH (PSC Detekt) |
+-------------------------------------------------------------+
                              ^
                              | (Diskteki .bin IQ Örnek Dosyası)
+-------------------------------------------------------------+
| SDR / RF KATMANI (LimeSDR Mini + python3-soapysdr)          |
| - Band 1 (LNAH), Band 8 (LNAW) RF port ve kazanç ayarları   |
+-------------------------------------------------------------+
```

---

## 2. Offline İşlem Modelinin Avantajları
1. **İşlem Yükü Dengesi:** Gerçek zamanlı (Real-time) WCDMA decode işlemi yüksek CPU gücü ve düşük gecikmeli (low-latency) işletim sistemi desteği gerektirir. Offline modelde, SDR sinyali milisaniyeler seviyesinde yakalayıp kaydeder; decoding ise arka planda CPU limitlerine takılmadan güvenli bir şekilde offline olarak tamamlanır.
2. **Tekrarlanabilirlik (Repeatability):** Alınan ham RF sinyali diskte `.bin` formatında saklandığı için, kod üzerinde yapılan bir değişiklik veya hata düzeltmesi, birebir aynı ham sinyal girdisi üzerinde defalarca test edilebilir.
3. **Kolay Debugging:** Sinyal işlemenin her adımında (Örn: P-SCH korelasyon piki, CPICH takımyıldız - constellation şeması) veriler `matplotlib` ile görselleştirilerek sistemin doğruluğu kolayca izlenebilir.

---

## 3. SDR Entegrasyonu ve Veri Yakalama Parametreleri
SDR donanımı olarak **LimeSDR Mini** (USB 3.0, FT601 denetleyici, LMS7002M transistör) kullanılır. Entegrasyon, venv ortamına symlink edilmiş olan sistem bağımlı **SoapySDR Python binding**'i ile sağlanır.

* **Örnekleme Hızı (Sample Rate):** Sabit çip hızı olan 3.84 Mcps'in tam olarak 2 katı olan **7.68 Msps** seçilir. Bu, Nyquist teoremini karşılar ve zamanlama kaymalarını (timing drift) telafi etmek için idealdir.
* **RF Port Seçimi (Critical!):** 
  * Band 1 (2140 MHz) $\implies$ **LNAH** portu.
  * Band 8 (945 MHz) $\implies$ **LNAW** portu.
* **Veri Tipi:** 32-bit kayan noktalı (float32) kompleks IQ örnekleri ($I_0, Q_0, I_1, Q_1, \dots$).
* **Kayıt Süresi:** Bir adet SIB paketinin (özellikle büyük olan SIB11) havada en az 1-2 kez tam olarak yayınlanmasını garanti etmek amacıyla minimum **1 ila 2 saniye** kesintisiz IQ kaydı yapılır. 1 saniyelik 7.68 Msps float32 IQ kaydı diskte yaklaşık **61.4 MB** alan kaplar:
  $$\text{Boyut} = 7,680,000 \text{ örnek} \times 8 \text{ byte (4 I + 4 Q)} \approx 61.44 \text{ MB}$$

---

## 4. Modüler Kod Organizasyonu
Faz 2 ve sonraki aşamalarda yazılacak Python kod yapısı aşağıdaki modüllerden oluşacaktır:
* `capture.py`: SoapySDR kullanarak seçilen UARFCN frekansından `.bin` dosyasına IQ kaydı yapan modül.
* `sync.py`: 3 adımlı Hücre Arama algoritmasını (P-SCH, S-SCH, CPICH) uygulayan DSP modülü.
* `pccpch.py`: P-CCPCH kanalını despread edip QPSK demodülasyon ile ham bitleri çıkaran modül.
* `bch.py`: Viterbi kod çözücüyü, CRC16 kontrolünü ve SIB birleştirmeyi üstlenen L2 modülü.
* `rrc.py`: `asn1tools` ile SIB ASN.1 dizisini okuyup CID, LAC ve komşu hücre listelerini parse eden modül.

## İlgili Konular
* [[synthesis/WCDMA Decode Zinciri|WCDMA Decode Zinciri]]
* [[concepts/WCDMA Bandlar|WCDMA Bandlar]]
* [[concepts/WCDMA Cell Search|WCDMA Cell Search]]
