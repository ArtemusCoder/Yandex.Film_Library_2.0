import csv
import sqlite3
import sys

from PyQt5 import uic, QtSql
from PyQt5.QtCore import Qt, qDebug
from PyQt5 import QtCore

from PyQt5.QtSql import *
from PyQt5.QtWidgets import *


def CheckINT(s):
    try:
        int(s)
        if int(s) != float(s):
            raise ValueError
        return True
    except ValueError:
        return False


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui.ui', self)
        self.con = sqlite3.connect("films_db.sqlite")
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Фильмотека 2.0')
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('films_db.sqlite')
        db.open()
        self.model1 = QSqlTableModel(self, db)
        self.model1.setTable('films')
        self.model1.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        self.model1.select()
        titles = ('ИД', 'Название фильма', 'Год выпуска', 'Жанр', 'Продолжительность')
        for i, title in enumerate(titles):
            self.model1.setHeaderData(i, QtCore.Qt.Horizontal, title)
        self.tableView_films.setModel(self.model1)
        self.tableView_films.show()
        self.query = QSqlQuery(db)
        self.model2 = QSqlTableModel(self, db)
        self.model2.setTable('genres')
        self.model2.select()
        titles = ('ИД', 'Название жанра')
        for i, title in enumerate(titles):
            self.model2.setHeaderData(i, QtCore.Qt.Horizontal, title)
        self.tableView_genres.setModel(self.model2)
        self.tableView_genres.show()
        self.add_film.clicked.connect(self.add_movie)
        self.add_genre.clicked.connect(self.add_genre_func)
        self.edit_genre.clicked.connect(self.edit_genre_window)
        self.delete_genre.clicked.connect(self.delete_genre_func)
        self.edit_film.clicked.connect(self.edit_movie)
        self.delete_film.clicked.connect(self.delete_film_func)

    def delete_film_func(self):
        index = self.tableView_films.selectionModel().currentIndex().row()
        id = self.tableView_films.model().data(
            self.tableView_films.model().index(index, 0))
        self.query.prepare("DELETE FROM films WHERE id = :id")
        self.query.bindValue(":id", id)
        self.query.exec_()
        self.model1.select()

    def edit_movie(self):
        index = self.tableView_films.selectionModel().currentIndex().row()
        self.id_edit = self.tableView_films.model().data(
            self.tableView_films.model().index(index, 0))
        title = self.tableView_films.model().data(
            self.tableView_films.model().index(index, 1))
        year = self.tableView_films.model().data(
            self.tableView_films.model().index(index, 2))
        genre = self.tableView_films.model().data(
            self.tableView_films.model().index(index, 3))
        duration = self.tableView_films.model().data(
            self.tableView_films.model().index(index, 4))
        self.edit_film_window = QDialog()
        self.edit_film_window.setWindowTitle("Изменение фильма")
        grid_layout = QGridLayout()
        self.edit_film_window.setLayout(grid_layout)
        labelname = QLabel(self.edit_film_window)
        labelname.setText('Название')
        labelyear = QLabel(self.edit_film_window)
        labelyear.setText('Год выпуска')
        labelgenre = QLabel(self.edit_film_window)
        labelgenre.setText('Жанр')
        labelduration = QLabel(self.edit_film_window)
        labelduration.setText('Длина')
        self.editname = QLineEdit(self.edit_film_window)
        self.editname.setText(title)
        self.edityear = QLineEdit(self.edit_film_window)
        self.edityear.setText(str(year))
        self.editdur = QLineEdit(self.edit_film_window)
        self.editdur.setText(str(duration))
        self.editcbadd = QComboBox()
        cur = self.con.cursor()
        res = cur.execute("""SELECT id, title FROM genres""").fetchall()
        count = 0
        for elem in res:
            self.editcbadd.addItem(elem[1])
            if elem[0] == genre:
                self.editcbadd.setCurrentIndex(count)
            count += 1
        if index >= 0:
            self.editcbadd.setCurrentIndex(index)
        grid_layout.addWidget(labelname, 0, 0)
        grid_layout.addWidget(self.editname, 0, 1)
        grid_layout.addWidget(labelyear, 1, 0)
        grid_layout.addWidget(self.edityear, 1, 1)
        grid_layout.addWidget(labelgenre, 2, 0)
        grid_layout.addWidget(self.editcbadd, 2, 1)
        grid_layout.addWidget(labelduration, 3, 0)
        grid_layout.addWidget(self.editdur, 3, 1)
        submit = QPushButton('Изменить', self.edit_film_window)
        submit.clicked.connect(self.edit_movie_inside)
        grid_layout.addWidget(submit, 4, 0)
        self.labeledit_error = QLabel(self.edit_film_window)
        grid_layout.addWidget(self.labeledit_error, 5, 0)
        self.edit_film_window.setWindowModality(Qt.ApplicationModal)
        self.edit_film_window.exec_()

    def edit_movie_inside(self):
        if bool(self.editname.text()) and bool(self.editdur.text()) and bool(
                self.edityear.text()) and CheckINT(self.editdur.text()) and CheckINT(
            self.edityear.text()):
            cur = self.con.cursor()
            genre_id = cur.execute("""SELECT id FROM genres WHERE title = ?""",
                                   (str(self.editcbadd.currentText()),)).fetchone()
            title = self.editname.text()
            dur = self.editdur.text()
            year = self.edityear.text()
            self.query.prepare(
                "UPDATE films SET title = :title, year = :year, genre = :genre, duration = :duration WHERE id = :id")
            self.query.bindValue(":id", self.id_edit)
            self.query.bindValue(":title", title)
            self.query.bindValue(":year", year)
            self.query.bindValue(":genre", genre_id[0])
            self.query.bindValue(":duration", dur)
            self.query.exec_()
            self.model1.select()
            self.edit_film_window.close()
            return None
        self.labeledit_error.setText('Неправильный формат!')

        self.labeledit_error.setText('Неправильный формат!')

    def delete_genre_func(self):
        index = self.tableView_genres.selectionModel().currentIndex().row()
        id = self.tableView_genres.model().data(
            self.tableView_genres.model().index(index, 0))
        self.query.prepare("DELETE FROM genres WHERE id = :id")
        self.query.bindValue(":id", id)
        self.query.exec_()
        self.model2.select()

    def edit_genre_window(self):
        self.index_edit_genre = self.tableView_genres.selectionModel().currentIndex().row()
        text = self.tableView_genres.model().data(
            self.tableView_genres.model().index(self.index_edit_genre, 1))
        self.editgenre_window = QDialog()
        self.editgenre_window.setWindowTitle("Редактирование жанра")
        grid_layout = QGridLayout()
        self.editgenre_window.setLayout(grid_layout)
        self.editlinegenre = QLineEdit(self.editgenre_window)
        self.editlinegenre.setText(text)
        labelname = QLabel(self.editgenre_window)
        labelname.setText('Название')
        submit = QPushButton('Изменить', self.editgenre_window)
        submit.clicked.connect(self.edit_genre_func)
        grid_layout.addWidget(labelname, 0, 0)
        grid_layout.addWidget(self.editlinegenre, 0, 1)
        grid_layout.addWidget(submit, 1, 1)
        self.labeleditgenre_error = QLabel(self.editgenre_window)
        grid_layout.addWidget(self.labeleditgenre_error, 2, 0)
        self.editgenre_window.setWindowModality(Qt.ApplicationModal)
        self.editgenre_window.exec_()

    def edit_genre_func(self):
        if bool(self.editlinegenre.text()):
            id = self.tableView_genres.model().data(
                self.tableView_genres.model().index(self.index_edit_genre, 0))
            text = self.editlinegenre.text()
            self.query.prepare("UPDATE genres SET title = :title WHERE id = :id")
            self.query.bindValue(":id", id)
            self.query.bindValue(":title", text)
            self.query.exec_()
            self.editgenre_window.close()
            self.model2.select()
            return None
        self.labeleditgenre_error.setText('Неправильный формат')

    def add_genre_func(self):
        self.add_genre_window = QDialog()
        self.add_genre_window.setWindowTitle("Добавление жанра")
        grid_layout = QGridLayout()
        self.add_genre_window.setLayout(grid_layout)
        labelname = QLabel(self.add_genre_window)
        labelname.setText('Название')
        self.addgenre_name = QLineEdit(self.add_genre_window)
        grid_layout.addWidget(labelname, 0, 0)
        grid_layout.addWidget(self.addgenre_name, 0, 1)
        submit = QPushButton('Добавить', self.add_genre_window)
        submit.clicked.connect(self.add_genre_inside)
        grid_layout.addWidget(submit, 1, 1)
        self.labeladd_genre_error = QLabel(self.add_genre_window)
        grid_layout.addWidget(self.labeladd_genre_error, 2, 0)
        self.add_genre_window.setWindowModality(Qt.ApplicationModal)
        self.add_genre_window.exec_()

    def add_genre_inside(self):
        cur = self.con.cursor()
        if bool(self.addgenre_name.text()):
            id = cur.execute("""SELECT id FROM genres ORDER BY id DESC LIMIT 1""").fetchone()
            self.query.prepare("INSERT INTO genres(id, title) VALUES(:id, :title)")
            self.query.bindValue(":id", id[0] + 1)
            self.query.bindValue(":title", self.addgenre_name.text())
            self.query.exec_()
            self.add_genre_window.close()
            self.model2.select()
            return None
        self.labeladd_genre_error.setText("Неправильный формат")
        return None

    def add_movie(self):
        self.add_film_window = QDialog()
        self.add_film_window.setWindowTitle("Добавление фильма")
        grid_layout = QGridLayout()
        self.add_film_window.setLayout(grid_layout)
        labelname = QLabel(self.add_film_window)
        labelname.setText('Название')
        labelyear = QLabel(self.add_film_window)
        labelyear.setText('Год выпуска')
        labelgenre = QLabel(self.add_film_window)
        labelgenre.setText('Жанр')
        labelduration = QLabel(self.add_film_window)
        labelduration.setText('Длина')
        self.addname = QLineEdit(self.add_film_window)
        self.addyear = QLineEdit(self.add_film_window)
        self.adddur = QLineEdit(self.add_film_window)
        self.cbadd = QComboBox()
        cur = self.con.cursor()
        res = cur.execute("""SELECT title FROM genres""").fetchall()
        for elem in res:
            self.cbadd.addItem(elem[0])
        grid_layout.addWidget(labelname, 0, 0)
        grid_layout.addWidget(self.addname, 0, 1)
        grid_layout.addWidget(labelyear, 1, 0)
        grid_layout.addWidget(self.addyear, 1, 1)
        grid_layout.addWidget(labelgenre, 2, 0)
        grid_layout.addWidget(self.cbadd, 2, 1)
        grid_layout.addWidget(labelduration, 3, 0)
        grid_layout.addWidget(self.adddur, 3, 1)
        submit = QPushButton('Добавить', self.add_film_window)
        submit.clicked.connect(self.add_movie_inside)
        grid_layout.addWidget(submit, 4, 0)
        self.labeladd_error = QLabel(self.add_film_window)
        grid_layout.addWidget(self.labeladd_error, 5, 0)
        self.add_film_window.setWindowModality(Qt.ApplicationModal)
        self.add_film_window.exec_()

    def add_movie_inside(self):
        if bool(self.addname.text()) and bool(self.adddur.text()) and bool(
                self.addyear.text()) and CheckINT(self.adddur.text()) and CheckINT(
            self.addyear.text()):
            cur = self.con.cursor()
            genre_id = cur.execute("""SELECT id FROM genres WHERE title = ?""",
                                   (str(self.cbadd.currentText()),)).fetchone()
            id = cur.execute("""SELECT id FROM films ORDER BY id DESC LIMIT 1""").fetchone()
            self.query.prepare(
                "INSERT INTO films(id, title, year, genre, duration) VALUES(:id, :title, :year, :genre, :duration)")
            self.query.bindValue(":id", id[0] + 1)
            self.query.bindValue(":title", self.addname.text())
            self.query.bindValue(":year", self.addyear.text())
            self.query.bindValue(":genre", genre_id[0])
            self.query.bindValue(":duration", self.adddur.text())
            self.query.exec_()
            self.add_film_window.close()
            self.model1.select()
            return None
        self.labeladd_error.setText('Неправильный формат')


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
