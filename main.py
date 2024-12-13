import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt

class LibraryManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestionnaire de Bibliothèques Python")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("background-color: #2E2E2E; color: white;")

        self.layout = QVBoxLayout()
        
        self.label = QLabel("Bibliothèques Python Installées:")
        self.layout.addWidget(self.label)

        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Nom de la bibliothèque à ajouter")
        self.layout.addWidget(self.input_field)

        self.add_button = QPushButton("Ajouter Bibliothèque")
        self.add_button.clicked.connect(self.add_library)
        self.layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Supprimer Bibliothèque")
        self.remove_button.clicked.connect(self.remove_library)
        self.layout.addWidget(self.remove_button)

        self.setLayout(self.layout)
        
        self.load_libraries()

    def load_libraries(self):
        """Charge les bibliothèques installées et les affiche dans la liste."""
        try:
            result = subprocess.check_output([sys.executable, '-m', 'pip', 'list']).decode('utf-8')
            libraries = result.splitlines()[2:]  # Ignore les deux premières lignes
            for lib in libraries:
                name = lib.split()[0]
                self.list_widget.addItem(name)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des bibliothèques: {e}")

    def add_library(self):
        """Ajoute une bibliothèque via pip."""
        library_name = self.input_field.text().strip()
        if library_name:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', library_name])
                self.list_widget.addItem(library_name)
                self.input_field.clear()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout de la bibliothèque: {e}")
    
    def remove_library(self):
        """Supprime une bibliothèque via pip."""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner une bibliothèque à supprimer.")
            return
        
        library_name = selected_items[0].text()
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', '-y', library_name])
            self.list_widget.takeItem(self.list_widget.row(selected_items[0]))
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression de la bibliothèque: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LibraryManager()
    window.show()
    sys.exit(app.exec())
