---
title: CPICH
category: concepts
tags: [wcdma, physical-layer, cpich, pilot, measurements]
aliases: [Common Pilot Channel]
sources: [CLAUDE.md]
summary: Common Pilot Channel (CPICH) özellikleri, $C_{ch,256,0}$ OVSF yayma kodu kullanımı, scrambling code tespiti ve RSCP/Ec-No sinyal kalitesi ölçümleri.
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

# CPICH (Common Pilot Channel)

**CPICH (Common Pilot Channel - Ortak Pilot Kanalı)**, WCDMA downlink sisteminde sürekli olarak yayınlanan, verisiz (yalnızca sabit semboller taşıyan) ve hücrenin sinyal kalitesini ölçmek, kanal kestirimi yapmak ve scrambling kodunu netleştirmek için kullanılan en kritik referans fiziksel kanaldır.

## Temel Özellikleri
* **Sürekli İletim:** Diğer kontrol kanallarının (SCH, P-CCPCH) aksine CPICH, çerçeve (frame) boyunca 15 slotun tamamında **kesintisiz olarak** yayınlanır.
* **Sabit Spreading Kodu:** CPICH her zaman **$C_{ch,256,0}$** OVSF kodu ile yayılır. Bu kod, OVSF kod ağacının en üstündeki ilk koddur ve tamamı 1'lerden oluşur ($\langle 1, 1, \dots, 1 \rangle$ - 256 adet).
* **Sabit Pilot Semboller:** Kanal üzerinden iletilen ham veri sabittir. Sembol seviyesinde her zaman **$A = 1 + j$** (veya bit seviyesinde sürekli ardışık sıfırlar) iletilir.
* **Scrambling Uygulanır:** CPICH, SCH kanallarının aksine hücrenin **Primary Scrambling Code**'u ([[concepts/Scrambling Code|Scrambling Code]]) ile çırpılır.

## Hücre Aramadaki Rolü (Scrambling Code Tespiti)
Hücre aramanın 3. adımında (bkz. [[concepts/WCDMA Cell Search|WCDMA Cell Search]]), cihaz S-SCH üzerinden hücrenin ait olduğu scrambling kod grubunu (0-63) tespit etmiştir.
* Her kod grubunda tam olarak **8 adet Primary Scrambling Code** bulunur (Grup $g$ için kodlar $8g$ ila $8g+7$).
* Alıcı cihaz, kaydettiği IQ verisi üzerinde bu gruptaki 8 olası scrambling kodunu tek tek dener (descrambling).
* Descrambling işleminden sonra bilinen CPICH kodu $C_{ch,256,0}$ ile despreading yapar.
* Hangi scrambling kodu uygulandığında CPICH çıkışında çok yüksek bir enerji (korelasyon pik noktası) elde edilirse, hücrenin **Primary Scrambling Code**'unun o olduğu kesinleşir.

## Sinyal Kalitesi Ölçümleri (RSCP ve $E_c/N_0$)
CPICH sabit güçte iletildiği için, mobil cihazlar (UE) ve tarayıcılar (Scanner) tarafından hücrenin kapsama alanı ve sinyal kalitesi doğrudan CPICH üzerinden ölçülür. Bu ölçümler handover ve hücre seçimi kararlarında kullanılır.

### 1. RSCP (Received Signal Code Power)
RSCP, alıcı tarafından **yalnızca CPICH kanalı üzerinden alınan mutlak sinyal gücüdür**.
* Sinyalin despread edildikten sonra ölçülen net gücüdür.
* dBm cinsinden ifade edilir. Hücre kapsama sınırını belirlemede kullanılır (Örn. -95 dBm iyi, -115 dBm zayıf sinyal).

### 2. $E_c/N_0$ (Energy per Chip over Noise Spectral Density)
$E_c/N_0$, **sinyal kalitesini (gürültü oranını)** gösteren bir değerdir.
* Toplam alınan güç spektral yoğunluğuna ($I_0$ veya $RSSI$) bölünmüş çip enerjisidir.
* Genellikle negatif bir dB değeridir.
* WCDMA CDMA tabanlı bir sistem olduğundan, ortamda çok fazla hücre (girişim/interference) varsa RSCP yüksek olsa bile $E_c/N_0$ çok düşük olabilir ve bu durum bağlantı kopmalarına yol açar. ^[inferred]
* Tipik sınır değerleri: $E_c/N_0 > -12 \text{ dB}$ (kabul edilebilir), $E_c/N_0 < -15 \text{ dB}$ (yüksek girişim/başarısız decode riski).

## İlgili Konular
* [[concepts/Channelization Code|Channelization Code (OVSF)]]
* [[concepts/Scrambling Code|Scrambling Code]]
* [[concepts/WCDMA Cell Search|WCDMA Cell Search]]
