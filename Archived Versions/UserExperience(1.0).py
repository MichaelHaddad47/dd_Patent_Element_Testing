'''

INITIAL RELEASE

SOME TESTING HAS BEEN DONE
This uses terminal, no GUI has been implemented

**Important notes**
- Forces exact matching of user-input patent numbers to <doc-number> in XML files, but...
allows leading zeros in patent number input.

- Error handling, includes:
    - Verifying and processing only XML files
    - Mandatory user input for patent numbers
    - Mandatory user input for element searching

- Handles both text and sub-elements within requested XML elements

'''

import xml.etree.ElementTree as ET
import xml.dom.minidom
import os
import zipfile

class Colors:
    RED = "\033[91m"
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    RESET = "\033[0m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"

    @staticmethod
    def color_text(text, color):
        return f"{color}{text}{Colors.RESET}"

    @staticmethod
    def red(text):
        return Colors.color_text(text, Colors.RED)

    @staticmethod
    def bold(text):
        return Colors.color_text(text, Colors.BOLD)

    @staticmethod
    def italic(text):
        return Colors.color_text(text, Colors.ITALIC)

    @staticmethod
    def green(text):
        return Colors.color_text(text, Colors.GREEN)

    @staticmethod
    def blue(text):
        return Colors.color_text(text, Colors.BLUE)

    @staticmethod
    def yellow(text):
        return Colors.color_text(text, Colors.YELLOW)

class Extractor:
    @staticmethod
    def prettify_xml_element(element):
        pretty_xml_as_string = ''
        for child in list(element):
            child_string = ET.tostring(child, 'unicode')
            parsed_child = xml.dom.minidom.parseString(child_string)
            child_pretty_string = '\n'.join(
                [line for line in parsed_child.toprettyxml(indent="  ").split('\n') if line.strip() and not line.startswith('<?xml')]
            )
            pretty_xml_as_string += child_pretty_string + '\n'
        return pretty_xml_as_string.strip()

    @staticmethod
    def extract_first_element_value_from_xml(file_path, element_names):
        element_values = {element_name: None for element_name in element_names}
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            for element_name in element_names:
                for element in root.findall('.//{}'.format(element_name)):
                    if list(element):
                        element_values[element_name] = Extractor.prettify_xml_element(element)
                        break
                    elif element.text and element.text.strip():
                        element_values[element_name] = element.text
                        break
        except ET.ParseError as e:
            print(f"Error parsing {file_path}: {e}")
        return element_values

    @staticmethod
    def list_all_elements(file_path):
        elements = set()
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            for elem in root.iter():
                elements.add(elem.tag)
        except ET.ParseError as e:
            print(f"Error parsing {file_path}: {e}")
        return sorted(elements)

    @staticmethod
    def find_xml_file_for_patent(xml_dir, patent_number):
        for filename in os.listdir(xml_dir):
            if not filename.endswith('.xml'):
                continue
            file_path = os.path.join(xml_dir, filename)
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                for doc_num in root.findall('.//doc-number'):
                    if doc_num.text == patent_number or doc_num.text.lstrip('0') == patent_number.lstrip('0'):
                        return file_path
            except ET.ParseError as e:
                print(f"Error parsing {file_path}: {e}")
        return None

    @staticmethod
    def extract_zip_if_needed(zip_path, extract_to):
        if not os.path.exists(extract_to):
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)

# Constants for the paths
def setup_paths():
    data_dir = 'C:/Users/haddadm1/Desktop/Random Things/dd_Patent_Element_Testing'
    sample_zip_path = os.path.join(data_dir, 'Sample.zip')
    sample_dir = os.path.join(data_dir, 'Sample')
    return data_dir, sample_zip_path, sample_dir

def get_user_input(prompt, error_message):
    user_input = input(prompt).strip()
    while not user_input:
        print(Colors.red(error_message))
        user_input = input(prompt).strip()
    return user_input

def display_element_content(patent_number, element_name, value):
    print(f"\nContent for '{element_name}' in patent {patent_number}:")
    if value:
        if '<' in value:
            print("Sub elements found in '{}':".format(element_name))
            print(value)
        else:
            print(value)
    else:
        print(Colors.red("No content found."))

def main():
    data_dir, sample_zip_path, sample_dir = setup_paths()
    Extractor.extract_zip_if_needed(sample_zip_path, sample_dir)

    patent_number = get_user_input("\nEnter the patent number: ", "Patent number cannot be empty.")
    xml_file_path = Extractor.find_xml_file_for_patent(sample_dir, patent_number)

    if not xml_file_path:
        print(Colors.bold(Colors.red("The patent provided does not exist.")))
        return

    print(f"\nListing all elements for patent {patent_number}:\n")
    all_elements = Extractor.list_all_elements(xml_file_path)
    for element in all_elements:
        print(element)

    elements_input = get_user_input(Colors.bold("\nPlease enter at least one element name, separated by commas: "), "Input cannot be empty.")
    element_names = [element.strip() for element in elements_input.split(',')]

    element_values = Extractor.extract_first_element_value_from_xml(xml_file_path, element_names)
    for element_name, value in element_values.items():
        display_element_content(patent_number, element_name, value)

if __name__ == "__main__":
    main()
