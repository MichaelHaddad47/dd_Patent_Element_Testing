import xml.etree.ElementTree as ET
import os
import zipfile
import time

# Extracts ZIP file, then extracts XML files and finds elements within them
    # Verifies that the file is an XML file
    # Returns error if XML file cannot be parsed
class Extractor:
    @staticmethod
    def extract_elements_from_xml(file_path):
        elements = set()
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            for elem in root.iter():
                elements.add(elem.tag)
        except ET.ParseError as e:
            print(f"Error parsing {file_path}: {e}")
        return elements

    @staticmethod
    def extract_zip(zip_path, extract_to):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

    @staticmethod
    def find_elements_in_xml_files(xml_files_dir):
        master_set = set()
        xml_files = [f for f in os.listdir(xml_files_dir) if f.endswith('.xml')]
        for xml_file in xml_files:
            file_path = os.path.join(xml_files_dir, xml_file)
            elements = Extractor.extract_elements_from_xml(file_path)
            master_set.update(elements)
        return master_set

def write_master_list(data_dir, master_set):
    output_path = os.path.join(data_dir, 'Output_ListOfAllElementsInXMLFiles.txt')
    with open(output_path, 'w') as output_file:
        for element in sorted(master_set):
            output_file.write(f"{element}\n")

def setup_paths():
    data_dir = 'C:/Users/haddadm1/Desktop/Random Things/dd_Patent_Element_Testing'
    sample_zip_path = os.path.join(data_dir, 'Sample.zip')
    sample_dir = os.path.join(data_dir, 'Sample')
    return data_dir, sample_zip_path, sample_dir

# For error handling
def check_sample_exists(sample_zip_path, sample_dir):
    if not os.path.exists(sample_dir):
        Extractor.extract_zip(sample_zip_path, sample_dir)

# Executes functions in sequential order
def main():
    start_time = time.time()
    data_dir, sample_zip_path, sample_dir = setup_paths()
    check_sample_exists(sample_zip_path, sample_dir)
    master_set = Extractor.find_elements_in_xml_files(sample_dir)
    write_master_list(data_dir, master_set)
    end_time = time.time()
    print(f"The script took {end_time - start_time:.4f} seconds to complete.")

if __name__ == "__main__":
    main()
