import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QMessageBox, QSplitter, QListWidgetItem, QHBoxLayout, QTextEdit, QInputDialog, QProgressDialog
)
from PyQt6.QtCore import Qt

class LibraryManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestionnaire de Bibliothèques Python")
        self.setGeometry(100, 100, 600, 400)
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
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet("background-color: black; color: white; font-family: monospace;")
        self.splitter.addWidget(QWidget()) 
        self.splitter.addWidget(self.console_output)
        self.layout.addLayout(self.library_layout)
        self.toggle_console_button = QPushButton("Afficher/Masquer Console")
        self.style_button(self.toggle_console_button)
        self.toggle_console_button.clicked.connect(self.toggle_console)
        self.layout.addWidget(self.toggle_console_button)
        self.layout.addWidget(self.splitter)
        self.setLayout(self.layout)
        self.load_libraries()

    def style_button(self, button):
        """Applique un style aux boutons."""
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
                background-color: #666666; /* Couleur grise pour le bouton désactivé */
                color: #999999; /* Couleur du texte grisé */
            }
            """)

    def log_message(self, message):
        if message:
            self.console_output.append(message)

    def load_libraries(self):
        command = [sys.executable, '-m', 'pip', 'list']
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.stdout:
                libraries = result.stdout.splitlines()[2:]
                for lib in libraries:
                    name = lib.split()[0]
                    item = QListWidgetItem(name)
                    item.setData(Qt.ItemDataRole.UserRole, name)  # Stocke le nom de la bibliothèque
                    self.list_widget.addItem(item)
                self.log_message("Bibliothèques chargées avec succès.")
            if result.stderr:
                self.log_message(f"Erreur lors du chargement des bibliothèques : {result.stderr}")
                
            # Connecter le signal de sélection pour activer/désactiver le bouton supprimer
            self.list_widget.itemSelectionChanged.connect(self.update_remove_button_state)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des bibliothèques: {e}")
            self.log_message(f"Erreur lors du chargement des bibliothèques: {e}")

    def update_remove_button_state(self):
        """Met à jour l'état du bouton de suppression en fonction de la sélection."""
        selected_items = self.list_widget.selectedItems()
        
        if selected_items:
            self.remove_button.setEnabled(True) 
            self.style_button(self.remove_button)
        else:
            self.remove_button.setEnabled(False) 
            self.style_button(self.remove_button) 

    def prompt_add_library(self):
        library_name, ok = QInputDialog.getText(self, "Ajouter une bibliothèque", "Nom de la bibliothèque:")
        
        if ok and library_name.strip():
            self.install_library(library_name.strip())

    def install_library(self, library_name):
        command = [sys.executable, '-m', 'pip', 'install', library_name]
        
        progress_dialog = QProgressDialog("Installation en cours...", "Annuler", 0, 0, self)
        
        try:
            progress_dialog.show()
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            progress_dialog.close()
            
            if result.stdout:
                self.log_message(result.stdout)
                item = QListWidgetItem(library_name)
                item.setData(Qt.ItemDataRole.UserRole, library_name)  
                self.list_widget.addItem(item)  
                
            if result.stderr:
                QMessageBox.warning(self, "Erreur", f"Erreur lors de l'ajout de la bibliothèque : {result.stderr}")
                
            QMessageBox.information(self, "Succès", f"La bibliothèque '{library_name}' a été installée avec succès.")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout de la bibliothèque: {e}")
            self.log_message(f"Erreur lors de l'ajout de la bibliothèque: {e}")

    def remove_library(self):
        selected_items = self.list_widget.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner une bibliothèque à supprimer.")
            return
        
        library_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        command = [sys.executable, '-m', 'pip', 'uninstall', '-y', library_name]
        
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if result.stdout:
                self.log_message(result.stdout)
                row_index = self.list_widget.row(selected_items[0])
                self.list_widget.takeItem(row_index)  
                
            if result.stderr:
                QMessageBox.warning(self, "Erreur", f"Erreur lors de la suppression de la bibliothèque : {result.stderr}")
                
            QMessageBox.information(self, "Succès", f"La bibliothèque '{library_name}' a été supprimée avec succès.")
            
            self.update_remove_button_state()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression de la bibliothèque: {e}")
            self.log_message(f"Erreur lors de la suppression de la bibliothèque: {e}")

    def toggle_console(self):
        """Affiche ou masque la console."""
        
        if self.console_output.isVisible():
            index = 1  
            widget = self.splitter.widget(index)
            widget.hide()  
            self.toggle_console_button.setText("Afficher Console")
            
        else:
            index = 1  
            widget = self.splitter.widget(index)
            widget.show()  
            self.toggle_console_button.setText("Masquer Console")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LibraryManager()
    window.show()
    sys.exit(app.exec())