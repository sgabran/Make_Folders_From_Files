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

        self.files_to_process = []
        self.files_moved_fullpath = []
        self.folders_created_fullpath = []
        self.bad_undo_folder = {}
        self.n_files_to_process = 0
        self.n_files_moved_fullpath = 0
        self.n_folders_created_fullpath = 0
        self.n_restored_files = 0
        self.n_deleted_folders = 0
        self.finished_with_errors = 1

        # GUI Frames
        self.frame_root_title = Frame(root, highlightthickness=0)
        self.frame_root_session = LabelFrame(root, width=120, height=390, padx=5, pady=5, text="Session")

        # Disable resizing the window
        root.resizable(False, False)

        # Grids
        self.frame_root_title.grid(row=0, column=0, padx=10, pady=5, ipadx=5, ipady=5)
        self.frame_root_session.grid(row=1, column=0, sticky="W", padx=10, pady=(5, 5), ipadx=5, ipady=2)

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
        self.button_open_folder = Button(self.frame_root_session, text="Open Folder",
                                         command=lambda: self.open_folder(), pady=0, width=10)
        self.button_undo = Button(self.frame_root_session, text="Undo",
                                  command=lambda: self.undo_move_files_to_folders(self.folders_created_fullpath),
                                  pady=0, width=10)
        self.button_exit = Button(self.frame_root_session, text="Exit", fg='red', command=self.quit_program, pady=0,
                                  width=10)

        # Grids
        self.entry_files_location.grid(row=1, column=1, sticky=W, padx=(5, 0))
        self.button_files_location.grid(row=1, column=0, sticky=NE)
        self.button_start.grid(row=2, column=0, sticky=NE)
        self.button_open_folder.grid(row=2, column=1, sticky=NW)
        self.button_undo.grid(row=2, column=1, sticky=NW, padx=(80, 0))
        self.button_exit.grid(row=2, column=1, sticky=NW, padx=(180, 0))

        # END OF FRAME #######################################################

        self.root_frame.mainloop()

    ######################################################################

    def set_state(self, widget, state):
        print(type(widget))
        try:
            widget.configure(state=state)
        except:
            pass
        for child in widget.winfo_children():
            self.set_state(child, state=state)

    @staticmethod
    def quit_program():
        # quit()  # quit() does not work with pyinstaller, use sys.exit()
        sys.exit()

    def start_process(self):
        self.files_to_process = []
        self.files_moved_fullpath = []
        self.folders_created_fullpath = []
        self.bad_undo_folder = {}

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

            if self.n_files_to_process == self.n_folders_created_fullpath == self.n_files_moved_fullpath:
                message = "Number of Folders Created: " + str(self.n_folders_created_fullpath) + '\n'
                colour = 'green'
                self.session_log.write_textbox(message, colour)
                message = "Number of Files Moved: " + str(self.n_files_moved_fullpath) + '\n'
                colour = 'green'
                self.session_log.write_textbox(message, colour)
                message = "Process Finished Successfully" + '\n'
                colour = 'green'
                self.session_log.write_textbox(message, colour)
            else:
                message = "WARNING: MISMATCH" + '\n'
                colour = 'red'
                self.session_log.write_textbox(message, colour)
                message = "Number of Folders Created: " + str(self.n_folders_created_fullpath) + '\n'
                colour = 'red'
                self.session_log.write_textbox(message, colour)
                message = "Number of Files Moved: " + str(self.n_files_moved_fullpath) + '\n'
                colour = 'red'
                self.session_log.write_textbox(message, colour)
                message = "Process Finished with Errors" + '\n'
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

    def create_folders_and_move_files(self, filenames_list, destination_root_folder):
        # Check if the destination folder exists
        if not os.path.exists(destination_root_folder):
            message = "Folder path does not exist .. Process will terminate" + '\n'
            colour = 'brown'
            self.session_log.write_textbox(message, colour)
            print(message)
            return -1

        for filename in filenames_list:
            # Create a folder using the filename in the destination folder
            folder_name = os.path.splitext(filename)[0]
            folder_path = os.path.join(destination_root_folder, folder_name)

            # Create the folder
            try:
                os.makedirs(folder_path)
                self.folders_created_fullpath.append(folder_path)
                print(f"Folder created: {folder_path}")
            except FileExistsError:
                message = f"Folder already exists: {folder_path}" + '\n'
                colour = 'brown'
                self.session_log.write_textbox(message, colour)
                print(message)

            # Move the file to the created folder
            try:
                file_path = os.path.join(destination_root_folder, filename)
                new_file_path = os.path.join(folder_path, filename)

                if not os.path.isfile(new_file_path):
                    shutil.move(file_path, new_file_path)
                    self.files_moved_fullpath.append(new_file_path)
                    message = str(filename) + "  >>>  " + str(os.path.dirname(new_file_path)) + '\n'
                    colour = 'black'
                    self.session_log.write_textbox(message, colour)
                    print(message)

                else:
                    message = f"File {file_path} Exists and Will Be Ignored" + '\n'
                    colour = 'red'
                    self.session_log.write_textbox(message, colour)
                    print(message)

                self.n_folders_created_fullpath = len(self.folders_created_fullpath)
                self.n_files_moved_fullpath = len(self.files_moved_fullpath)

            except FileNotFoundError:
                message = f"File not found: {filename}" + '\n'
                colour = 'red'
                self.session_log.write_textbox(message, colour)
                print(message)

    def open_folder(self):
        folder_path = self.user_entry.folder_path
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            os.startfile(self.user_entry.folder_path)
        else:
            messagebox.showinfo(title="Error", message="Folder Does Not Exist")
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

    def undo_move_files_to_folders(self, folders_fullpath):

        self.bad_undo_folder = {}
        self.n_restored_files = 0
        self.n_deleted_folders = 0
        self.finished_with_errors = 1

        # check if changes were done
        if self.n_folders_created_fullpath == self.n_files_moved_fullpath == 0:
            message = "Nothing to Undo" + '\n'
            colour = 'red'
            self.session_log.write_textbox(message, colour)
            messagebox.showinfo(title="Warning", message=message)
            return -1

        message = "Start to Undo" + '\n'
        colour = 'black'
        self.session_log.write_textbox(message, colour)

        # Check folder integrity. "folder" is full pathname
        for folder_fullpath in folders_fullpath:

            # 1. Check if folder exists
            if os.path.exists(folder_fullpath) and os.path.isdir(folder_fullpath):

                # 2. Check number of folder contents: must equal to 1.
                # "folder_contents" is filename with extension
                folder_contents = os.listdir(folder_fullpath)
                if len(folder_contents) == 0:
                    # self.bad_undo_folder.append(folder_fullpath)
                    self.bad_undo_folder[folder_fullpath] = BAD_FOLDER_ERROR_2

                elif len(folder_contents) > 1:
                    # self.bad_undo_folder.append(folder_fullpath)
                    self.bad_undo_folder[folder_fullpath] = BAD_FOLDER_ERROR_3

                else:
                    # 3. Check folder contents: file must have same folder name
                    folder_name = os.path.basename(folder_fullpath)
                    filename_without_extension = os.path.splitext(os.path.basename(folder_contents[0]))[0]
                    if folder_name != filename_without_extension:
                        # self.bad_undo_folder.append(folder_fullpath)
                        self.bad_undo_folder[folder_fullpath] = BAD_FOLDER_ERROR_4

                    else:
                        filename = os.path.basename(folder_contents[0])
                        filename_original_path = os.path.join(folder_fullpath, filename)
                        file_destination_path = os.path.join(self.user_entry.folder_path, filename)
                        # Move file
                        shutil.move(filename_original_path, file_destination_path)
                        message = "Moved: " + filename_original_path + " >> to >> " + file_destination_path + '\n'
                        colour = 'black'
                        self.session_log.write_textbox(message, colour)
                        self.n_restored_files += 1
                        # Delete folder
                        shutil.rmtree(folder_fullpath)
                        self.n_deleted_folders += 1
                        message = "Folder Deleted" + '\n'
                        colour = 'black'
                        self.session_log.write_textbox(message, colour)

            else:
                # self.bad_undo_folder.append(folder_fullpath)
                self.bad_undo_folder[folder_fullpath] = BAD_FOLDER_ERROR_1

        # List bad folders
        if len(self.bad_undo_folder) > 0:
            message = "Errors Found in Some Folders. Bad Folders are Ignored" + '\n'
            colour = 'red'
            self.session_log.write_textbox(message, colour)
            message = "Bad Folders: " + '\n'
            colour = 'red'
            self.session_log.write_textbox(message, colour)

            for folder, error in self.bad_undo_folder.items():
                message = '\t' + folder + " >> " + error + '\n'
                colour = 'red'
                self.session_log.write_textbox(message, colour)

            message = "Errors Found in Some Folders" + '\n' + "Bad Folders are Ignored" + '\n'
            messagebox.showinfo(title="Error", message=message)

        else:
            self.finished_with_errors = 0

        message = "Number of Files Restored: " + str(self.n_restored_files) + '\n'
        colour = 'black'
        self.session_log.write_textbox(message, colour)
        message = "Number of Folder Deleted: " + str(self.n_deleted_folders) + '\n'
        colour = 'black'
        self.session_log.write_textbox(message, colour)

        if not self.finished_with_errors:
            message = "Process Finished Successfully" + '\n'
            colour = 'green'
            self.session_log.write_textbox(message, colour)

        else:
            message = "Process Finished with Errors" + '\n'
            colour = 'red'
            self.session_log.write_textbox(message, colour)

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
