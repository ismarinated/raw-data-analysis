import os
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter.messagebox import showerror

from matplotlib import pyplot as plt
import numpy as np

# Получить длительность эксперемента
def get_duration(lines):
    len_lines = len(lines)

    seconds = int(len_lines / 10)
    minutes = int(seconds / 60)
    hours = int(minutes / 60)

    return f"{hours:02d}:{(minutes % 60):02d}:{(seconds % 60):02d}"

# Прочитать файл по введенному пути, либо вывести сообщения об ошибке и заблокировать элементы интерфейса
def get_values(filepath):
    values, duration = [], ''
    flag = 0
    try:
        f = open(filepath, 'r', encoding='UTF-8')
        lines = f.read()
        f.close()

        lines = lines.split('\n')
        lines = lines[0::2] # Удалить дублирующиеся строки
        duration = get_duration(lines)

        itr = 0

        for line in lines:
            line = line.split('\t')
            values.append([])
            for sub_line in line:
                values[itr].append(float(sub_line.replace(',', '.')))
            itr += 1
    except:
        editor.config(state=DISABLED)
        btn_k.config(state=DISABLED)
        btn_plot_Ik_Uk.config(state=DISABLED)
        btn_plot_spectrum.config(state=DISABLED)
        btn_plot_pt.config(state=DISABLED)
        btn_plot_Pt_Qt_St.config(state=DISABLED)
        flag = 1
        duration = "            "
        showerror(title="Ошибка", message="Ошибка чтения файла")

    return values, duration, flag

