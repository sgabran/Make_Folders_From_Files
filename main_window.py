import os
import os.path
from idlelib.tooltip import *
from tkinter import filedialog
from tkinter import messagebox

import sys
import shutil

import filename_methods as fm
import misc_methods as mm
from constants import *
from session_log import SessionLog
from user_entry import UserEntry


# Class to create GUI
class MainWindow:
    # Dependencies: MainWindow communicate with classes that are related to GUI contents and buttons
    def __init__(self):  # instantiation function. Use root for GUI and refers to main window

        root = Tk()
        root.title("Folder Maker")
        self.root_frame = root
        self.user_entry = UserEntry()
        self.session_log = SessionLog(self.user_entry)

        self.files = NONE

        # GUI Frames
        self.frame_root_title = Frame(root, highlightthickness=0)
        self.frame_root_session = LabelFrame(root, width=120, height=390, padx=5, pady=5, text="Session")

        # Disable resizing the window
        root.resizable(False, False)

        # Grids
        self.frame_root_title.grid(row=0, column=0, padx=10, pady=5, ipadx=5, ipady=5)
        self.frame_root_session.grid(row=1, column=0, sticky="W", padx=10, pady=(5, 5), ipadx=5, ipady=2)

        entry_validation_positive_numbers = root.register(mm.only_positive_numbers)
        entry_validation_numbers = root.register(mm.only_digits)
        entry_validation_numbers_space = root.register(mm.digits_or_space)
        entry_validation_positive_numbers_comma = root.register(mm.positive_numbers_or_comma)

        ######################################################################
        # Frame Session

        # Entries
        self.entry_files_location_entry = StringVar()
        self.entry_files_location_entry.trace("w", lambda name, index, mode, entry_files_location_entry=self.entry_files_location_entry: self.entry_update_files_location())
        self.entry_files_location = Entry(self.frame_root_session, width=80, textvariable=self.entry_files_location_entry)
        self.entry_files_location.insert(END, os.path.normcase(FOLDER_PATH))

        # Buttons
        self.button_files_location = Button(self.frame_root_session, text="Files Location", command=lambda: self.open_folder(), pady=0, width=10, fg='brown')
        self.button_start = Button(self.frame_root_session, text="Start", fg='green', command=self.start_process, pady=0, width=10)
        self.button_exit = Button(self.frame_root_session, text="Exit", fg='red', command=self.quit_program, pady=0, width=10)

        # Grids
        self.entry_files_location.grid       (row=1, column=1, sticky=W)
        self.button_files_location.grid     (row=1, column=0, sticky=NE)
        self.button_start.grid              (row=2, column=0, sticky=NE)
        self.button_exit.grid               (row=2, column=1, sticky=NW)

        # END OF FRAME #######################################################

        self.root_frame.mainloop()

    ######################################################################

    def setState(self, widget, state):
        print(type(widget))
        try:
            widget.configure(state=state)
        except:
            pass
        for child in widget.winfo_children():
            self.setState(child, state=state)

    def entry_update_files_location(self):
        files_location = self.entry_files_location_entry.get()
        if fm.FileNameMethods.check_file_location_valid(files_location):
            self.user_entry.files_location = files_location
        else:
            self.user_entry.files_location = FOLDER_PATH
        print("::user_entry.files_location: ", self.user_entry.files_location)

    @staticmethod
    def quit_program():
        # quit()  # quit() does not work with pyinstaller, use sys.exit()
        sys.exit()

    def start_process(self):
        self.scan_files_in_folder(self.user_entry.folder_path)
        self.create_folders_and_move_files(self.files, self.user_entry.folder_path)

    def scan_files_in_folder(self, folder_path):
        # Check if folder path exists
        if os.path.exists(folder_path):
            # Get a list of files in the folder
            self.files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            print("Files in folder:")
            for file in self.files:
                print(file)
            return self.files
        else:
            print("Folder path does not exist.")

    def create_folders_and_move_files(self, filenames, destination_folder):
        # Check if the destination folder exists
        if not os.path.exists(destination_folder):
            print("Destination folder does not exist.")
            return

        for filename in filenames:
            # Create a folder using the filename in the destination folder
            folder_name = os.path.splitext(filename)[0]
            folder_path = os.path.join(destination_folder, folder_name)

            # Create the folder
            try:
                os.makedirs(folder_path)
                print(f"Folder created: {folder_path}")
            except FileExistsError:
                print(f"Folder already exists: {folder_path}")

            # Move the file to the created folder
            file_path = os.path.join(destination_folder, filename)
            new_file_path = os.path.join(folder_path, filename)
            try:
                shutil.move(file_path, new_file_path)
                print(f"File moved: {filename} -> {new_file_path}")
            except FileNotFoundError:
                print(f"File not found: {filename}")
            except shutil.Error:
                print(f"File already exists in the folder: {filename}")

    ######################################################################

    ######################################################################
    def open_folder(self):
        self.user_entry.folder_path = filedialog.askdirectory(initialdir=FOLDER_PATH)
        if self.user_entry.folder_path:
            # Open the folder in the default file explorer
            os.startfile(self.user_entry.folder_path)
            print("Folder opened successfully!")
        else:
            print("No folder selected.")

        # temp_path = os.path.realpath(folder_path)
        # try:
        #     os.startfile(temp_path)
        # except:
        #     try:
        #         os.mkdir(FILES_LOCATION)
        #         self.user_entry.files_location = FILES_LOCATION
        #         self.session_log.write_textbox("Folder Created", "blue")
        #         print("Folder Created")
        #     except OSError as e:
        #         print("Failed to Create Folder")
        #         e = Exception("Failed to Create Folder")
        #         self.session_log.write_textbox(str(e), "red")
        #         raise e

    ######################################################################

    @staticmethod
    def message_box(title, data):
        try:
            messagebox.showinfo(title=title, message=data)
        except:
            data = 'Invalid data'

    def display_session_settings(self):
        message = 'File To Process: ' + fm.FileNameMethods.build_file_name_full(
            self.user_entry.files_location, self.user_entry.file_name, self.user_entry.file_suffix) + '\n'
        colour = "blue"
        self.session_log.write_textbox(message, colour)

        message = 'Extract Timestamp: ' + ('yes' if self.user_entry.timestamp_extract == 1 else 'no') + '\n'
        self.session_log.write_textbox(message, colour)

        message = ' Header at Row: ' + str(self.user_entry.header_row_index) + '\n'
        self.session_log.write_textbox(message, colour)

        message = 'Data Start at Row: ' + str(self.user_entry.data_start_row_index) + '\n'
        self.session_log.write_textbox(message, colour)

        message = 'Data Length Requested: ' + str(self.user_entry.data_length_requested) + '\n'
        self.session_log.write_textbox(message, colour)

        message = 'Include Header in Plot: ' + str(self.user_entry.header_include_plots) + '\n'
        self.session_log.write_textbox(message, colour)
