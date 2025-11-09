import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image
from PIL.ExifTags import TAGS
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

# --- Configuration ---
WATCH_DIR = "" #insert directory to watch here
DEST_DIR = "" #insert directory to sort to

# This map can be customized, the format is as follows:
# "FOLDER_NAME": [".extension_type"]
FILE_TYPE_MAP = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".xlsx", ".md"],
    "Audio": [".mp3", ".wav", ".aac", ".flac"],
    "Video": [".mp4", ".mov", ".avi", ".mkv", ".webm"],
    "Archives": [".zip", ".rar", ".7z", ".gz"],
    "Code": [".py", ".js", ".html", ".css", ".json", ".xml"],
    "Programs and Installers": [".exe", ".msi"],
    "Jars": [".jar"],
    "Other": []
}
# ---------------------
class OrganizationHandler(FileSystemEventHandler):

    def process_file(self, file_path):
        """The main sorting logic, triggered by a new file."""
        time.sleep(1) 
        try:
            item_name = os.path.basename(file_path)
            file_name, file_extension = os.path.splitext(item_name)
            file_extension = file_extension.lower()
            if file_extension == ".tmp" or file_extension.startswith("~"):
                print(f"Skipping temp file: {item_name}")
                return
            dest_folder_name = "Other"
            for folder_name, extensions in FILE_TYPE_MAP.items():
                if file_extension in extensions:
                    dest_folder_name = folder_name
                    break
            dest_folder_path = os.path.join(DEST_DIR, dest_folder_name)
            if not os.path.exists(dest_folder_path):
                os.makedirs(dest_folder_path)
            final_dest_path = os.path.join(dest_folder_path, item_name)
            shutil.move(file_path, final_dest_path)
            print(f"Moved: {item_name}  ->  {dest_folder_name}")
            if dest_folder_name == "Images" and file_extension in [".jpg", ".jpeg"]:
                pass
            if dest_folder_name == "Audio" and file_extension == ".mp3":
                pass
        except FileNotFoundError:
            print(f"File not found, may have been processed: {item_name}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    def on_created(self, event):
        """Called by watchdog when a file is CREATED."""
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            self.process_file(event.src_path)

    def on_modified(self, event):
        """
        We process on 'modified' too, because many browsers create a.tmp file
        and then 'modify' it into the final.zip or.jpg file.
        """
        if not event.is_directory:
            if os.path.exists(event.src_path):
                print(f"File modified, checking: {event.src_path}")
                self.process_file(event.src_path)
if __name__ == "__main__":
    print(f"Starting file organizer to watch: {WATCH_DIR}")
    print(f"Files will be moved to: {DEST_DIR}")
    
    event_handler = OrganizationHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
        print("Observer stopped.")
    
    observer.join()
