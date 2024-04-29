import xml.etree.ElementTree as ET
import os
import zipfile
import time
import re

'''

link used for Patents.txt:
https://www.wipo.int/standards/en/st96/v7-1/annex-iii/index.html

'''

# Manages element name variations for XML parsing, includes:
    # lowercase/UPERCASE
    # with(out) spaces
    # dashes
class ElementVariations:
    @staticmethod
    def dash_to_camel(s):
        return ''.join(word.capitalize() for word in s.split('-'))

    @staticmethod
    def generate_variations(patent_element):
        lowercase = patent_element.lower()
        with_spaces = re.sub(r"(?<!^)(?=[A-Z])", " ", patent_element).lower()
        no_spaces = re.sub(r" ", "", patent_element).lower()
        with_dashes = re.sub(r"(?<!^)(?=[A-Z])", "-", patent_element).lower()
        dash_to_camel = ElementVariations.dash_to_camel(with_dashes)
        
        variations =  {
            lowercase: patent_element,
            with_spaces: patent_element,
            no_spaces: patent_element,
            with_dashes: patent_element,
            dash_to_camel: patent_element,
        }
    
        return variations

    @staticmethod
    def normalize_element(tag):
        normalized = tag.split('}', 1)[-1].lower()
        return ElementVariations.dash_to_camel(normalized)

# Extracts ZIP file, then extracts XML files and finds elements within them
    # Verifies that the file is an XML file
    # Returns error if XML file cannot be parsed
class Extractor:
    @staticmethod
    def extract_elements_from_xml(file_path):
        if not file_path.lower().endswith('.xml'):
            return set()
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            return {elem.tag for elem in root.iter()}
        except ET.ParseError as e:
            print(f"Error parsing {file_path}: {e}")
            return set()

    @staticmethod
    def find_elements_in_xml_files(xml_files_dir, variations_map):
        master_list = set()
        xml_files = os.listdir(xml_files_dir)
        for xml_file in xml_files:
            file_path = os.path.join(xml_files_dir, xml_file)
            if not os.path.isfile(file_path):
                continue
            elements = Extractor.extract_elements_from_xml(file_path)
            for element in elements:
                normalized_element = ElementVariations.normalize_element(element)
                if normalized_element in variations_map:
                    master_list.add(variations_map[normalized_element])
        return master_list

    @staticmethod
    def extract_zip(zip_path, extract_to):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

def setup_paths():
    data_dir = 'C:/Users/haddadm1/Desktop/Random Things/dd_Patent_Element_Testing'
    patents_path = os.path.join(data_dir, 'Patents.txt')
    sample_zip_path = os.path.join(data_dir, 'Sample.zip')
    sample_dir = os.path.join(data_dir, 'Sample')
    
    return data_dir, patents_path, sample_zip_path, sample_dir

# For error handling
def check_for_nested_directory(sample_dir):
    nested_sample_dir = os.path.join(sample_dir, 'Sample')
    if os.path.exists(nested_sample_dir):
        for file in os.listdir(nested_sample_dir):
            os.rename(os.path.join(nested_sample_dir, file), os.path.join(sample_dir, file))
        os.rmdir(nested_sample_dir)

# For error handling
def check_sample_exists(sample_zip_path, sample_dir):
    if not os.path.exists(sample_dir):
        Extractor.extract_zip(sample_zip_path, sample_dir)

# Creates a map of variations for each element in the patents file
def create_variations_map(patents_path):
    variations_map = {}
    with open(patents_path, 'r') as patents_file:
        for line in patents_file:
            element = line.strip()
            if element:
                variations = ElementVariations.generate_variations(element)
                for variation, original in variations.items():
                    variations_map[variation] = original
    return variations_map

def write_master_list(data_dir, master_list_of_elements):
    output_path = os.path.join(data_dir, 'Output_ListOfPatentsInXMLFiles.txt')
    with open(output_path, 'w') as output_file:
        for element in sorted(master_list_of_elements):
            output_file.write(f"{element}\n")

# Executes functions in sequential order
def main():
    start_time = time.time()
    
    data_dir, patents_path, sample_zip_path, sample_dir = setup_paths()
    check_sample_exists(sample_zip_path, sample_dir)
    check_for_nested_directory(sample_dir)
    variations_map = create_variations_map(patents_path)
    master_list_of_elements = Extractor.find_elements_in_xml_files(sample_dir, variations_map)
    write_master_list(data_dir, master_list_of_elements)
    
    end_time = time.time()
    print(f"The script took {end_time - start_time:.4f} seconds to complete.")

if __name__ == "__main__":
    main()
