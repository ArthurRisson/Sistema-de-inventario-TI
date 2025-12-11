import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, filedialog
import datetime
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.models import Equipamento
from src.services import DEFAULT_STATUSES


class InventarioApp:
	def __init__(self, root, service):
		self.root = root
		self.root.title("Sistema de Inventário TI")
		self.service = service
		self.root.geometry("1000x700")

		self.notebook = ttk.Notebook(root)
		self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

		self.tab_dash = ttk.Frame(self.notebook)
		self.notebook.add(self.tab_dash, text="Dashboard")
		self.tab_crud = ttk.Frame(self.notebook)
		self.notebook.add(self.tab_crud, text="Gerenciar Equipamentos")

		self.setup_dashboard(self.tab_dash)
		self.setup_crud(self.tab_crud)
		self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

	def _on_tab_change(self, event):
		if self.notebook.index("current") == 0:
			self.atualizar_graficos()


	def setup_dashboard(self, parent):
		title = ttk.Label(parent, text="Visão Geral do Parque Tecnológico", font=("Helvetica", 16, "bold"))
		title.pack(pady=20)

		graphs_frame = ttk.Frame(parent)
		graphs_frame = ttk.Frame(parent)
		graphs_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

		self.fig1 = Figure(figsize=(5, 4), dpi=100)
		self.ax1 = self.fig1.add_subplot(111)
		self.canvas1 = FigureCanvasTkAgg(self.fig1, graphs_frame)
		self.canvas1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

		self.fig2 = Figure(figsize=(5, 4), dpi=100)
		self.ax2 = self.fig2.add_subplot(111)
		self.canvas2 = FigureCanvasTkAgg(self.fig2, graphs_frame)
		self.canvas2.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

		btn_refresh = ttk.Button(parent, text="Atualizar Dados", command=self.atualizar_graficos, bootstyle="outline")
		btn_refresh.pack(pady=10)

	def atualizar_graficos(self):
		stats_status, stats_setor = self.service.get_dashboard_stats()
		
		self.ax1.clear()
		if stats_status:
			labels = list(stats_status.keys())
			sizes = list(stats_status.values())
			self.ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
			self.ax1.set_title("Equipamentos por Status")
		else:
			self.ax1.text(0.5, 0.5, "Sem dados", ha='center')
			self.ax1.set_title("Equipamentos por Status")

		self.ax2.clear()
		if stats_setor:
			setores = list(stats_setor.keys())
			counts = list(stats_setor.values())
			bars = self.ax2.bar(setores, counts, color='#4c72b0')
			self.ax2.set_title("Equipamentos por Setor")
			self.ax2.set_ylabel("Quantidade")
			self.ax2.tick_params(axis='x', rotation=45)
		else:
			self.ax2.text(0.5, 0.5, "Sem dados", ha='center')
			self.ax2.set_title("Equipamentos por Setor")
		
		self.fig1.tight_layout()
		self.fig2.tight_layout()

		self.canvas1.draw()
		self.canvas2.draw()


	def setup_crud(self, parent):

		frm = ttk.Frame(parent, padding=15)
		frm.pack(fill=tk.BOTH, expand=True)

		
		row = 0
		ttk.Label(frm, text="Tipo:").grid(column=0, row=row, sticky=tk.W, padx=6, pady=6)
		self.entry_tipo = ttk.Entry(frm, width=30)
		self.entry_tipo.grid(column=1, row=row, sticky=tk.W, padx=6, pady=6)

		ttk.Label(frm, text="Marca:").grid(column=2, row=row, sticky=tk.W, padx=6, pady=6)
		self.entry_marca = ttk.Entry(frm, width=20)
		self.entry_marca.grid(column=3, row=row, sticky=tk.W, padx=6, pady=6)

		row += 1
		ttk.Label(frm, text="Patrimônio:").grid(column=0, row=row, sticky=tk.W, padx=6, pady=6)
		self.entry_patrimonio = ttk.Entry(frm, width=20)
		self.entry_patrimonio.grid(column=1, row=row, sticky=tk.W, padx=6, pady=6)

		ttk.Label(frm, text="Setor:").grid(column=2, row=row, sticky=tk.W, padx=6, pady=6)
		self.entry_setor = ttk.Entry(frm, width=20)
		self.entry_setor.grid(column=3, row=row, sticky=tk.W, padx=6, pady=6)

		row += 1
		ttk.Label(frm, text="Status:").grid(column=0, row=row, sticky=tk.W, padx=6, pady=6)
		self.status_combo = ttk.Combobox(frm, values=DEFAULT_STATUSES, state="readonly")
		self.status_combo.set(DEFAULT_STATUSES[0])
		self.status_combo.grid(column=1, row=row, sticky=tk.W, padx=6, pady=6)

		add_btn = ttk.Button(frm, text="Adicionar", command=self.adicionar_equipamento, bootstyle="success")
		add_btn.grid(column=3, row=row, sticky=tk.E, padx=6, pady=6)

		search_frame = ttk.Frame(frm)
		search_frame.grid(column=0, row=row+1, columnspan=4, sticky=tk.EW, pady=10)
		
		ttk.Label(search_frame, text="Pesquisar:").pack(side=tk.LEFT, padx=5)
		self.search_entry = ttk.Entry(search_frame, width=40)
		self.search_entry.pack(side=tk.LEFT, padx=5)
		
		btn_search = ttk.Button(search_frame, text="Buscar", command=self.realizar_busca, bootstyle="info-outline")
		btn_search.pack(side=tk.LEFT, padx=5)
		
		btn_clear = ttk.Button(search_frame, text="Limpar", command=self.listar_equipamentos, bootstyle="secondary-outline")
		btn_clear.pack(side=tk.LEFT, padx=5)
		
		row += 2 

		row += 1
		cols = ("id", "tipo", "marca", "patrimonio", "setor", "status")
		self.tree = ttk.Treeview(frm, columns=cols, show="headings", height=10, bootstyle="primary")
		for c in cols:
			self.tree.heading(c, text=c.capitalize())
			self.tree.column(c, width=100)
		self.tree.grid(column=0, row=row, columnspan=4, pady=10, padx=6, sticky=tk.NSEW)

		sb = ttk.Scrollbar(frm, orient=tk.VERTICAL, command=self.tree.yview)
		self.tree.configure(yscroll=sb.set)
		sb.grid(column=4, row=row, sticky=tk.NS, padx=4)

		row += 1
		btn_frame = ttk.Frame(frm, padding=6)
		btn_frame.grid(column=0, row=row, columnspan=4, sticky=tk.W)
		
		del_btn = ttk.Button(btn_frame, text="Excluir", command=self.excluir_equipamento, bootstyle="danger")
		del_btn.grid(column=0, row=0, padx=6, pady=6)
		edit_btn = ttk.Button(btn_frame, text="Editar", command=self.editar_equipamento, bootstyle="info")
		edit_btn.grid(column=1, row=0, padx=6, pady=6)
		exp_btn = ttk.Button(btn_frame, text="Exportar CSV", command=self.export_csv, bootstyle="secondary")
		exp_btn.grid(column=2, row=0, padx=6, pady=6)
		bkp_btn = ttk.Button(btn_frame, text="Backup DB", command=self.backup_db, bootstyle="secondary")
		bkp_btn.grid(column=3, row=0, padx=6, pady=6)

		frm.columnconfigure(1, weight=1)
		frm.rowconfigure(row - 1, weight=1)

		self.listar_equipamentos()


	def listar_equipamentos(self):
		for i in self.tree.get_children():
			self.tree.delete(i)
		try:
			rows = self.service.list_equipamentos()
			for r in rows:
				self.tree.insert("", tk.END, values=(r.id, r.tipo, r.marca or "", r.patrimonio, r.setor or "", r.status))
		except Exception as e:
			messagebox.showerror("Erro", f"Falha ao listar: {e}")

	def realizar_busca(self):
		termo = self.search_entry.get()
		for i in self.tree.get_children():
			self.tree.delete(i)
		try:
			rows = self.service.search_general(termo)
			for r in rows:
				self.tree.insert("", tk.END, values=(r.id, r.tipo, r.marca or "", r.patrimonio, r.setor or "", r.status))
		except Exception as e:
			messagebox.showerror("Erro", f"Falha na busca: {e}")

	def adicionar_equipamento(self):
		tipo = self.entry_tipo.get().strip()
		marca = self.entry_marca.get().strip() or None
		patrimonio = self.entry_patrimonio.get().strip()
		setor = self.entry_setor.get().strip() or None
		status = self.status_combo.get()
		if not tipo or not patrimonio:
			messagebox.showwarning("Atenção", "Preencha Tipo e Patrimônio")
			return
		eq = Equipamento(id=None, tipo=tipo, marca=marca, patrimonio=patrimonio, setor=setor, status=status)
		try:
			self.service.add_equipamento(eq)
			self._limpar_campos()
			self.listar_equipamentos()
			messagebox.showinfo("Sucesso", "Equipamento adicionado")
		except Exception as e:
			messagebox.showerror("Erro", f"Falha ao adicionar: {e}")

	def excluir_equipamento(self):
		sel = self.tree.selection()
		if not sel:
			messagebox.showwarning("Atenção", "Selecione um item na tabela para excluir!")
			return
		item = self.tree.item(sel[0])
		valores = item.get('values')
		id_equip = valores[0]
		confirm = messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir o ID {id_equip}?")
		if not confirm:
			return
		try:
			self.service.delete_equipamento(id_equip)
			self.listar_equipamentos()
			messagebox.showinfo("Sucesso", "Equipamento deletado!")
		except Exception as e:
			messagebox.showerror("Erro", f"Erro ao deletar: {e}")

	def editar_equipamento(self):
		sel = self.tree.selection()
		if not sel:
			messagebox.showwarning("Atenção", "Selecione um item na tabela para editar!")
			return
		item = self.tree.item(sel[0])
		valores = item.get('values')
		id_equip = valores[0]

		rows = self.service.list_equipamentos()
		current = None
		for r in rows:
			if r.id == id_equip:
				current = r
				break
		if current is None:
			messagebox.showerror("Erro", "Item não encontrado")
			return

		dlg = tk.Toplevel(self.root)
		dlg.title(f"Editar ID {id_equip}")
		dlg.transient(self.root)
		dlg.grab_set()

		ttk.Label(dlg, text="Tipo:").grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
		tipo_e = ttk.Entry(dlg, width=40)
		tipo_e.grid(column=1, row=0, padx=5, pady=5)
		tipo_e.insert(0, current.tipo)

		ttk.Label(dlg, text="Marca:").grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
		marca_e = ttk.Entry(dlg, width=30)
		marca_e.grid(column=1, row=1, padx=5, pady=5)
		if current.marca:
			marca_e.insert(0, current.marca)

		ttk.Label(dlg, text="Patrimônio:").grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)
		pat_e = ttk.Entry(dlg, width=30)
		pat_e.grid(column=1, row=2, padx=5, pady=5)
		pat_e.insert(0, current.patrimonio)

		ttk.Label(dlg, text="Setor:").grid(column=0, row=3, sticky=tk.W, padx=5, pady=5)
		setor_e = ttk.Entry(dlg, width=30)
		setor_e.grid(column=1, row=3, padx=5, pady=5)
		if current.setor:
			setor_e.insert(0, current.setor)

		ttk.Label(dlg, text="Status:").grid(column=0, row=4, sticky=tk.W, padx=5, pady=5)
		status_cb = ttk.Combobox(dlg, values=DEFAULT_STATUSES, state="readonly")
		status_cb.grid(column=1, row=4, padx=5, pady=5)
		status_cb.set(current.status)

		def _salvar():
			tipo = tipo_e.get().strip()
			marca = marca_e.get().strip() or None
			patrimonio = pat_e.get().strip()
			setor = setor_e.get().strip() or None
			status = status_cb.get()
			try:
				self.service.update_equipamento(id_equip, tipo, marca, patrimonio, setor, status)
				dlg.destroy()
				self.listar_equipamentos()
				messagebox.showinfo("Sucesso", "Equipamento atualizado")
			except Exception as e:
				messagebox.showerror("Erro", f"Falha ao atualizar: {e}")

		btn_fr = ttk.Frame(dlg, padding=6)
		btn_fr.grid(column=0, row=5, columnspan=2, pady=10)
		save_btn = ttk.Button(btn_fr, text="Salvar", command=_salvar, bootstyle="success")
		save_btn.grid(column=0, row=0, padx=6)
		cancel_btn = ttk.Button(btn_fr, text="Cancelar", command=dlg.destroy, bootstyle="secondary")
		cancel_btn.grid(column=1, row=0, padx=6)

	def export_csv(self):
		default_name = f"inventario_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
		path = filedialog.asksaveasfilename(defaultextension='.csv', initialfile=default_name, filetypes=[('CSV files','*.csv')])
		if not path:
			return
		try:
			self.service.export_csv(path)
			messagebox.showinfo("Sucesso", f"Exportado para {os.path.basename(path)}")
		except Exception as e:
			messagebox.showerror("Erro", f"Falha ao exportar: {e}")

	def backup_db(self):
		default_name = f"inventario_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
		path = filedialog.asksaveasfilename(defaultextension='.db', initialfile=default_name, filetypes=[('SQLite DB','*.db')])
		if not path:
			return
		try:
			self.service.backup_db(path)
			messagebox.showinfo("Sucesso", f"Backup criado: {os.path.basename(path)}")
		except Exception as e:
			messagebox.showerror("Erro", f"Falha no backup: {e}")

	def _limpar_campos(self):
		self.entry_tipo.delete(0, tk.END)
		self.entry_marca.delete(0, tk.END)
		self.entry_patrimonio.delete(0, tk.END)
		self.entry_setor.delete(0, tk.END)
		self.status_combo.set(DEFAULT_STATUSES[0])