import sys
import os
import io
import re
import math
import time
import base64
from datetime import datetime

# PyQt imports
from PyQt5.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QPushButton,
    QTextEdit, 
    QVBoxLayout, 
    QHBoxLayout,
    QWidget, 
    QFileDialog, 
    QLabel, 
    QProgressBar,
    QMessageBox, 
    QFrame, 
    QPlainTextEdit,
    QDialog,  # Add this import
)
from PyQt5.QtCore import (
    Qt, 
    QThread, 
    pyqtSignal, 
    QPoint
)
from PyQt5.QtGui import (
    QTextCursor, 
    QTextBlockFormat, 
    QTextOption, 
    QFont, 
    QPalette, 
    QColor
)

# Audio processing
from pydub import AudioSegment

# OpenAI
from openai import OpenAI

def get_embedded_api_key():
    # This function will run when creating the executable to embed your key
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        encoded_key = "ENCODED_KEY_PLACEHOLDER"  # This will be replaced during build
        return base64.b64decode(encoded_key).decode()
    else:
        # Running in development - get from environment
        return os.environ.get('OPENAI_API_KEY')

from pydub import AudioSegment
import io
import math
import re
import time
import os
from PyQt5.QtCore import QThread, pyqtSignal


class ProofreadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("הצעות הגהה")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        self.suggestions_text = QPlainTextEdit()
        self.suggestions_text.setReadOnly(True)
        self.suggestions_text.setLayoutDirection(Qt.RightToLeft)
        self.suggestions_text.document().setDefaultTextOption(QTextOption(Qt.AlignRight))
        
        layout.addWidget(QLabel("הערות והצעות לתיקון:"))
        layout.addWidget(self.suggestions_text)
        
        close_button = QPushButton("סגור")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

class ProofreadingWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, text, client):
        super().__init__()
        self.text = text
        self.client = client

    def run(self):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """
                    אתה עורך לשוני מקצועי. תפקידך:
                    1. לתקן שגיאות כתיב
                    2. לתקן ניסוח במידת הצורך
                    3. להוסיף סימני פיסוק חסרים
                    4. להחזיר את הטקסט המתוקן בלבד, ללא הערות או הסברים
                    5. לשמור על המשמעות המקורית של הטקסט
                    """},
                    {"role": "user", "content": f"ערוך ותקן את הטקסט הבא:\n{self.text}"}
                ]
            )
            self.finished.emit(response.choices[0].message.content)
        except Exception as e:
            self.error.emit(str(e))


class TranscriptionWorker(QThread):
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        api_key = get_embedded_api_key()
        self.client = OpenAI(api_key=api_key)

    def format_transcript(self, text):
        text = re.sub(r'([.!?])\s+', r'\1\n\n', text)
        text = re.sub(r',\s+(?=[^,]{40,})', ',\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def split_audio(self, audio_segment, max_size_mb=24):
        chunks = []
        chunk_size_ms = len(audio_segment)
        
        # Calculate initial chunk size (try to split into roughly equal parts)
        file_size_mb = (len(audio_segment.raw_data) / (1024 * 1024))
        num_chunks = math.ceil(file_size_mb / max_size_mb)
        chunk_duration = math.floor(len(audio_segment) / num_chunks)

        # Create chunks
        for i in range(0, len(audio_segment), chunk_duration):
            chunk = audio_segment[i:i + chunk_duration]
            
            # Convert to mp3 in memory with reduced quality to ensure size limit
            buffer = io.BytesIO()
            chunk.export(buffer, format='mp3', parameters=['-q:a', '9'])
            
            # Verify chunk size
            buffer.seek(0, io.SEEK_END)
            chunk_size_mb = buffer.tell() / (1024 * 1024)
            
            # If chunk is still too large, reduce quality further
            if chunk_size_mb > max_size_mb:
                buffer = io.BytesIO()
                chunk = chunk.set_frame_rate(16000).set_channels(1)
                chunk.export(buffer, format='mp3', parameters=['-q:a', '9'])
            
            buffer.seek(0)
            chunks.append(buffer)

        return chunks

    def run(self):
        try:
            self.progress.emit("טוען את קובץ האודיו...", 10)
            
            # Load and convert the audio file
            audio = AudioSegment.from_file(self.file_path)
            audio = audio.set_channels(1).set_frame_rate(22050)  # Convert to mono and set sample rate
            
            # Export to buffer in supported format
            buffer = io.BytesIO()
            audio.export(buffer, format='mp3', parameters=['-ac', '1'])  # Ensure mono audio
            buffer.seek(0)
            
            # Check file size
            buffer.seek(0, io.SEEK_END)
            file_size_mb = buffer.tell() / (1024 * 1024)
            buffer.seek(0)

            if file_size_mb <= 25:
                # Process single file
                self.progress.emit("מעבד את הקובץ...", 30)
                
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=("audio.mp3", buffer),  # Provide filename hint
                    response_format="text",
                    language="he"
                )
                formatted_transcript = self.format_transcript(transcript)
            
            else:
                # Split and process multiple chunks
                self.progress.emit("מפצל את הקובץ...", 20)
                chunks = self.split_audio(audio)
                total_chunks = len(chunks)
                
                all_transcripts = []
                for i, chunk in enumerate(chunks, 1):
                    progress = int(30 + (i / total_chunks * 50))
                    self.progress.emit(f"מעבד חלק {i} מתוך {total_chunks}...", progress)
                    
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=("chunk.mp3", chunk),  # Provide filename hint
                        response_format="text",
                        language="he"
                    )
                    all_transcripts.append(transcript)
                    chunk.close()
                
                self.progress.emit("מחבר את כל החלקים...", 90)
                combined_transcript = " ".join(all_transcripts)
                formatted_transcript = self.format_transcript(combined_transcript)

            self.progress.emit("הושלם!", 100)
            self.finished.emit(formatted_transcript)

        except Exception as e:
            self.error.emit(str(e))

class TranscriptionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.init_ui()
        self.current_transcript = None
        self.oldPos = None
   
    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def copy_text(self):
        if self.current_transcript:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.text_area.toPlainText())
            self.status_label.setText("סטטוס: הטקסט הועתק ללוח")

    def init_ui(self):
        self.setMinimumSize(800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(10, 0, 10, 10)

        # Custom title bar
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(10, 10, 10, 10)

        # Window controls (left side)
        window_controls = QWidget()
        controls_layout = QHBoxLayout(window_controls)
        controls_layout.setSpacing(5)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        # Close button
        close_button = QPushButton("×")
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #ff0000;
                color: white;
            }
        """)

        # Maximize button
        maximize_button = QPushButton("□")
        maximize_button.setFixedSize(30, 30)
        maximize_button.clicked.connect(self.toggle_maximize)
        maximize_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)

        # Minimize button
        minimize_button = QPushButton("−")
        minimize_button.setFixedSize(30, 30)
        minimize_button.clicked.connect(self.showMinimized)
        minimize_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)

        controls_layout.addWidget(minimize_button)
        controls_layout.addWidget(maximize_button)
        controls_layout.addWidget(close_button)

        # Window title (right side)
        title_label = QLabel("כלי תמלול אודיו")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        # Add components to title layout
        title_layout.addWidget(window_controls, 0, Qt.AlignLeft)
        title_layout.addStretch(1)
        title_layout.addWidget(title_label, 0, Qt.AlignRight)
        layout.addWidget(title_container)

        # File selection area - right aligned container
        file_container = QWidget()
        file_layout = QHBoxLayout(file_container)
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_layout.setSpacing(10)

        self.browse_button = QPushButton(" בחר קובץ אודיו/וידאו")
        self.browse_button.clicked.connect(self.browse_file)
        self.browse_button.setFixedWidth(150)

        self.file_label = QLabel("לא נבחר קובץ")
        self.file_label.setAlignment(Qt.AlignRight)

        file_layout.addStretch(1)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.browse_button)
        layout.addWidget(file_container)

        # Status label
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        
        self.status_label = QLabel("סטטוס: מוכן")
        self.status_label.setAlignment(Qt.AlignRight)
        status_layout.addStretch(1)
        status_layout.addWidget(self.status_label)
        layout.addWidget(status_container)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Buttons container
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)

        self.save_button = QPushButton("שמור קובץ")
        self.save_button.clicked.connect(self.save_transcript)
        self.save_button.setEnabled(False)
        self.save_button.setFixedWidth(100)

        self.copy_button = QPushButton("העתק טקסט")
        self.copy_button.clicked.connect(self.copy_text)
        self.copy_button.setEnabled(False)
        self.copy_button.setFixedWidth(100)

        self.proofread_button = QPushButton("הגהה")
        self.proofread_button.clicked.connect(self.start_proofreading)
        self.proofread_button.setEnabled(False)
        self.proofread_button.setFixedWidth(100)

        self.transcribe_button = QPushButton("תמלל")
        self.transcribe_button.clicked.connect(self.start_transcription)
        self.transcribe_button.setEnabled(False)
        self.transcribe_button.setFixedWidth(100)
        buttons_layout.addWidget(self.proofread_button)  


        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.copy_button)
        buttons_layout.addWidget(self.proofread_button)
        buttons_layout.addWidget(self.transcribe_button)
        layout.addWidget(buttons_container)

        # Text area
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)

        self.text_area = QPlainTextEdit()
        self.text_area.setLayoutDirection(Qt.RightToLeft)
        self.text_area.setReadOnly(True)
        self.text_area.document().setDefaultTextOption(QTextOption(Qt.AlignRight))
        
        font = QFont('David', 16)
        self.text_area.setFont(font)
        
        self.text_area.setStyleSheet("""
            QPlainTextEdit {
                padding: 10px;
                font-size: 16px;
                line-height: 1.8;
                font-family: 'David', 'Arial Hebrew', 'Noto Sans Hebrew', sans-serif;
            }
        """)

        text_layout.addWidget(self.text_area)
        layout.addWidget(text_container)
        
        # Save status
        self.save_status = QLabel("")
        self.save_status.setAlignment(Qt.AlignRight)
        layout.addWidget(self.save_status)

        # Make window draggable
        title_container.mousePressEvent = self.mousePressEvent
        title_container.mouseMoveEvent = self.mouseMoveEvent

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.oldPos:
            delta = event.globalPos() - self.oldPos
            self.move(self.pos() + delta)
            self.oldPos = event.globalPos()

    def update_status(self, text):
        self.status_label.setText(f"סטטוס: {text}")
        self.status_label.setAlignment(Qt.AlignRight)

    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "בחר קובץ אודיו",
            "",
            "Audio/Video Files (*.mp3 *.m4a *.wav *.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm)"
        )
        if file_name:
            self.selected_file = file_name
            self.file_label.setText(os.path.basename(file_name))
            self.transcribe_button.setEnabled(True)
            self.update_status("נבחר קובץ")
            self.progress_bar.setValue(0)
            self.save_status.clear()
            self.save_button.setEnabled(False)
            self.copy_button.setEnabled(False)
            self.proofread_button.setEnabled(False)

    def start_transcription(self):
        if not hasattr(self, 'selected_file') or not self.selected_file:
            return

        self.transcribe_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.copy_button.setEnabled(False)
        self.proofread_button.setEnabled(False)
        self.text_area.clear()
        self.progress_bar.setValue(0)
        
        self.worker = TranscriptionWorker(self.selected_file)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.transcription_complete)
        self.worker.error.connect(self.transcription_error)
        self.worker.start()

    def start_proofreading(self):
        if not self.current_transcript:
            return
            
        self.proofread_button.setEnabled(False)
        self.update_status("מבצע הגהה...")
        
        self.proofreading_worker = ProofreadingWorker(self.current_transcript, self.worker.client)
        self.proofreading_worker.finished.connect(self.proofreading_complete)
        self.proofreading_worker.error.connect(self.proofreading_error)
        self.proofreading_worker.start()

    def proofreading_complete(self, corrected_text):
        self.proofread_button.setEnabled(True)
        self.update_status("הגהה הושלמה")
        
        # Update the text area with the corrected text
        self.current_transcript = corrected_text
        self.text_area.clear()
        self.text_area.document().setDefaultTextOption(QTextOption(Qt.AlignRight))
        self.text_area.setPlainText(corrected_text)
        
        # Move cursor to start
        cursor = self.text_area.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self.text_area.setTextCursor(cursor)
        
        QMessageBox.information(self, "הצלחה", "ההגהה הושלמה!\nהטקסט המתוקן מוצג בחלון")

    def proofreading_error(self, error_message):
        self.proofread_button.setEnabled(True)
        self.update_status("שגיאה בהגהה")
        QMessageBox.critical(self, "שגיאה", f"אירעה שגיאה בתהליך ההגהה:\n{error_message}")

    def update_progress(self, status, value):
        self.status_label.setText(f"סטטוס: {status}")
        self.progress_bar.setValue(value)

    def transcription_complete(self, transcript):
        self.current_transcript = transcript
        self.transcribe_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.copy_button.setEnabled(True)
        self.proofread_button.setEnabled(True)
        
        self.text_area.clear()
        self.text_area.document().setDefaultTextOption(QTextOption(Qt.AlignRight))
        
        self.text_area.setPlainText(transcript)
        
        cursor = self.text_area.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self.text_area.setTextCursor(cursor)
        
        self.status_label.setText("סטטוס: התמלול הושלם")
        QMessageBox.information(self, "הצלחה", "התמלול הושלם!\nלחץ על כפתור השמירה כדי לשמור את הקובץ.")    

    def save_transcript(self):
        if not self.current_transcript:
            return
            
        default_name = f"תמלול_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "שמירת תמלול",
            default_name,
            "Text Files (*.txt)"
        )
        
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    rtl_mark = '\u202B'  # RTL mark
                    text = self.text_area.toPlainText()
                    formatted_text = text.replace('\n', '\n' + rtl_mark)
                    f.write(f'{rtl_mark}{formatted_text}')
                    
                self.save_status.setText(f"נשמר בהצלחה: {file_name}")
                QMessageBox.information(self, "הצלחה", f"הקובץ נשמר בהצלחה:\n{file_name}")
            except Exception as e:
                QMessageBox.critical(self, "שגיאה", f"שגיאה בשמירת הקובץ:\n{str(e)}")

    def transcription_error(self, error_message):
        self.transcribe_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.copy_button.setEnabled(False)
        self.proofread_button.setEnabled(False)
        
        self.status_label.setText("סטטוס: אירעה שגיאה")
        QMessageBox.critical(self, "שגיאה", f"אירעה שגיאה:\n{error_message}")
        self.progress_bar.setValue(0)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = TranscriptionApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()