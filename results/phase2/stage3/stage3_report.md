# Stage 3 Report — LOO Sensitivity Analysis
Date: 2026-06-01

## Pass Conditions

| Condition | CePNEM | GCaMP |
|---|---|---|
| Median top-50 retention ≥ 0.70 | **PASS** (0.960) | **PASS** (0.940) |

## Retention Summary

| Metric | CePNEM | GCaMP |
|---|---|---|
| Median | 0.960 | 0.940 |
| Mean   | 0.907   | 0.886 |
| Min    | 0.480    | 0.500 |
| p25    | 0.860    | 0.840 |
| p75    | 0.980    | 0.960 |
| N recs with retention < 0.70 | 2 | 3 |

## Rank Correlation Summary

| Metric | CePNEM | GCaMP |
|---|---|---|
| Spearman (all Class 4, median) | 0.9820 | 0.9618 |
| Spearman (all Class 4, min)    | 0.7971    | 0.7401 |
| Spearman (top-100, median)     | 0.9652 | 0.9430 |
| Pearson |ΔQ| (median)          | 0.9943     | 0.9855 |
| Pearson |ΔQ| (min)             | 0.7445        | 0.7283 |

## Per-Recording Retention Table

| Rec | ID | CePNEM ret | GCaMP ret | CePNEM ρ | GCaMP ρ | Roam? | Flag |
|---|---|---|---|---|---|---|---|
|  0 | 2022-06-14-01 | 0.960 | 0.980 | 0.9876 | 0.9847 |  |  |
|  1 | 2022-06-14-07 | 0.860 | 0.660 | 0.9304 | 0.9013 | YES | **FLAG** |
|  2 | 2022-06-14-13 | 0.960 | 0.960 | 0.9767 | 0.9611 |  |  |
|  3 | 2022-06-28-01 | 0.800 | 0.720 | 0.9031 | 0.8836 | YES |  |
|  4 | 2022-06-28-07 | 1.000 | 0.980 | 0.9897 | 0.9896 |  |  |
|  5 | 2022-07-15-06 | 0.840 | 0.840 | 0.9534 | 0.9093 | YES |  |
|  6 | 2022-07-15-12 | 0.840 | 0.820 | 0.9485 | 0.9126 | YES |  |
|  7 | 2022-07-20-01 | 1.000 | 0.960 | 0.9943 | 0.9557 |  |  |
|  8 | 2022-07-26-01 | 1.000 | 1.000 | 0.9998 | 0.9991 |  |  |
|  9 | 2022-08-02-01 | 0.980 | 0.960 | 0.9862 | 0.9635 |  |  |
| 10 | 2022-12-21-06 | 0.860 | 0.820 | 0.9645 | 0.9313 | YES |  |
| 11 | 2023-01-05-01 | 0.940 | 0.940 | 0.9939 | 0.9743 |  |  |
| 12 | 2023-01-05-18 | 0.980 | 0.940 | 0.9845 | 0.9701 |  |  |
| 13 | 2023-01-06-01 | 0.880 | 0.840 | 0.9519 | 0.9217 | YES |  |
| 14 | 2023-01-06-08 | 0.980 | 0.900 | 0.9894 | 0.9677 |  |  |
| 15 | 2023-01-06-15 | 0.900 | 0.920 | 0.9529 | 0.9601 | YES |  |
| 16 | 2023-01-09-08 | 0.980 | 0.960 | 0.9625 | 0.9625 | YES |  |
| 17 | 2023-01-09-15 | 0.840 | 0.880 | 0.9459 | 0.9429 | YES |  |
| 18 | 2023-01-09-22 | 0.900 | 0.880 | 0.9504 | 0.9554 | YES |  |
| 19 | 2023-01-09-28 | 0.980 | 0.960 | 0.9907 | 0.9772 |  |  |
| 20 | 2023-01-10-07 | 0.980 | 0.980 | 0.9997 | 0.9940 |  |  |
| 21 | 2023-01-10-14 | 0.780 | 0.760 | 0.8655 | 0.9023 | YES |  |
| 22 | 2023-01-13-07 | 1.000 | 1.000 | 0.9828 | 0.9794 |  |  |
| 23 | 2023-01-16-01 | 0.920 | 0.920 | 0.9548 | 0.9519 | YES |  |
| 24 | 2023-01-16-08 | 0.960 | 0.960 | 0.9976 | 0.9680 |  |  |
| 25 | 2023-01-16-15 | 0.640 | 0.500 | 0.7971 | 0.7753 | YES | **FLAG** |
| 26 | 2023-01-16-22 | 0.980 | 0.920 | 0.9933 | 0.9757 |  |  |
| 27 | 2023-01-17-01 | 0.900 | 0.960 | 0.9440 | 0.9633 | YES |  |
| 28 | 2023-01-17-07 | 0.960 | 0.960 | 0.9932 | 0.9759 |  |  |
| 29 | 2023-01-17-14 | 0.480 | 0.540 | 0.8294 | 0.7401 | YES | **FLAG** |
| 30 | 2023-01-18-01 | 0.960 | 0.960 | 0.9812 | 0.9628 |  |  |
| 31 | 2023-01-19-01 | 0.980 | 0.940 | 0.9866 | 0.9594 |  |  |
| 32 | 2023-01-19-08 | 0.980 | 0.960 | 0.9871 | 0.9860 |  |  |
| 33 | 2023-01-19-15 | 0.980 | 0.960 | 0.9964 | 0.9848 |  |  |
| 34 | 2023-01-19-22 | 1.000 | 0.980 | 0.9938 | 0.9933 |  |  |
| 35 | 2023-01-23-01 | 0.900 | 0.840 | 0.9837 | 0.9460 | YES |  |
| 36 | 2023-01-23-08 | 0.720 | 0.800 | 0.9168 | 0.8968 | YES |  |
| 37 | 2023-01-23-15 | 0.900 | 0.840 | 0.9766 | 0.9348 | YES |  |
| 38 | 2023-01-23-21 | 0.980 | 0.940 | 0.9830 | 0.9747 |  |  |
| 39 | 2023-03-07-01 | 0.820 | 0.800 | 0.9664 | 0.9185 | YES |  |

## DEV-005 Assessment

DEV-005: all-animal pooling without prior systematic outlier screening.
A recording is flagged as influential if removing it reduces top-50 retention below 0.70.

**CePNEM:** 2 influential recordings flagged. (min retention = 0.480)
**GCaMP:**  3 influential recordings flagged.  (min retention = 0.500)

**Influential recordings (CePNEM):** ['2023-01-16-15', '2023-01-17-14']
**Influential recordings (GCaMP):**  ['2022-06-14-07', '2023-01-16-15', '2023-01-17-14']

**Overall DEV-005 verdict:** DEV-005 UNRESOLVED: At least one influential recording identified. See influential_recordings lists.

## Coordinate-Specific Sensitivity Comparison

| Metric | CePNEM | GCaMP | More stable |
|---|---|---|---|
| Median retention      | 0.960 | 0.940 | CePNEM |
| Min retention         | 0.480    | 0.500    | GCaMP |
| N influential recs    | 2              | 3              | CePNEM |
| Spearman median       | 0.9820  | 0.9618  | CePNEM |

## Next Step

Stage 4 (enrichment tests) requires **explicit human authorization**.
Do NOT begin enrichment analysis automatically.

---
*Stage 3 scope: LOO sensitivity, DEV-005 assessment, rank stability. No enrichment statistics.*