import sqlite3
from typing import Any, List, Tuple, Optional


class Database:
	def __init__(self, path: str = "inventario.db"):
		self.path = path
		self.conn = sqlite3.connect(self.path, timeout=10)
		self.conn.row_factory = sqlite3.Row
		self._inicializar_banco()

	def _inicializar_banco(self) -> None:
		with self.conn:
			self.conn.execute(
				'''
				CREATE TABLE IF NOT EXISTS equipamentos (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					tipo TEXT NOT NULL,
					marca TEXT,
					patrimonio TEXT UNIQUE NOT NULL,
					setor TEXT,
					status TEXT NOT NULL
				)
				'''
			)
			self.conn.execute(
				'''
				CREATE TABLE IF NOT EXISTS historico (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					equipamento_id INTEGER,
					data_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
					descricao TEXT,
					FOREIGN KEY(equipamento_id) REFERENCES equipamentos(id)
				)
				'''
			)

			self.conn.execute('CREATE INDEX IF NOT EXISTS idx_setor ON equipamentos(setor)')
			self.conn.execute('CREATE INDEX IF NOT EXISTS idx_setor ON equipamentos(setor)')

	def execute(self, query: str, params: Tuple = ()) -> None:
		with self.conn:
			self.conn.execute(query, params)

	def fetchall(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
		cur = self.conn.cursor()
		cur.execute(query, params)
		return cur.fetchall()

	def fetchone(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
		cur = self.conn.cursor()
		cur.execute(query, params)
		return cur.fetchone()

	def close(self) -> None:
		try:
			self.conn.close()
		except Exception:
			pass