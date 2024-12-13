import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QLineEdit, QMessageBox, QHBoxLayout, QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt

class LibraryManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestionnaire de Bibliothèques Python")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("background-color: #2E2E2E; color: white;")

        self.layout = QVBoxLayout()

        self.library_layout = QVBoxLayout()
        
        self.label = QLabel("Bibliothèques Python Installées:")
        self.library_layout.addWidget(self.label)

        self.list_widget = QListWidget()
        self.library_layout.addWidget(self.list_widget)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Nom de la bibliothèque à ajouter")
        self.library_layout.addWidget(self.input_field)

        self.add_button = QPushButton("Ajouter Bibliothèque")
        self.add_button.clicked.connect(self.add_library)
        self.library_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Supprimer Bibliothèque")
        self.remove_button.clicked.connect(self.remove_library)
        self.library_layout.addWidget(self.remove_button)

        # Création d'un QSplitter pour gérer la console
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Création du champ de texte pour la console
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        
        # Modification du style pour avoir un fond noir et du texte blanc
        self.console_output.setStyleSheet("background-color: black; color: white; font-family: monospace;")

        # Ajout des widgets au splitter
        self.splitter.addWidget(QWidget())  # Espace vide pour le premier widget (pour les bibliothèques)
        self.splitter.addWidget(self.console_output)

        # Ajout du splitter au layout principal
        self.layout.addLayout(self.library_layout)
        
        # Bouton pour afficher/masquer la console
        self.toggle_console_button = QPushButton("Afficher/Masquer Console")
        self.toggle_console_button.clicked.connect(self.toggle_console)
        self.layout.addWidget(self.toggle_console_button)

        # Ajout du splitter au layout principal
        self.layout.addWidget(self.splitter)

        self.setLayout(self.layout)
        
        self.load_libraries()

    def log_message(self, message):
        if message:  # Vérifie si le message n'est pas vide
            self.console_output.append(message)

    def load_libraries(self):
        command = [sys.executable, '-m', 'pip', 'list']
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.stdout:
                libraries = result.stdout.splitlines()[2:]  # Ignore les deux premières lignes
                for lib in libraries:
                    name = lib.split()[0]
                    self.list_widget.addItem(name)
                self.log_message("Bibliothèques chargées avec succès.")
            if result.stderr:
                self.log_message(f"Erreur lors du chargement des bibliothèques : {result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des bibliothèques: {e}")
            self.log_message(f"Erreur lors du chargement des bibliothèques: {e}")

    def add_library(self):
        library_name = self.input_field.text().strip()
        if library_name:
            command = [sys.executable, '-m', 'pip', 'install', library_name]
            try:
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.stdout:
                    self.log_message(result.stdout)
                    self.list_widget.addItem(library_name)  # Ajoute à la liste si réussi
                if result.stderr:
                    self.log_message(f"Erreur lors de l'ajout de la bibliothèque : {result.stderr}")
                self.input_field.clear()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout de la bibliothèque: {e}")
                self.log_message(f"Erreur lors de l'ajout de la bibliothèque: {e}")

    def remove_library(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner une bibliothèque à supprimer.")
            return
        
        library_name = selected_items[0].text()
        
        command = [sys.executable, '-m', 'pip', 'uninstall', '-y', library_name]
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.stdout:
                self.log_message(result.stdout)
                self.list_widget.takeItem(self.list_widget.row(selected_items[0]))  # Supprime de la liste
            if result.stderr:
                self.log_message(f"Erreur lors de la suppression de la bibliothèque : {result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression de la bibliothèque: {e}")
            self.log_message(f"Erreur lors de la suppression de la bibliothèque: {e}")

    def toggle_console(self):
        """Affiche ou masque la console."""
        if self.console_output.isVisible():
            # Masquer la console
            index = 1  # Index du widget console dans le splitter
            widget = self.splitter.widget(index)
            widget.hide()  # Masquer le widget
            
            # Changer le texte du bouton
            self.toggle_console_button.setText("Afficher Console")
            
        else:
            # Afficher la console
            index = 1  # Index du widget console dans le splitter
            widget = self.splitter.widget(index)
            widget.show()  # Afficher le widget
            
            # Changer le texte du bouton
            self.toggle_console_button.setText("Masquer Console")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LibraryManager()
    window.show()
    sys.exit(app.exec())
