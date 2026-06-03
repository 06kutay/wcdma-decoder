---
title: WCDMA Bandlar
category: concepts
tags: [wcdma, bands, turkey, operators, frequency-plan]
aliases: [WCDMA Bandlar, Türkiye 3G Bandları, UMTS Bands]
sources: [CLAUDE.md]
summary: Türkiye'de kullanılan WCDMA (3G) frekans bandları (Band 1 ve Band 8) ve Turkcell, Vodafone, Türk Telekom operatör dağılımları.
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

# WCDMA Bandlar (Türkiye Operatör Dağılımları)

Türkiye'de WCDMA (3G / UMTS) mobil iletişim şebekeleri, Bilgi Teknolojileri ve İletişim Kurumu (BTK) tarafından tahsis edilen frekans lisanslarına göre **iki ana frekans bandı** üzerinden çalışmaktadır.

---

## 1. Band 1 (IMT 2100 MHz Bandı)
* **Karakteristik:** Yüksek frekanslıdır. Şehir merkezlerinde yüksek kapasite ve veri hızları sunar. Ancak bina nüfuziyeti (sinyal geçişi) ve kapsama alanı mesafesi düşüktür.
* **Kanal Bant Genişliği:** Operatörler bu bantta genellikle **2 veya 3 adet 5 MHz'lik taşıyıcı kanalı** yan yana çalıştırır.
* **Operatör Frekans Tahsisleri:**
  * **Turkcell:** 2140 MHz civarında (Örn. UARFCN DL: **10712**, **10737**)
  * **Vodafone:** 2125 MHz civarında (Örn. UARFCN DL: **10638**, **10662**)
  * **Türk Telekom:** 2115 MHz civarında (Örn. UARFCN DL: **10562**, **10587**)

---

## 2. Band 8 (GSM 900 MHz Bandı)
* **Karakteristik:** Düşük frekanslıdır. Çok uzun kapsama alanı mesafesi sağlar ve binaların derinliklerine kadar sinyal ulaştırabilir (Kırsal alanlar ve kapalı otoparklar için idealdir).
* **Kısıtlama:** 900 MHz bandı esasen 2G GSM şebekeleri için tasarlandığından, bu banttaki spektrum genişliği çok dardır. Operatörler bu bantta genellikle **sadece 1 adet 5 MHz'lik WCDMA taşıyıcı kanalı** çalıştırabilir.
* **Operatör Frekans Tahsisleri:**
  * **Turkcell:** 952.4 MHz civarında (Örn. UARFCN DL: **3062**)
  * **Vodafone:** 945.0 MHz civarında (Örn. UARFCN DL: **3025**)
  * **Türk Telekom:** 937.6 MHz civarında (Örn. UARFCN DL: **2988**)

---

## Türkiye WCDMA Operatör Spektrum Özet Tablosu

Aşağıdaki tablo, Türkiye'deki operatörlerin WCDMA yayını yaptıkları bilinen nominal UARFCN kodlarını ve merkez downlink frekanslarını özetlemektedir:

| Operatör | Band | Nominal UARFCN (DL) | Merkez DL Frekansı | Rolü ve Karakteristiği |
|---|---|---|---|---|
| **Turkcell** | Band 1 | 10712 / 10737 | 2142.4 MHz / 2147.4 MHz | Şehir içi ana 3G kapasite taşıyıcıları |
| **Turkcell** | Band 8 | 3062 | 952.4 MHz | Kırsal alan ve indoor (bina içi) geniş kapsama |
| **Vodafone** | Band 1 | 10638 / 10662 | 2127.6 MHz / 2132.4 MHz | Şehir içi ana 3G kapasite taşıyıcıları |
| **Vodafone** | Band 8 | 3025 | 945.0 MHz | Kırsal alan ve indoor geniş kapsama |
| **Türk Telekom** | Band 1 | 10562 / 10587 | 2112.4 MHz / 2117.4 MHz | Şehir içi ana 3G kapasite taşıyıcıları |
| **Türk Telekom** | Band 8 | 2988 | 937.6 MHz | Kırsal alan ve indoor geniş kapsama |

---

## SDR Tarayıcı LimeSDR Mini Donanım Konfigürasyonu
WCDMA komşu analizör projesinde kullanılacak olan **LimeSDR Mini** donanımının RF girişleri bu iki bandın frekanslarına göre optimize edilmelidir:
* **Frekans Sınırı:** 1.5 GHz eşik değeridir.
* **Band 1 (2100 MHz):** Frekans > 1.5 GHz olduğu için RF kanal seçimi **LNAH (High Band RX Input)** portuna yapılmalıdır.
* **Band 8 (900 MHz):** Frekans < 1.5 GHz olduğu için RF kanal seçimi **LNAW (Wide Band / Low Band RX Input)** portuna yapılmalıdır.

RF port konfigürasyonunun doğru yapılması, sinyal hassasiyetini ve dolayısıyla yakalanabilecek komşu hücre sayısını doğrudan arttırır. ^[inferred]

## İlgili Konular
* [[concepts/WCDMA ARFCN|WCDMA ARFCN (UARFCN)]]
* [[references/UARFCN Frekans Tablosu|UARFCN Frekans Tablosu]]
* [[synthesis/Sistem Mimarisi|Sistem Mimarisi]]
