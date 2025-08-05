"""
====================================================
 MapleStory Artale 自動骰點工具
====================================================

作者: Eric (你的名字)
日期: 2025-08-06
專案: AutoDiceRoll
用途:
- template_generator.py : 生成角色創建畫面所需的模板圖片
- stat_reroll_gui.py    : 自動重骰能力值直到符合設定

版權聲明:
本程式僅限個人學習與娛樂用途，嚴禁任何形式的商業用途。
若需修改或轉載，請務必註明原作者。

授權條款: CC BY-NC-SA 4.0
(姓名標示-非商業性-相同方式分享)

====================================================
"""

import customtkinter as ctk
from tkinter import messagebox
from PIL import ImageGrab
import pytesseract
import pyautogui
import numpy as np
import cv2
import os
import time
import json
import keyboard  # 新增全域熱鍵監聽

pytesseract.pytesseract.tesseract_cmd = os.path.join(
    os.getcwd(), "Tesseract-OCR", "tesseract.exe"
)

FONT = ("Microsoft JhengHei", 14)
CONFIG_FILE = "stat_reroll_config.json"
LOG_FILE = "stat_reroll_log.txt"
TEMPLATE_DIR = "templates"

TEMPLATES = {
    "str": os.path.join(TEMPLATE_DIR, "template_str.png"),
    "dex": os.path.join(TEMPLATE_DIR, "template_dex.png"),
    "int": os.path.join(TEMPLATE_DIR, "template_int.png"),
    "luk": os.path.join(TEMPLATE_DIR, "template_luk.png"),
    "roll": os.path.join(TEMPLATE_DIR, "template_roll.png"),
}

DEBUG_MODE = False
stop_flag = False
stop_hotkey = "F12"  # 預設中斷熱鍵


def register_hotkey(key="F12"):
    global stop_hotkey
    stop_hotkey = key

    try:
        # 先解除舊的熱鍵（若存在）
        keyboard.remove_hotkey(stop_hotkey)
    except KeyError:
        pass  # 如果沒有舊的熱鍵，忽略錯誤

    keyboard.add_hotkey(stop_hotkey, stop_reroll)
    print(f"⏹️ 已綁定熱鍵 [{stop_hotkey}] 作為骰點中斷")


def stop_reroll():
    global stop_flag
    stop_flag = True
    print("⏹️ 已觸發中斷熱鍵")


def find_template(template_path, threshold=0.7):
    screen = ImageGrab.grab()
    screen_gray = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2GRAY)
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"❌ 找不到範本：{template_path}")
        return None
    res = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    if max_val < threshold:
        print(f"⚠️ {os.path.basename(template_path)} 相似度過低：{max_val:.2f}")
        return None
    h, w = template.shape
    return (max_loc[0], max_loc[1], w, h)


def ocr_number(bbox, label=""):
    img = ImageGrab.grab(bbox).convert("L")
    img = img.resize((img.width * 2, img.height * 2))
    _, thresh = cv2.threshold(np.array(img), 180, 255, cv2.THRESH_BINARY)
    text = pytesseract.image_to_string(
        thresh, config="--psm 7 -c tessedit_char_whitelist=0123456789"
    ).strip()

    if DEBUG_MODE:
        cv2.imshow(f"OCR Debug - {label}", thresh)
        print(f"[DEBUG] {label}: OCR結果 -> {repr(text)}")
        cv2.waitKey(500)
        cv2.destroyWindow(f"OCR Debug - {label}")

    return int(text) if text.isdigit() else None


def get_stats(return_boxes=False):
    stats = {}
    boxes = {}
    for key in ["str", "dex", "int", "luk"]:
        loc = find_template(TEMPLATES[key])
        if loc:
            x, y, w, h = loc
            bbox = (x + w, y, x + 2 * w, y + h)  # 往右同寬
            stats[key] = ocr_number(bbox, label=key.upper())
            boxes[key] = bbox
        else:
            stats[key] = None
    if return_boxes:
        return stats, boxes
    return stats


def check_match(stats, targets):
    if sum(stats.values()) != 25:
        return False
    for stat in ["str", "dex", "int", "luk"]:
        if targets[stat] != "X" and stats[stat] != int(targets[stat]):
            return False
    return True


