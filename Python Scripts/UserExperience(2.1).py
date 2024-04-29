'''

RELEASE 2.1

FULL GUI EXPERIENCE!

**Important notes**
- Forces exact matching of user-input patent numbers to <doc-number> in XML files, 
but allows leading zero(s) in patent number input.

- Error handling, includes:
    - Extracting ZIP file only if necessary
    - Verifying and processing only XML files
    - Mandatory user input for patent numbers
    - Mandatory user input for element searching
    - Handles both text and sub-elements (children) within requested XML elements

- Creates a pkl file to store indexed files for faster (immediate) access

'''

import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import zipfile
import tkinter as tk
from tkinter import messagebox, scrolledtext
import pickle

class Extractor:
    def __init__(self):
        self.sample_dirs = {}
        self.indexed_files = {}

    # Sets the directory for patent files and extracts them if necessary.
    # If the directory is a ZIP file, it is extracted to a temporary directory.
    # Checks if the ZIP directory exists first, if not, extracts the ZIP file.
    def set_directory(self, directory, side):
        if directory.endswith('.zip'):
            extract_dir = directory[:-4] # for cases with .zip
            if not os.path.exists(extract_dir):
                try:
                    with zipfile.ZipFile(directory, 'r') as zip_ref:
                        zip_ref.extractall(extract_dir)
                    messagebox.showinfo("Information", f"Extracted ZIP file for {side}.")
                except zipfile.BadZipFile:
                    messagebox.showerror("Error", f"Invalid ZIP file for {side}.")
                    return False
            directory = extract_dir

        if not os.path.isdir(directory):
            messagebox.showerror("Error", f"Invalid directory path for {side}.")
            return False
        
        if side in self.sample_dirs and self.sample_dirs[side] == directory:
            return True
        
        self.sample_dirs[side] = directory
        return self.preprocess_files(side)

    # Processes files in the set directory and indexes them by patent number.
    # Only runs if the index file does not exist.
    def preprocess_files(self, side):
        directory = self.sample_dirs[side]
        index_file_path = os.path.join(directory, 'patent_file_index.pkl')

        if os.path.exists(index_file_path):
            with open(index_file_path, 'rb') as f:
                self.indexed_files[side] = pickle.load(f)
            messagebox.showinfo("Information", f"Files preprocessed for {side}. READY TO USE.")
        else:
            self.indexed_files[side] = {}
            for filename in os.listdir(directory):
                if filename.endswith('.xml'):
                    patent_number = self.extract_patent_number(filename)
                    if patent_number:
                        self.indexed_files[side][patent_number] = os.path.join(directory, filename)
            with open(index_file_path, 'wb') as f:
                pickle.dump(self.indexed_files[side], f)

        return True

    def extract_patent_number(self, filename):
        parts = filename.split('-')
        if len(parts) > 2 and parts[2].isdigit():
            return parts[2].lstrip('0')
        return None

    def find_xml_file_for_patent(self, patent_number, side):
        return self.indexed_files[side].get(patent_number.lstrip('0')) if side in self.indexed_files else None

    # Prases the entire XML tree.
    # Lists all UNIQUE elements in the given XML file.
    def list_all_elements(self, file_path):
        elements = set()
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            for elem in root.iter():
                elements.add(elem.tag)
        except ET.ParseError:
            messagebox.showerror("Error", f"Failed to parse XML in {file_path}")

        return sorted(elements)
    
    # Retrieves and formats the content of a specific XML element and its children.
    def get_element_content(self, file_path, element_name):
        content = ''
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            for elem in root.findall('.//' + element_name):
                xmlstr = minidom.parseString(ET.tostring(elem)).toprettyxml(indent="  ")
                content += '\n'.join(xmlstr.split('\n')[1:])  # Remove the XML declaration
                content += '\n\n'
        except ET.ParseError:
            messagebox.showerror("Error", f"Failed to parse XML in {file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        
        return content

class PatentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.extractor = Extractor()
        self.title("Patent Document Viewer")
        self.geometry("1200x600+30+20")
        self.create_widgets()

    # Creates initial widgets like the status label.
    # Added short delay to simulate loading time.
    def create_widgets(self):
        self.status_label = tk.Label(self, text="Opening application, please wait...")
        self.status_label.pack(pady=10, fill=tk.X)
        self.after(1000, self.remove_initial_message)

    def remove_initial_message(self):
        self.status_label.pack_forget()
        self.paned_window = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=6)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        self.create_side_widgets("left")
        self.create_side_widgets("right")

    # Configures and sets up widgets for each side of the application's paned window (left + right).
    # Sets up all the necessary widgets for directory input, patent number input, and filtering.
    # Also stores references to all these widgets for easy access elsewhere in the application.
    def create_side_widgets(self, side):
        frame = tk.Frame(self.paned_window)
        self.paned_window.add(frame, stretch="always")

        # Widgets for directory input
        directory_label = tk.Label(frame, text=f"Enter Directory for {side.capitalize()}:")
        directory_entry = tk.Entry(frame)
        set_directory_button = tk.Button(frame, text="Set Directory", command=lambda: self.set_directory(directory_entry.get(), side))
        directory_entry.bind('<Return>', lambda event: self.set_directory(directory_entry.get(), side))

        # Widget for displaying the directory currently open
        directory_open_label = tk.Label(frame, text="", font=('Helvetica', 9, 'italic'))
        
        # Pack directory input section widgets
        directory_label.pack(pady=10)
        directory_entry.pack(pady=10)
        set_directory_button.pack(pady=10)

        # Widgets for patent number input, initially hidden
        patent_number_label = tk.Label(frame, text=f"Search Patent {side.capitalize()}:")
        patent_number_entry = tk.Entry(frame)
        search_button = tk.Button(frame, text="Search", command=lambda: self.perform_search(patent_number_entry.get(), side))
        results_text = scrolledtext.ScrolledText(frame, height=10)
        
        # Bind the 'Enter' key to search patents
        patent_number_entry.bind('<Return>', lambda event: self.perform_search(patent_number_entry.get(), side))

        # Widgets for filtering, initially not visible
        filter_label = tk.Label(frame, text="Filter:")
        filter_entry = tk.Entry(frame)
        filter_entry.bind('<KeyRelease>', lambda event: self.on_filter_update(side))

        # Store references to widgets for later use
        setattr(self, f"{side}_frame", frame)
        setattr(self, f"{side}_directory_open_label", directory_open_label)
        setattr(self, f"{side}_directory_label", directory_label)
        setattr(self, f"{side}_directory_entry", directory_entry)
        setattr(self, f"{side}_set_directory_button", set_directory_button)
        setattr(self, f"{side}_patent_number_label", patent_number_label)
        setattr(self, f"{side}_patent_number_entry", patent_number_entry)
        setattr(self, f"{side}_search_button", search_button)
        setattr(self, f"{side}_results_text", results_text)
        setattr(self, f"{side}_filter_label", filter_label)
        setattr(self, f"{side}_filter_entry", filter_entry)

        self.filter_label = tk.Label(frame, text="Filter:")
        self.filter_entry = tk.Entry(frame)

        # Store references to the filter widgets
        setattr(self, f"{side}_filter_label", self.filter_label)                                                                                                                                                                                                                    # EASTER EGG YOU FOUND ME #
        setattr(self, f"{side}_filter_entry", self.filter_entry)                                                                                                                                                                                                                    # Fatmike (Michael Haddad) was here #

    # Sets the directory for a side and processes files if directory is valid.
    def set_directory(self, directory, side):
        if self.extractor.set_directory(directory, side):
            self.show_patent_widgets(side)

    # Shows the patent search widgets for a side after a directory is set.
    def show_patent_widgets(self, side):
        patent_number_label = getattr(self, f"{side}_patent_number_label")
        patent_number_entry = getattr(self, f"{side}_patent_number_entry")
        search_button = getattr(self, f"{side}_search_button")
        results_text = getattr(self, f"{side}_results_text")

        # Pack label and entry for the patent number
        patent_number_label.pack(pady=10)
        patent_number_entry.pack(pady=10)

        # Pack the search button and results text area
        search_button.pack(pady=10)
        results_text.pack(pady=10, fill=tk.BOTH, expand=True)

    # Displays all elements found in a file for a specific side.
    # Configures the results_text widget to show interactive entries for each element found in the file.
    # Elements have hover effects and a click event (clickable)
    def display_elements(self, side, file_path):
        results_text = getattr(self, f"{side}_results_text")
        results_text.config(state=tk.NORMAL)
        results_text.delete('1.0', tk.END)
        
        elements = self.extractor.list_all_elements(file_path)
        for element in elements:
            tag = element.replace(':', '_')
            results_text.insert(tk.END, element + '\n', tag)
            
            # Bind hover effects and click event
            results_text.tag_bind(tag, '<Enter>', lambda event, t=tag: results_text.tag_config(t, background='yellow'))
            results_text.tag_bind(tag, '<Leave>', lambda event, t=tag: results_text.tag_config(t, background=''))
            results_text.tag_bind(tag, '<Button-1>', lambda event, e=element, s=side: self.on_element_click(e, file_path, s))
        
        # To ensure filter interface is visible
        filter_label = getattr(self, f"{side}_filter_label")
        filter_entry = getattr(self, f"{side}_filter_entry")
        filter_label.pack(pady=2)
        filter_entry.pack(pady=2)
        filter_entry.bind('<KeyRelease>', lambda event: self.on_filter_update(side))
        results_text.config(state=tk.DISABLED)

    # Searches for a patent number and displays its elements if found.
    # 2 checks are made:
        # 1) If the patent number is empty, a warning message is displayed.
        # 2) If the patent number is incorrect, an error message is displayed.
    def perform_search(self, patent_number, side):
        results_text = getattr(self, f"{side}_results_text")

        if not patent_number:
            messagebox.showwarning("Warning", f"Patent number for {side} cannot be empty.")
            return
        file_path = self.extractor.find_xml_file_for_patent(patent_number, side)

        if file_path:
            setattr(self, f"{side}_file_path", file_path)
            self.display_elements(side, file_path)
        else:
            messagebox.showerror("Error", f"The patent for {side} provided does not exist.")

    # Handles the event when an XML element is clicked, displaying its content.
    # Display and bind the "Back" button to return to the list of elements.
    # Sets the GUI state to normal to allow:
        # 1) Changes to the content area
        # 2) Clearing the current content
        # 3) Inserting the "Back" button
    def on_element_click(self, element, file_path, side):
        # Enable text modification and clear existing content
        results_text = getattr(self, f"{side}_results_text")
        results_text.config(state=tk.NORMAL)
        results_text.delete('1.0', tk.END)
        
        # "Back" button
        go_back_tag = "go_back"
        results_text.insert(tk.END, " BACK \n\n", go_back_tag)
        results_text.tag_bind(go_back_tag, '<Button-1>', lambda event: self.display_elements(side, file_path))
        results_text.tag_config(go_back_tag, foreground='blue', underline=1)

        # Display the content for the selected element
        content = self.extractor.get_element_content(file_path, element)
        results_text.insert(tk.END, content)
        results_text.config(state=tk.DISABLED)

    # Filters and displays elements based on the filter input from the user.
    def on_filter_update(self, side):
        results_text = getattr(self, f"{side}_results_text")
        filter_text = getattr(self, f"{side}_filter_entry").get().lower()
        file_path = getattr(self, f"{side}_file_path", None)

        if file_path:
            # Clear existing text and re-display all elements filtered
            results_text.config(state=tk.NORMAL)
            results_text.delete('1.0', tk.END)
            elements = self.extractor.list_all_elements(file_path)

            for element in elements:
                if filter_text in element.lower():
                    tag = element.replace(':', '_')
                    results_text.insert(tk.END, element + '\n', tag)
                    # Re-bind the click event to the filtered elements
                    results_text.tag_bind(tag, '<Button-1>', lambda event, e=element, s=side: self.on_element_click(e, file_path, s))
            results_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    app = PatentApp()
    app.mainloop()
