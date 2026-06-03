---
title: WCDMA Fiziksel Kanallar
category: concepts
tags: [wcdma, physical-layer, channels, signal-processing]
aliases: [Physical Channels]
sources: [CLAUDE.md]
summary: WCDMA downlink fiziksel kanallarının sınıflandırılması, görevleri ve senkronizasyon, pilot, kontrol verisi taşıma işlevlerinin açıklanması.
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

# WCDMA Fiziksel Kanallar

WCDMA downlink yönünde (baz istasyonundan mobil cihaza) iletilen veriler, fiziksel katmanda belirli işlevleri yerine getiren **fiziksel kanallar (Physical Channels)** olarak haritalanır. Bu kanallar, kullanılan kodlar (OVSF ve Scrambling) ve zamanlama slotları ile ayrıştırılır.

## Downlink Fiziksel Kanalların Sınıflandırılması

Aşağıdaki tabloda, bir WCDMA baz istasyonunun yayınladığı ve alıcı cihaz tarafından hücre araması, senkronizasyon ve sistem bilgilerini decode etmek için kullanılan temel downlink kanalları özetlenmiştir:

| Fiziksel Kanal | Açılımı | Taşıma Kanalı (Transport Channel) | Modülasyon / Yapı | Temel Görevi |
|---|---|---|---|---|
| **[[concepts/P-SCH|P-SCH]]** | Primary Synchronization Channel | Yok (Saf Fiziksel) | Slot zamanlı, 256 chip PSC | Slot senkronizasyonu (Hücre Arama Adım 1) |
| **[[concepts/S-SCH|S-SCH]]** | Secondary Synchronization Channel | Yok (Saf Fiziksel) | Slot zamanlı, 256 chip SSC | Frame senkronizasyonu ve Kod Grubu tespiti (Hücre Arama Adım 2) |
| **[[concepts/CPICH|CPICH]]** | Common Pilot Channel | Yok (Saf Fiziksel) | Sürekli iletim, $C_{ch,256,0}$ | Scrambling code tespiti (Hücre Arama Adım 3), kanal tahmini ve RSCP/Ec/No ölçümü |
| **[[concepts/P-CCPCH|P-CCPCH]]** | Primary Common Control Physical Channel | **[[concepts/BCH|BCH]]** | Zaman çoklamalı, $C_{ch,256,1}$ | Sistem bilgilerini (MIB, SIB) taşıyan BCH transport kanalını iletmek |
| **S-CCPCH** | Secondary Common Control Physical Channel | **PCH** (Paging Channel) ve **FACH** (Forward Access Channel) | Değişken SF (4 ila 256) | Cihaz çağırma (Paging) sinyalleri ve ortak kontrol mesajları iletimi |

## Kanalların Güç ve Kod Dağılımı

WCDMA'de toplam baz istasyonu gücü, bu kanallar arasında paylaştırılır. Hücre sınırındaki cihazların hücreyi bulabilmesi için ortak kanallara (Common Channels) belirli bir güç bütçesi ayrılır:
* **CPICH:** Genellikle toplam hücre gücünün **%-10'u (-10 dB)** seviyesindedir. Sabit ve sürekli iletildiği için en kararlı referans sinyalidir.
* **SCH (P-SCH / S-SCH):** Slot başlarında (ilk 256 chip) yüksek güçle gönderilir, slotun geri kalanında kapatılır.
* **P-CCPCH:** Slotun 256 ila 2560 çiplik kısmında aktiftir ve BCH verisini taşır.

```
Slot Zamanlama Yapısı (Downlink):
+-----------------------------------------------------------------------+
|                              2560 Chips SLOT                          |
+-------------------+---------------------------------------------------+
| 0                 | 256                                           2560|
+-------------------+---------------------------------------------------+
|  SCH (P-SCH/S-SCH)|              P-CCPCH (BCH Verisi)                 |
|  (İlk 256 chip)   |              (Kalan 2304 chip)                    |
+-------------------+---------------------------------------------------+
|                   CPICH (Sürekli Pilot İletimi, SF=256)               |
+-----------------------------------------------------------------------+
```

## Kanal İlişkileri ve Hücre Arama Akışı

Alıcı cihaz WCDMA sinyalini aldığında bu kanalları belirli bir sıra ile işler:
1. Sinyalin nerede başlayıp bittiğini bilmediği için önce **P-SCH** üzerinden slot sınırlarını yakalar.
2. Slot sınırları bilindiğinde, **S-SCH**'in slotlardaki örüntüsünü çözerek frame başlangıcını (15 slotluk çerçevenin başını) ve 64 scrambling kod grubundan hangisinin kullanıldığını bulur.
3. Kod grubu bilindiğinde, o gruptaki 8 scrambling kodunu **CPICH** üzerinde tek tek deneyerek hücreye özgü **Primary Scrambling Code**'u tespit eder.
4. Scrambling Code ve frame senkronizasyonu tam olarak sağlandıktan sonra, **P-CCPCH** despread edilir ve **BCH** transport kanalı decode edilerek **SIB11** gibi komşu hücre listelerini içeren sistem bilgileri okunur.

## İlgili Konular
* [[concepts/P-SCH|P-SCH (Primary Synchronization Channel)]]
* [[concepts/S-SCH|S-SCH (Secondary Synchronization Channel)]]
* [[concepts/CPICH|CPICH (Common Pilot Channel)]]
* [[concepts/P-CCPCH|P-CCPCH (Primary Common Control Physical Channel)]]
* [[concepts/WCDMA Cell Search|WCDMA Cell Search]]
