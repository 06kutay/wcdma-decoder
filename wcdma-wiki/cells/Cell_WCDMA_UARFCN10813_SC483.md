---
source: "wcdma_cellsearch analysis"
created_date: 2026-06-11
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
| **CPICH RSCP** | -34.57 dBm | Ortak Pilot Kanalı Alış Gücü (Received Signal Code Power) |
| **CPICH Ec/No** | -4.16 dB | Spektral Sürültü/Sinyal Oranı |
| **Slot Timing** | 5014 | Slot Sınır Örnek Endeksi (5120 sample içinde) |
| **Frame Timing** | 30616 | Çerçeve Başlangıç Örnek Endeksi (76800 sample içinde) |
| **Frekans Düzeltme** | 2400883.635063506 Hz | SDR ppm kayması düzeltme değeri |
| **Analiz Zamanı** | 2026-06-11T13:37:08Z | Verinin capture edilme zaman damgası |

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
|        1 |   2997 |  937.0 MHz |             106 | UARFCN 2997 SC 106 |
|        2 |   2997 |  937.0 MHz |              65 | UARFCN 2997 SC 65 |
|        3 |  10838 | 2165.2 MHz |             424 | UARFCN 10838 SC 424 |
|        4 |   2277 |  793.0 MHz |             100 | UARFCN 2277 SC 100 |
|        5 |  10838 | 2165.2 MHz |              94 | UARFCN 10838 SC 94 |
|        6 |  10838 | 2165.2 MHz |             234 | UARFCN 10838 SC 234 |
|        7 |  10838 | 2165.2 MHz |             147 | UARFCN 10838 SC 147 |
|        8 |  10838 | 2165.2 MHz |             151 | UARFCN 10838 SC 151 |
|      N/A |  10838 | 2165.2 MHz |             362 | UARFCN 10838 SC 362 |
|      N/A |  10838 | 2165.2 MHz |             299 | UARFCN 10838 SC 299 |

### Komşu LTE Frekansları (SIB19 - Inter-RAT)
Hücrenin SIB19 içerisinde yayınladığı E-UTRA komşu taşıyıcı frekansları:

| EARFCN | LTE Bandı | Frekans | Bant Genişliği | Öncelik | Min Alış Seviyesi |
|--------|-----------|---------|----------------|---------|-------------------|
|    100 | Band 1     | 2120.0 MHz | 20 MHz (100 RBs) |       5 |  -62 dBm |
|    550 | Band 1     | 2165.0 MHz | 20 MHz (100 RBs) |       5 |  -62 dBm |
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
