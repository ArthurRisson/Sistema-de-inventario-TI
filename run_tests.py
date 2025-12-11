from src.database import Database
from src.models import Equipamento
from src.services import InventoryService
import os

DB_PATH = 'test_inventario.db'

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

print('Criando DB de teste...')
db = Database(DB_PATH)
service = InventoryService(db)

print('Adicionando equipamento de teste...')
eq = Equipamento(id=None, tipo='PC Teste', marca='MarcaX', patrimonio='TEST123', setor='TI', status='Ativo')
try:
    service.add_equipamento(eq)
    print('Inserido com sucesso')
except Exception as e:
    print('Erro ao inserir:', e)

rows = service.list_equipamentos()
print('Total de equipamentos no teste:', len(rows))
if rows:
    r = rows[0]
    print('Primeiro registro:', r)

print('Limpando registro de teste...')
try:
    service.delete_equipamento(rows[0].id)
    print('Registro deletado')
except Exception as e:
    print('Erro ao deletar:', e)

print('Fechando DB e removendo arquivo...')
db.close()
try:
    os.remove(DB_PATH)
    print('Arquivo removido')
except Exception as e:
    print('Não foi possível remover o arquivo:', e)

print('Teste concluído')
