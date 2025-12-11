from tkinter import Tk
from src.database import Database
from src.services import InventoryService
from src.ui_main import InventarioApp




def main():
	db = Database("inventario.db")
	service = InventoryService(db)
	root = Tk()
	app = InventarioApp(root, service)
	try:
		root.mainloop()
	except KeyboardInterrupt:
		# Allow Ctrl+C from terminal to close the GUI cleanly
		try:
			root.destroy()
		except Exception:
			pass
		print("Interrupted, exiting")
		import sys
		sys.exit(0)




if __name__ == "__main__":
	main()