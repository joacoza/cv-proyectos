import re
import sys
import sqlite3
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QMessageBox
from gui import Ui_MainWindow

class aplicacion(QMainWindow):
	def __init__(self):
		super().__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.show()
		self.iniciar_datos()
		self.cargar_datos_tabla()
		self.ui.bot_agregar.clicked.connect(lambda: self.añadir_datos_tabla())
		self.ui.bot_buscar.clicked.connect(lambda: self.select_tabla())
		self.ui.bot_borrar.clicked.connect(lambda: self.borrar_datos())
		self.ui.bot_salir.clicked.connect(lambda: self.salir())

	def iniciar_datos(self):
		conn = sqlite3.connect("clubsql.db")
		c = conn.cursor()
		c.execute("""CREATE TABLE IF NOT EXISTS club (
					nrosocio integer,
					nom text,
					apel text,
					edad integer,
					cate text,
					sexo text
					)""")
		c.execute("""SELECT * FROM club""")
		self.fetch = c.fetchall()
		print(self.fetch)

	def cargar_datos_tabla(self):
		self.ui.tabla.setSortingEnabled(False)
		fila = 0
		for registro in self.fetch:
			self.ui.tabla.insertRow(fila)
			columna = 0
			for elemento in registro:
				celda = QTableWidgetItem(elemento)
				if isinstance(elemento, int):
					celda.setData(QtCore.Qt.DisplayRole, elemento)
				self.ui.tabla.setItem(fila, columna, celda)
				columna += 1
			fila += 1
		self.ui.tabla.setSortingEnabled(True)

	def añadir_datos_tabla(self):
		self.status = True
		self.check_int(self.ui.c_nrosocio.text(), "Error en número de socio", "Carácteres Inválidos", "Error")
		self.check_str(self.ui.c_nombre.text(), "Error en nombre de socio", "Carácteres Inválidos", "Error")
		self.check_str(self.ui.c_apellido.text(), "Error en apellido de socio", "Carácteres Inválidos", "Error")
		self.check_int(self.ui.c_edad.text(), "Error en edad de socio", "Carácteres Inválidos", "Error")
		if self.status == True:
			conn = sqlite3.connect("clubsql.db")
			c = conn.cursor()
			listanros = c.execute("SELECT nrosocio FROM club WHERE nrosocio = ?", (self.ui.c_nrosocio.text(),))
			if c.fetchone():
				pregunta = QMessageBox.question(self, 'Alerta', 'Número de socio existente, desea actualizarlo?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
				if pregunta == QMessageBox.Yes:
					c.execute("UPDATE club SET nom = ?, apel = ?, edad = ?, cate = ?, sexo = ? WHERE nrosocio = ?", (self.ui.c_nombre.text(), self.ui.c_apellido.text(), self.ui.c_edad.text(), self.ui.c_categoria.currentText(), self.ui.c_sexo.currentText(), self.ui.c_nrosocio.text(),))
					conn.commit()
					self.eliminar_datos_tabla()
					self.iniciar_datos()
					self.cargar_datos_tabla()
			else:
				c.execute("INSERT INTO club (nrosocio, nom, apel, edad, cate, sexo) values (?, ?, ?, ?, ?, ?)", (self.ui.c_nrosocio.text(), self.ui.c_nombre.text(), self.ui.c_apellido.text(), self.ui.c_edad.text(), self.ui.c_categoria.currentText(), self.ui.c_sexo.currentText()))
				conn.commit()
				self.eliminar_datos_tabla()
				self.iniciar_datos()
				self.cargar_datos_tabla()

	def eliminar_datos_tabla(self):
		self.ui.tabla.setRowCount(0)

	def error_datos(self, text, info, window):
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Critical)
		msg.setText(text)
		msg.setInformativeText(info)
		msg.setWindowTitle(window)
		msg.exec_()
		self.status = False

	def check_str(self, ref, text, info, window):
		if not re.match("^[a-zA-Z ]*$", ref) or not ref:
			self.error_datos(text, info, window)

	def check_int(self, ref, text, info, window):
		try:
			i = int(ref)
			if i < 1:
				raise ValueError
		except ValueError:
			self.error_datos(text, info, window)

	def borrar_datos(self):
		conn = sqlite3.connect("clubsql.db")
		c = conn.cursor()
		filas = sorted(set(i.row() for i in self.ui.tabla.selectedIndexes()))
		print(filas)
		if filas != []:
			pregunta = QMessageBox.question(self, 'Alerta', 'Desea borrar los socios seleccionados?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
			if pregunta == QMessageBox.Yes:
				for fila in filas:
					print(fila)
					numdel = self.ui.tabla.item(fila, 0).text()
					print(numdel)
					c.execute("DELETE FROM club WHERE nrosocio = ?", (numdel,))
				conn.commit()
				self.eliminar_datos_tabla()
				self.iniciar_datos()
				self.cargar_datos_tabla()
				
	def select_tabla(self):
		numfila = self.ui.tabla.rowCount()
		for fila in range(numfila):
			item = self.ui.tabla.item(fila, 0)
			if item.text() == self.ui.c_nrosocio.text():
				self.ui.tabla.setCurrentCell(fila, 0)

	def salir(self):
		sys.exit()

def main():
	app = QApplication(sys.argv)
	instance = aplicacion()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()