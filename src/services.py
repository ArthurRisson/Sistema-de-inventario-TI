import csv
import shutil
import sqlite3
import datetime
import os
from typing import List

from src.models import Equipamento


DEFAULT_STATUSES = ["Ativo", "Inativo", "Em Manutenção", "Descartado"]


class InventoryService:
	def __init__(self, db):
		self.db = db

	def get_equipamento(self, id_equip: int) -> Equipamento:
		"""Busca um equipamento pelo ID. Útil para auditoria."""
		row = self.db.fetchone("SELECT * FROM equipamentos WHERE id = ?", (id_equip,))
		if not row:
			raise ValueError("Equipamento não encontrado")
		return self._row_to_equipamento(row)

	def add_equipamento(self, equipamento: Equipamento) -> None:
		equipamento.tipo = equipamento.tipo.strip()
		equipamento.marca = (equipamento.marca or "").strip() or None
		equipamento.setor = (equipamento.setor or "").strip() or None
		equipamento.patrimonio = equipamento.patrimonio.strip()
		equipamento.status = (equipamento.status or DEFAULT_STATUSES[0]).strip()

		try:
			self.db.execute(
				"INSERT INTO equipamentos (tipo, marca, patrimonio, setor, status) VALUES (?, ?, ?, ?, ?)",
				equipamento.to_tuple(),
			)
		except sqlite3.IntegrityError as e:
			raise sqlite3.IntegrityError("Patrimônio já cadastrado") from e

	def list_equipamentos(self, order_by: str = "patrimonio") -> List[Equipamento]:
		rows = self.db.fetchall(f"SELECT * FROM equipamentos ORDER BY {order_by}")
		return [self._row_to_equipamento(r) for r in rows]

	def search_by_setor(self, termo: str) -> List[Equipamento]:
		"""Busca antiga apenas por setor (mantida por compatibilidade)."""
		termo = (termo or "").strip()
		if not termo:
			return []
		like = f"%{termo}%"
		rows = self.db.fetchall("SELECT * FROM equipamentos WHERE LOWER(setor) LIKE LOWER(?)", (like,))
		return [self._row_to_equipamento(r) for r in rows]

	def search_general(self, termo: str) -> List[Equipamento]:
		"""Nova busca: Procura em Tipo, Marca, Patrimônio ou Setor."""
		termo = (termo or "").strip()
		if not termo:
			return self.list_equipamentos()
		
		like = f"%{termo}%"
		query = """
			SELECT * FROM equipamentos 
			WHERE LOWER(tipo) LIKE LOWER(?) 
			OR LOWER(marca) LIKE LOWER(?)
			OR LOWER(patrimonio) LIKE LOWER(?)
			OR LOWER(setor) LIKE LOWER(?)
		"""
		rows = self.db.fetchall(query, (like, like, like, like))
		return [self._row_to_equipamento(r) for r in rows]

	def update_status(self, id_equip: int, novo_status: str) -> None:
		if not novo_status:
			raise ValueError("Status inválido")
		novo_status = novo_status.strip()
		self.db.execute("UPDATE equipamentos SET status = ? WHERE id = ?", (novo_status, id_equip))

	def update_equipamento(self, id_equip: int, tipo: str, marca: str | None, patrimonio: str, setor: str | None, status: str) -> None:
		"""Atualiza equipamento e gera log de histórico se houver mudanças."""
		try:
			atual = self.get_equipamento(id_equip)
		except ValueError:
			raise ValueError("Equipamento não encontrado para edição")

		if not tipo or not patrimonio:
			raise ValueError("Tipo e patrimônio são obrigatórios")
		tipo = tipo.strip()
		marca = (marca or "").strip() or None
		setor = (setor or "").strip() or None
		patrimonio = patrimonio.strip()
		status = (status or DEFAULT_STATUSES[0]).strip()

		try:
			self.db.execute(
				"UPDATE equipamentos SET tipo = ?, marca = ?, patrimonio = ?, setor = ?, status = ? WHERE id = ?",
				(tipo, marca, patrimonio, setor, status, id_equip),
			)

			log_msg = []
			if atual.setor != setor:
				log_msg.append(f"Setor alterado de '{atual.setor or 'N/A'}' para '{setor or 'N/A'}'")
			if atual.status != status:
				log_msg.append(f"Status alterado de '{atual.status}' para '{status}'")
			if atual.patrimonio != patrimonio:
				log_msg.append(f"Patrimônio alterado de '{atual.patrimonio}' para '{patrimonio}'")

			if log_msg:
				msg_final = "; ".join(log_msg)
				self.db.execute(
					"INSERT INTO historico (equipamento_id, descricao) VALUES (?, ?)", 
					(id_equip, msg_final)
				)

		except sqlite3.IntegrityError as e:
			raise sqlite3.IntegrityError("Patrimônio já cadastrado") from e

	def delete_equipamento(self, id_equip: int) -> None:
		self.db.execute("DELETE FROM equipamentos WHERE id = ?", (id_equip,))

	def export_csv(self, path: str) -> None:
		rows = self.db.fetchall("SELECT * FROM equipamentos ORDER BY patrimonio")
		with open(path, "w", newline="", encoding="utf-8") as f:
			writer = csv.writer(f)
			writer.writerow(["id", "tipo", "marca", "patrimonio", "setor", "status"])
			for r in rows:
				writer.writerow([r["id"], r["tipo"], r["marca"], r["patrimonio"], r["setor"], r["status"]])

	def backup_db(self, dest_path: str) -> None:
		try:
			self.db.conn.commit()
		except Exception:
			pass
		src = getattr(self.db, "path", None)
		if not src:
			raise RuntimeError("Caminho do banco de dados desconhecido")
		shutil.copyfile(src, dest_path)

	@staticmethod
	def _row_to_equipamento(row) -> Equipamento:
		return Equipamento(
			id=row["id"],
			tipo=row["tipo"],
			marca=row["marca"],
			patrimonio=row["patrimonio"],
			setor=row["setor"],
			status=row["status"],
		)
	
	
	def get_dashboard_stats(self):
		"""Retorna dados consolidados para os gráficos."""
		
		rows_status = self.db.fetchall("SELECT status, COUNT(*) as total FROM equipamentos GROUP BY status")
		stats_status = {r['status']: r['total'] for r in rows_status}
		
		
		rows_setor = self.db.fetchall("SELECT setor, COUNT(*) as total FROM equipamentos WHERE setor IS NOT NULL AND setor != '' GROUP BY setor")
		stats_setor = {r['setor']: r['total'] for r in rows_setor}
		
		return stats_status, stats_setor