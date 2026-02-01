
import time
import subprocess
import ctypes
import yaml
import os
from datetime import datetime

# Yasb bar hide/show commands
YASBC_HIDE = ["yasbc", "hide-bar"]
YASBC_SHOW = ["yasbc", "show-bar"]

# GlazeWM config path and gap keys
glazewm_config = os.path.expanduser(r'C:/Users/mert/.glzr/glazewm/config.yaml')
GAP_KEY = ["gaps", "outer_gap", "top"]

def get_mouse_pos():
    class POINT(ctypes.Structure):
        _fields_ = [ ("x", ctypes.c_long), ("y", ctypes.c_long) ]
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

def get_bar_height():
    # Yasb bar height is 32px by default, plus top padding (4px)
    return 32 + 4

def get_screen_size():
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def read_glazewm_top_gap():
    with open(glazewm_config, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    gap = data
    for k in GAP_KEY:
        gap = gap[k]
    if isinstance(gap, str) and gap.endswith('px'):
        return int(gap[:-2])
    return int(gap)

def set_glazewm_top_gap(val):
    with open(glazewm_config, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    gap = data
    for k in GAP_KEY[:-1]:
        gap = gap[k]
    # px ekle
    gap[GAP_KEY[-1]] = f"{val}px"
    with open(glazewm_config, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)
    log(f"GlazeWM config güncellendi: top gap -> {val}px")

def log(msg):
    log_path = os.path.expanduser(r'C:/Users/mert/.config/yasb/yasb_glazewm_auto_hide.log')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"[{now}] {msg}\n")

def reload_glazewm():
    # Komut satırı penceresi açılmasın diye
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    subprocess.Popen(["glazewm", "command", "wm-reload-config"], startupinfo=startupinfo)

def run_yasbc(cmd):
    # Komut satırı penceresi açılmasın diye
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    subprocess.Popen(cmd, startupinfo=startupinfo)

def main():
    bar_height = get_bar_height()
    screen_w, _ = get_screen_size()
    # Script başlarken top gap'i her durumda 0px yap
    with open(glazewm_config, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    gap = data
    for k in GAP_KEY[:-1]:
        gap = gap[k]
    gap[GAP_KEY[-1]] = "0px"
    with open(glazewm_config, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)
    log("Script başında top gap 0px olarak ayarlandı.")
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    subprocess.Popen(["glazewm", "command", "wm-reload-config"], startupinfo=startupinfo)
    time.sleep(0.5)
    orig_gap = read_glazewm_top_gap()
    last_state = None
    hide_start_time = None

    while True:
        _, y = get_mouse_pos()
        in_bar = y <= bar_height
        
        if in_bar:
            # Mouse bar üzerinde: saklama süresini sıfırla, barı göster
            hide_start_time = None
            if last_state != 'show':
                log("YASB bar SHOW + gap restore")
                run_yasbc(YASBC_SHOW)
                set_glazewm_top_gap(orig_gap)
                reload_glazewm()
                last_state = 'show'
        else:
            # Mouse bar dışında
            if last_state != 'hide':
                # Eğer bar açıksa, süre saymaya başla
                if hide_start_time is None:
                    hide_start_time = time.time()
                
                # 2 saniye geçtiyse gizle
                if time.time() - hide_start_time > 2.0:
                    log("YASB bar HIDE + gap -30")
                    run_yasbc(YASBC_HIDE)
                    time.sleep(0.5)
                    set_glazewm_top_gap(-30)
                    reload_glazewm()
                    last_state = 'hide'
                    hide_start_time = None

        time.sleep(0.1)

if __name__ == "__main__":
    main()
