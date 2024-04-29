'''

RELEASE 2.0
This is the first version that uses GUI

**Important notes**
- Forces exact matching of user-input patent numbers to <doc-number> in XML files, but...
allows leading zeros in patent number input.

- Error handling, includes:
    - Verifying and processing only XML files
    - Mandatory user input for patent numbers
    - Mandatory user input for element searching

- Handles both text and sub-elements within requested XML elements

- The code preprocesses the XML file names, extracting and indexing 
patent numbers, then saves this data to a pkl file. When script runs, 
it directly checks this index for a match, greatly speeding up searches.

'''

import xml.etree.ElementTree as ET
import xml.dom.minidom
import os
import zipfile
import tkinter as tk
from tkinter import messagebox, scrolledtext
import pickle

class Extractor:
    def __init__(self, sample_dir):
        self.sample_dir = sample_dir
        self.indexed_files = None
        self.preprocess_files()

    def preprocess_files(self):
        if os.path.exists('patent_file_index.pkl'):
            with open('patent_file_index.pkl', 'rb') as f:
                self.indexed_files = pickle.load(f)
            print("Files preprocessed. Ready to use.")
        else:
            print("Preprocessing files, please wait...")
            self.indexed_files = {}
            for filename in os.listdir(self.sample_dir):
                if filename.endswith('.xml'):
                    patent_number = self.extract_patent_number(filename)
                    if patent_number is not None:
                        self.indexed_files[patent_number] = os.path.join(self.sample_dir, filename)
            with open('patent_file_index.pkl', 'wb') as f:
                pickle.dump(self.indexed_files, f)
            print("Files preprocessed. Ready to use.")

    def extract_patent_number(self, filename):
        parts = filename.split('-')
        if len(parts) > 2 and parts[2].isdigit():
            return parts[2].lstrip('0')
        return None

    def prettify_xml_element(self, element):
        pretty_xml_as_string = ''
        for child in list(element):
            child_string = ET.tostring(child, 'unicode')
            parsed_child = xml.dom.minidom.parseString(child_string)
            pretty_xml_as_string += '\n'.join([line for line in parsed_child.toprettyxml(indent="  ").split('\n') if line.strip()])
        return pretty_xml_as_string.strip()

    def find_xml_file_for_patent(self, patent_number):
        return self.indexed_files.get(patent_number.lstrip('0'))

    def extract_first_element_value_from_xml(self, file_path, element_names):
        element_values = {}
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            for element_name in element_names:
                element = root.find('.//{}'.format(element_name))
                if element is not None:
                    element_values[element_name] = self.prettify_xml_element(element) if list(element) else element.text.strip()
        except ET.ParseError:
            messagebox.showerror("Error", f"Failed to parse the file: {file_path}")
        return element_values

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

    def extract_zip_if_needed(self, zip_path, extract_to):
        if not os.path.exists(extract_to):
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)

def setup_paths():
    data_dir = 'C:/Users/haddadm1/Desktop/Random Things/dd_Patent_Element_Testing'
    sample_zip_path = os.path.join(data_dir, 'CA-WEEKLY-BFT-UPDATE-FROM-20240311-TO-20240317-ON-20240318.zip')
    sample_dir = os.path.join(data_dir, 'CA-WEEKLY-BFT-UPDATE-FROM-20240311-TO-20240317-ON-20240318')
    return data_dir, sample_zip_path, sample_dir

class PatentApp(tk.Tk):
    def __init__(self, extractor):
        super().__init__()
        self.extractor = extractor
        self.title("Patent Document Viewer")
        self.geometry("600x400")
        self.create_widgets()
        self.preprocess_data()

    def create_widgets(self):
        self.status_label = tk.Label(self, text="Opening application, please wait...")
        self.patent_number_label = tk.Label(self, text="Enter Patent Number:")
        self.patent_number_entry = tk.Entry(self)
        self.search_button = tk.Button(self, text="Search", command=self.on_search)
        self.results_text = scrolledtext.ScrolledText(self, height=10)

    def start_loading(self):
        self.status_label.pack(pady=10)
        self.after(100, self.finish_loading)

    def finish_loading(self):
        self.status_label.pack_forget()
        self.patent_number_label.pack(pady=10)
        self.patent_number_entry.pack(pady=10)
        self.search_button.pack(pady=10)
        self.results_text.pack(fill=tk.BOTH, expand=True)

    def preprocess_data(self):
        self.status_label.pack(pady=10)
        self.after(100, self.extractor.preprocess_files)
        self.after(100, self.finish_loading)

    def update_after_preprocessing(self):
        self.status_label.pack_forget()
        tk.Label(self, text="Enter Patent Number:").pack(pady=10)
        self.patent_number_entry.pack(pady=10)
        self.search_button.pack(pady=10)
        self.results_text.pack(fill=tk.BOTH, expand=True)

    def on_search(self):
        patent_number = self.patent_number_entry.get().strip()
        if not patent_number:
            messagebox.showwarning("Warning", "Patent number cannot be empty.")
            return
        file_path = self.extractor.find_xml_file_for_patent(patent_number)
        if file_path:
            elements = self.extractor.list_all_elements(file_path)
            self.results_text.delete('1.0', tk.END)
            for element in elements:
                self.results_text.insert(tk.END, element + '\n')
        else:
            messagebox.showerror("Error", "The patent provided does not exist.")

if __name__ == "__main__":
    data_dir, sample_zip_path, sample_dir = setup_paths()
    extractor = Extractor(sample_dir)
    extractor.extract_zip_if_needed(sample_zip_path, sample_dir)
    app = PatentApp(extractor)
    app.mainloop()
