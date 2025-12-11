from ttkbootstrap import Window
from src.database import Database
from src.services import InventoryService
from src.ui_main import InventarioApp




def main():
	db = Database("inventario.db")
	service = InventoryService(db)
	root = Window(themename="superhero")
	app = InventarioApp(root, service)
	try:
		root.mainloop()
	except KeyboardInterrupt:
		try:
			root.destroy()
		except Exception:
			pass
		print("Interrupted, exiting")
		import sys
		sys.exit(0)




if __name__ == "__main__":
	main()