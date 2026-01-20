# =========================
# IMPORT MODULE
# =========================
import sys                  # Untuk argumen sistem & menjalankan aplikasi
import sqlite3              # Database SQLite

# Import komponen PyQt6
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QComboBox, QSpinBox,
    QDateEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QGroupBox, QMessageBox,
    QFrame, QDialog
)

# Import core PyQt
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QFont

# Nama database
DB_NAME = "keuangan.db"


# ==================================================
# DATABASE (MODEL)
# ==================================================
class Database:
    def __init__(self):
        # Koneksi ke database
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Tabel users
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        """)

        # Tabel transaksi
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaksi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                tanggal TEXT,
                deskripsi TEXT,
                jenis TEXT,
                sumber TEXT,
                jumlah INTEGER
            )
        """)
        self.conn.commit()

        # User default
        self.cursor.execute(
            "INSERT OR IGNORE INTO users (username, password) VALUES ('karissa','1')"
        )
        self.conn.commit()

    # Proses login
    def login(self, username, password):
        self.cursor.execute(
            "SELECT id FROM users WHERE username=? AND password=?",
            (username, password)
        )
        return self.cursor.fetchone()

    # Tambah transaksi
    def insert_transaksi(self, data):
        self.cursor.execute("""
            INSERT INTO transaksi (user_id, tanggal, deskripsi, jenis, sumber, jumlah)
            VALUES (?, ?, ?, ?, ?, ?)
        """, data)
        self.conn.commit()

    # Ambil semua transaksi
    def fetch_transaksi(self, user_id):
        self.cursor.execute("""
            SELECT id, tanggal, deskripsi, jenis, sumber, jumlah
            FROM transaksi WHERE user_id=? ORDER BY id DESC
        """, (user_id,))
        return self.cursor.fetchall()

    # Hapus transaksi
    def delete_transaksi(self, id_data):
        self.cursor.execute("DELETE FROM transaksi WHERE id=?", (id_data,))
        self.conn.commit()

    # Ambil data saldo
    def fetch_saldo(self, user_id):
        self.cursor.execute(
            "SELECT jenis, sumber, jumlah FROM transaksi WHERE user_id=?",
            (user_id,)
        )
        return self.cursor.fetchall()


