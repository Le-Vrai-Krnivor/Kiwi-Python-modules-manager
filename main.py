import sys
import subprocess
import requests
import os
import zipfile
import shutil
import pythoncom
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, 
    QMessageBox, QSplitter, QListWidgetItem, QHBoxLayout, QTextEdit, 
    QInputDialog, QLineEdit, QProgressBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor

class ConsoleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(30)
        self.title_bar.setStyleSheet("background-color: #1a1a1a;")
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)

        title_label = QLabel("Console")
        title_label.setStyleSheet("color: white; font-weight: bold;")
        title_layout.addWidget(title_label)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setFixedSize(50, 20)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid white;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """)
        title_layout.addWidget(self.clear_button)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: white;
                font-family: 'Courier New';
                border: none;
                padding: 5px;
            }
        """)

        self.input = QLineEdit()
        self.input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                font-family: 'Courier New';
                border: none;
                padding: 5px;
            }
        """)
        self.input.setPlaceholderText("Entrez une commande...")

        self.layout.addWidget(self.title_bar)
        self.layout.addWidget(self.output)
        self.layout.addWidget(self.input)

        self.input.returnPressed.connect(self.execute_command)
        self.clear_button.clicked.connect(self.clear_console)

    def execute_command(self):
        command = self.input.text()
        self.output.append(f"\n$ {command}")
        self.input.clear()
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.stdout:
                self.output.append(result.stdout)
            if result.stderr:
                self.output.append(f'<span style="color: red;">{result.stderr}</span>')
        except Exception as e:
            self.output.append(f'<span style="color: red;">Erreur : {str(e)}</span>')
        self.output.moveCursor(QTextCursor.MoveOperation.End)

    def clear_console(self):
        self.output.clear()

class LibraryManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestionnaire de Bibliothèques Python")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #2E2E2E; color: white; font-family: Arial;")

        self.layout = QVBoxLayout()

        self.library_layout = QVBoxLayout()
        self.label = QLabel("Bibliothèques Python Installées:")
        self.library_layout.addWidget(self.label)
        self.list_widget = QListWidget()
        self.library_layout.addWidget(self.list_widget)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Ajouter")
        self.style_button(self.add_button)
        self.add_button.clicked.connect(self.prompt_add_library)
        button_layout.addWidget(self.add_button)
        self.remove_button = QPushButton("Supprimer")
        self.style_button(self.remove_button)
        self.remove_button.clicked.connect(self.remove_library)
        self.remove_button.setEnabled(False)
        button_layout.addWidget(self.remove_button)
        self.library_layout.addLayout(button_layout)

        self.splitter = QSplitter(Qt.Orientation.Vertical)
        library_widget = QWidget()
        library_widget.setLayout(self.library_layout)
        self.splitter.addWidget(library_widget)

        self.console = ConsoleWidget()
        self.splitter.addWidget(self.console)

        self.layout.addWidget(self.splitter)

        self.setLayout(self.layout)

        self.load_libraries()

        if getattr(sys, 'frozen', False):
            latest_commit = self.check_for_updates()
            if latest_commit:
                reply = QMessageBox.question(self, 'Mise à jour disponible', 
                                             'Une nouvelle version stable est disponible. Voulez-vous mettre à jour ?',
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    self.download_and_update(latest_commit)

    def style_button(self, button):
        button.setStyleSheet("""
            QPushButton {
                background-color: #003366;
                border-radius: 15px;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #002244;
            }
            QPushButton:pressed {
                background-color: #001122;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
        """)

    def log_message(self, message):
        if message:
            self.console.output.append(message)
            self.console.output.moveCursor(QTextCursor.MoveOperation.End)

    def load_libraries(self):
        process = subprocess.Popen([sys.executable, '-m', 'pip', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate()
        if output:
            libraries = output.splitlines()[2:]
            for lib in libraries:
                name = lib.split()[0]
                item = QListWidgetItem(name)
                item.setData(Qt.ItemDataRole.UserRole, name)
                self.list_widget.addItem(item)
            self.log_message("Bibliothèques chargées avec succès.")
        if error:
            self.log_message(f"Erreur lors du chargement des bibliothèques : {error}")
        self.list_widget.itemSelectionChanged.connect(self.update_remove_button_state)

    def update_remove_button_state(self):
        self.remove_button.setEnabled(bool(self.list_widget.selectedItems()))
        self.style_button(self.remove_button)

    def prompt_add_library(self):
        library_name, ok = QInputDialog.getText(self, "Ajouter une bibliothèque", "Nom de la bibliothèque:")
        if ok and library_name.strip():
            self.install_library(library_name.strip())

    def install_library(self, library_name):
        self.log_message(f"Installation de {library_name}...")
        process = subprocess.Popen([sys.executable, '-m', 'pip', 'install', library_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.log_message(output.strip())
        rc = process.poll()
        if rc == 0:
            item = QListWidgetItem(library_name)
            item.setData(Qt.ItemDataRole.UserRole, library_name)
            self.list_widget.addItem(item)
            QMessageBox.information(self, "Succès", f"La bibliothèque '{library_name}' a été installée avec succès.")
        else:
            error = process.stderr.read()
            self.log_message(f"Erreur lors de l'installation : {error}")
            QMessageBox.warning(self, "Erreur", f"Échec de l'installation de '{library_name}'.")

    def remove_library(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
        library_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.log_message(f"Suppression de {library_name}...")
        process = subprocess.Popen([sys.executable, '-m', 'pip', 'uninstall', '-y', library_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.log_message(output.strip())
        rc = process.poll()
        if rc == 0:
            self.list_widget.takeItem(self.list_widget.row(selected_items[0]))
            QMessageBox.information(self, "Succès", f"La bibliothèque '{library_name}' a été supprimée avec succès.")
        else:
            error = process.stderr.read()
            self.log_message(f"Erreur lors de la suppression : {error}")
            QMessageBox.warning(self, "Erreur", f"Échec de la suppression de '{library_name}'.")
        self.update_remove_button_state()

    def check_for_updates(self):
        try:
            repo_url = "https://api.github.com/repos/Le-Vrai-Krnivor/Kiwi-Python-modules-manager/commits"
            response = requests.get(repo_url)
            commits = response.json()
            
            for commit in commits:
                if commit['commit']['message'].startswith("STABLE VERSION"):
                    return commit['sha']
            return None
        except Exception as e:
            self.log_message(f"Erreur lors de la vérification des mises à jour : {str(e)}")
            return None

    def download_and_update(self, commit_sha):
        try:
            progress = QProgressBar(self)
            progress.setGeometry(30, 40, 200, 25)
            progress.setStyleSheet("QProgressBar::chunk { background-color: green; }")
            self.layout.addWidget(progress)
            
            url = f"https://github.com/Le-Vrai-Krnivor/Kiwi-Python-modules-manager/archive/{commit_sha}.zip"
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            block_size = 1024
            wrote = 0
            with open("update.zip", "wb") as f:
                for data in response.iter_content(block_size):
                    wrote = wrote + len(data)
                    f.write(data)
                    progress.setValue(int(wrote / total_size * 100))
            
            with zipfile.ZipFile("update.zip", 'r') as zip_ref:
                zip_ref.extractall("update")
            
            os.chdir(f"update/Kiwi-Python-modules-manager-{commit_sha}")
            subprocess.run(["pyinstaller", "--onefile", "main.py"])
            
            os.replace("dist/main.exe", "../../Kiwi-Python-modules-manager.exe")
            
            os.chdir("../..")
            shutil.rmtree("update")
            os.remove("update.zip")
            
            QMessageBox.information(self, "Mise à jour", "Mise à jour effectuée avec succès. Veuillez redémarrer l'application.")
            sys.exit()
        except Exception as e:
            self.log_message(f"Erreur lors de la mise à jour : {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LibraryManager()
    window.show()
    sys.exit(app.exec())
