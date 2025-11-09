# Auto-Sorter: A Real-Time File Organizer

## Overview

This is a Python script that automatically organizes a folder (like your "Downloads" folder) in real-time. It watches for new files and instantly moves them into designated subfolders (like "Images," "Documents," "Video," etc.) based on their file type.

It is designed to run in a terminal and will actively monitor the target folder until you stop it.

## Features

  * **Real-Time Monitoring:** Uses the `watchdog` library to monitor a folder for new files the moment they are created or modified.
  * **Customizable Sorting:** Uses a simple dictionary (`FILE_TYPE_MAP`) to let you define exactly which file extensions go into which folders.
  * **Smart Download Handling:** Watches for both `on_created` and `on_modified` events. This is essential for handling downloads from web browsers, which often create a temporary file (e.g., `.tmp` or `.crdownload`) and then rename/modify it to the final file (e.g., `.jpg` or `.exe`).
  * **Ignores Temp Files:** Automatically skips common temporary files to prevent errors.

## Requirements

This script requires Python 3 and a few third-party libraries.

  * **watchdog:** The core library for monitoring file system events.
  * **Pillow (PIL):** Used for reading image metadata (EXIF data).
  * **mutagen:** Used for reading audio file metadata (ID3 tags).

## Installation & Setup

1.  **Install Libraries:**
    Before running the script, you must install the required libraries using pip:

    ```bash
    pip install watchdog pillow mutagen
    ```

2.  **Configure the Script:**
    Open the Python script (`.py` file) in a text editor and **set the two main variables** at the top:

      * **`WATCH_DIR`**: The full path to the folder you want to monitor.
        *Example:* `WATCH_DIR = "C:/Users/YourUser/Downloads"`

      * **`DEST_DIR`**: The full path to the "master" folder where you want your sorted subfolders to be created.
        *Example:* `DEST_DIR = "C:/Users/YourUser/Documents/OrganizedFiles"`

    ***Note:*** *Use forward slashes (`/`) for paths, even on Windows, to avoid errors.*

3.  **Customize `FILE_TYPE_MAP` (Optional):**
    You can add, remove, or change any of the folders and file extensions in the `FILE_TYPE_MAP` dictionary to fit your needs.

## How to Run

1.  Open your terminal or command prompt.
2.  Navigate to the directory where you saved this script:
    ```bash
    cd path/to/your/script
    ```
3.  Run the script using Python:
    ```bash
    python your_script_name.py
    ```
4.  The script will start and print:
    ```
    Starting file organizer to watch: C:/Users/YourUser/Downloads
    Files will be moved to: C:/Users/YourUser/Documents/OrganizedFiles
    ```
5.  The script is now running. You can minimize this window. It will continue to watch for files.
6.  To **stop the script**, go back to the terminal window and press **`Ctrl+C`**.

-----

## How It Works: A Technical Breakdown

This script is built on two main components: the **Observer** and the **Event Handler**.

### 1\. The Observer (The "Lookout")

The code in the `if __name__ == "__main__":` block is the part that starts the program.

  * `observer = Observer()`: We create an `Observer` object. This object's job is to watch a folder.
  * `event_handler = OrganizationHandler()`: We create an instance of our custom `OrganizationHandler` class (see below). This class contains the *logic* for what to do when a file is found.
  * `observer.schedule(...)`: This line tells the observer: "Watch the `WATCH_DIR` folder, and when you see *anything*, tell the `event_handler`."
  * `observer.start()`: This starts the observer in a new background thread, so it can watch the folder without freezing the rest of the script.
  * `while True: time.sleep(10)`: This loop keeps the main script alive. Without it, the script would finish, and the background observer thread would be terminated.
  * `except KeyboardInterrupt:`: This is a clean way to shut down. When you press `Ctrl+C`, it catches the interruption, tells the `observer` to stop, and exits gracefully.

### 2\. The Event Handler (The "Brain")

The `OrganizationHandler` class is the "brain" of the operation. It inherits from `FileSystemEventHandler` and defines what to do when the `Observer` reports an event.

  * `on_created(self, event)`: This function is automatically called by the `Observer` when a new file or folder is *created*. It checks if the event is a file (and not a directory) and then calls `self.process_file`.
  * `on_modified(self, event)`: This function is called when a file is *changed*. This is critical for web browser downloads. A browser might first create `my_file.tmp` (triggers `on_created`, which we skip) and then, once the download is complete, rename it to `my_file.jpg` (triggers `on_modified`). This handler ensures we catch the *final* file.
  * `process_file(self, file_path)`: This is where all the sorting logic happens.
    1.  **Wait:** `time.sleep(1)` pauses for one second. This is a safety measure to prevent errors by giving the system time to finish writing and "unlock" the file.
    2.  **Get Info:** It gets the file's name and extension (e.g., `.jpg`).
    3.  **Triage:** It checks for temporary files (`.tmp` or `~`) and skips them.
    4.  **Find Destination:** It loops through `FILE_TYPE_MAP`. If it finds `.jpg` in the "Images" list, it sets `dest_folder_name = "Images"`. If it finds no match, it defaults to `"Other"`.
    5.  **Create Folder:** It checks if the destination (e.g., `C:/Users/YourUser/Documents/OrganizedFiles/Images`) exists. If not, it creates it using `os.makedirs()`.
    6.  **Move File:** It uses `shutil.move()` to move the file from the `WATCH_DIR` to the final sorted folder.

### 3\. Future Enhancements (The `pass` Statements)

You'll notice two `pass` statements under the "Images" and "Audio" checks. These are placeholders for "deep sorting."

The script already imports the `Pillow` and `mutagen` libraries. You can expand this script by replacing `pass` with code to:

  * **For Images:** Use `Pillow` to open the `final_dest_path`, read its EXIF metadata, find the "Date Taken," and move it to a subfolder like `.../Images/2024/10-October`.
  * **For Audio:** Use `mutagen` to open the `final_dest_path`, read its ID3 tags, find the "Artist" and "Album," and move it to a subfolder like `.../Audio/Artist Name/Album Name`.
