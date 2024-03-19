import tkinter as tk
from tkinter import ttk   


class TextInput(tk.Frame):
    def __init__(self, parent):

        self.parent = parent
        
        tk.Frame.__init__(self, parent)

        self.input = tk.Entry(master=parent)

        self.input.grid(column=1, row=2)
        self.input_button = ttk.Button(parent, text="submit??", command=self.display_input).grid(column=2, row=0)

        self.storage = []

    def display_input(self):
        what = self.input.get()
        self.storage.append(what)
        #tk.Label(self.parent, text=what, background = "green").grid(column=1, row=3)

        for i in range(len(self.storage)):
            tk.Label(self.parent, text=self.storage[i], background = "#188FA7").grid(column=1, row=10+i)

    def get_inupt():
        what = input.get()

class Window:
    def __init__(self):
        self.tk = tk.Tk()

        self.tk.geometry('600x400') 

        self.tk.title("Lumo? I hardely Know her!!!!")
        self.window_frame = tk.Frame(master=self.tk, bg="#769FB6")
        self.window_frame.pack(fill = tk.BOTH, side=tk.LEFT, expand=True)
        ttk.Label(self.window_frame, text="Hello Lumo!").grid(column=1, row=0)
        button = tk.Button(self.window_frame, text="Kill myself nowwwww!!!!.", command=self.destroy).grid(column = 1, row = 99)

        self.text_input = TextInput(self.window_frame)

        self.tk.mainloop()


    def destroy(self):
        self.tk.destroy()


window = Window()