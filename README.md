# 古埃及文字 ↔ 繁體中文翻譯器
Ancient Egyptian to Simplified Chinese lexicon and hieroglyph translator. (and vice versa)
是一个古埃及文字 // 简体中文词典与象形文字翻译工具，支持 Unicode 埃及象形文字、转写、中文释义、上下文含义和本地 GUI。
小型本地工具。

## 啟動

```bash
python gui.py
```

左邊輸入，右邊自動翻譯。

可選方向：

- Auto
- Egyptian → 中文
- 中文 → Egyptian

## 詞典

詞典在 `dictionary.json`。

中文轉古埃及文字需要詞典裡有對應詞條。沒有的字會顯示 `[未知:字]`。
