---
source: "wcdma_cellsearch analysis"
created_date: 2026-06-03
tags:
  - cells
  - wcdma
  - uarfcn_10813
  - decoded_sibs
  - operator_turkcell
---

# WCDMA Cell: UARFCN 10813 - SC 483

Bu sayfa, LimeSDR Mini üzerinden alınan ham IQ capture verisinin offline analizi sonucunda elde edilen WCDMA hücresinin teknik parametrelerini barındırır. Analiz işlemi [[WCDMA Cell Search]] ve [[CPICH]] despreading matematiksel modellerini kullanır.

## Hücre Parametreleri

| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| **UARFCN** | 10813 | 3GPP Kanal Numarası |
| **Frekans** | 2160.2 MHz | Merkez Taşıyıcı Frekansı |
| **Primary Scrambling Code (PSC)** | [[Scrambling Code|483]] | Hücre Tanımlama Kodu (0 - 511) |
| **Code Group** | 60 | [[Scrambling Code|Scrambling Code Grubu]] (0 - 63) |
| **CPICH RSCP** | -35.35 dBm | Ortak Pilot Kanalı Alış Gücü (Received Signal Code Power) |
| **CPICH Ec/No** | -4.14 dB | Spektral Sürültü/Sinyal Oranı |
| **Slot Timing** | 1098 | Slot Sınır Örnek Endeksi (5120 sample içinde) |
| **Frame Timing** | 21598 | Çerçeve Başlangıç Örnek Endeksi (76800 sample içinde) |
| **Frekans Düzeltme** | 2402000.0 Hz | SDR ppm kayması düzeltme değeri |
| **Analiz Zamanı** | 2026-06-03T07:54:03Z | Verinin capture edilme zaman damgası |

## RRC Sistem Bilgileri (BCH Decode - Faz 4)

BCH transport kanalı başarıyla çözülmüş ve UPER ASN.1 şeması yardımıyla Sistem Bilgi Blokları (SIB) ayrıştırılmıştır.

### Servis Sağlayıcı ve Hücre Parametreleri
* **Mobil Ülke Kodu (MCC):** 286 (Türkiye)
* **Mobil Şebeke Kodu (MNC):** 01 (Turkcell)
* **Hücre Kimliği (Cell Identity):** 139474100
* **RNC ID:** 2128
* **Yerel Hücre ID (Local Cell ID):** 13492

### Komşu WCDMA Hücreleri (SIB11 - Inter-Frequency)
Aşağıdaki hücreler SIB11 mesajı içerisinde komşu hücre olarak bildirilmiştir:

| Komşu ID | UARFCN | Frekans | Komşu Hücre PSC | Wiki Sayfası |
|----------|--------|---------|-----------------|--------------|
|        0 |  10838 | 2165.2 MHz |             480 | UARFCN 10838 SC 480 |
|        1 |   2997 |  937.0 MHz |             100 | UARFCN 2997 SC 100 |
|        2 |  10838 | 2165.2 MHz |              94 | UARFCN 10838 SC 94 |
|        3 |  10838 | 2165.2 MHz |             234 | UARFCN 10838 SC 234 |
|        4 |  10838 | 2165.2 MHz |             147 | UARFCN 10838 SC 147 |
|        5 |  10838 | 2165.2 MHz |             151 | UARFCN 10838 SC 151 |
|        6 |  10838 | 2165.2 MHz |              73 | UARFCN 10838 SC 73 |
|        7 |   2997 |  937.0 MHz |             182 | UARFCN 2997 SC 182 |
|        8 |  10838 | 2165.2 MHz |             453 | UARFCN 10838 SC 453 |
|      N/A |  10838 | 2165.2 MHz |             212 | UARFCN 10838 SC 212 |
|       12 |   2997 |  937.0 MHz |             259 | UARFCN 2997 SC 259 |
|       13 |  10838 | 2165.2 MHz |             436 | UARFCN 10838 SC 436 |
|       14 |  10838 | 2165.2 MHz |             363 | UARFCN 10838 SC 363 |
|       15 |   2997 |  937.0 MHz |              59 | UARFCN 2997 SC 59 |
|       16 |   2997 |  937.0 MHz |              83 | UARFCN 2997 SC 83 |
|       16 |   2997 |  937.0 MHz |              77 | UARFCN 2997 SC 77 |
|       20 |   2997 |  937.0 MHz |             266 | UARFCN 2997 SC 266 |

### Komşu LTE Frekansları (SIB19 - Inter-RAT)
Hücrenin SIB19 içerisinde yayınladığı E-UTRA komşu taşıyıcı frekansları:

| EARFCN | LTE Bandı | Frekans | Bant Genişliği | Öncelik | Min Alış Seviyesi |
|--------|-----------|---------|----------------|---------|-------------------|
|    550 | Band 1     | 2165.0 MHz | 20 MHz (100 RBs) |       5 |  -62 dBm |
|    100 | Band 1     | 2120.0 MHz | 20 MHz (100 RBs) |       5 |  -62 dBm |
|   1651 | Band 3     | 1850.1 MHz | 20 MHz (100 RBs) |       5 |  -62 dBm |
|   2850 | Band 7     | 2630.0 MHz | 20 MHz (100 RBs) |       5 |  -62 dBm |
|   6400 | Band 20    |  816.0 MHz | 10 MHz (50 RBs) |       4 |  -62 dBm |

### Çapraz RAT ve Harici Doğrulama
> [!NOTE]
> **Doğrulama:** UARFCN 2997 bağımsız iki kaynakta (WCDMA SIB11 + harici GSM SI2quater) komşu olarak doğrulanmıştır.


## Mimari İlişkiler
* **Erişim Metodu:** [[WCDMA Genel]] CDMA teknolojisi ile aynı frekansta kod bölmeli çoğullama.
* **Senkronizasyon:** P-SCH ([[P-SCH]]) ile slot senkronizasyonu ve S-SCH ([[S-SCH]]) ile frame senkronizasyonu tamamlanmıştır.
* **Pilot Sinyali:** [[CPICH]] kanalı SF=256 OVSF kodu ile sürekli olarak yayınlanmaktadır.
* **BCH Çözümleme:** [[BCH]] transport kanalı üzerinden MIB, SIB3, SIB5, SIB11 ve SIB19 çözümlenmiştir.

---
*Bu sayfa wcdma_wiki_helper.py tarafından otomatik olarak üretilmiştir.*
