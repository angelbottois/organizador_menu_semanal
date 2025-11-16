import customtkinter as ctk
from tkinter import messagebox
from core.planificador import generar_plan_semanal
from core.lista_compra import generar_lista_compra
from data.recetas import recetas
from data.personas import cocineros, personas_menus, semana, momentos
from data.restricciones import restricciones

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Planificador de Menús Semanal")
        self.root.geometry("900x400")

        # Botones superiores
        frame_buttons = ctk.CTkFrame(root)
        frame_buttons.pack(fill="x", padx=20, pady=10)

        self.btn_plan = ctk.CTkButton(frame_buttons, text="Generar Nuevo Plan", command=self.generar_plan)
        self.btn_plan.pack(side="left", padx=10, pady=5)

        self.btn_compra = ctk.CTkButton(frame_buttons, text="Mostrar Lista de la Compra", command=self.mostrar_compra)
        self.btn_compra.pack(side="left", padx=10, pady=5)

        # Frame de tabla (sin scroll)
        self.frame_tabla = ctk.CTkFrame(root)
        self.frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

        self.inner_frame = ctk.CTkFrame(self.frame_tabla)
        self.inner_frame.pack(fill="both", expand=True)

        # Generar plan automáticamente al iniciar
        self.generar_plan()

    def generar_plan(self):
        try:
            self.plan = generar_plan_semanal(semana, momentos, recetas, cocineros, restricciones, personas_menus)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        self.mostrar_tabla()

    def mostrar_tabla(self):
        # Limpiar tabla anterior
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        # Encabezados de días
        for col, dia in enumerate([""] + semana):
            ctk.CTkLabel(self.inner_frame, text=dia, width=20, fg_color="#2C2F33", corner_radius=5).grid(
                row=0, column=col, padx=5, pady=5, sticky="nsew"
            )

        # Filas: Comida / Cena
        for row, momento in enumerate(momentos, start=1):
            ctk.CTkLabel(self.inner_frame, text=momento, width=20, fg_color="#2C2F33", corner_radius=5).grid(
                row=row, column=0, padx=5, pady=5, sticky="nsew"
            )
            for col, dia in enumerate(semana, start=1):
                e = self.plan[dia][momento]
                text = f"{e['receta']}\n({e['cocinero']})"
                ctk.CTkLabel(
                    self.inner_frame,
                    text=text,
                    width=120,
                    height=60,
                    fg_color="#7289DA",
                    corner_radius=5,
                    justify="center"
                ).grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        # Hacer que las columnas y filas se expandan uniformemente
        for i in range(len(semana) + 1):
            self.inner_frame.grid_columnconfigure(i, weight=1)
        for i in range(len(momentos) + 1):
            self.inner_frame.grid_rowconfigure(i, weight=1)

    def mostrar_compra(self):
        try:
            lista = generar_lista_compra(self.plan)
        except AttributeError:
            messagebox.showwarning("Atención", "Primero genera el plan semanal")
            return

        ventana_compra = ctk.CTkToplevel(self.root)
        ventana_compra.title("Lista de la Compra")
        ventana_compra.geometry("400x400")

        texto = ctk.CTkTextbox(ventana_compra)
        texto.pack(fill="both", expand=True, padx=10, pady=10)
        texto.delete("0.0", "end")
        for ing, cant in lista.items():
            texto.insert("end", f"{ing}: {cant}\n")
        texto.configure(state="disabled")


if __name__ == "__main__":
    root = ctk.CTk()
    app = MenuApp(root)
    root.mainloop()
