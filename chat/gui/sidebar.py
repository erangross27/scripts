from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QMenu
from PyQt5.QtCore import Qt

class Sidebar(QListWidget):
    def __init__(self, conversation_manager):
        super().__init__()
        self.conversation_manager = conversation_manager
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.update_conversations()

    def update_conversations(self):
        self.clear()
        conversations = self.conversation_manager.load_conversations()
        for conv_id, title in conversations:
            item = QListWidgetItem(title)
            item.setData(Qt.UserRole, conv_id)
            self.addItem(item)

    def show_context_menu(self, position):
        item = self.itemAt(position)
        if item:
            menu = QMenu()
            rename_action = menu.addAction("Rename")
            delete_action = menu.addAction("Delete")
            action = menu.exec_(self.mapToGlobal(position))
            if action == rename_action:
                self.rename_conversation(item)
            elif action == delete_action:
                self.delete_conversation(item)

    def rename_conversation(self, item):
        # Implement rename functionality
        pass

    def delete_conversation(self, item):
        # Implement delete functionality
        pass