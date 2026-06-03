---
source: "wcdma_cellsearch analysis"
created_date: 2026-06-03
tags:
  - cells
  - wcdma
  - uarfcn_10838
---

# WCDMA Cell: UARFCN 10838 - SC 59

Bu sayfa, LimeSDR Mini üzerinden alınan ham IQ capture verisinin offline analizi sonucunda elde edilen WCDMA hücresinin teknik parametrelerini barındırır. Analiz işlemi [[WCDMA Cell Search]] ve [[CPICH]] despreading matematiksel modellerini kullanır.

## Hücre Parametreleri

| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| **UARFCN** | 10838 | 3GPP Kanal Numarası |
| **Frekans** | 2165.2 MHz | Merkez Taşıyıcı Frekansı |
| **Primary Scrambling Code (PSC)** | [[Scrambling Code|59]] | Hücre Tanımlama Kodu (0 - 511) |
| **Code Group** | 7 | [[Scrambling Code|Scrambling Code Grubu]] (0 - 63) |
| **CPICH RSCP** | -62.12 dBm | Ortak Pilot Kanalı Alış Gücü (Received Signal Code Power) |
| **CPICH Ec/No** | -30.95 dB | Spektral Sürültü/Sinyal Oranı |
| **Slot Timing** | 1946 | Slot Sınır Örnek Endeksi (5120 sample içinde) |
| **Frame Timing** | 42911 | Çerçeve Başlangıç Örnek Endeksi (76800 sample içinde) |
| **Frekans Düzeltme** | 2400000.0 Hz | SDR ppm kayması düzeltme değeri |
| **Analiz Zamanı** | 2026-06-02T13:41:23Z | Verinin capture edilme zaman damgası |

## Mimari İlişkiler
* **Erişim Metodu:** [[WCDMA Genel]] CDMA teknolojisi ile aynı frekansta kod bölmeli çoğullama.
* **Senkronizasyon:** P-SCH ([[P-SCH]]) ile slot senkronizasyonu ve S-SCH ([[S-SCH]]) ile frame senkronizasyonu tamamlanmıştır.
* **Pilot Sinyali:** [[CPICH]] kanalı SF=256 OVSF kodu ile sürekli olarak yayınlanmaktadır.
* **BCH Çözümleme:** [[BCH]] transport kanalı üzerinden MIB, SIB3, SIB5, SIB11 ve SIB19 çözümlenmiştir.

---
*Bu sayfa wcdma_wiki_helper.py tarafından otomatik olarak üretilmiştir.*
