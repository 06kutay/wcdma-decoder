---
title: Channelization Code
category: concepts
tags: [wcdma, physical-layer, ovsf, spreading, mathematics]
aliases: [Channelization Code, OVSF Code, Orthogonal Variable Spreading Factor]
sources: [CLAUDE.md]
summary: OVSF (Orthogonal Variable Spreading Factor) yayma kodlarının yapısı, kod ağacı üretimi, CPICH ve P-CCPCH kanallarındaki sabit kod değerleri.
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

# Channelization Code (Kanal Yayma Kodu)

WCDMA sisteminde **Channelization Code (Kanal Yayma Kodu)**, aynı baz istasyonundan (aynı scrambling kodu altında) yayınlanan farklı downlink kanallarını (veri, ses, kontrol kanalları vb.) birbirine girişim yapmadan ortogonal olarak ayırmak amacıyla kullanılan matematiksel kod dizileridir. 

Bu kodlar **OVSF (Orthogonal Variable Spreading Factor - Dikgen Değişken Yayma Faktörü)** teknolojisine dayanır.

## OVSF Kod Ağacı Yapısı
OVSF kodları, değişken veri hızlarını destekleyebilmek için ağaç yapısında tasarlanmıştır. Spreading Factor (SF) değeri değiştikçe ağacın farklı seviyelerindeki kodlar kullanılır.

```
OVSF Kod Ağacı Üretim Mantığı:
                  SF=1                  SF=2                  SF=4
                                        +--- C_ch,2,0 (1,1) --+--- C_ch,4,0 (1,1,1,1)
                                        |                     +--- C_ch,4,1 (1,1,-1,-1)
                  +--- C_ch,1,0 (1) ----+
                                        |                     +--- C_ch,4,2 (1,-1,1,-1)
                                        +--- C_ch,2,1 (1,-1) -+
                                                              +--- C_ch,4,3 (1,-1,-1,1)
```

### Matematiksel Üretim Kuralları
Kodlar, $C_{ch,SF,k}$ şeklinde gösterilir. Burada:
* **$SF$:** Spreading Factor (Yayma Faktörü). Downlink için $SF \in \{4, 8, 16, 32, 64, 128, 256, 512\}$.
* **$k$:** Kod indeksidir ($k \in [0, SF-1]$).

Ağaçta bir seviyedeki kod, bir önceki seviyedeki koddan şu iki kurala göre türetilir (Kronecker tabanlı üretim):
$$C_{ch,2SF,2k} = \langle C_{ch,SF,k}, C_{ch,SF,k} \rangle$$
$$C_{ch,2SF,2k+1} = \langle C_{ch,SF,k}, -C_{ch,SF,k} \rangle$$

### Dikgenlik (Orthogonality) Kuralı
Aynı scrambling kodu altındaki iki kanalın birbirine karışmaması için kullanılan OVSF kodlarının birbirine tamamen dikgen olması gerekir. 
* **Dikgenlik Koşulu:** İki kodun iç çarpımının sıfır olmasıdır.
* **Ağaç Kısıtlaması:** Ağaçta seçilen bir kod, kendisinin alt dallarında bulunan (türetilmiş) hiçbir kodla veya kendisini türeten üst dallardaki ata kodlarla **aynı anda kullanılamaz**. Aksi takdirde dikgenlik bozulur ve kanallar birbirine girişim yapar.

## Kritik Downlink Kanallarının OVSF Kodları
WCDMA downlink sisteminde bazı kanalların OVSF kodları standart tarafından sabit olarak tanımlanmıştır:

1. **[[concepts/CPICH|CPICH (Common Pilot Channel)]]:**
   * Her zaman **$C_{ch,256,0}$** kodunu kullanır.
   * SF 256 seviyesinin en üstündeki ilk koddur.
   * Tamamı 1'lerden oluşur: $\langle 1, 1, 1, \dots, 1 \rangle$ (256 adet).
2. **[[concepts/P-CCPCH|P-CCPCH (Primary Common Control Physical Channel)]]:**
   * Her zaman **$C_{ch,256,1}$** kodunu kullanır.
   * CPICH'in hemen altındaki daldır.
   * Yapısı: $\langle 1, 1, -1, -1, 1, 1, -1, -1, \dots \rangle$ örüntüsünün tekrarlanmasıdır.

Bu iki kanal aynı SF (256) seviyesindedir ve birbirinin alt/üst soyundan olmadığı için mükemmel dikgendir.

## Despreading (Geri Yayma) Matematiksel Süreci
Alıcı cihaz descrambling işlemini yaptıktan sonra, havadan gelen kompleks çip dizisini $d(i)$ elde eder. İlgili fiziksel kanaldaki verileri süzmek için OVSF kodu ile **despreading** gerçekleştirilir.

Örnek olarak P-CCPCH kanalındaki sembolleri süzmek için ($SF = 256$):
1. Gelen çip dizisi 256 çiplik bloklara ayrılır.
2. Her blok, $C_{ch,256,1}$ kodunun elemanları ile tek tek çarpılır ve toplanır (entegrasyon):

$$S(m) = \frac{1}{256} \sum_{i=0}^{255} d(256m + i) \times C_{ch,256,1}(i)$$

Burada:
* $S(m)$: Çözülen $m$-inci QPSK sembolüdür.
* Elde edilen bu sembol, QPSK Demodülasyon aşamasına geçilerek ikili bitlere ($\pm 1 \to 0, 1$) dönüştürülür.

## İlgili Konular
* [[concepts/WCDMA Genel|WCDMA Genel]]
* [[concepts/Scrambling Code|Scrambling Code]]
* [[concepts/P-CCPCH|P-CCPCH]]
