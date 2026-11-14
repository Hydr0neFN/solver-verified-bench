[English](README.en.md) · **繁體中文**

# solver-verified-bench

一組小型的可重現題庫，用來比較 Antigravity CLI 能取用的模型。每題答案都由 solver 產生、並確認唯一解，計分完全機械化。

**先讀這個：**[METHODOLOGY.md](METHODOLOGY.md) 寫清楚這份測試*不能*拿來主張什麼。最重要的一點：每個模型在測試中都有程式執行權，所以分數代表「模型 + 工具」，不能當成純推理能力。

## 一覽

| | |
|---|---|
| 問題 | 用答案唯一、已驗證的題目，比較 Antigravity CLI 能取用的各個模型。 |
| 做了什麼 | 三層生成的題目、solver 驗證過的答案、runner、機械化計分器、歧義稽核。 |
| 結果（實測） | `gemini-3.6-flash-high` 在 Tier 1、Tier 2 拿 **100.0%**，Tier 3 拿 **85.0%**；`gpt-oss-120b-medium` 分別是 **96.7%**、**77.1%**、**15.0%**。 |
| 技術 | Python 生成器、計分器、稽核；bash runner；Antigravity CLI（`agy`） |
| 狀態 | 2026-10-10 起暫停——要等 agy 恢復（Student re-verification）才能跑 `bench/run-model.sh`。詳見 [METHODOLOGY.md](METHODOLOGY.md)。 |

## 運作方式

```
bench/make_tier{1,2,3}.py --fixed seeds--> tasks/tier{1,2,3}/  (prompts)
                                             |
      bench/run-model.sh <model> --agy------>  results/raw/  (reply, stderr, timing)
                                             |
      truth/tier{1,2,3}.json --bench/score.py--> results/scores-tier{1,2,3}.json
```

圖中 `fixed seeds` 是固定 seed，`prompts` 是題目，`reply, stderr, timing` 是回覆、stderr、計時。

生成器寫出每道題目，同時產出答案。
Runner 每次 `agy` 呼叫只送一道題，回覆、stderr、計時全部留下。
計分器只讀回覆最後一行 `FINAL: <answer>`，拿去跟 truth 檔比對。

整理後的 key 裡，`H8_spe` 和 `H12_falsepremise2` 的答案值不變，只是格式改過：字串 `"Rc|2|5"` 改成 token 清單 `["rc","2","5"]`，字串 `"REJECT"` 改成 `reject` 型別。`F05_fab2` 和 `H9_spec` 則是修正過，詳見 [docs/answer-keys.zh-TW.md](docs/answer-keys.zh-TW.md)。

runner 的用法與設定見 [docs/bench.zh-TW.md](docs/bench.zh-TW.md)。

## 三層題目

| 層 | 題數 | 每格 trial 數 | 內容 |
|---|---|---|---|
| Tier 1 — 基準 | 15：12 道推理 + 3 組事實測驗 | 2 | 基準。五個模型中四個全拿 100%，`gpt-oss-120b-medium` 為 96.7%，只能看出下限在哪。 |
| Tier 2 — 硬題 | 14 道，皆經 solver 驗證 | 3 | Tier 1 都滿分後才寫的。每題答案由暴力搜尋或 DFS solver 產出，並確認唯一解。 |
| Tier 3 — 範例歸納 | 4 條複合網格歸納規則 | 5 | 專門用來釐清 Tier 2 上唯一有分歧的那一題。 |

## 結果

格內為該題平均得分 %。各層表格：

