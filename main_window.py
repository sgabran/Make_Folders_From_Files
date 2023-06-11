import os
import os.path
from idlelib.tooltip import *
from tkinter import filedialog

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

        self.files_to_process = NONE
        self.n_files_to_process = 0
        self.n_files_moved = 0
        self.n_folders_created = 0

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
        self.entry_files_location_entry.trace("w", lambda name, index, mode,
                                                          entry_files_location_entry=self.entry_files_location_entry: self.entry_update_files_location())
        self.entry_files_location = Entry(self.frame_root_session, width=80,
                                          textvariable=self.entry_files_location_entry)
        self.entry_files_location.insert(END, os.path.normcase(FOLDER_PATH))

        # Buttons
        self.button_files_location = Button(self.frame_root_session, text="Files Location",
                                            command=lambda: self.choose_folder(), pady=0, width=10, fg='brown')
        self.button_start = Button(self.frame_root_session, text="Start", fg='green', command=self.start_process,
                                   pady=0, width=10)
        self.button_exit = Button(self.frame_root_session, text="Exit", fg='red', command=self.quit_program, pady=0,
                                  width=10)
        self.button_open_folder = Button(self.frame_root_session, text="Open Folder",
                                         command=lambda: self.open_folder(),
                                         pady=0, width=10)
        # Grids
        self.entry_files_location.grid(row=1, column=1, sticky=W, padx=(5, 0))
        self.button_files_location.grid(row=1, column=0, sticky=NE)
        self.button_start.grid(row=2, column=0, sticky=NE)
        self.button_open_folder.grid(row=2, column=1, sticky=NW)
        self.button_exit.grid(row=2, column=1, sticky=NW, padx=(80, 0))

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

    @staticmethod
    def quit_program():
        # quit()  # quit() does not work with pyinstaller, use sys.exit()
        sys.exit()

    def start_process(self):
        self.n_files_to_process = 0
        self.n_files_moved = 0
        self.n_folders_created = 0

        # Scan Folder
        result = self.scan_files_in_folder(self.user_entry.folder_path)

        # No Files
        if result == 0:
            message = "No Files to Process: " + str(self.n_files_to_process) + '\n'
            colour = 'red'
            self.session_log.write_textbox(message, colour)
            return

        # No Folder
        elif result == -1:
            message = "Folder path does not exist .. Process will terminate" + '\n'
            colour = 'brown'
            self.session_log.write_textbox(message, colour)
            print(message)
            return

        # Files Detected
        else:
            self.create_folders_and_move_files(self.files_to_process, self.user_entry.folder_path)

            if self.n_files_to_process == self.n_folders_created == self.n_files_moved:
                message = "Number of Folders Created: " + str(self.n_folders_created) + '\n'
                colour = 'green'
                self.session_log.write_textbox(message, colour)
                message = "Number of Files Moved: " + str(self.n_files_moved) + '\n'
                colour = 'green'
                self.session_log.write_textbox(message, colour)
            else:
                message = "WARNING: MISMATCH" + '\n'
                colour = 'red'
                self.session_log.write_textbox(message, colour)
                message = "Number of Folders Created: " + str(self.n_folders_created) + '\n'
                colour = 'red'
                self.session_log.write_textbox(message, colour)
                message = "Number of Files Moved: " + str(self.n_files_moved) + '\n'
                colour = 'red'
                self.session_log.write_textbox(message, colour)

    def scan_files_in_folder(self, folder_path):
        message = "Scanning Folder" + '\n'
        colour = "black"
        self.session_log.write_textbox(message, colour)

        # Check if folder path exists
        if os.path.exists(folder_path):
            # Get a list of files in the folder
            self.files_to_process = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            self.n_files_to_process = len(self.files_to_process)

            if self.n_files_to_process < 1:
                return 0

            else:
                message = "Number of Files to Process: " + str(self.n_files_to_process) + '\n'
                colour = 'blue'
                self.session_log.write_textbox(message, colour)

            message = 'Files List:' + '\n'
            colour = 'black'
            self.session_log.write_textbox(message, colour)

            return 1

        else:
            return -1

    def create_folders_and_move_files(self, filenames_list, destination_folder):
        # Check if the destination folder exists
        if not os.path.exists(destination_folder):
            message = "Folder path does not exist .. Process will terminate" + '\n'
            colour = 'brown'
            self.session_log.write_textbox(message, colour)
            print(message)
            return -1

        for filename in filenames_list:
            # Create a folder using the filename in the destination folder
            folder_name = os.path.splitext(filename)[0]
            folder_path = os.path.join(destination_folder, folder_name)

            # Create the folder
            try:
                os.makedirs(folder_path)
                self.n_folders_created += 1
                print(f"Folder created: {folder_path}")
            except FileExistsError:
                message = f"Folder already exists: {folder_path}" + '\n'
                colour = 'brown'
                self.session_log.write_textbox(message, colour)
                print(message)

            # Move the file to the created folder
            try:
                file_path = os.path.join(destination_folder, filename)
                new_file_path = os.path.join(folder_path, filename)

                if not os.path.isfile(new_file_path):
                    shutil.move(file_path, new_file_path)
                    self.n_files_moved += 1
                    message = str(filename) + "  >>>  " + str(os.path.dirname(new_file_path)) + '\n'
                    colour = 'black'
                    self.session_log.write_textbox(message, colour)
                    print(message)

                else:
                    message = f"File {file_path} Exists and Will Be Ignored" + '\n'
                    colour = 'red'
                    self.session_log.write_textbox(message, colour)
                    print(message)

            except FileNotFoundError:
                message = f"File not found: {filename}" + '\n'
                colour = 'red'
                self.session_log.write_textbox(message, colour)
                print(message)

    def open_folder(self):
        temp_path = os.path.realpath(self.user_entry.folder_path)
        try:
            os.startfile(temp_path)
        except:
            self.user_entry.file_location = FOLDER_PATH

    def choose_folder(self):
        self.user_entry.folder_path = filedialog.askdirectory(initialdir=FOLDER_PATH)
        self.update_entry_files_location(os.path.normcase(self.user_entry.folder_path))

        message = 'Files Location: ' + os.path.normcase(self.user_entry.folder_path) + '\n'
        colour = "blue"
        self.session_log.write_textbox(message, colour)

    def update_entry_files_location(self, string):
        self.entry_files_location.delete(0, END)
        self.entry_files_location.insert(0, string)

    def undo_move_files_to_folders(self, filenames, destination_folder):
        # Check if the destination folder exists
        if not os.path.exists(destination_folder):
            print("Destination folder does not exist.")
            return

        for filename in filenames:
            # Create a folder using the filename in the destination folder
            folder_name = os.path.splitext(filename)[0]
            folder_path = os.path.join(destination_folder, folder_name)

            # Check if the folder exists
            if os.path.exists(folder_path):
                # Move the file back to the original location
                new_file_path = os.path.join(destination_folder, filename)
                file_path = os.path.join(folder_path, filename)
                try:
                    shutil.move(file_path, new_file_path)
                    print(f"File moved back to: {new_file_path}")
                except FileNotFoundError:
                    print(f"File not found: {file_path}")
                # Remove the empty folder
                try:
                    os.rmdir(folder_path)
                    print(f"Folder removed: {folder_path}")
                except OSError:
                    print(f"Failed to remove folder: {folder_path}")
            else:
                print(f"Folder not found: {folder_path}")

    def entry_update_files_location(self):
        file_location = self.entry_files_location_entry.get()
        if fm.FileNameMethods.check_file_location_valid(file_location):
            self.user_entry.folder_path = file_location
        else:
            self.user_entry.folder_path = FOLDER_PATH
        message = 'Files Location: ' + os.path.normcase(self.user_entry.folder_path) + '\n'
        colour = 'blue'
        self.session_log.write_textbox(message, colour)
        print("::user_entry.folder_path: ", self.user_entry.folder_path)
