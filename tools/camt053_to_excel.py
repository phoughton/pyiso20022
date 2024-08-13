from lxml import etree
import re
import pandas as pd
from pyiso20022.tools import lookup


def _iso20022_term_translator(mnemonic):
    new_name = ""
    list_of_mnems = re.split(r'(?<=[a-z])(?=[A-Z])', mnemonic)
    for key in list_of_mnems:
        new_name += lookup.mnemonics.get(key, key)
        new_name += " "

    return new_name.strip()


def _modify_key(key, translate=True):
    clean_mnems = key.split('}')[-1]
    if translate:
        clean_mnems = _iso20022_term_translator(clean_mnems)
    return clean_mnems


def _parse_element(element, parent_name='', translate=True):
    data_dict = {}
    for child in element:
        child_name = f"{parent_name}_{child.tag}" if parent_name else child.tag

        if len(child):
            data_dict.update(_parse_element(child,
                                            child_name,
                                            translate=translate))
        else:
            data_dict[child_name] = child.text

    modified_dict = {_modify_key(k, translate=translate): v for k, v in data_dict.items()}

    return modified_dict


def camt053_to_df(xml_fname, translate=True):
    """
    Create a pandas DataFrame from a camt053 xml file
    """
    with open(xml_fname, "rb") as xml_file:
        xml_data = xml_file.read()

    root = etree.fromstring(xml_data)
    data = []
    elements = root.xpath('//*[local-name()="Ntry"]')

    for record in elements:
        record_data = _parse_element(record, translate=translate)
        data.append(record_data)

    return pd.DataFrame(data)


def camt053_to_excel(xml_fname, excel_fname, translate=True):
    """
    Create an excel file from a camt053 xml file
    """
    df = camt053_to_df(xml_fname, translate)
    df.to_excel(excel_fname, index=False)
