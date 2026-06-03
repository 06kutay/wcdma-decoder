---
title: WCDMA SIB3
category: concepts
tags: [wcdma, rrc, sib, sib3, cell-identity, lac]
aliases: [SIB3]
sources: [CLAUDE.md]
summary: WCDMA RRC katmanındaki SIB3 (System Information Block 3) detayları, Hücre Kimliği (Cell Identity), LAC ve Hücre Seçim kriterlerinin incelenmesi.
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

# WCDMA SIB3 (System Information Block 3)

**WCDMA SIB3 (System Information Block 3 - Sistem Bilgi Bloğu 3)**, hizmet veren (serving) hücreye ait temel kimlik bilgilerini ve mobil cihazın o hücrede kalıp kalamayacağını (hücre seçimi / cell selection kriterleri) belirleyen parametreleri içeren kritik bir RRC bloğudur.

GSM sistemindeki **System Information 3 (SI3)** ve LTE/5G sistemlerindeki **SIB1** bloklarının işlevsel karşılığıdır.

## Temel Görevleri
* **Hücre Kimliklendirme:** Cihaza o an bağlı olduğu baz istasyonunun küresel ve yerel kimlik kodlarını bildirir.
* **Hücre Seçimi Kontrolü (Cell Selection):** Cihazın hücrede "Idle" modda bekleyebilmesi için gereken minimum sinyal eşiklerini ($Q_{rxlevmin}$) tanımlar.
* **Erişim Kısıtlamaları:** Hücrenin operatör tarafından test amaçlı kapatılıp kapatılmadığını (Cell Barred) veya rezerve edilip edilmediğini bildirir.

## SIB3 İçeriğindeki Önemli Parametreler (ASN.1 Yapısı)

SIB3 birleştirilip UPER ile çözüldüğünde aşağıdaki ana parametre grupları elde edilir:

### 1. Cell Identity (Hücre Kimliği - CID)
* **Boyut:** **28-bit** tamsayı değerindedir.
* **Yapısı:** Küresel olarak benzersiz olan bu değer iki parçadan oluşur:
  * **RNC ID (Radio Network Controller Identifier):** İlk 12 ila 16 biti kapsar. Hücrenin bağlı olduğu RNC kontrol merkezini belirtir.
  * **Cell ID:** Son 12 ila 16 biti kapsar. RNC altındaki spesifik anten/sektör numarasını belirtir.
  * **Örnek:** `Cell Identity = 10564952` $\rightarrow$ Hex olarak `0xA13458` $\rightarrow$ RNC ID: `2579` (üst bitler), Cell ID: `13400` (alt bitler).

### 2. LAC (Location Area Code - Konum Alanı Kodu)
* **Boyut:** **16-bit** değerindedir (0 ila 65535 arası).
* **Görevi:** Hücrelerin gruplandığı çağrı alanını (Location Area) belirtir. Cihaz bir hücreden diğerine geçtiğinde LAC değişirse ağa **Location Update (Konum Güncellemesi)** mesajı gönderir.
* *Not:* LAC parametresi teknik olarak RRC katmanında SIB1 veya SIB3 içinde haritalandırılabilir, ancak hücresel taramalarda SIB3 çözüldüğünde hücre kimliği ile birlikte LAC bilgisi de elde edilmiş olur. ^[inferred]

### 3. Cell Selection ve Re-selection Parametreleri
* **$Q_{rxlevmin}$ (Minimum Alış Seviyesi):** Hücreye kamp kurabilmek (camp-on) için gereken minimum CPICH RSCP gücüdür. Birimi dBm'dir ve formülü şöyledir:
  $$\text{Minimum Güç (dBm)} = Q_{rxlevmin} \times 2$$
  *Örnek:* ASN.1 çıktısında $Q_{rxlevmin} = -58$ ise, gereken asgari sinyal gücü $-116 \text{ dBm}$'dir.
* **$Q_{qualmin}$ (Minimum Sinyal Kalitesi):** Hücrede kalabilmek için gereken minimum CPICH $E_c/N_0$ sinyal kalitesidir.
  $$\text{Minimum Kalite (dB)} = Q_{qualmin}$$

### 4. Cell Access Restriction (Hücre Erişim Kısıtlaması)
* **Cell Barred:** `barred` veya `notBarred` değerini alır. Eğer `barred` ise cihaz bu hücreye bağlanamaz, acil durum aramaları hariç hücreyi pas geçer.

## Tarama Projesindeki Önemi
Bir WCDMA baz istasyonunun kimliğini tespit etmek için sadece scrambling kodunu bilmek yetmez. Scrambling kodları yereldir ve birkaç kilometre sonra başka bir hücre tarafından tekrar kullanılabilir (Code Reuse). 

Baz istasyonunun **küresel ve kesin kimliğini (Cell Identity ve LAC)** öğrenmek için **SIB3** bloğunun çözülmesi şarttır.

## İlgili Konular
* [[concepts/WCDMA SIB Genel|WCDMA SIB Genel]]
* [[concepts/WCDMA SIB11|WCDMA SIB11]]
* [[concepts/BCH|BCH]]
