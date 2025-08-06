import xml.etree.ElementTree as ET

# Parse the XML file
tree = ET.parse('model.xml')
root = tree.getroot()

# Loop through each TcClass and extract attributeNames from TcAttribute
for tc_class in root.findall(".//TcClass"):
    class_name = tc_class.attrib.get("className")
    print(f"\nClass: {class_name}")

    for attr in tc_class.findall("TcAttribute"):
        attr_name = attr.attrib.get("attributeName")
        print(f"  - {attr_name}")
