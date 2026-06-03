---
title: WCDMA SIB Genel
category: concepts
tags: [wcdma, rrc, sib, system-information, asn1]
aliases: [SIB Genel, System Information Block]
sources: [CLAUDE.md]
summary: WCDMA RRC katmanındaki SIB (System Information Block) yapısı, BCCH haritalaması, segmentasyon, birleştirme mekanizmaları ve MIB/SB kullanımı.
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

# WCDMA SIB Genel (System Information Block)

WCDMA sisteminde baz istasyonu (NodeB), hücreye bağlanmak isteyen veya hücrede bekleme (idle) modunda olan cihazların bilmesi gereken tüm parametreleri **RRC (Radio Resource Control)** katmanında **BCCH (Broadcast Control Channel)** mantıksal kanalı üzerinden yayınlar. Bu bilgilere **System Information (Sistem Bilgileri)** denir.

## SIB Hiyerarşisi (MIB, SB, SIB)
Sistem bilgileri, mantıksal olarak farklı işlevlere sahip bloklara bölünmüştür. Bu hiyerarşik yapı, cihazların sadece ihtiyaç duydukları blokları okuyarak pil tasarrufu yapmasını sağlar:

```
RRC Sistem Bilgisi Hiyerarşisi:
+--------------------------------------------------------+
|           MASTER INFORMATION BLOCK (MIB)               |
|  - Temel sistem kimliği (PLMN vb.)                     |
|  - SIB'lerin versiyon ve zamanlama (scheduling) bilgisi|
+--------------------------------------------------------+
         |                                   |
         v                                   v
+------------------------+       +-----------------------+
|  SCHEDULING BLOCK (SB) |       | SYSTEM INFO BLOCKS    |
|  - Diğer SIB'ler için  |       | (SIB1, SIB3, SIB11)   |
|    ek zamanlama bilgisi|       | - Gerçek parametreler |
+------------------------+       +-----------------------+
```

### 1. Master Information Block (MIB)
* **Giriş Noktası:** Alıcı cihazın sistem bilgilerini okurken ilk çözmesi gereken bloktur.
* **İçerik:** Operatör kimliği (PLMN: MCC+MNC) ve diğer SIB'lerin havada hangi periyotlarda ve hangi slotlarda yayınlanacağını gösteren **Scheduling (Zamanlama)** parametrelerini içerir.
* **Periyot:** MIB, sabit olarak her **8 çerçevede bir (80 ms)** yayınlanır.

### 2. Scheduling Block (SB)
* **Ek Zamanlayıcı:** SIB sayısı çok fazla olduğunda MIB içerisine sığmayan ek zamanlama bilgilerini taşımak amacıyla kullanılan yardımcı bloklardır (SB1 ve SB2).

### 3. System Information Blocks (SIBs)
Gerçek hücresel parametreleri taşıyan bloklardır. Toplam 20'ye yakın farklı SIB tanımlıdır. En önemlileri şunlardır:
* **SIB1:** NAS katmanı bilgileri, timers.
* **[[concepts/WCDMA SIB3|SIB3]]:** Hücre seçimi (Cell Selection) kriterleri, LAC (Location Area Code) ve **Cell Identity (Hücre Kimliği)**.
* **SIB5 / SIB6:** Ortak fiziksel kanalların (PRACH, SCCPCH) konfigürasyonları.
* **[[concepts/WCDMA SIB11|SIB11]] / [[concepts/WCDMA SIB11bis|SIB11bis]]:** Ölçüm kontrolü ve **Komşu Hücre Listesi (Neighbor Cell List)**. WCDMA tarayıcı projesinin ana hedefidir.
* **[[concepts/WCDMA SIB19|SIB19]]:** Inter-RAT (diğer teknolojiler olan LTE veya GSM) komşu hücre listesi.

## SIB Segmentasyonu ve Birleştirme (Segmentation & Reassembly)
BCH taşıma kanalının limitli blok boyutu (TTI başına 246 bilgi biti) nedeniyle, büyük SIB paketleri doğrudan tek seferde gönderilemez. RRC katmanı SIB paketlerini **segmentlere ayırarak** gönderir.

### Segment Türleri
Her BCH veri paketi, bir **System Information Message** içerir. Bu mesajın başında segmentasyon durumunu gösteren bir RRC header bulunur:
* **First Segment:** SIB paketinin ilk parçasıdır. Paketin toplam uzunluğunu ve sonraki parçaların geleceğini belirtir.
* **Subsequent Segment:** Orta parçalardır.
* **Last Segment:** SIB paketinin son parçasıdır. Birleştirmeyi tetikler.
* **Complete SIB:** SIB paketi küçükse tek bir BCH bloğuna sığdırılarak "Complete" olarak gönderilir.

### Birleştirme Süreci (Reassembly)
Alıcı cihaz (SDR tarayıcı), BCH çözücüden gelen CRC'si doğrulanmış paketlerin segment başlıklarını (Header) okur:
1. `First Segment` alındığında yeni bir SIB tampon belleği (buffer) açılır.
2. `Subsequent Segment` parçaları sırayla bu tampona eklenir.
3. `Last Segment` ulaştığında birleştirme tamamlanır ve tüm paket tek bir ASN.1 bit dizisi haline getirilir.
4. Birleştirilen ASN.1 dizisi çözülmek üzere **UPER (Unaligned Packet Encoding Rules)** çözücüye gönderilir.

## İlgili Konular
* [[concepts/BCH|BCH]]
* [[concepts/WCDMA SIB3|WCDMA SIB3]]
* [[concepts/WCDMA SIB11|WCDMA SIB11]]
* [[concepts/WCDMA SIB11bis|WCDMA SIB11bis]]
* [[concepts/WCDMA SIB19|WCDMA SIB19]]
