from lxml import etree
import pandas as pd


def modify_key(key, translate=True):
    return key.split('}')[-1]


def parse_element(element, parent_name=''):
    data_dict = {}
    for child in element:
        child_name = f"{parent_name}_{child.tag}" if parent_name else child.tag

        if len(child):
            data_dict.update(parse_element(child, child_name))
        else:
            data_dict[child_name] = child.text
            
    modified_dict = {modify_key(k): v for k, v in data_dict.items()}

    return modified_dict


def camt053_to_excel(xml_fname, excel_fname):
    with open(xml_fname, "rb") as xml_file:
        xml_data = xml_file.read()

    root = etree.fromstring(xml_data)
    data = []
    elements = root.xpath('//*[local-name()="Ntry"]')

    for record in elements:
        record_data = parse_element(record)
        data.append(record_data)

    df = pd.DataFrame(data)

    df.to_excel(excel_fname, index=False)


camt053_to_excel("example_files/gs_camt/camt053_001_02.xml", "camt053_001_02.xlsx")
