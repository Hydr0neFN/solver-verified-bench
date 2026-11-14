[English](scoring.md) · [繁體中文](scoring.zh-TW.md)

# 計分

[回 README](../README.md)

`bench/score.py` 怎麼把一份原始回覆變成分數，以及怎麼分辨模型失敗和基礎設施失敗。

## 一則回覆怎麼計分

計分完全機械化。題目要求每份回覆最後一行是 `FINAL: <answer>`，計分器取最後一條這種行上的答案，跟 `truth/tier{1,2,3}.json` 比對。比對前會先正規化答案：只留小寫的 ASCII 字母和數字，標點全部拿掉。結果寫進 `results/scores-tier{1,2,3}.json`，並印出比較表。

## 空回覆

空回覆不會被默默丟掉：

1. **模型跑爆自己的時間預算就計 0 分，不剔除。** 剔除逾時等於偏袒最慢的模型。而且逾時一旦發生就被釘死：事後重跑成功也不會把那一格改回來，否則「重跑到過為止」就能把真實失敗洗掉。
2. **基礎設施失敗（配額、節流、認證）排除不計**，那不是模型的問題。兩者靠 stderr 內容與耗時區分。

計分器在 stderr 裡找的標記：基礎設施失敗是 `eligibility check failed`、`authentication required`、`quota`、`resource_exhausted`；逾時是 `timeout waiting for response`。逾時釘在 590 秒，因為 Tier 2、Tier 3 的 `agy --print-timeout` 是 600 秒。用來區分「被節流」和「真的逾時」的耗時表在 [bench.md](bench.zh-TW.md)。
