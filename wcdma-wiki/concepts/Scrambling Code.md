---
title: Scrambling Code
category: concepts
tags: [wcdma, physical-layer, scrambling, gold-code, mathematics]
aliases: [Primary Scrambling Code, PSC Code, Gold Code]
sources: [CLAUDE.md]
summary: WCDMA Downlink Scrambling Code matematiksel yapısı, 18-dereceli m-dizileri kullanan Gold kodu üretimi, 64 kod grubu ve descrambling formülleri.
provenance:
  extracted: 0.98
  inferred: 0.02
  ambiguous: 0.00
base_confidence: 0.95
lifecycle: draft
lifecycle_changed: 2026-06-02
tier: core
created: 2026-06-02T16:16:00Z
updated: 2026-06-02T16:16:00Z
---

# Scrambling Code (Çırpma Kodu)

WCDMA downlink sisteminde **Scrambling Code (Çırpma Kodu)**, farklı hücreleri (baz istasyonlarını) birbirinden ayırmak ve iletilen sinyallerin havada girişimini en aza indirerek spektral olarak beyaz gürültüye benzemesini sağlamak amacıyla kullanılan kompleks-değerli psödo-rastgele kod dizisidir.

## Kod Yapısı ve Gruplandırma
WCDMA downlink yönünde toplam **262.143 adet** scrambling kodu tanımlıdır. Ancak pratik kullanım kolaylığı ve hücre arama süresini kısaltmak amacıyla bu kodlar belirli alt kümelere ayrılmıştır:
* **Primary Scrambling Codes (Birincil Çırpma Kodları):** Hücre aramada kullanılan ana kodlardır. Toplam **512 adet** birincil scrambling kodu bulunur (0 ila 511 arası numaralandırılır).
* **Scrambling Code Groups (Kod Grupları):** 512 birincil scrambling kodu, **64 farklı gruba** ayrılmıştır. Her grup tam olarak **8 adet** birincil scrambling kodu içerir.
  $$\text{Grup } g \in [0, 63] \implies \text{Kodlar: } [8g, 8g+1, \dots, 8g+7]$$
* **Secondary Scrambling Codes (İkincil Çırpma Kodları):** Çok yoğun veri trafiğinin olduğu ve birincil scrambling kodunun altındaki OVSF kod ağacının yetersiz kaldığı durumlarda ek kapasite sağlamak amacıyla kullanılır. Normal şartlarda tarayıcılar (Scanner) tarafından dinlenmez. ^[inferred]

## Gold Kodu Üretim Matematiği (3GPP TS 25.213 Section 5.2.2)
Downlink scrambling kodları, 18. dereceden iki adet doğrusal geri beslemeli kaydırmalı yazmaç (LFSR - Linear Feedback Shift Register) kullanılarak üretilen psödo-rastgele **Gold dizilerinden** türetilir.

### 1. LFSR Üreteç Polinomları
Kod üretimi için kullanılan iki adet m-dizisi ($x$ ve $y$) aşağıdaki 18. derece primitif polinomlara göre oluşturulur:
* **$x$ dizisi polinomu:** $1 + X^7 + X^{18}$
* **$y$ dizisi polinomu:** $1 + X^5 + X^7 + X^{10} + X^{18}$

Bu polinomlara göre dizilerin recursive (öz yinelemeli) üretim formülleri şöyledir (modulo 2 aritmetiğinde, yani XOR işlemiyle):
$$x(i+18) = (x(i+7) + x(i)) \bmod 2, \quad i = 0, \dots, 2^{18}-20$$
$$y(i+18) = (y(i+10) + y(i+7) + y(i+5) + y(i)) \bmod 2, \quad i = 0, \dots, 2^{18}-20$$

### 2. Başlangıç Koşulları (Initial Conditions)
LFSR yazmaçlarının başlangıç durumları (seed değerleri) sabit olarak tanımlanmıştır:
* **$x$ yazmacı:** $x(0) = 1$, ve $x(1) = x(2) = \dots = x(17) = 0$
* **$y$ yazmacı:** $y(0) = y(1) = \dots = y(17) = 1$