def preview_positions():
    messagebox.showinfo("提示", "請切換至遊戲畫面後按確定，3 秒後開始預覽")
    time.sleep(3)

    screen = ImageGrab.grab()
    screen_np = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
    stats, boxes = get_stats(return_boxes=True)
    roll_loc = find_template(TEMPLATES["roll"])

    for key, bbox in boxes.items():
        x1, y1, x2, y2 = bbox
        cv2.rectangle(screen_np, (x1, y1), (x2, y2), (0, 255, 0), 2)
        text = str(stats[key]) if stats[key] is not None else "?"
        cv2.putText(
            screen_np,
            f"{key.upper()}={text}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

    if roll_loc:
        rx, ry, rw, rh = roll_loc
        cv2.rectangle(screen_np, (rx, ry), (rx + rw, ry + rh), (0, 0, 255), 2)
        cv2.putText(
            screen_np,
            "ROLL",
            (rx, ry - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
        )

    cv2.imshow("定位預覽", screen_np)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def auto_reroll(targets):
    global stop_flag
    stop_flag = False
    messagebox.showinfo(
        "提示", f"請切換至遊戲畫面後按確定，3 秒後開始骰點\n中斷熱鍵: [{stop_hotkey}]"
    )
    time.sleep(3)

    roll_loc = find_template(TEMPLATES["roll"])
    if not roll_loc:
        messagebox.showerror("錯誤", "找不到骰子按鈕模板！")
        return
    roll_x = roll_loc[0] + roll_loc[2] // 2
    roll_y = roll_loc[1] + roll_loc[3] // 2

    print(f"⚡ 開始骰點，按 [{stop_hotkey}] 可隨時中斷")
    count = 0
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            while True:
                if stop_flag:
                    print("⏹️ 使用者透過熱鍵中斷")
                    messagebox.showinfo("中斷", "骰點已由使用者中斷")
                    break

                stats = get_stats()
                line = f"{count+1:03d} 次: {stats}\n"
                print(line.strip())
                f.write(line)
                if all(v is not None for v in stats.values()) and check_match(
                    stats, targets
                ):
                    print("✅ 匹配成功！")
                    messagebox.showinfo("完成", f"找到符合條件的點數：{stats}")
                    break
                pyautogui.click(roll_x, roll_y)
                time.sleep(0.5)
                count += 1
    except Exception as e:
        print("❌ 出錯:", e)


class StatRerollGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("角色自動骰點工具")
        self.root.geometry("420x480")
        self.targets = {"str": "X", "dex": "X", "int": "X", "luk": "X"}
        self.create_widgets()
        self.load_config()

    def create_widgets(self):
        global DEBUG_MODE
        row = 0
        for stat in ["str", "dex", "int", "luk"]:
            ctk.CTkLabel(self.root, text=f"{stat.upper()} 目標值", font=FONT).grid(
                row=row, column=0, padx=10, pady=10
            )
            setattr(self, f"{stat}_entry", ctk.CTkEntry(self.root, width=60, font=FONT))
            getattr(self, f"{stat}_entry").grid(row=row, column=1)
            row += 1

        self.debug_check = ctk.CTkCheckBox(
            self.root, text="啟用 Debug 模式", font=FONT, command=self.toggle_debug
        )
        self.debug_check.grid(row=row, column=0, columnspan=2, pady=10)
        row += 1

        ctk.CTkLabel(self.root, text="中斷熱鍵 (預設F12)", font=FONT).grid(
            row=row, column=0
        )
        self.hotkey_entry = ctk.CTkEntry(self.root, width=80, font=FONT)
        self.hotkey_entry.insert(0, "F12")
        self.hotkey_entry.grid(row=row, column=1)
        row += 1

        ctk.CTkButton(
            self.root, text="套用熱鍵", font=FONT, command=self.apply_hotkey
        ).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1

        ctk.CTkButton(
            self.root, text="預覽定位", font=FONT, command=preview_positions
        ).grid(row=row, column=0, columnspan=2, pady=10)
        row += 1

        ctk.CTkButton(
            self.root, text="開始骰點", font=FONT, command=self.start_reroll
        ).grid(row=row, column=0, columnspan=2, pady=20)
        row += 1
        ctk.CTkButton(
            self.root, text="儲存設定", font=FONT, command=self.save_config
        ).grid(row=row, column=0)
        ctk.CTkButton(self.root, text="離開", font=FONT, command=self.root.quit).grid(
            row=row, column=1
        )

    def toggle_debug(self):
        global DEBUG_MODE
        DEBUG_MODE = not DEBUG_MODE
        print(f"🔍 Debug 模式 {'開啟' if DEBUG_MODE else '關閉'}")

    def apply_hotkey(self):
        new_key = self.hotkey_entry.get().strip().upper()
        if new_key:
            register_hotkey(new_key)
            messagebox.showinfo("熱鍵設定", f"已設定 [{new_key}] 為中斷熱鍵")

    def start_reroll(self):
        for stat in ["str", "dex", "int", "luk"]:
            self.targets[stat] = getattr(self, f"{stat}_entry").get().strip() or "X"
        auto_reroll(self.targets)

    def save_config(self):
        config = {
            "targets": self.targets,
            "stop_hotkey": self.hotkey_entry.get().strip().upper(),
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        messagebox.showinfo("成功", "設定已儲存！")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.targets = config.get("targets", self.targets)
                for stat in ["str", "dex", "int", "luk"]:
                    getattr(self, f"{stat}_entry").insert(
                        0, self.targets.get(stat, "X")
                    )
                hotkey = config.get("stop_hotkey", "F12")
                self.hotkey_entry.delete(0, "end")
                self.hotkey_entry.insert(0, hotkey)
                register_hotkey(hotkey)


if __name__ == "__main__":
    root = ctk.CTk()
    app = StatRerollGUI(root)
    root.mainloop()