# ==================================================
# LOGIN DIALOG (MODERN & BEWARNA)
# ==================================================
class LoginDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.user_id = None

        self.setFixedSize(420, 320)
        self.setWindowTitle("Login User")

        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2
                );
            }
            QFrame {
                background: white;
                border-radius: 16px;
            }
            QLabel#title {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
            }
            QLabel#subtitle {
                color: #7f8c8d;
            }
            QLineEdit {
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #ccc;
                font-size: 13px;
            }
            QPushButton {
                background-color: #667eea;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #5a67d8;
            }
        """)

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setFixedSize(320, 260)
        layout = QVBoxLayout(card)

        title = QLabel("🔐 LOGIN")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Aplikasi Keuangan Pribadi")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.username = QLineEdit()
        self.username.setPlaceholderText("👤 Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("🔑 Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        btn_login = QPushButton("MASUK")
        btn_login.clicked.connect(self.do_login)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(10)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addSpacing(10)
        layout.addWidget(btn_login)
        layout.addStretch()

        outer.addWidget(card)

    def do_login(self):
        result = self.db.login(self.username.text(), self.password.text())
        if result:
            self.user_id = result[0]
            self.accept()
        else:
            QMessageBox.warning(self, "Login Gagal", "Username atau password salah!")


# ==================================================
# APLIKASI UTAMA
# ==================================================
class KeuanganApp(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id

        self.setWindowTitle("Aplikasi Keuangan Pribadi")
        self.setGeometry(200, 80, 1000, 650)

        # =========================
        # STYLE UTAMA APLIKASI
        # =========================
        self.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                font-size: 12px;
            }

            QGroupBox {
                background-color: #ffffff;
                border: 2px solid #3498db;
                border-radius: 10px;
                margin-top: 10px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                background-color: #3498db;
                color: white;
                border-radius: 5px;
            }

            QLineEdit, QComboBox, QSpinBox, QDateEdit {
                padding: 6px;
                border-radius: 5px;
                border: 1px solid #bdc3c7;
                background-color: #ffffff;
            }

            QPushButton {
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: bold;
            }

            QPushButton:hover {
                opacity: 0.85;
            }

            QTableWidget {
                background-color: white;
                border-radius: 10px;
            }

            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 5px;
                border: none;
            }

            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)

        self.init_ui()
        self.load_data()
        self.update_saldo()

    def init_ui(self):
        main = QVBoxLayout()

        # Judul
        title = QLabel("💰 Aplikasi Keuangan Pribadi")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        main.addWidget(title)

        # =========================
        # KARTU SALDO
        # =========================
        saldo = QHBoxLayout()
        self.card_rek = self.card("Saldo Rekening", "#3498db")
        self.card_cash = self.card("Uang Cash", "#f39c12")
        self.card_total = self.card("Total Saldo", "#2ecc71")

        saldo.addWidget(self.card_rek)
        saldo.addWidget(self.card_cash)
        saldo.addWidget(self.card_total)
        main.addLayout(saldo)

        # =========================
        # FORM INPUT
        # =========================
        form = QGroupBox("Input Transaksi")
        fl = QHBoxLayout()

        self.deskripsi = QLineEdit()
        self.deskripsi.setPlaceholderText("Deskripsi")

        self.jenis = QComboBox()
        self.jenis.addItems(["Pemasukan", "Pengeluaran"])

        self.sumber = QComboBox()
        self.sumber.addItems(["Rekening", "Cash"])

        self.jumlah = QSpinBox()
        self.jumlah.setMaximum(100000000)

        self.tanggal = QDateEdit(QDate.currentDate())
        self.tanggal.setCalendarPopup(True)


        
        btn_add = QPushButton("Tambah")
        btn_add.setStyleSheet("background-color:#1abc9c;color:white;")
        btn_add.clicked.connect(self.tambah)

        btn_del = QPushButton("Hapus")
        btn_del.setStyleSheet("background-color: #ff7675;color: white;")
        btn_del.clicked.connect(self.hapus)

        btn_exit = QPushButton("Keluar")
        btn_exit.setStyleSheet("background-color: #6f4e37;color: white;")
        btn_exit.clicked.connect(self.close)

        for w in [
            self.deskripsi, self.jenis, self.sumber,
            self.jumlah, self.tanggal,
            btn_add, btn_del, btn_exit
        ]:
            fl.addWidget(w)

        form.setLayout(fl)
        main.addWidget(form)

        # =========================
        # TABEL
        # =========================
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Tanggal", "Deskripsi", "Jenis", "Sumber", "Jumlah"]
        )
        main.addWidget(self.table)

        self.setLayout(main)

    # Membuat kartu saldo
    def card(self, title, color):
        frame = QFrame()
        frame.setStyleSheet(f"""
            background-color: {color};
            color: white;
            border-radius: 15px;
        """)
        layout = QVBoxLayout(frame)
        lbl_title = QLabel(title)
        lbl_value = QLabel("Rp 0")
        lbl_value.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        frame.value = lbl_value
        return frame

    # Tambah transaksi
    def tambah(self):
        if self.deskripsi.text() == "" or self.jumlah.value() == 0:
            QMessageBox.warning(self, "Error", "Lengkapi data!")
            return

        data = (
            self.user_id,
            self.tanggal.date().toString("yyyy-MM-dd"),
            self.deskripsi.text(),
            self.jenis.currentText(),
            self.sumber.currentText(),
            self.jumlah.value()
        )
        self.db.insert_transaksi(data)
        self.deskripsi.clear()
        self.jumlah.setValue(0)
        self.load_data()
        self.update_saldo()

    # Load tabel
    def load_data(self):
        self.table.setRowCount(0)
        for row_data in self.db.fetch_transaksi(self.user_id):
            r = self.table.rowCount()
            self.table.insertRow(r)
            for c, d in enumerate(row_data):
                self.table.setItem(r, c, QTableWidgetItem(str(d)))

    # Hapus data
    def hapus(self):
        row = self.table.currentRow()
        if row < 0:
            return
        id_data = self.table.item(row, 0).text()
        self.db.delete_transaksi(id_data)
        self.load_data()
        self.update_saldo()

    # Update saldo
    def update_saldo(self):
        rekening = cash = 0
        for jenis, sumber, jumlah in self.db.fetch_saldo(self.user_id):
            if jenis == "Pemasukan":
                rekening += jumlah if sumber == "Rekening" else 0
                cash += jumlah if sumber == "Cash" else 0
            else:
                rekening -= jumlah if sumber == "Rekening" else 0
                cash -= jumlah if sumber == "Cash" else 0

        total = rekening + cash
        self.card_rek.value.setText(f"Rp {rekening:,}")
        self.card_cash.value.setText(f"Rp {cash:,}")
        self.card_total.value.setText(f"Rp {total:,}")


# ==================================================
# MAIN
# ==================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = Database()

    login = LoginDialog(db)
    if login.exec():
        window = KeuanganApp(db, login.user_id)
        window.show()
        sys.exit(app.exec())