- [Tier 1 — 基準](docs/results.zh-TW.md#tier-1--基準)
- [Tier 2 — 硬題](docs/results.zh-TW.md#tier-2--硬題)
- [Tier 3 — 範例歸納](docs/results.zh-TW.md#tier-3--範例歸納)

`⚠` 表示該模型至少有一格的 trial 數低於該層目標（Tier 1 各 2 次、Tier 2 各 3 次、Tier 3 各 5 次）：少一次抽樣就足以翻轉排名，看到 `⚠` 請把該列的平均當成參考值。`partial` 表示該模型有題目完全沒跑，這種情況不給平均。

簡單講：Tier 1 五個模型有四個拿 **100.0%**。Tier 2 把差距拉開，從 **77.1%** 到 **100.0%**。Tier 3 差距最大，從 **15.0%** 到 **85.0%**，`gemini-3.1-pro-high` 也從 Tier 2 的 **97.6%** 掉到 **45.0%**。

## 延遲

僅列覆蓋率足夠的層。**跨帳號不可比**——見 [ACCOUNT-PROVENANCE.md](ACCOUNT-PROVENANCE.md)，不同訂閱層級與時段的服務容量不同。

| model | tier 1 | tier 2 | tier 3 |
|---|---|---|---|
| `gemini-3.7-flash-high` | — | 15s | 165s |
| `gemini-3.7-flash-medium` | — | 12s | 215s |
| `gemini-3.6-flash-high` | 9s | 11s | 65s |
| `gemini-3.1-pro-high` | — | 29s | 467s |
| `gpt-oss-120b-medium` | 10s | 16s | 55s |

## 量到什麼、量不到什麼

每次跑測試，模型都有 shell 和程式執行權，而且真的用了。歸納題上模型會自己寫 Python 跑搜尋找規則。所以分數代表的是**模型 + 工具**。每個模型的權限都一樣，模型之間的比較仍然公平。Tier 3 的長延遲就是這些反覆迭代造成的。

限制：每格只有 2–5 次 trial，題目是為這份測試寫的（所以數字不能跟任何公開排行榜比），跑在兩個訂閱帳號上，而且只有一家供應商、一天之內的資料。完整清單見 [METHODOLOGY.md](METHODOLOGY.md) 的 Limits 一節。

## 計分規則

1. **模型跑爆自己的時間預算就計 0 分，不剔除。** 剔除逾時等於偏袒最慢的模型。而且逾時一旦發生就被釘死：事後重跑成功也不會把那一格改回來，否則「重跑到過為止」就能把真實失敗洗掉。
2. **基礎設施失敗（配額、節流、認證）排除不計**，那不是模型的問題。兩者靠 stderr 內容與耗時區分。

第二條背後的耗時門檻，以及並行度那次教訓，見 [docs/scoring.zh-TW.md](docs/scoring.zh-TW.md)。

## 建置與執行

需要 Python 3 和 bash。只用現成的原始輸出重新計分，不需要 `agy`：

```bash
# regenerate the task files (fixed seeds, byte-identical to the ones used)
python bench/make_tier1.py && python bench/make_tier2.py && python bench/make_tier3.py

# sweep one model; skips any cell that already has output
bash bench/run-model.sh <model-slug> [parallelism] [tiers]

# score everything from the raw outputs
python bench/score.py

# check whether an induction task is actually unambiguous
python bench/audit_ambiguity.py
```

四組指令依序：重新生成題目檔（固定 seed，與實際跑測用的逐位元相同）；跑單一模型，已有輸出的格子會自動跳過；從原始輸出重新計分；檢查某道歸納題的規則是否真的唯一。

另外兩個檢查：`python bench/verify_tier1.py` 會從頭重算手寫的 Tier 1 答案；`python bench/render_readme.py` 會從 `results/scores-tier{1,2,3}.json` 重新產生 `README.md` 和 `README.en.md`。`run-model.sh` 的掃描需要 Antigravity CLI（`agy`），目前跑不了（見狀態）。

## 目錄

| | |
|---|---|
| `bench/` | 生成器、runner、計分器、歧義稽核 |
| `tasks/` | 實際送給模型的題目全文 |
| `truth/` | 答案，資料而非程式碼；含兩次改 key 的理由 |
| `results/` | 分數 JSON + 全部原始輸出、stderr、計時 |
| `METHODOLOGY.md` | 怎麼測的，以及不能主張什麼 |
| `ACCOUNT-PROVENANCE.md` | 哪些跑在哪個帳號，為何延遲不可跨組比 |
| `docs/` | 延伸說明：[bench 設定](docs/bench.zh-TW.md)、[計分](docs/scoring.zh-TW.md)、[答案 key](docs/answer-keys.zh-TW.md)、[完整結果](docs/results.zh-TW.md) |

## 延伸文件

- [docs/bench.zh-TW.md](docs/bench.zh-TW.md) — runner 的用法、並行度造成的問題，以及為何有一題 trial 數特別多。
- [docs/scoring.zh-TW.md](docs/scoring.zh-TW.md) — 計分器怎麼讀回覆、怎麼分類失敗。
- [docs/answer-keys.zh-TW.md](docs/answer-keys.zh-TW.md) — 答案怎麼驗證，以及兩次改 key 的原因。
- [docs/results.zh-TW.md](docs/results.zh-TW.md) — 三張結果表與延遲表的全文。

## 授權

MIT — see [LICENSE](LICENSE).
