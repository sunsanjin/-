"""
鼠标光标颜色更改器 (Mouse Cursor Color Changer)
Windows 应用程序 - 更改系统鼠标指针颜色
"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import ctypes
import ctypes.wintypes
import winreg
import sys
import os

# ============================================================
# Windows API 定义
# ============================================================

# 常量
OCR_NORMAL = 32512  # IDC_ARROW
SPI_SETCURSORS = 0x0057
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02
DIB_RGB_COLORS = 0
BI_RGB = 0
IMAGE_CURSOR = 2
LR_SHARED = 0x00008000
CURSOR_SHOWING = 0x00000001

# DLL 加载
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

# ---- 结构定义 ----

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.wintypes.LONG), ("y", ctypes.wintypes.LONG)]

class ICONINFO(ctypes.Structure):
    _fields_ = [
        ("fIcon",   ctypes.wintypes.BOOL),
        ("xHotspot", ctypes.wintypes.DWORD),
        ("yHotspot", ctypes.wintypes.DWORD),
        ("hbmMask",  ctypes.wintypes.HBITMAP),
        ("hbmColor", ctypes.wintypes.HBITMAP),
    ]

class BITMAP(ctypes.Structure):
    _fields_ = [
        ("bmType",      ctypes.wintypes.LONG),
        ("bmWidth",     ctypes.wintypes.LONG),
        ("bmHeight",    ctypes.wintypes.LONG),
        ("bmWidthBytes", ctypes.wintypes.LONG),
        ("bmPlanes",    ctypes.wintypes.WORD),
        ("bmBitsPixel", ctypes.wintypes.WORD),
        ("bmBits",      ctypes.c_void_p),
    ]

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize",          ctypes.wintypes.DWORD),
        ("biWidth",         ctypes.wintypes.LONG),
        ("biHeight",        ctypes.wintypes.LONG),
        ("biPlanes",        ctypes.wintypes.WORD),
        ("biBitCount",      ctypes.wintypes.WORD),
        ("biCompression",   ctypes.wintypes.DWORD),
        ("biSizeImage",     ctypes.wintypes.DWORD),
        ("biXPelsPerMeter", ctypes.wintypes.LONG),
        ("biYPelsPerMeter", ctypes.wintypes.LONG),
        ("biClrUsed",       ctypes.wintypes.DWORD),
        ("biClrImportant",  ctypes.wintypes.DWORD),
    ]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ("bmiHeader", BITMAPINFOHEADER),
        ("bmiColors", ctypes.wintypes.DWORD * 1),
    ]

class CURSORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize",     ctypes.wintypes.DWORD),
        ("flags",      ctypes.wintypes.DWORD),
        ("hCursor",    ctypes.wintypes.HANDLE),
        ("ptScreenPos", POINT),
    ]

# ---- 函数签名 ----

user32.LoadCursorW.argtypes = [ctypes.wintypes.HINSTANCE, ctypes.c_void_p]
user32.LoadCursorW.restype = ctypes.wintypes.HICON

user32.GetIconInfo.argtypes = [ctypes.wintypes.HICON, ctypes.POINTER(ICONINFO)]
user32.GetIconInfo.restype = ctypes.wintypes.BOOL

user32.CreateIconIndirect.argtypes = [ctypes.POINTER(ICONINFO)]
user32.CreateIconIndirect.restype = ctypes.wintypes.HICON

user32.SetSystemCursor.argtypes = [ctypes.wintypes.HICON, ctypes.wintypes.DWORD]
user32.SetSystemCursor.restype = ctypes.wintypes.BOOL

user32.DestroyIcon.argtypes = [ctypes.wintypes.HICON]
user32.DestroyIcon.restype = ctypes.wintypes.BOOL

user32.SystemParametersInfoW.argtypes = [
    ctypes.wintypes.UINT, ctypes.wintypes.UINT,
    ctypes.c_void_p, ctypes.wintypes.UINT
]
user32.SystemParametersInfoW.restype = ctypes.wintypes.BOOL

user32.GetDC.argtypes = [ctypes.wintypes.HWND]
user32.GetDC.restype = ctypes.wintypes.HDC

user32.ReleaseDC.argtypes = [ctypes.wintypes.HWND, ctypes.wintypes.HDC]
user32.ReleaseDC.restype = ctypes.c_int

user32.GetCursorInfo.argtypes = [ctypes.POINTER(CURSORINFO)]
user32.GetCursorInfo.restype = ctypes.wintypes.BOOL

user32.DrawIcon.argtypes = [ctypes.wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.wintypes.HICON]
user32.DrawIcon.restype = ctypes.wintypes.BOOL

gdi32.GetObjectW.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p]
gdi32.GetObjectW.restype = ctypes.c_int

gdi32.CreateCompatibleDC.argtypes = [ctypes.wintypes.HDC]
gdi32.CreateCompatibleDC.restype = ctypes.wintypes.HDC

gdi32.DeleteDC.argtypes = [ctypes.wintypes.HDC]
gdi32.DeleteDC.restype = ctypes.wintypes.BOOL

gdi32.SelectObject.argtypes = [ctypes.wintypes.HDC, ctypes.wintypes.HGDIOBJ]
gdi32.SelectObject.restype = ctypes.wintypes.HGDIOBJ

gdi32.CreateDIBSection.argtypes = [
    ctypes.wintypes.HDC, ctypes.POINTER(BITMAPINFO),
    ctypes.wintypes.UINT, ctypes.POINTER(ctypes.c_void_p),
    ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
]
gdi32.CreateDIBSection.restype = ctypes.wintypes.HBITMAP

gdi32.GetDIBits.argtypes = [
    ctypes.wintypes.HDC, ctypes.wintypes.HBITMAP,
    ctypes.wintypes.UINT, ctypes.wintypes.UINT,
    ctypes.c_void_p, ctypes.POINTER(BITMAPINFO),
    ctypes.wintypes.UINT
]
gdi32.GetDIBits.restype = ctypes.c_int

gdi32.SetDIBits.argtypes = [
    ctypes.wintypes.HDC, ctypes.wintypes.HBITMAP,
    ctypes.wintypes.UINT, ctypes.wintypes.UINT,
    ctypes.c_void_p, ctypes.POINTER(BITMAPINFO),
    ctypes.wintypes.UINT
]
gdi32.SetDIBits.restype = ctypes.c_int

gdi32.DeleteObject.argtypes = [ctypes.wintypes.HGDIOBJ]
gdi32.DeleteObject.restype = ctypes.wintypes.BOOL

gdi32.CreateBitmap.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p]
gdi32.CreateBitmap.restype = ctypes.wintypes.HBITMAP

# ============================================================
# 光标颜色更改引擎
# ============================================================

def _make_bmi(width, height, bpp=32):
    """创建 BITMAPINFO 结构（32bpp top-down DIB）"""
    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = width
    bmi.bmiHeader.biHeight = -height  # top-down
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = bpp
    bmi.bmiHeader.biCompression = BI_RGB
    return bmi


def change_cursor_color(r, g, b):
    """
    将系统光标的颜色改为指定 RGB 值。
    通过绘制当前光标 → 读取像素 → 着色 → 创建新光标 的方式实现。
    """
    # ---- 1. 加载系统光标 ----
    hCursor = user32.LoadCursorW(0, OCR_NORMAL)
    if not hCursor:
        raise RuntimeError("无法加载系统光标")

    # ---- 2. 获取光标尺寸和热点 ----
    icon_info = ICONINFO()
    if not user32.GetIconInfo(hCursor, ctypes.byref(icon_info)):
        raise RuntimeError("无法获取光标信息")

    width = height = 32  # 默认值
    try:
        if icon_info.hbmColor:
            bmp = BITMAP()
            gdi32.GetObjectW(icon_info.hbmColor, ctypes.sizeof(BITMAP), ctypes.byref(bmp))
            width = bmp.bmWidth
            height = abs(bmp.bmHeight)
        elif icon_info.hbmMask:
            bmp = BITMAP()
            gdi32.GetObjectW(icon_info.hbmMask, ctypes.sizeof(BITMAP), ctypes.byref(bmp))
            width = bmp.bmWidth
            height = abs(bmp.bmHeight) // 2
    except Exception:
        pass  # 使用默认值

    hot_x, hot_y = icon_info.xHotspot, icon_info.yHotspot

    # ---- 3. 将光标绘制到内存 DC 并读回像素 ----
    screen_dc = user32.GetDC(0)
    if not screen_dc:
        raise RuntimeError("无法获取屏幕 DC")

    mem_dc = gdi32.CreateCompatibleDC(screen_dc)
    if not mem_dc:
        user32.ReleaseDC(0, screen_dc)
        raise RuntimeError("无法创建兼容 DC")

    bmi = _make_bmi(width, height)
    ppvBits = ctypes.c_void_p(0)
    hBitmap = gdi32.CreateDIBSection(
        screen_dc, ctypes.byref(bmi), DIB_RGB_COLORS,
        ctypes.byref(ppvBits), 0, 0
    )
    if not hBitmap:
        gdi32.DeleteDC(mem_dc)
        user32.ReleaseDC(0, screen_dc)
        raise RuntimeError("无法创建 DIB Section")

    old_bmp = gdi32.SelectObject(mem_dc, hBitmap)

    # 绘制光标
    user32.DrawIcon(mem_dc, 0, 0, hCursor)

    # 读取像素
    pixel_size = width * height * 4
    pixels = (ctypes.c_ubyte * pixel_size)()
    dib_ok = gdi32.GetDIBits(screen_dc, hBitmap, 0, height, pixels,
                              ctypes.byref(bmi), DIB_RGB_COLORS)

    gdi32.SelectObject(mem_dc, old_bmp)
    gdi32.DeleteObject(hBitmap)
    gdi32.DeleteDC(mem_dc)
    user32.ReleaseDC(0, screen_dc)

    if dib_ok == 0:
        # GetDIBits 失败，回退到注册表方法
        return _change_by_registry(r, g, b)

    # ---- 4. 着色（将非透明像素改为目标颜色）----
    # 像素格式: BGRA (Blue, Green, Red, Alpha)
    for i in range(width * height):
        offset = i * 4
        alpha = pixels[offset + 3]
        if alpha > 128:
            pixels[offset]     = b      # Blue
            pixels[offset + 1] = g      # Green
            pixels[offset + 2] = r      # Red
            # Alpha 保持不变

    # ---- 5. 创建 AND 掩码（单色位图，全 0 表示透明度由 alpha 通道控制）----
    stride = ((width + 31) // 32) * 4
    mask_data = (ctypes.c_ubyte * (stride * height))()  # 全零
    hbmMask = gdi32.CreateBitmap(width, height, 1, 1, mask_data)
    if not hbmMask:
        raise RuntimeError("无法创建掩码位图")

    # ---- 6. 创建新的颜色位图 ----
    screen_dc2 = user32.GetDC(0)
    hbmColor = gdi32.CreateDIBSection(
        screen_dc2, ctypes.byref(bmi), DIB_RGB_COLORS,
        ctypes.byref(ppvBits), 0, 0
    )
    if not hbmColor:
        user32.ReleaseDC(0, screen_dc2)
        gdi32.DeleteObject(hbmMask)
        raise RuntimeError("无法创建颜色位图")

    gdi32.SetDIBits(screen_dc2, hbmColor, 0, height, pixels,
                    ctypes.byref(bmi), DIB_RGB_COLORS)
    user32.ReleaseDC(0, screen_dc2)

    # ---- 7. 创建新光标 ----
    new_info = ICONINFO()
    new_info.fIcon = False
    new_info.xHotspot = hot_x
    new_info.yHotspot = hot_y
    new_info.hbmMask = hbmMask
    new_info.hbmColor = hbmColor

    hNewCursor = user32.CreateIconIndirect(ctypes.byref(new_info))
    gdi32.DeleteObject(hbmColor)
    gdi32.DeleteObject(hbmMask)

    if not hNewCursor:
        raise RuntimeError("无法创建新光标")

    # ---- 8. 应用 ----
    if not user32.SetSystemCursor(hNewCursor, OCR_NORMAL):
        user32.DestroyIcon(hNewCursor)
        raise RuntimeError("无法设置系统光标")

    user32.DestroyIcon(hNewCursor)


def _change_by_registry(r, g, b):
    """
    备选方案：通过 Windows 10/11 辅助功能设置更改指针颜色。
    """
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Accessibility"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0,
                             winreg.KEY_SET_VALUE)
        # CursorType=0 表示使用自定义颜色
        winreg.SetValueEx(key, "CursorType", 0, winreg.REG_DWORD, 0)
        # CursorColor 格式: 0x00BBGGRR
        color_val = (b << 16) | (g << 8) | r
        winreg.SetValueEx(key, "CursorColor", 0, winreg.REG_DWORD, color_val)
        winreg.CloseKey(key)

        # 发送系统设置变更广播
        user32.SystemParametersInfoW(
            SPI_SETCURSORS, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
        )
        return True
    except Exception as e:
        raise RuntimeError(f"注册表方式也失败: {e}")


def reset_cursor():
    """将光标重置为系统默认。"""
    user32.SystemParametersInfoW(
        SPI_SETCURSORS, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )


def apply_change(r, g, b):
    """尝试 GDI 方式，失败则回退到注册表方式。"""
    try:
        change_cursor_color(r, g, b)
    except RuntimeError:
        # 回退到注册表方式
        _change_by_registry(r, g, b)


# ============================================================
# GUI 界面
# ============================================================

# 预置颜色 (名称, RGB)
PRESET_COLORS = [
    ("红色",    (220, 50,  50)),
    ("蓝色",    (30,  120, 255)),
    ("绿色",    (40,  200, 60)),
    ("黄色",    (255, 220, 30)),
    ("紫色",    (160, 40,  240)),
    ("橙色",    (255, 140, 20)),
    ("青色",    (0,   220, 220)),
    ("粉色",    (255, 80,  160)),
    ("白色",    (240, 240, 240)),
    ("黑色",    (40,  40,  40)),
]


class CursorChangerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("鼠标光标颜色更改器")
        x = (root.winfo_screenwidth() - 480) // 2
        y = (root.winfo_screenheight() - 400) // 2
        self.root.geometry(f"480x400+{x}+{y}")
        self.root.resizable(False, False)
        self.root.configure(bg="#f5f5f5")

        try:
            # Windows: 设置任务栏图标
            root.iconbitmap(default="")
        except Exception:
            pass

        # ----- 顶部标题 -----
        title_frame = tk.Frame(root, bg="#f5f5f5")
        title_frame.pack(fill="x", pady=(25, 5))

        tk.Label(
            title_frame, text="鼠标光标颜色更改器",
            font=("Microsoft YaHei", 18, "bold"),
            bg="#f5f5f5", fg="#222"
        ).pack()

        tk.Label(
            title_frame, text="选择颜色即可立即更改鼠标指针颜色",
            font=("Microsoft YaHei", 9),
            bg="#f5f5f5", fg="#888"
        ).pack(pady=(2, 0))

        # ----- 状态栏 -----
        self.status_var = tk.StringVar(value="准备就绪")
        self.status_label = tk.Label(
            root, textvariable=self.status_var,
            font=("Microsoft YaHei", 9),
            bg="#f5f5f5", fg="#888"
        )
        self.status_label.pack(pady=(15, 5))

        # ----- 颜色按钮 ----
        colors_frame = tk.Frame(root, bg="#f5f5f5")
        colors_frame.pack(pady=5)

        for row_idx in range(2):
            row_frame = tk.Frame(colors_frame, bg="#f5f5f5")
            row_frame.pack(pady=4)
            for col_idx in range(5):
                i = row_idx * 5 + col_idx
                if i >= len(PRESET_COLORS):
                    break
                name, (cr, cg, cb) = PRESET_COLORS[i]
                luminance = 0.299 * cr + 0.587 * cg + 0.114 * cb
                text_color = "white" if luminance < 150 else "#222"

                btn = tk.Button(
                    row_frame,
                    text=name,
                    width=6,
                    command=lambda r=cr, g=cg, b=cb, n=name: self._on_color(r, g, b, n),
                    font=("Microsoft YaHei", 10),
                    bg=f"#{cr:02x}{cg:02x}{cb:02x}",
                    fg=text_color,
                    activebackground=f"#{min(cr+40,255):02x}{min(cg+40,255):02x}{min(cb+40,255):02x}",
                    activeforeground=text_color,
                    relief=tk.RAISED, bd=1,
                    padx=6, pady=8,
                    cursor="hand2",
                )
                btn.pack(side=tk.LEFT, padx=5)

        # ----- 自定义颜色按钮 -----
        btn_frame = tk.Frame(root, bg="#f5f5f5")
        btn_frame.pack(pady=(12, 4))

        tk.Button(
            btn_frame, text="自定义颜色...",
            command=self._pick_custom,
            font=("Microsoft YaHei", 10),
            bg="#e8e8e8", fg="#333",
            activebackground="#ddd",
            relief=tk.RAISED, bd=1,
            padx=16, pady=4, cursor="hand2",
        ).pack(side=tk.LEFT, padx=6)

        tk.Button(
            btn_frame, text="恢复默认",
            command=self._reset,
            font=("Microsoft YaHei", 10),
            bg="#ff6b6b", fg="white",
            activebackground="#ff5252",
            relief=tk.RAISED, bd=1,
            padx=16, pady=4, cursor="hand2",
        ).pack(side=tk.LEFT, padx=6)

        # ----- 底部说明 -----
        tk.Label(
            root, text="提示：程序退出后光标颜色会保留到下次重启",
            font=("Microsoft YaHei", 8),
            bg="#f5f5f5", fg="#aaa"
        ).pack(side="bottom", pady=(0, 12))

    def _set_status(self, text, color="#888"):
        self.status_var.set(text)
        self.status_label.config(fg=color)
        self.root.update()

    def _on_color(self, r, g, b, name):
        try:
            self._set_status(f"正在应用: {name} ...", "#555")
            apply_change(r, g, b)
            self._set_status(f"已更改为: {name}", "#2ecc71")
        except Exception as e:
            self._set_status(f"失败: {e}", "#e74c3c")
            messagebox.showerror("错误",
                f"更改光标颜色时出错:\n{e}\n\n"
                "请尝试以管理员身份运行此程序。",
                parent=self.root)

    def _pick_custom(self):
        code = colorchooser.askcolor(title="选择光标颜色", parent=self.root)
        if code and code[0]:
            r, g, b = (int(x) for x in code[0])
            self._on_color(r, g, b, f"RGB({r},{g},{b})")

    def _reset(self):
        try:
            self._set_status("正在恢复默认 ...", "#555")
            reset_cursor()
            self._set_status("已恢复默认光标", "#2ecc71")
        except Exception as e:
            self._set_status(f"失败: {e}", "#e74c3c")


def main():
    root = tk.Tk()
    app = CursorChangerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
