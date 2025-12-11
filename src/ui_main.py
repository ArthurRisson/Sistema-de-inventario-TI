import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import os

from src.models import Equipamento
from src.services import DEFAULT_STATUSES


class InventarioApp:
	def __init__(self, root, service):
		self.root = root
		self.root.title("Inventário")
		self.service = service

		frm = ttk.Frame(root, padding=10)
		frm.pack(fill=tk.BOTH, expand=True)

		# Inputs
		row = 0
		ttk.Label(frm, text="Tipo:").grid(column=0, row=row, sticky=tk.W)
		self.entry_tipo = ttk.Entry(frm, width=30)
		self.entry_tipo.grid(column=1, row=row, sticky=tk.W)

		ttk.Label(frm, text="Marca:").grid(column=2, row=row, sticky=tk.W)
		self.entry_marca = ttk.Entry(frm, width=20)
		self.entry_marca.grid(column=3, row=row, sticky=tk.W)

		row += 1
		ttk.Label(frm, text="Patrimônio:").grid(column=0, row=row, sticky=tk.W)
		self.entry_patrimonio = ttk.Entry(frm, width=20)
		self.entry_patrimonio.grid(column=1, row=row, sticky=tk.W)

		ttk.Label(frm, text="Setor:").grid(column=2, row=row, sticky=tk.W)
		self.entry_setor = ttk.Entry(frm, width=20)
		self.entry_setor.grid(column=3, row=row, sticky=tk.W)

		row += 1
		ttk.Label(frm, text="Status:").grid(column=0, row=row, sticky=tk.W)
		self.status_combo = ttk.Combobox(frm, values=DEFAULT_STATUSES, state="readonly")
		self.status_combo.set(DEFAULT_STATUSES[0])
		self.status_combo.grid(column=1, row=row, sticky=tk.W)

		add_btn = ttk.Button(frm, text="Adicionar", command=self.adicionar_equipamento)
		add_btn.grid(column=3, row=row, sticky=tk.E)

		# Treeview
		row += 1
		cols = ("id", "tipo", "marca", "patrimonio", "setor", "status")
		self.tree = ttk.Treeview(frm, columns=cols, show="headings", height=10)
		for c in cols:
			self.tree.heading(c, text=c.capitalize())
			self.tree.column(c, width=100)
		self.tree.grid(column=0, row=row, columnspan=4, pady=10, sticky=tk.NSEW)

		# Scrollbar
		sb = ttk.Scrollbar(frm, orient=tk.VERTICAL, command=self.tree.yview)
		self.tree.configure(yscroll=sb.set)
		sb.grid(column=4, row=row, sticky=tk.NS)

		# Actions
		row += 1
		btn_frame = ttk.Frame(frm)
		btn_frame.grid(column=0, row=row, columnspan=4, sticky=tk.W)
		# action buttons: place them in separate columns to avoid overlap
		ttk.Button(btn_frame, text="Excluir", command=self.excluir_equipamento).grid(column=0, row=0, padx=5)
		ttk.Button(btn_frame, text="Editar", command=self.editar_equipamento).grid(column=1, row=0, padx=5)
		ttk.Button(btn_frame, text="Exportar CSV", command=self.export_csv).grid(column=2, row=0, padx=5)
		ttk.Button(btn_frame, text="Backup DB", command=self.backup_db).grid(column=3, row=0, padx=5)

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
		"""Abre um diálogo para editar o equipamento selecionado."""
		sel = self.tree.selection()
		if not sel:
			messagebox.showwarning("Atenção", "Selecione um item na tabela para editar!")
			return
		item = self.tree.item(sel[0])
		valores = item.get('values')
		id_equip = valores[0]

		# Obter dados atuais do item (para consistência, buscar da lista do serviço)
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

		# Fields
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

		btn_fr = ttk.Frame(dlg)
		btn_fr.grid(column=0, row=5, columnspan=2, pady=10)
		ttk.Button(btn_fr, text="Salvar", command=_salvar).grid(column=0, row=0, padx=5)
		ttk.Button(btn_fr, text="Cancelar", command=dlg.destroy).grid(column=1, row=0, padx=5)

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