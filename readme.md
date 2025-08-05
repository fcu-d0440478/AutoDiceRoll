# MapleStory Artale 自動骰點工具

這是一個針對 **MapleStory Worlds - Artale (繁體中文版)** 開發的輔助工具。  
可在角色創建時自動重骰能力值，直到符合玩家設定的條件。
能自動識別屬性數值位置，並且不需要額外框選圖片位置。

---

## 🛠️ 使用技術

- **Python GUI**：使用 [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) 建立介面
- **畫面截圖**：透過 [Pillow (ImageGrab)](https://pillow.readthedocs.io/) 抓取遊戲畫面
- **影像處理**：利用 [OpenCV](https://opencv.org/) 進行模板比對 (Template Matching)
- **文字辨識**：整合 [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) 辨識能力值數字
- **自動操作**：用 [PyAutoGUI](https://pyautogui.readthedocs.io/) 模擬滑鼠點擊骰子按鈕
- **全域熱鍵監聽**：透過 [keyboard](https://pypi.org/project/keyboard/) 支援遊戲前景下的中斷快捷鍵

---

## 📦 環境需求

- Windows 系統
- Python 3.9 ~ 3.13
- 已放置 **Tesseract-OCR** 資料夾於專案根目錄（內含 `tesseract.exe`）
- 已放置 templates 資料夾需包含四個屬性的文字以及骰子的截圖

### 安裝套件

```bash
pip install customtkinter pytesseract opencv-python screeninfo pillow pyautogui keyboard
```

---

# 🚀 使用方式

啟動自動骰點 GUI
執行：`python stat_reroll_gui.py`

# GUI 功能

## 1.輸入目標數值

輸入 STR/DEX/INT/LUK 四項（例：4/4/13/4）

輸入 X 表示該屬性任意值

## 2.預覽定位(可略過)

顯示目前模板定位框與 OCR 結果

按「確定」後，3 秒後開始截圖預覽

## 3.Debug 模式(可略過)

勾選後，OCR 過程會顯示擷取的數值影像與辨識結果

## 4.中斷熱鍵

預設為 F12

可輸入 F10/F11/F12 等自訂熱鍵

## 5.儲存設定

基本上輸入目標數值後，就可以儲存設定準備使用了

## 6.開始骰點

程式會自動擲骰，直到符合條件

可隨時按下熱鍵(預設 F12)中斷

## 📌 注意事項

- 開始前務必切回遊戲畫面，並於提示框按下「確定」
- 程式會等待 3 秒 緩衝後再執行
- 辨識結果會記錄到 stat_reroll_log.txt
- 若 OCR 結果不準，可開啟 Debug 模式確認

---

## 產生模板圖片的程式碼

若玩的是國際服語言不同可以使用這個蓋掉原來中文的的模板圖片。
執行：`python template_generator.py`

依序框選：

1. 力量文字
2. 敏捷文字
3. 智力文字
4. 幸運文字
5. 骰子按鈕

完成後會在 templates/ 產生：

- template_str.png
- template_dex.png
- template_int.png
- template_luk.png
- template_roll.png
