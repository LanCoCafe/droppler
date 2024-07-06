# LanCo Café

1. 利用特定 Prompt 詢問 LLM 是否有做事實查核的必要，而且能夠查證

> This is a message from a casual group chat. Please tell if the fact checking is needed, and the reason that fact checking is needed.\n
> {message}
> Output in the following JSON format:
```json
{
    "needed": true,
    "reason": "..."
}
```

2. 標記這則訊息，利用 LLM 為訊息進行分類，目前暫定以下幾個：

>  Categorize the message with the following tags. Match as much as possible.
```json
[
    "政治",
    "明星",
    "爭議"
]
```

3. 如果任何一個 Tag 符合群組的設定，詢問 LLM 可以以什麼關鍵字進行搜尋
```json
{
    "keywords": []
}
```

4. 利用 Google 或 Bing 等搜尋引擎搜尋相關議題，並將前五個網頁作為 Prompt 回傳給 LLM，並結合訊息本身與網頁訊息進行 Fact-Checking

5. 回傳訊息

## Images
如果訊息是 Image，將 Image 傳入給 Gemini Vision API 獲得他的對應文字，並放入上方的 Workflow


## Caching
將每一則完整經過 Fact-Checking Flow 的訊息存入資料庫，使下次查詢不必重新經過整個流程