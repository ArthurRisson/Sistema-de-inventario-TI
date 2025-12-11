from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class Equipamento:
	id: Optional[int]
	tipo: str
	marca: Optional[str]
	patrimonio: str
	setor: Optional[str]
	status: str

	def to_tuple(self) -> Tuple[Optional[str], Optional[str], str, Optional[str], str]:
		return (self.tipo, self.marca, self.patrimonio, self.setor, self.status)