### 3. İkili Gold Dizisinin Oluşturulması
$n$-inci Gold dizisi $z_n$, $x$ dizisinin $n$ kadar kaydırılmış hali ile $y$ dizisinin eleman eleman XOR'lanması ile elde edilir:
$$z_n(i) = (x((i+n) \bmod (2^{18}-1)) + y(i)) \bmod 2, \quad i = 0, \dots, 2^{18}-2$$

Burada $n \in [0, 262142]$ kod numarasıdır. Birincil scrambling kodları için $n \in [0, 511]$ aralığı kullanılır.

### 4. Reel-Değerli Dönüşüm
İkili Gold dizisi $z_n(i) \in \{0, 1\}$, bipolarlık sağlamak amacıyla reel-değerli $\{1, -1\}$ kümesine haritalanır:
$$Z_n(i) = 1 - 2 z_n(i)$$

### 5. Kompleks Downlink Scrambling Kodunun Oluşturulması
$n$-inci downlink scrambling kodu $S_{dl,n}$, reel $Z_n$ dizisinin kendisi ve $131072$ ($2^{17}$) çip kaydırılmış versiyonunun kompleks düzlemde birleştirilmesiyle elde edilir:
$$S_{dl,n}(i) = Z_n(i) + j \cdot Z_n((i + 131072) \bmod (2^{18} - 1))$$

Burada $i = 0, 1, \dots, 38399$ çip indeksidir. Üretilen bu kompleks dizi tam olarak **10 ms'lik radyo çerçevesi uzunluğundadır (38,400 çip)** ve her çerçeve başında sıfırlanarak tekrar başa döner.

## Alıcıda Descrambling İşlemi
Baz istasyonu sinyalleri iletmeden önce yayılan çipleri $S_{dl,n}(i)$ ile çarpar. Alıcı cihaz havadan gelen kompleks veri sinyalini $r(i)$ olarak kaydettiğinde, orijinal yayılmış sinyali elde etmek için scrambling kodunun eşleniği (complex conjugate) ile çip bazında çarpar:

$$r_{descramble}(i) = r(i) \times S_{dl,n}^*(i)$$

Burada $S_{dl,n}^*(i)$ eşlenik kodudur:
$$S_{dl,n}^*(i) = Z_n(i) - j \cdot Z_n((i + 131072) \bmod (2^{18} - 1))$$

Descrambling işlemi tamamlandıktan sonra, kanalları ayırmak için [[concepts/Channelization Code|OVSF (Channelization Code)]] kodu ile çarpılarak despreading aşamasına geçilir.

## Python Uygulama Referansı (Algoritma Taslağı)
Kod yazarken kullanılacak mantıksal yapı şöyledir:
```python
import numpy as np

def generate_scrambling_code(code_num, length=38400):
    # LFSR dizilerini oluştur
    x = np.zeros(length + code_num + 18, dtype=np.uint8)
    y = np.zeros(length + 18, dtype=np.uint8)
    
    # Başlangıç durumları
    x[0] = 1
    y[:] = 1  # Hepsi 1
    
    # x dizisi üretimi: x(i+18) = x(i+7) ^ x(i)
    for i in range(length + code_num):
        x[i+18] = x[i+7] ^ x[i]
        
    # y dizisi üretimi: y(i+18) = y(i+10) ^ y(i+7) ^ y(i+5) ^ y(i)
    for i in range(length):
        y[i+18] = y[i+10] ^ y[i+7] ^ y[i+5] ^ y[i]
        
    # z_n(i) = x(i+n) ^ y(i)
    z = x[code_num:code_num+length] ^ y[:length]
    
    # z_n(i + 131072) için ikinci z dizisi
    # Not: pratik kodda 131072 kaydırma LFSR uzunluğu arttırılarak veya hızlı indeksleme ile çözülür.
```

## İlgili Konular
* [[concepts/WCDMA Genel|WCDMA Genel]]
* [[concepts/Channelization Code|Channelization Code (OVSF)]]
* [[concepts/WCDMA Cell Search|WCDMA Cell Search]]
