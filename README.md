# 💻 Sistema de Inventário de TI

Sistema de gerenciamento de ativos de TI desenvolvido em Python com interface gráfica moderna e banco de dados SQL (SQLite).

## 📦 Download do Executável
Disponibilizamos uma versão compilada (`.exe`) pronta para uso, ideal para quem não tem o Python instalado.
- **[Clique aqui para baixar a versão mais recente](https://github.com/ArthurRisson/Sistema-de-inventario-TI/releases/tag/1.2)**

> **Nota:** Basta fazer o download e executar o arquivo para abrir o sistema. Lembre-se de manter o arquivo `inventario.db` na mesma pasta do executável.

## 🚀 Funcionalidades
- **CRUD Completo:** Cadastrar, Ler, Atualizar e Deletar equipamentos.
- **Banco de Dados:** Persistência de dados automática com SQLite.
- **Validação:** Impede cadastro duplicado de patrimônio e campos vazios.
- **Busca:** Filtro de equipamentos por setor.
- **Interface Moderna:** GUI construída com Tkinter e **ttkbootstrap** (Tema Superhero).

## 🛠️ Tecnologias
- Python 3.x
- Tkinter (Interface Gráfica)
- ttkbootstrap (Estilização Moderna)
- SQLite3 (Banco de Dados)

## ▶️ Como Rodar (Código Fonte)
Caso prefira rodar diretamente o código em Python:

1. Clone o repositório.
2. Certifique-se de ter o Python 3.x instalado.
3. Instale a dependência visual:
   ```bash
   pip install ttkbootstrap
