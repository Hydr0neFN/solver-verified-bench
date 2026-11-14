[English](answer-keys.md) · [繁體中文](answer-keys.zh-TW.md)

# 答案 key

[回 README](../README.md)

各層答案怎麼驗證，以及跑完看到結果後改掉的兩份 key。逐檔說明見 [truth/README.md](../truth/README.md)，以及 `truth/tier2.json` 裡的 `note` 欄位。

## 各層的驗證方式

- **Tier 1。** `tier1.json` 是手寫的，沒有生成器輸出可以比對，所以由 `bench/verify_tier1.py` 從頭重算每一題能算的答案再對 key。結果是 **8 verified, 0 mismatched, 7 not computable**，那七題會在輸出裡逐一點名。
- **Tier 2。** `generated-tier2.json` 是 solver 原始輸出，`tier2.json` 是整理後的 key。兩份都進版控，差異可以直接查。
- **Tier 3。** 整理後的 key 跟生成器產出值相同，只有外層格式不同。`bench/audit_ambiguity.py` 會列舉一個 64 條規則的家族，確認只剩一個預測成立。

## 兩份錯誤的答案 key，是看到結果後才改的

兩次都是同一條規則抓出來的：*每個模型都錯同一題，先懷疑 key，別先懷疑模型。* 兩次修正對所有模型一視同仁，所以不會偏袒誰。兩筆都寫在 `truth/tier2.json` 裡。

1. **IEEE 754 binary64 裡最大的可精確表示整數。** key 寫 `2^53`。所有模型都答 `2^1024 - 2^971`，這是對的；`2^53` 回答的是另一個問題：在這數字以下每個整數都可表示。
2. **排程器規格矛盾那題。** 出題時多塞了一個冗餘答案：要求「lease 到期必須重新指派」跟「最多執行一次」、「從不並行執行」都衝突。九次裡七次給的是較強的那一組。現在 key 兩組都接受。

還有一題查過之後沒問題。某條複合網格規則上，所有模型收斂到同一個錯誤網格，這通常是題目有歧義的訊號。`bench/audit_ambiguity.py` 列舉 64 條規則，確認範例足以唯一決定規則，而且 query 用到的每一欄兩種 parity 值都有示範。題目沒問題，只是所有模型一起答錯。
