import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import requests
from bs4 import BeautifulSoup
import os

class CitationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tareas U. MX")
        self.root.geometry("700x550")
        self.root.configure(bg="#D3D3D3")  # Fondo estilo Linux Mint/Ubuntu
        self.root.iconbitmap("icono.ico")  # Asegúrate de que 'icono.ico' esté en la misma carpeta
        
        # Agregar soporte para tema claro/oscuro
        self.dark_mode = False
        self.apply_theme()
        
        tk.Label(root, text="Ingrese el DOI del artículo:", font=("Arial", 12), bg=self.root['bg']).pack(pady=5)
        self.doi_entry = tk.Entry(root, width=70, font=("Arial", 10))
        self.doi_entry.pack(pady=5)
        
        tk.Label(root, text="Seleccione el formato de cita:", font=("Arial", 12), bg=self.root['bg']).pack(pady=5)
        self.format_var = tk.StringVar(value="APA")
        tk.Radiobutton(root, text="APA", variable=self.format_var, value="APA", font=("Arial", 10), bg=self.root['bg']).pack()
        tk.Radiobutton(root, text="Vancouver", variable=self.format_var, value="Vancouver", font=("Arial", 10), bg=self.root['bg']).pack()
        
        tk.Button(root, text="Generar Cita", command=self.generate_citation, font=("Arial", 12)).pack(pady=10)
        tk.Button(root, text="Exportar Citas a TXT", command=self.export_citations, font=("Arial", 12)).pack(pady=10)
        
        # Cuadro de visualización con scroll
        self.citation_display = scrolledtext.ScrolledText(root, width=70, height=10, font=("Arial", 10), wrap=tk.WORD)
        self.citation_display.pack(pady=10)
        
        # Cuadro de búsqueda en Sci-Hub
        tk.Label(root, text="¿Quieres buscar el artículo en Sci-Hub?", font=("Arial", 12), bg=self.root['bg']).pack(pady=5)
        self.scihub_entry = tk.Entry(root, width=50, font=("Arial", 10))
        self.scihub_entry.pack(pady=5)
        tk.Button(root, text="Buscar en Sci-Hub", command=self.search_scihub, font=("Arial", 12)).pack(pady=5)
        
        # Botón para alternar tema
        tk.Button(root, text="Cambiar Tema", command=self.toggle_theme, font=("Arial", 12)).pack(pady=10)
        
        # Cerrar con confirmación
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.citations = []
    
    def generate_citation(self):
        doi = self.doi_entry.get().strip()
        if not doi:
            messagebox.showerror("Error", "Por favor, ingrese un DOI válido.")
            return

        metadata = self.extract_doi_metadata(doi)
        if not metadata:
            messagebox.showerror("Error", "No se pudo obtener información del DOI.")
            return

        citation_format = self.format_var.get()
        if citation_format == "APA":
            citation = f"{metadata['author']} ({metadata['date']}). {metadata['title']}. Recuperado de {metadata['url']}"
        else:
            citation = f"{metadata['author']}. {metadata['title']}. {metadata['date']}; Disponible en: {metadata['url']}"
        
        self.citations.append(citation)
        self.citation_display.insert(tk.END, citation + "\n\n")
        self.citation_display.yview(tk.END)
    
    def extract_doi_metadata(self, doi):
        try:
            url = f"https://doi.org/{doi}"
            headers = {"Accept": "application/vnd.citationstyles.csl+json"}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return {
                    "title": data.get("title", "Título Desconocido"),
                    "author": ", ".join([author["family"] for author in data.get("author", [])]),
                    "date": data.get("issued", {}).get("date-parts", [["Fecha Desconocida"]])[0][0],
                    "url": f"https://doi.org/{doi}"
                }
        except Exception as e:
            print("Error obteniendo datos de DOI:", e)
            return None
    
    def export_citations(self):
        if not self.citations:
            messagebox.showerror("Error", "No hay citas para exportar.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not file_path:
            return

        with open(file_path, "w", encoding="utf-8") as f:
            for citation in self.citations:
                f.write(citation + "\n\n")
        
        messagebox.showinfo("Exportación Exitosa", f"Las citas se han guardado en {file_path}")
    
    def search_scihub(self):
        doi = self.scihub_entry.get().strip()
        if not doi:
            messagebox.showerror("Error", "Por favor, ingrese un DOI para buscar en Sci-Hub.")
            return
        
        url = f"https://sci-hub.red/{doi}"
        os.system(f'start {url}')  # Abrir en navegador
    
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()
    
    def apply_theme(self):
        if self.dark_mode:
            self.root.configure(bg="#333333")
        else:
            self.root.configure(bg="#D3D3D3")  # Color estilo Linux Mint/Ubuntu
    
    def on_closing(self):
        if messagebox.askyesno("Salir", "¿Seguro que quieres cerrar el programa?"):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CitationApp(root)
    root.mainloop()
