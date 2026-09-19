# Gate 1 review — 2026-09-17

## Result

**FAIL. Do not publish this candidate.** The reproducible preflight result is in `gate1_preflight.json`. The candidate is `candidate-a0425db09a1b57fc`: 231 source records, 37 parsed documents, 2,440 chunks, no parsed-document quarantine, and no missing source files, source-hash mismatches, dangling source references, or duplicate chunk IDs. All 37 document records and all 2,440 chunks remain pending. Every document title is currently its number, and every issue date is null. All 15 required coverage entries remain pending; `verified_as_of` is null. The review queue still has 10 random chunks, 5 structural boundaries, and 3 relations without legal sign-off. There are 74 source identity quarantines.

The PDF text extractor previously retained page furniture such as `84 CÔNG BÁO/Số 977 + 978/Ngày 25-7-2025` inside the last normative article of Decree 188/2025 and `CÔNG BÁO/Số 1073 + 1074/Ngày 20-8-2025 27` inside Decree 219/2025. This is now filtered by a narrow header/footer pattern and covered by a regression test against the archived PDFs. The rebuilt corpus has two fewer chunks after filtering; the exact partition changes have not been independently reviewed. This is a structural fix, not a legal-content sign-off.

The final candidate was built twice from identical inputs. SHA-256 matched for `parsed.json` (`e810bce476913ae3c0f4e122f46790bdda3168847fb2774831f7fa9b95df07ee`), `chunks.jsonl` (`8c89b988b7b1d722071ff8a7d441cba6bda967666c807f343f2648eeccf57a20`), and `manifest.json` (`f90608b97a4c0d2b4322fc7dfadfd42354b1c41a61e96c032777b7b2db39d296`). The test suite reports 16 passed. The stage builder now carries reviewed `issued_date` and `valid_from` values from document records when present; no dates have been promoted yet.

`metadata_review_queue.json` now collects the original source header, source hash and article span for each of the 37 documents, with the 15 required coverage documents first. These are evidence packets for review, not verified metadata. Page 1 of the archived Công báo PDF used for Decree 219/2025 contains a stray `CÔNG BÁO/Số 1065 + 1066/Ngày 19-10-2023` header above its 2025 issue cover. The decree starts on PDF page 2, which is the pipeline's extraction start. A reviewer should record this source anomaly and cross-check the decree's signed text before metadata sign-off.

## Concrete legal-chain gaps

- The registry contains Social Insurance Law 41/2024/QH15, but not Law 73/2025/QH15. [The official VBPL text of Law 73](https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=179262&Keyword=) states that it amends Article 66 of Law 41. The [official consolidated-law record](https://vbpl.vn/TW/Pages/vbpq-thuoctinh-hopnhat.aspx?ItemID=182335&View=0) lists Laws 73/2025 and 84/2025 as amendments. Their exact operative clauses, dates and population conditions still need extraction and review.
- [The official VBPL text of Law 142/2025/QH15](https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=187584) states that it amends point a, clause 1, Article 37 of Law 41/2024/QH15 and refers to prior amendments by Laws 73/2025, 84/2025 and 113/2025. All four amendment sources need inventory and effective-date/scope review before the social-insurance coverage entry can be marked verified as of September 2026. This search finding is a review lead; it has not been converted into a verified relation.
- [The official VBPL text of Law 51/2024/QH15](https://vbpl.vn/boyte/Pages/vbpq-toanvan.aspx?ItemID=172923) enumerates multiple earlier amendments to Health Insurance Law 25/2008/QH12. The registry currently includes only the base law and Law 51 in the required health-insurance coverage list. The complete intervening amendment chain and transition clauses need to be reconciled before the base law can be represented as current content.

## Required work before PASS

1. Verify each document's number, true title, issue date, effective date and applicable population against the official original; record source locator and any conflict. Carry reviewed metadata through the staging build rather than hard-coding null dates.
2. Resolve the 74 flattened Markdown identities against original DOCX where possible; document exclusions and their effect on coverage.
3. Inventory, obtain and review omitted amendment/transition sources across every required topic. Record each relation at document/provision/fragment scope with evidence and dates; construct versioned provisions only from reviewed operations.
4. Compare each of the 10 random chunks, 5 boundaries and 3 relations to the original official sources, record an outcome and evidence per item, then investigate all Critical findings across the affected source class. The queue is not itself sign-off.
5. Rebuild twice with identical inputs, compare parsed/chunk/manifest hashes, run tests and full validation, and only then make a release decision. Keep staging separate from `data/chunks.jsonl` while Gate 1 is FAIL.

The preflight script checks objective local invariants only. A zero-error preflight cannot certify completeness of amendments or legal applicability; those require documented source review.
