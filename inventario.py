import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

def conectar():
    return sqlite3.connect('inventario.db')

def inicializar_banco():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            marca TEXT,
            patrimonio INTEGER UNIQUE,
            setor TEXT,
            status TEXT
        )
    ''')
    conexao.commit()
    conexao.close()

def adicionar_equipamento():
    tipo = entry_tipo.get().strip()
    marca = entry_marca.get().strip()
    patrimonio = entry_patrimonio.get().strip()
    setor = entry_setor.get().strip()
    status = "Ativo"

    if not tipo or not patrimonio:
        messagebox.showwarning("Atenção", "Tipo e Patrimônio são obrigatórios!")
        return

    try:
        patrimonio = int(patrimonio)
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("INSERT INTO equipamentos (tipo, marca, patrimonio, setor, status) VALUES (?, ?, ?, ?, ?)", 
                       (tipo, marca, patrimonio, setor, status))
        conexao.commit()
        conexao.close()
        
        limpar_campos()
        listar_equipamentos()
        messagebox.showinfo("Sucesso", "Equipamento cadastrado!")
    except ValueError:
        messagebox.showerror("Erro", "Patrimônio deve ser um número!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "Patrimônio já cadastrado!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao cadastrar: {e}")

def listar_equipamentos():
    for i in tree.get_children():
        tree.delete(i)
    
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM equipamentos")
    resultados = cursor.fetchall()
    conexao.close()

    for item in resultados:
        tree.insert("", "end", values=item)

def buscar_por_setor():
    busca = entry_busca.get().strip()
    if not busca:
        messagebox.showwarning("Atenção", "Digite um setor para buscar!")
        return
    
    for i in tree.get_children():
        tree.delete(i)
    
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM equipamentos WHERE setor = ?", (busca,))
    resultados = cursor.fetchall()
    conexao.close()
    
    if resultados:
        for item in resultados:
            tree.insert("", "end", values=item)
    else:
        messagebox.showinfo("Resultado", f"Nenhum equipamento encontrado no setor: {busca}")

def atualizar_status():
    item_selecionado = tree.selection()
    if not item_selecionado:
        messagebox.showwarning("Atenção", "Selecione um equipamento para atualizar!")
        return
    
    valores = tree.item(item_selecionado)['values']
    id_equip = valores[0]
    
    novo_status = entry_status.get().strip()
    if not novo_status:
        messagebox.showwarning("Atenção", "Digite um novo status!")
        return
    
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("UPDATE equipamentos SET status = ? WHERE id = ?", (novo_status, id_equip))
        conexao.commit()
        conexao.close()
        
        entry_status.delete(0, tk.END)
        listar_equipamentos()
        messagebox.showinfo("Sucesso", f"Status do ID {id_equip} atualizado!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao atualizar: {e}")

def excluir_equipamento():
    item_selecionado = tree.selection()
    if not item_selecionado:
        messagebox.showwarning("Atenção", "Selecione um item na tabela para excluir!")
        return
    
    valores = tree.item(item_selecionado)['values']
    id_equip = valores[0]

    resposta = messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir o ID {id_equip}?")
    if resposta:
        try:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM equipamentos WHERE id = ?", (id_equip,))
            conexao.commit()
            conexao.close()
            listar_equipamentos()
            messagebox.showinfo("Sucesso", "Equipamento deletado!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao deletar: {e}")

def limpar_campos():
    entry_tipo.delete(0, tk.END)
    entry_marca.delete(0, tk.END)
    entry_patrimonio.delete(0, tk.END)
    entry_setor.delete(0, tk.END)
    entry_busca.delete(0, tk.END)
    entry_status.delete(0, tk.END)

inicializar_banco()

janela = tk.Tk()
janela.title("Sistema de Inventário TI - Prefeitura")
janela.geometry("900x600")

frame_cadastro = tk.LabelFrame(janela, text="Novo Cadastro", font=("Arial", 10, "bold"))
frame_cadastro.pack(fill="x", padx=10, pady=10)

tk.Label(frame_cadastro, text="Tipo:").grid(row=0, column=0, padx=5, pady=5)
entry_tipo = tk.Entry(frame_cadastro)
entry_tipo.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_cadastro, text="Marca:").grid(row=0, column=2, padx=5, pady=5)
entry_marca = tk.Entry(frame_cadastro)
entry_marca.grid(row=0, column=3, padx=5, pady=5)

tk.Label(frame_cadastro, text="Patrimônio:").grid(row=1, column=0, padx=5, pady=5)
entry_patrimonio = tk.Entry(frame_cadastro)
entry_patrimonio.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_cadastro, text="Setor:").grid(row=1, column=2, padx=5, pady=5)
entry_setor = tk.Entry(frame_cadastro)
entry_setor.grid(row=1, column=3, padx=5, pady=5)

btn_salvar = tk.Button(frame_cadastro, text="Salvar Equipamento", command=adicionar_equipamento, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
btn_salvar.grid(row=2, column=0, columnspan=4, sticky="we", padx=5, pady=10)

frame_busca = tk.LabelFrame(janela, text="Buscar por Setor", font=("Arial", 10, "bold"))
frame_busca.pack(fill="x", padx=10, pady=5)

tk.Label(frame_busca, text="Setor:").pack(side="left", padx=5)
entry_busca = tk.Entry(frame_busca, width=20)
entry_busca.pack(side="left", padx=5)

btn_buscar = tk.Button(frame_busca, text="Buscar", command=buscar_por_setor, bg="#2196F3", fg="white")
btn_buscar.pack(side="left", padx=5, pady=5)

btn_listar_tudo = tk.Button(frame_busca, text="Listar Tudo", command=listar_equipamentos, bg="#FF9800", fg="white")
btn_listar_tudo.pack(side="left", padx=5, pady=5)

colunas = ("ID", "Tipo", "Marca", "Patrimônio", "Setor", "Status")
tree = ttk.Treeview(janela, columns=colunas, show="headings", height=12)

for col in colunas:
    tree.heading(col, text=col)
    tree.column(col, width=130)

tree.pack(fill="both", expand=True, padx=10, pady=5)

frame_acoes = tk.LabelFrame(janela, text="Ações", font=("Arial", 10, "bold"))
frame_acoes.pack(fill="x", padx=10, pady=5)

tk.Label(frame_acoes, text="Novo Status:").pack(side="left", padx=5)
entry_status = tk.Entry(frame_acoes, width=20)
entry_status.pack(side="left", padx=5)

btn_atualizar = tk.Button(frame_acoes, text="Atualizar Status", command=atualizar_status, bg="#FF5722", fg="white")
btn_atualizar.pack(side="left", padx=5, pady=5)

btn_excluir = tk.Button(frame_acoes, text="Excluir Selecionado", command=excluir_equipamento, bg="#F44336", fg="white", font=("Arial", 10, "bold"))
btn_excluir.pack(side="left", padx=5, pady=5)

listar_equipamentos()

janela.mainloop()