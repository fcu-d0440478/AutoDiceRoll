import cv2
import numpy as np
from PIL import ImageGrab
import screeninfo
import time
import os

OUTPUT_DIR = "templates"
os.makedirs(OUTPUT_DIR, exist_ok=True)

drawing = False
start_point = (0, 0)
end_point = (0, 0)
bbox_result = None
img = None
img_copy = None
current_target = None


def draw_rectangle(event, x, y, flags, param):
    global start_point, end_point, drawing, img_copy, bbox_result
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_point = (x, y)
    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        end_point = (x, y)
        img_copy = img.copy()
        cv2.rectangle(img_copy, start_point, end_point, (0, 255, 0), 2)
        cv2.imshow("Select Area", img_copy)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_point = (x, y)
        left = min(start_point[0], end_point[0])
        top = min(start_point[1], end_point[1])
        right = max(start_point[0], end_point[0])
        bottom = max(start_point[1], end_point[1])
        bbox_result = (left, top, right, bottom)
        cv2.rectangle(img_copy, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.imshow("Select Area", img_copy)


def capture_templates(targets):
    global img, img_copy, bbox_result, current_target
    monitor = screeninfo.get_monitors()[0]
    screen_width = monitor.width
    screen_height = monitor.height

    print("⚡ 請切到遊戲創角畫面，3 秒後開始截圖...")
    time.sleep(3)

    screenshot = ImageGrab.grab(bbox=(0, 0, screen_width, screen_height))
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    for name in targets:
        print(f"👉 請框選 {name.upper()} 區域 (滑鼠左鍵拖曳，放開即可)")
        img_copy = img.copy()
        bbox_result = None

        cv2.namedWindow("Select Area", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Select Area", draw_rectangle)

        while True:
            cv2.imshow("Select Area", img_copy)
            if cv2.waitKey(1) == 27 or bbox_result is not None:
                break
        cv2.destroyAllWindows()

        if bbox_result:
            crop = screenshot.crop(bbox_result)
            filename = os.path.join(OUTPUT_DIR, f"template_{name}.png")
            crop.save(filename)
            print(f"✅ 已儲存 {filename}")
        else:
            print(f"⚠️ {name} 未成功框選，跳過。")


if __name__ == "__main__":
    targets = ["str", "dex", "int", "luk", "roll"]
    capture_templates(targets)
    print("🎉 所有模板已完成！存放於 templates/ 資料夾")
