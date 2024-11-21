import sys
import psutil
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QComboBox, QMessageBox)
from PyQt5.QtCore import Qt
import subprocess

class DiskPartitioner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Disk Partition Manager")
        self.setMinimumSize(600, 400)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create disk selection dropdown
        disk_layout = QHBoxLayout()
        disk_label = QLabel("Select Disk:")
        self.disk_combo = QComboBox()
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_disks)
        
        disk_layout.addWidget(disk_label)
        disk_layout.addWidget(self.disk_combo)
        disk_layout.addWidget(self.refresh_button)
        layout.addLayout(disk_layout)

        # Create partition list layout
        self.partition_layout = QVBoxLayout()
        layout.addLayout(self.partition_layout)

        # Add warning label
        warning_label = QLabel("WARNING: Deleting partitions can result in data loss!\nUse at your own risk!")
        warning_label.setStyleSheet("color: red; font-weight: bold;")
        warning_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(warning_label)

        # Initialize
        self.refresh_disks()
        self.disk_combo.currentIndexChanged.connect(self.show_partitions)

    def refresh_disks(self):
        """Refresh the list of available disks"""
        self.disk_combo.clear()
        for disk in psutil.disk_partitions():
            self.disk_combo.addItem(f"{disk.device} ({disk.mountpoint})")
        self.show_partitions()

    def show_partitions(self):
        """Show partitions for selected disk"""
        # Clear existing partition widgets
        for i in reversed(range(self.partition_layout.count())): 
            self.partition_layout.itemAt(i).widget().setParent(None)

        if self.disk_combo.currentText():
            # Get disk name from combo box
            disk = self.disk_combo.currentText().split()[0]
            
            # Use diskpart to list partitions
            cmd = f'echo list partition | diskpart'
            try:
                output = subprocess.check_output(cmd, shell=True).decode()
                
                # Parse and display partitions
                for line in output.split('\n'):
                    if 'Partition' in line and not 'Volume' in line:
                        partition = QWidget()
                        part_layout = QHBoxLayout(partition)
                        
                        info_label = QLabel(line.strip())
                        delete_btn = QPushButton("Delete")
                        delete_btn.setStyleSheet("background-color: #ff4444;")
                        delete_btn.clicked.connect(lambda x, l=line: self.delete_partition(l))
                        
                        part_layout.addWidget(info_label)
                        part_layout.addWidget(delete_btn)
                        self.partition_layout.addWidget(partition)

            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "Error", f"Failed to get partition info: {str(e)}")

    def delete_partition(self, partition_info):
        """Delete selected partition"""
        reply = QMessageBox.question(self, 'Confirm Delete',
            f"Are you sure you want to delete this partition?\n{partition_info}",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Parse partition number from info
            try:
                partition_num = int(partition_info.split()[1])
                disk_num = int(self.disk_combo.currentText().split()[0].strip(':'))
                
                # Create diskpart script
                script = f"""select disk {disk_num}
select partition {partition_num}
delete partition override"""

                # Execute diskpart script
                try:
                    with open('delete_script.txt', 'w') as f:
                        f.write(script)
                    
                    subprocess.run(['diskpart', '/s', 'delete_script.txt'], 
                                 check=True, capture_output=True)
                    
                    QMessageBox.information(self, "Success", "Partition deleted successfully!")
                    self.refresh_disks()
                    
                except subprocess.CalledProcessError as e:
                    QMessageBox.critical(self, "Error", 
                        f"Failed to delete partition: {e.stderr.decode()}")
                
            except (ValueError, IndexError):
                QMessageBox.critical(self, "Error", "Failed to parse partition information")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DiskPartitioner()
    window.show()
    sys.exit(app.exec_())