---
title: Hot Cache
updated: 2026-06-11 16:26
---

# Hot Cache

*A ~500-word semantic snapshot of recent activity. Updated after every major write operation.*

## Recent Activity

- [2026-06-02 16:10] INIT — vault created at ./wcdma-wiki
- [2026-06-02 16:20] INGEST — 22 pages created for WCDMA/UMTS Neighbor Analysis System Phase 1 (Concepts, Synthesis, and References).

## Active Threads

- **WCDMA Domain Knowledge Ingestion (Phase 1):** Complete end-to-end WCDMA/UMTS domain knowledge has been compiled and ingested. Pages cover physical layer channel processing, 3-step cell search, Gold & Golay codes, SIB RRC messaging, and Turkish operator frequency band definitions. This forms the absolute baseline for the upcoming Phase 2 decoding code development.

## Key Takeaways

- **Physical Layer Timing:** WCDMA FDD mode uses a 3.84 Mcps chip rate. A 10 ms frame consists of 15 slots (2560 chips each), resulting in 38,400 chips per frame.
- **3-Step Cell Search:** Slot synchronization is acquired via P-SCH matched filter (PSC Golay sequence); frame boundary and scrambling code group (0-63) are found via S-SCH (SSC Comma-Free codes); and finally, the unique primary scrambling code (0-511) is detected via CPICH.
- **RRC System Info:** Serving cell identity (CID) and LAC are carried on SIB3, while neighbor cells are carried on SIB11 and SIB11bis (Intra-frequency/Inter-frequency) and SIB19 (Inter-RAT: LTE/GSM).
- **Turkish Operator Specs:** Band 1 (2100 MHz) and Band 8 (900 MHz) are active. LimeSDR Mini must use LNAH for Band 1 (>1.5 GHz) and LNAW for Band 8 (<1.5 GHz) to achieve optimal RX performance.

## Flagged Contradictions

*None.*

## Son Tespit Edilen Aktif Hücreler (Phase 2 & 4)

| UARFCN | Frekans | PSC (Scrambling) | Kod Grubu | CPICH RSCP | CPICH Ec/No | Slot Timing | Kayıt Zamanı | SIB Dekodlama |
|--------|---------|------------------|-----------|------------|-------------|-------------|--------------|---------------|
| 10813 | 2160.2 MHz | 483 | 60 | -39.70 dBm | -3.69 dB | 1013 | 2026-06-11T13:24:41Z | Yapılmadı |
| 2997 | 937.0 MHz | 5 | 0 | -61.96 dBm | -11.82 dB | 5094 | 2026-06-05T12:33:01Z | Yapılmadı |
