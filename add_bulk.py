from src.database import Database
from src.models import Equipamento
from src.services import InventoryService
import itertools

# Map of sector -> count
data = {
    
    "Saguão": 9,
    "ICMS": 4,
    "ITBI/ITR": 5,
    "André": 3,
    "PGM": 12,
    "IPTU": 11,
    "ISS": 19,
}

# Prefixes for patrimonios per setor (short codes)
prefix_map = {
    
    "Saguão": "SAG",
    "ICMS": "ICMS",
    "ITBI/ITR": "ITBI",
    "André": "AND",
    "PGM": "PGM",
    "IPTU": "IPTU",
    "ISS": "ISS",
}

DB_PATH = "inventario.db"

print("Conectando ao banco:", DB_PATH)
db = Database(DB_PATH)
service = InventoryService(db)

# generate patrimonios starting at 1000 for readability
start_counters = {k: 1000 for k in data.keys()}

inserted = 0
skipped = 0

for setor, count in data.items():
    prefix = prefix_map.get(setor, "XX")
    counter = start_counters[setor]
    for i in range(count):
        patrimonio = f"{prefix}-{counter + i}"
        eq = Equipamento(id=None, tipo="PC", marca=None, patrimonio=patrimonio, setor=setor, status="Ativo")
        try:
            service.add_equipamento(eq)
            inserted += 1
        except Exception as e:
            # if duplicate or other error, skip and continue
            print(f"Aviso: não inseriu {patrimonio} ({setor}): {e}")
            skipped += 1

print(f"Inserções concluídas. Inseridos: {inserted}, Pulados: {skipped}")

# Verificar contagem por setor
rows = service.list_equipamentos(order_by='id')
counts = {}
for r in rows:
    counts[r.setor] = counts.get(r.setor, 0) + 1

print("Contagens por setor (inclui dados já existentes):")
for setor in data.keys():
    print(f"- {setor}: {counts.get(setor,0)}")

print("Fechando DB")
db.close()
