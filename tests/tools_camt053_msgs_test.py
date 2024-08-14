import pytest
from pyiso20022.tools.camt053_extract import *
import tempfile
import pandas as pd


@pytest.mark.parametrize("entry_reference, msg_id", [
        ("52198301", "20230928LTERMID100000312221631FT01")
    ])
def test_pandas_df_camt053_001_02(entry_reference, msg_id):

    df = camt053_to_df("example_files/gs_camt/camt053_001_02.xml") 

    result = df[df['Entry Reference'] == entry_reference]["Entry Details / Transaction Details / References / Message Identification"]

    assert result.values[0] == msg_id


@pytest.mark.parametrize("entry_reference, msg_id", [
        ("52198301", "20230928LTERMID100000312221631FT01")
    ])
def test_excel_camt053_001_02(entry_reference, msg_id):

    tmp_file = tempfile.NamedTemporaryFile(suffix=".xlsx")
    tmp_file_name = tmp_file.name

    camt053_to_excel("example_files/gs_camt/camt053_001_02.xml", tmp_file_name)

    df = pd.read_excel(tmp_file_name, sheet_name='Sheet1')

    tmp_file.close()

    result = df[df['Entry Reference'].astype(str) == str(entry_reference)]["Entry Details / Transaction Details / References / Message Identification"]
    assert result.values[0] == msg_id
