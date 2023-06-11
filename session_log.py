# ver = 2022-4-27-1

from datetime import datetime
from tkinter import *


class SessionLog:
    def __init__(self, user_entry):
        self.user_entry = user_entry
        self.frame = Tk()
        self.frame.title('Session Log')

        # Disable closing the session log window
        self.frame.protocol("WM_DELETE_WINDOW", self.do_nothing)

        self.text_box_tag = 1
        self.text_box_entry_counter = 1

        # Text Box
        self.text_box = Text(self.frame, height=25, width=90, font=('Arial', 8), spacing3=2, selectbackground='grey',
                             wrap='word', highlightthickness=2)
        self.scroll_bar = Scrollbar(self.frame)
        self.scroll_bar.config(command=self.text_box.yview)
        self.text_box.config(yscrollcommand=self.scroll_bar.set)

        # Buttons
        self.button_log_save = Button(self.frame, text="Save Log", command=self.save_log, height=1, width=15)
        self.button_log_clear = Button(self.frame, text="Clear Log", command=self.clear_textbox, height=1, width=15)

        # Grid
        self.text_box.grid(row=0, column=0, sticky=E, columnspan=4)
        self.scroll_bar.grid(row=0, column=5, sticky=NS)
        self.button_log_save.grid(row=1, sticky=W, pady=3, padx=(10, 30))
        self.button_log_clear.grid(row=1, sticky=E, pady=3, padx=(30, 10))

        # Disable resizing the window
        # self.frame.resizable(False, False)

    # Write to textbox, include message counter. User must add new line '\n' to message
    def write_textbox(self, message, message_colour):
        tag = str(self.text_box_tag)
        counter = str(self.text_box_entry_counter)
        self.text_box.tag_config(tag, foreground=message_colour)
        self.text_box.insert(END, (counter + ". " + message), tag)
        self.text_box_tag = self.text_box_tag + 1
        self.text_box_entry_counter = self.text_box_entry_counter + 1
        self.text_box.see("end")
        self.frame.update_idletasks()

    # Append to previous textbox, without including message counter
    def write_textbox_append(self, message, message_colour):
        tag = str(self.text_box_tag)
        self.text_box.tag_config(tag, foreground=message_colour)
        self.text_box.insert(END, message, tag)
        self.text_box_tag = self.text_box_tag + 1
        self.text_box.see("end")
        self.frame.update_idletasks()

    # Function that does nothing. Used in frame_sessionlog.protocol()
    def do_nothing(self):
        pass

    # Methods for Session log
    def save_log(self):
        log_text = self.text_box.get("0.0", END)
        now = datetime.now()
        now = now.strftime("%m-%d-%Y, %H.%M.%S")
        file_name = ("Session Log " + str(now) + ".txt")
        file_address = (self.user_entry.file_location + "/" + file_name)
        text_file = open(file_address, "w")
        text_file.write(str(log_text))
        text_file.close()
        message = "Session log saved: " + str(file_address) + '\n'
        message_colour = 'black'
        self.write_textbox(message, message_colour)

    # Clear log from text box
    def clear_textbox(self):
        self.text_box.delete('1.0', END)

    def enable_button_log_save(self):
        self.button_log_save["state"] = ACTIVE

    def enable_button_log_clear(self):
        self.button_log_clear["state"] = ACTIVE

    def disable_button_log_save(self):
        self.button_log_save["state"] = DISABLED

    def disable_button_log_clear(self):
        self.button_log_clear["state"] = DISABLED
