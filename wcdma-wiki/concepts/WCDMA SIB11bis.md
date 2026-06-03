---
title: WCDMA SIB11bis
category: concepts
tags: [wcdma, rrc, sib, sib11bis, neighbor-list]
aliases: [SIB11bis]
sources: [CLAUDE.md]
summary: WCDMA RRC katmanındaki SIB11bis (System Information Block 11bis) işlevi, SIB11 limit aşımı durumlarında ek komşu listesi taşıma mekanizması.
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

# WCDMA SIB11bis (System Information Block 11bis)

**WCDMA SIB11bis (System Information Block 11bis - Sistem Bilgi Bloğu 11bis)**, RRC katmanında yayınlanan ve **[[concepts/WCDMA SIB11|SIB11]]** bloğunun veri taşıma sınırlarını aştığı durumlarda devreye giren **ek bir komşu hücre listesi** kaynağıdır.

## Neden İhtiyaç Duyulur?
WCDMA sisteminde her bir SIB paketi segmentlere ayrılıp BCH taşıma kanalı üzerinden gönderilir (bkz. [[concepts/WCDMA SIB Genel|WCDMA SIB Genel]]). Ancak bir RRC mesajının toplam segment sayısı ve boyutu sınırlıdır.

Özellikle şehir merkezleri gibi baz istasyonlarının çok yoğun olduğu bölgelerde:
* Intra-frequency komşu listesi,
* Inter-frequency komşu listesi,
* Ve bunlara ait ölçüm parametrelerinin tamamı tek bir SIB11 mesajı içine sığmayabilir (maksimum SIB11 boyutu genellikle aşılır).
* Bu durumda operatörler, temel ve öncelikli komşuları **SIB11** içine koyar; geri kalan ek komşu hücre listelerini ise **SIB11bis** bloğu ile yayınlar.

## Çalışma Mantığı ve Yapısı
* **Haritalama:** SIB11bis, tıpkı SIB11 gibi UPER formatında kodlanmış `MeasurementControlSysInfoExtension` ASN.1 yapısını taşır.
* **Bağımsız Çözüm:** Cihaz SIB11bis çözdüğünde elde ettiği komşu listelerini (Intra-frequency ve Inter-frequency) SIB11'den gelen listelerin sonuna **ekler (append)**.
* **Farklılık:** SIB11bis genellikle karmaşık ölçüm kurallarını veya raporlama kriterlerini içermez; sadece ek hücrelerin **UARFCN** ve **Primary Scrambling Code (PSC)** bilgilerini listeler, bu sayede havada kapladığı alan daha küçüktür. ^[inferred]

## Tarama Projesindeki Rolü
Komşu hücre analizi yapan bir tarayıcının eksiksiz bir topoloji haritası çıkarabilmesi için sadece SIB11 dinlemesi yetmez. Eğer baz istasyonu SIB11bis yayınlıyorsa (bu durum Master Information Block - MIB zamanlama tablosunda görünür), tarayıcı yazılımı **SIB11bis segmentlerini de toplayıp decode etmelidir**. Aksi takdirde komşu listesinin önemli bir kısmı (özellikle diğer frekanslardaki hücreler) eksik kalacaktır.

## İlgili Konular
* [[concepts/WCDMA SIB Genel|WCDMA SIB Genel]]
* [[concepts/WCDMA SIB11|WCDMA SIB11]]
* [[concepts/WCDMA SIB19|WCDMA SIB19]]
