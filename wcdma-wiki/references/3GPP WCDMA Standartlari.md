---
title: 3GPP WCDMA Standartları
category: references
tags: [wcdma, references, standards, 3gpp, physical-layer, rrc]
aliases: [3GPP Standartları, 3GPP Standards]
sources: [CLAUDE.md]
summary: WCDMA offline decode projesinde temel alınan 3GPP TS 25 serisi teknik standartlarının dokümantasyon haritası.
provenance:
  extracted: 0.98
  inferred: 0.02
  ambiguous: 0.00
base_confidence: 0.95
lifecycle: draft
lifecycle_changed: 2026-06-02
tier: supporting
created: 2026-06-02T16:16:00Z
updated: 2026-06-02T16:16:00Z
---

# 3GPP WCDMA Standartları Referans Haritası

WCDMA/UMTS projesinde offline sinyal işleme, hata düzeltme ve mesaj ayrıştırma (decode) algoritmaları geliştirilirken, 3GPP (3rd Generation Partnership Project) tarafından yayınlanan resmi standartlar birebir referans alınmıştır.

Aşağıdaki liste, projenin hangi fazında hangi standart dokümanına başvurulacağını gösteren teknik haritadır.

---

## 1. Fiziksel Katman (Physical Layer - L1) Standartları

Fiziksel kanalların yapısı, slot süreleri, yayma (spreading) ve çırpma (scrambling) kodlarının matematiksel üretim kuralları bu grupta tanımlanmıştır.

### **3GPP TS 25.213: Spreading and Modulation (FDD)**
* **Projedeki Yeri:** En kritik L1 dökümanıdır.
* **Referans Alınan Bölümler:**
  * **Section 5.2.2:** Downlink Scrambling Code (Gold Code) üreteci, $x$ ve $y$ polinomları, başlangıç yazmaç değerleri ve kompleks birleştirme formülleri. (bkz. [[concepts/Scrambling Code|Scrambling Code]])
  * **Section 5.2.3.1:** Primary Synchronization Code (PSC) genelleştirilmiş hiyerarşik Golay dizisi formülü. (bkz. [[concepts/P-SCH|P-SCH]])
  * **Section 5.2.3.2:** Secondary Synchronization Code (SSC) Hadamard matrisi modülasyonu ve S-SCH 64 Comma-Free kod kelimesi tablosu (Table 4). (bkz. [[concepts/S-SCH|S-SCH]])
  * **Section 5.2.1:** OVSF (Orthogonal Variable Spreading Factor) kod ağacı üretim kuralları. (bkz. [[concepts/Channelization Code|Channelization Code]])

### **3GPP TS 25.211: Physical Channels and Mapping (FDD)**
* **Projedeki Yeri:** Kanalların zaman dilimlerindeki slot bazlı çip yerleşimlerini tanımlar.
* **Referans Alınan Bölümler:**
  * **Section 5.3.1:** CPICH kanalının sürekli pilot iletimi ve sabit pilot sembolleri ($A = 1+j$). (bkz. [[concepts/CPICH|CPICH]])
  * **Section 5.3.3.1:** P-CCPCH kanalı slot yapısı, ilk 256 çipin boş bırakılması ve kalan 2304 çipteki sembol zamanlaması. (bkz. [[concepts/P-CCPCH|P-CCPCH]])

---

## 2. Kanal Kodlama ve Çoğullama (Multiplexing & L2) Standartları

Sinyalin gürültüye karşı korunması, hata algılama ve çerçevelere bölünmesi kurallarını tanımlar.

### **3GPP TS 25.212: Multiplexing and Channel Coding (FDD)**
* **Projedeki Yeri:** Viterbi çözücü ve CRC aşamalarının doğrulanmasında referans alınır.
* **Referans Alınan Bölümler:**
  * **Section 4.2.1:** CRC16 ($X^{16} + X^{12} + X^5 + 1$) hata algılama kodunun eklenme kuralları. (bkz. [[concepts/BCH|BCH]])
  * **Section 4.2.3.1:** $R=1/2$ oranındaki evrişimsel kodlayıcı (Convolutional Encoder) generator polinomları ($G_0=561$, $G_1=753$ oktal) ve kuyruk bitleri (tail bits). (bkz. [[concepts/BCH|BCH]])
  * **Section 4.2.11:** 20 ms'lik TTI aralığı için 1. serpiştirme (interleaving) matris yapısı.

---

## 3. Üst Katman ve Protokol (RRC - L3) Standartları

Sistem bilgi bloklarının (SIB) yapısı, mesaj içerikleri ve ASN.1 UPER kodlama şemaları burada yer alır.

### **3GPP TS 25.331: Radio Resource Control (RRC) Protocol Specification**
* **Projedeki Yeri:** ASN.1 UPER decode işleminin temel kaynağıdır. `asn1tools` kütüphanesine girdi olarak verilen `.asn` schema dosyasının orijinal kaynağıdır.
* **Referans Alınan Bölümler:**
  * **Section 8.1.1:** BCCH mantıksal kanalı üzerinden SIB segmentasyon, paketleme ve birleştirme (reassembly) durum makineleri. (bkz. [[concepts/WCDMA SIB Genel|WCDMA SIB Genel]])
  * **Section 10.2.48.8.4:** `SystemInformationBlockType3` ASN.1 veri şeması tanımı (Cell ID, LAC). (bkz. [[concepts/WCDMA SIB3|WCDMA SIB3]])
  * **Section 10.2.48.8.11:** `SystemInformationBlockType11` ASN.1 veri şeması tanımı (PSC + UARFCN listesi). (bkz. [[concepts/WCDMA SIB11|WCDMA SIB11]])
  * **Section 11:** Komple UPER (Unaligned Packet Encoding Rules) kodlama prensipleri ve bit bazlı hizalama kuralları.

---

## 4. RF ve Alıcı Hassasiyeti Standartları

### **3GPP TS 25.101: User Equipment (UE) Radio Transmission and Reception (FDD)**
* **Projedeki Yeri:** Frekans bandı hesaplama formülleri ve alıcı duyarlılık sınırlarını tanımlar.
* **Referans Alınan Bölümler:**
  * **Section 5.4.1.1:** Band 1 ve Band 8 downlink/uplink merkez frekansı UARFCN formülleri. (bkz. [[concepts/WCDMA ARFCN|WCDMA ARFCN]])
  * **Section 5.2:** Frekans bant sınırları. (bkz. [[concepts/WCDMA Bandlar|WCDMA Bandlar]])

## İlgili Konular
* [[concepts/WCDMA Genel|WCDMA Genel]]
* [[synthesis/WCDMA Decode Zinciri|WCDMA Decode Zinciri]]
