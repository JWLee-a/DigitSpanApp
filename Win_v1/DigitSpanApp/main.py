import os
import sys
import csv
import json
import tkinter as tk
from tkinter import messagebox, filedialog, Toplevel, scrolledtext
from datetime import datetime
from playsound import playsound
import pygame
from digit_sets import digit_sets

# ------- 리소스 경로 처리 -------
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

# ------- 전역 상태 -------
data_saved = False
response_widgets = {}
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".digitspan_config.json")

# ------- 기본 저장 경로 설정 -------
default_path = os.path.expanduser("~/DigitSpan_save")
def load_last_path():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                return data.get("save_path", default_path)
        except:
            return default_path
    return default_path

def save_last_path(path):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({"save_path": path}, f)
    except:
        pass

os.makedirs(default_path, exist_ok=True)

# ------- GUI 초기화 -------
root = tk.Tk()
root.title("Digit-span test")
root.geometry("1500x600")

# ------- 상단 정보 입력 영역 -------
top_frame = tk.Frame(root)
top_frame.pack(fill='x', padx=10, pady=5)

subject_name = tk.StringVar()
save_path = tk.StringVar(value=load_last_path())

# Subject 입력
tk.Label(top_frame, text="Subject name:").grid(row=0, column=0, sticky='e')
tk.Entry(top_frame, textvariable=subject_name, width=25).grid(row=0, column=1, padx=5)

# 저장 경로 선택
def choose_folder():
    path = filedialog.askdirectory()
    if path:
        save_path.set(path)
        save_last_path(path)

tk.Label(top_frame, text="Save path:").grid(row=1, column=0, sticky='e')
tk.Label(top_frame, textvariable=save_path, fg='blue').grid(row=1, column=1, sticky='w')
tk.Button(top_frame, text="...", command=choose_folder).grid(row=1, column=2)

# Manual 팝업

from tkinter import scrolledtext

def open_manual():
    manual_window = Toplevel(root)
    manual_window.title("Manual")
    manual_window.geometry("700x500")

    manual_text = scrolledtext.ScrolledText(manual_window, wrap='word')
    manual_text.pack(expand=True, fill='both', padx=10, pady=10)

    try:
        with open(resource_path("manual.md"), "r", encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = "Manual 파일을 찾을 수 없습니다.'./manual.md' 파일을 생성해주세요."

    manual_text.insert('1.0', content)
    manual_text.config(state='disabled')

# Manual 버튼 활성화
tk.Button(top_frame, text="Manual", command=open_manual).grid(row=0, column=3, padx=20)

# 제목
tk.Label(root, text="Digit-span test", font=("Helvetica", 16, "bold")).pack(pady=5)

# ------- 메인 테스트 영역 -------
main_frame = tk.Frame(root)
main_frame.pack()

set_categories = ["F_S1", "F_S2", "B_S1", "B_S2"]
column_titles = ["Forward\nSet1", "Forward\nSet2", "Backward\nSet1", "Backward\nSet2"]

for col, set_prefix in enumerate(set_categories):
    section = tk.LabelFrame(main_frame, text=column_titles[col], padx=5, pady=5)
    section.grid(row=0, column=col, padx=5, pady=5)

    tk.Label(section, text="Step", font=("Arial", 10, "bold"), width=4).grid(row=0, column=0, padx=1)
    tk.Label(section, text="Answer", font=("Arial", 10, "bold"), width=8).grid(row=0, column=1, padx=1)
    tk.Label(section, text="", width=2).grid(row=0, column=2)
    tk.Label(section, text="Response", font=("Arial", 10, "bold"), width=10).grid(row=0, column=3, padx=1)
    tk.Label(section, text="Correct?", font=("Arial", 10, "bold"), width=6).grid(row=0, column=4)

    relevant_keys = [k for k in digit_sets if k.startswith(set_prefix)]
    relevant_keys.sort(key=lambda x: int(x.split('_')[2]))

    for r, key in enumerate(relevant_keys, start=1):
        step = key.split('_')[2]
        answer_str = ''.join(str(d) for d in digit_sets[key])
        audio_path = resource_path(os.path.join("wav", "sp_angelina", "Gen", f"{key}.wav"))

        tk.Label(section, text=step, width=4).grid(row=r, column=0, padx=1, pady=1)
        tk.Label(section, text=answer_str, width=8).grid(row=r, column=1, padx=1)


        def play(path=audio_path):
            try:
                pygame.mixer.init()
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
            except Exception as e:
                messagebox.showerror("오류", f"오디오 재생 실패:\n{e}")
        tk.Button(section, text="▶", width=2, command=play).grid(row=r, column=2, padx=1)

        entry = tk.Entry(section, width=10)
        entry.grid(row=r, column=3, padx=1)

        var = tk.IntVar()
        check = tk.Checkbutton(section, variable=var)
        check.grid(row=r, column=4)

        response_widgets[key] = (entry, var)

# ------- 저장 기능 -------
def save_data():
    global data_saved

    subj = subject_name.get().strip()
    path = save_path.get().strip()

    if not subj or not path:
        messagebox.showwarning("입력 필요", "Subject name과 Save path를 모두 입력해주세요.")
        return

    date_str = datetime.today().strftime("%Y-%m-%d")
    filename = f"{subj}_{date_str}.csv"
    fullpath = os.path.join(path, filename)

    if os.path.exists(fullpath):
        messagebox.showerror("파일 중복", f"이미 동일한 이름의 파일이 존재합니다:\n{fullpath}")
        return

    try:
        with open(fullpath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Set", "Step", "DigitLength", "Answer", "Response", "Correct"])
            for key, (entry, checkvar) in response_widgets.items():
                parts = key.split('_')
                set_id = f"{parts[0]}_{parts[1]}"
                step = int(parts[2])
                answer = ''.join(str(d) for d in digit_sets[key])
                response = entry.get().strip()
                correct = int(checkvar.get())
                writer.writerow([set_id, step, len(answer), answer, response, correct])

        messagebox.showinfo("저장 완료", f"데이터가 저장되었습니다:\n{fullpath}")
        data_saved = True
        save_last_path(path)

    except Exception as e:
        messagebox.showerror("저장 실패", str(e))

# ------- 저장 버튼 -------
tk.Button(root, text="Save Data", font=("Arial", 12), width=40, height=2, command=save_data).pack(pady=20)

# ------- 종료 전 확인 -------
def on_closing():
    if not data_saved:
        if messagebox.askyesno("종료 확인", "데이터를 저장하지 않았습니다. 정말 종료하시겠습니까?"):
            root.destroy()
    else:
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