class Figure:
    filepath_Ik, filepath_Uk, duration = '', '', "        "
    k, flag_spec, flag_pow, flag_Ik, flag_Uk = 0, 0, 0, 1, 1
    lines_p, lines_Ik, lines_Uk = [], [], []

    # Проверка ошибки ввода файлов
    def check_files(self):
        flag = 0
        if (self.flag_Uk == 1 or self.flag_Ik == 1):
            flag = 1
        return flag
    
    # Блокировка либо разблокировка элементов интерфейса в зависимости от состояния ввода файлов
    def set_state_to_normal(self):
        if (self.check_files() == 0):
            editor.config(state=NORMAL)
            btn_k.config(state=NORMAL)
            btn_plot_Ik_Uk.config(state=NORMAL)
            btn_plot_spectrum.config(state=NORMAL)
            btn_plot_pt.config(state=NORMAL)
            btn_plot_Pt_Qt_St.config(state=NORMAL)
        else:
            editor.config(state=DISABLED)
            btn_k.config(state=DISABLED)
            btn_plot_Ik_Uk.config(state=DISABLED)
            btn_plot_spectrum.config(state=DISABLED)
            btn_plot_pt.config(state=DISABLED)
            btn_plot_Pt_Qt_St.config(state=DISABLED)

    # Вызов диалогового окна для выбора файла с сигналом i(t)
    def open_file_Ik(self):
        self.filepath_Ik = filedialog.askopenfilename(filetypes=[('text files', '*.txt')])
        path_label = ttk.Label(text=self.filepath_Ik, font=("Times New Roman", 10), foreground='#6e6e6e')
        path_label.grid(row=1, column=0, sticky=N)

        self.lines_Ik, self.duration, self.flag_Ik = get_values(self.filepath_Ik)
        self.set_state_to_normal()

        duration_label = ttk.Label(text=f"Продолжительность эксперимента: {self.duration}", font=("Times New Roman", 11), background='#f0f0f0')
        duration_label.grid(row=2, column=0, columnspan=2, ipadx=6, ipady=6, padx=[15, 4], pady=4)

    # Вызов диалогового окна для выбора файла с сигналом u(t)
    def open_file_Uk(self):
        self.filepath_Uk = filedialog.askopenfilename(filetypes=[('text files', '*.txt')])
        path_label = ttk.Label(text=self.filepath_Uk, font=("Times New Roman", 10), foreground='#6e6e6e')
        path_label.grid(row=1, column=1, sticky=N)

        self.lines_Uk, self.duration, self.flag_Uk = get_values(self.filepath_Uk)
        self.set_state_to_normal()

        duration_label = ttk.Label(text=f"Продолжительность эксперимента: {self.duration}", font=("Times New Roman", 11), background='#f0f0f0')
        duration_label.grid(row=2, column=0, columnspan=2, ipadx=6, ipady=6, padx=[15, 4], pady=4)

    # Обработка ввода номера строки измерений k пользователем и блокирование элементов интерфейса в случае некорректного ввода
    def get_text(self):
        k = editor.get("1.0", "end-1c")
        
        if (k.isdigit()):
            self.k = int(k)
            k_label.config(foreground='#f0f0f0')
            btn_plot_Ik_Uk.config(state=NORMAL)
            btn_plot_spectrum.config(state=NORMAL)
            btn_plot_pt.config(state=NORMAL)
            btn_plot_Pt_Qt_St.config(state=NORMAL)
        else:
            k_label.config(foreground='#ad5e5e')
            btn_plot_Ik_Uk.config(state=DISABLED)
            btn_plot_spectrum.config(state=DISABLED)
            btn_plot_pt.config(state=DISABLED)
            btn_plot_Pt_Qt_St.config(state=DISABLED)

    # Построение графика сигналов ik(t) и uk(t)
    def plot_uk_ik(self):        
        plt.plot(list(range(0, len(self.lines_Uk[self.k]))), self.lines_Uk[self.k], label='uk(t)', color='blue')
        plt.plot(list(range(0, len(self.lines_Uk[self.k]))), self.lines_Ik[self.k], label='ik(t)', color='red')
        plt.title('Графики сигналов uk(t), ik(t)')
        plt.xlabel('t, c')
        plt.ylabel('Сигнал')
        plt.grid(True)
        plt.legend()
        plt.show()

    # Нахождение спектра сигнала для одного цикла измерений i(t)
    def plot_spectrum(self):
        spectrum = np.fft.fft(self.lines_Ik[self.k]) # Вычисление дискретного спектра
        spectrum = np.abs(spectrum) # Преобразование спектр в абсолютные значения
        spectrum = spectrum[:len(spectrum)//2] # Выборка реальной части спектра при первых половинных частотах

        freq = np.fft.fftfreq(len(self.lines_Ik[self.k]), d=1/800) # Массив частот для рассматриваемого сигнала (шаг d при условии записи 800 точек в секунду)
        freq = freq[:len(freq)//2] # Выборка первой половины частот

        # Запись вычисленных значений в файл
        if (self.flag_spec == 0):
            file_path = '/'.join([os.path.dirname(self.filepath_Ik), "Спектр.txt"])
            with open(file_path, 'w', encoding='UTF-8') as file:
                file.write(f"Частота, Гц\tСпектр\n")
                for i in range(len(spectrum)):
                    file.write(f"{freq[i]}\t{spectrum[i]}\n")

        # Построение графика спектра
        plt.plot(freq, spectrum, label='Спектр')
        plt.title('Спектр')
        plt.xlabel('Частота, Гц')
        plt.ylabel('Амплитуда')
        plt.grid(True)
        plt.legend()
        plt.show()
        
        self.flag_spec = 1

    # Расчет мгновенных мощностей p(t)
    def calculate_pt(self):
        for i in range(len(self.lines_Uk)):
            self.lines_p.append([])
            for j in range(len(self.lines_Uk[i])):
                self.lines_p[i].append(float(self.lines_Ik[i][j]) * float(self.lines_Uk[i][j]))
        
    # Построение графика мгновенных мощностей p(t)
    def plot_pt(self):
        self.calculate_pt()

        plt.plot(list(range(0, len(self.lines_p[self.k]))), self.lines_p[self.k], label='p(t)')
        plt.title('График мгновенной мощности')
        plt.xlabel('t, c')
        plt.ylabel('p(t)')
        plt.grid(True)
        plt.legend()
        plt.show()

    # Расщет и построение графиков изменения активной мощности P(t), реактивной мощности Q(t) и полной мощности S(t)
    def plot_Pt_Qt_St(self):
        lines_Pt, lines_Qt, lines_St = [], [], []

        # Создание файла для записи вычисляемых значений
        if (self.flag_pow == 0):
            file_path = '/'.join([os.path.dirname(self.filepath_Ik), "Мощности.txt"])
            with open(file_path, 'w', encoding='UTF-8') as file:
                file.write(f"t, с\tP(t)\tQ(t)\tS(t)\n")

        for i in range(len(self.lines_Ik)):
            calc_It = np.mean(np.sqrt(np.mean(np.array(self.lines_Ik[i]) ** 2))) # Расчет действующего значения тока I
            calc_Ut = np.mean(np.sqrt(np.mean(np.array(self.lines_Uk[i]) ** 2))) # Расчет действующего значения напряжения U

            calc_Pt = np.mean(np.array(self.lines_Ik[i]) * np.array(self.lines_Uk[i])) # Расчет активной мощности P(t)

            lines_Pt.append(calc_Pt)
            lines_St.append(calc_It * calc_Ut) # Расчет значения полной мощности S(t)
            lines_Qt.append(np.sqrt((calc_It * calc_Ut) ** 2 - calc_Pt ** 2)) # Расчет значения реактивной мощности Q(t)

            # Запись вычисленных значений в файл
            if (self.flag_pow == 0):
                with open(file_path, 'a', encoding='UTF-8') as file:
                    file.write(f"{i}\t{lines_Pt[-1]}\t{lines_Qt[-1]}\t{lines_St[-1]}\n")

        # Построение графиков изменения активной мощности P(t), реактивной мощности Q(t) и полной мощности S(t)
        plt.plot(list(range(0, len(lines_Pt))), lines_Pt, label='P(t)', color='blue')
        plt.plot(list(range(0, len(lines_St))), lines_St, label='S(t)', color='red')
        plt.plot(list(range(0, len(lines_Qt))), lines_Qt, label='Q(t)', color='green')
        plt.title('Кривые P(t), Q(t), S(t)')
        plt.xlabel('t, c')
        plt.ylabel('Мощность')
        plt.grid(True)
        plt.legend()
        plt.show()

        self.flag_pow = 1

root = Tk() # Создание корневого объекта - окна
root.title("Программа")
root.iconbitmap(default="icon.ico")
root.geometry("400x300")

for c in range(2): root.columnconfigure(index=c, weight=1)
for r in range(8): root.rowconfigure(index=r, weight=1)

figure = Figure() # Создание экземпляра класса

# Кнопка открытия файла с сигналом i(t)
btn_filepath_Ik = ttk.Button(text="Выбор файла (I)", command=figure.open_file_Ik, width=18)
btn_filepath_Ik.grid(row=0, column=0, sticky=S, ipadx=6, ipady=6, padx=[15, 4], pady=4)

# Кнопка открытия файла с сигналом u(t)
btn_filepath_Uk = ttk.Button(text="Выбор файла (U)", command=figure.open_file_Uk, width=18)
btn_filepath_Uk.grid(row=0, column=1, sticky=S, ipadx=6, ipady=6, padx=[15, 4], pady=4)

# Текстовая подпись к окну ввода k
k_input_label = ttk.Label(text="Ввод k (по умолчанию 0):", font=("Times New Roman", 10))
k_input_label.grid(row=3, ipadx=6, padx=[15, 4], column=0, sticky=S)

# Окно ввода k
editor = Text(height=0.5, width=18, state=DISABLED, font=("Arial", 10))
editor.grid(row=4, column=0, ipadx=6, ipady=6, padx=[15, 4], pady=4)

# Кнопка подтверждения ввода k
btn_k = ttk.Button(text="Добавить", command=figure.get_text, state=DISABLED, width=18)
btn_k.grid(row=4, column=1, ipadx=6, ipady=6, padx=[15, 4], sticky=N)

# Текстовая подпись, меняющая цвет текста на красный, при некорректном вводе k
k_label = ttk.Label(text="Некорректное значение", font=("Times New Roman", 10), foreground='#f0f0f0')
k_label.grid(row=5, column=0, sticky=N)

# Кнопка вызова метода построения графиков сигналов uk(t) ik(t)
btn_plot_Ik_Uk = ttk.Button(text="Сигналы uk(t) и ik(t)", command=figure.plot_uk_ik, state=DISABLED, width=18)
btn_plot_Ik_Uk.grid(row=6, column=0, ipadx=6, ipady=6, padx=[15, 4], pady=4)

# Кнопка вызова метода построения графика спектра
btn_plot_spectrum = ttk.Button(text="Спектр сигнала", command=figure.plot_spectrum, state=DISABLED, width=18)
btn_plot_spectrum.grid(row=6, column=1, ipadx=6, ipady=6, padx=[15, 4], pady=4)

# Кнопка вызова метода построения графика мгновенныых мощностей p(t)
btn_plot_pt = ttk.Button(text="Кривая p(t)", command=figure.plot_pt, state=DISABLED, width=18)
btn_plot_pt.grid(row=7, column=0, ipadx=6, ipady=6, padx=[15, 4], pady=4)

# Кнопка вызова метода построения графиков изменения активной мощности P(t), реактивной мощности Q(t) и полной мощности S(t)
btn_plot_Pt_Qt_St = ttk.Button(text="Кривые P(t), Q(t), S(t)", command=figure.plot_Pt_Qt_St, state=DISABLED, width=18)
btn_plot_Pt_Qt_St.grid(row=7, column=1, ipadx=6, ipady=6, padx=[15, 4], pady=4)

root.mainloop() # Вызов метода для отображения окна