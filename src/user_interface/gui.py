import tkinter as tk
import time  # for delay
import threading
import pyglet  # for custom font stuff
from tkinter import filedialog, messagebox
from capabilities.knowledge_base import Document
from user_interface.user_interface import UserInterface


class GUI(UserInterface):
    """A simple GUI interface for interacting with MASAPI."""

    def __init__(self):
        super().__init__()
        # tkinter window
        self.root = tk.Tk()
        self.root.title("MAS GUI")
        self.root.geometry("800x500")
        self.custom_font = self.load_custom_font(
            "user_interface/fonts/NebulaSans-Medium.ttf", size=16
        )  # just edit if you want a diff font, not certain this is working though
        self.setup_layout()
        self.create_buttons()
        # flag for the window type, whether it's actively in the messaging/chat mode
        self.messaging_mode = False

    def load_custom_font(self, font_path, size):
        try:
            pyglet.font.add_file(font_path)
            font_name = font_path.split("/")[-1].replace(".ttf", "")
            return (font_name, size)
        except Exception as e:
            print(f"Error loading font: {e}")
            return ("Helvetica", size)

    # main window formatting
    def setup_layout(self):
        # main window frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # side buttons frame
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # output window frame
        self.output_frame = tk.Frame(self.main_frame)
        self.output_frame.pack(
            side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10
        )

        # text box output frame
        self.text_output = tk.Text(
            self.output_frame,
            height=20,
            wrap=tk.WORD,
            font=(self.custom_font[0], self.custom_font[1]),
        )
        self.text_output.pack(fill=tk.BOTH, expand=True)
        self.text_output.config(state=tk.DISABLED)

        # input frame (below the main output box)
        self.text_input = tk.Entry(
            self.output_frame, font=(self.custom_font[0], self.custom_font[1])
        )
        self.text_input.pack(fill=tk.X, padx=10, pady=5)
        self.text_input.bind("<Return>", self.submit_query)

    def create_buttons(self):
        buttons = [
            ("List Agents", self.list_agents),
            ("View Chat/Query MAS", self.enter_messaging_mode),
            ("Add Document", self.add_document),
            ("List Documents", self.list_documents),
            ("Exit", self.exit),
        ]
        for label, command in buttons:
            button = tk.Button(
                self.button_frame,
                text=label,
                width=20,
                command=command,
                font=(self.custom_font[0], self.custom_font[1]),
            )
            button.pack(pady=5)

    def run(self):
        # start
        self.root.mainloop()

    def clear_output(self):
        self.text_output.config(state=tk.NORMAL)
        self.text_output.delete(1.0, tk.END)
        self.text_output.config(state=tk.DISABLED)
        # just some read/write stuff

    def print_output(self, text):
        self.text_output.config(state=tk.NORMAL)
        self.text_output.delete(1.0, tk.END)
        self.text_output.insert(tk.END, text)
        self.text_output.config(state=tk.DISABLED)

    # list agents button
    def list_agents(self):
        agents = self.api.mas_api.get_agents()
        result = (
            "Agents:\n" + "\n".join(f"- {agent.name}" for agent in agents)
            if agents
            else "No agents found."
        )
        self.print_output(result)

    # for the chat message window, should probably make it visually change beyond the text (?)
    # this is for selecting the button versus sending a message BUT i'd wanna move things about to have similar code/less repeats
    def enter_messaging_mode(self):
        self.clear_output()

        def fetch_history():
            try:
                history = self.api.mas_api.get_chat_history()
                if history and history.messages:
                    result = "Chat History:\n" + "\n".join(
                        f"- {msg.who}: {msg.content}" for msg in history.messages
                    )
                else:
                    result = "No chat history yet. Use enter key to send prompt."
            except Exception as e:
                result = f"Error loading chat history: {e}"
            self.root.after(0, lambda: self.print_output(result))

        threading.Thread(
            target=fetch_history, daemon=True
        ).start()  # run on diff thread
        self.start_messaging_mode()

    def submit_query(self, event=None):
        query = self.text_input.get()
        if not query:
            self.print_output("Please enter a query.")  # upon no input
            return

        self.text_input.delete(0, tk.END)
        self.clear_output()
        self.start_messaging_mode()

        # loading window while waiting for output
        loading_popup = tk.Toplevel(self.root)
        loading_popup.title("Loading...")
        loading_popup.geometry("200x100")
        tk.Label(
            loading_popup,
            text="Loading...",
            font=(self.custom_font[0], self.custom_font[1]),
        ).pack(expand=True)
        loading_popup.transient(self.root)
        loading_popup.grab_set()

        # thread to receive response upon sending query, bit redundant/should make more funcs so less overlap with initial grab
        def query_thread():
            try:
                self.api.mas_api.query_mas(query)
                time.sleep(1.5)  # Wait for response
                history = self.api.mas_api.get_chat_history()

                if history and history.messages:
                    result = "Chat History:\n" + "\n".join(
                        f"- {msg.who}: {msg.content}" for msg in history.messages
                    )
                else:
                    result = "Sorry, I couldn't find a response."
                self.root.after(0, lambda: self.print_output(result))

            except Exception as e:
                self.root.after(0, lambda: self.print_output(f"An error occurred: {e}"))
            # kill popup
            finally:
                self.root.after(0, loading_popup.destroy)
                self.root.after(0, self.end_messaging_mode)

        threading.Thread(target=query_thread, daemon=True).start()

    # just flag stuff
    def start_messaging_mode(self):
        self.messaging_mode = True

    def end_messaging_mode(self):
        self.messaging_mode = False

    # add doc button
    def add_document(self):
        agents = self.api.mas_api.get_agents()
        agent_names = [agent.name for agent in agents]
        if not agent_names:
            messagebox.showerror("Error", "No agents available.")
            return

        # spawn separate window
        add_doc_window = tk.Toplevel(self.root)
        add_doc_window.title("Add Document")
        add_doc_window.geometry("400x400")

        agent_var = tk.StringVar(add_doc_window)
        agent_var.set(agent_names[0])

        agent_label = tk.Label(
            add_doc_window,
            text="Select Agent",
            font=(self.custom_font[0], self.custom_font[1]),
        )
        agent_label.pack(pady=10)

        agent_dropdown = tk.OptionMenu(add_doc_window, agent_var, *agent_names)
        agent_dropdown.pack(pady=10)

        doc_label = tk.Label(
            add_doc_window,
            text="Document Path",
            font=(self.custom_font[0], self.custom_font[1]),
        )
        doc_label.pack(pady=10)

        doc_input = tk.Entry(
            add_doc_window, font=(self.custom_font[0], self.custom_font[1])
        )
        doc_input.pack(pady=5)

        # choose from file explorer/finder
        def select_file():
            path = filedialog.askopenfilename(title="Select Document")
            if path:
                doc_input.delete(0, tk.END)
                doc_input.insert(0, path)

        # button
        select_button = tk.Button(
            add_doc_window,
            text="Select File",
            command=select_file,
            width=20,
            font=(self.custom_font[0], self.custom_font[1]),
        )
        select_button.pack(pady=5)

        # confirm doc
        def confirm_selection():
            selected_agent = agent_var.get()
            doc_path = doc_input.get()
            if not doc_path:
                messagebox.showerror("Error", "No document selected.")
                return
            try:
                agent = self.api.mas_api.get_agent(selected_agent)
            except KeyError:
                messagebox.showerror(
                    "Error", f"No agent found with name: {selected_agent}"
                )
                return
            extension = doc_path.split(".")[-1]
            document = Document(path=doc_path, extension=extension)
            self.api.mas_api.add_document(document, agent)
            messagebox.showinfo("Success", "Document added successfully.")
            add_doc_window.destroy()  # kill window

        #  button
        confirm_button = tk.Button(
            add_doc_window,
            text="Confirm",
            command=confirm_selection,
            width=20,
            font=(self.custom_font[0], self.custom_font[1]),
        )
        confirm_button.pack(pady=5)

    # self explanatory, lists docs
    def list_documents(self):
        docs = self.api.mas_api.get_documents()
        result = (
            "Documents:\n" + "\n".join(f"- {doc.path}" for doc in docs)
            if docs
            else "No documents available."
        )
        self.print_output(result)

    def exit(self):
        # super exit
        super().exit()
        self.root.quit()
