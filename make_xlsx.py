import pyiso20022.tools as isotools

isotools.camt053_to_excel("example_files/gs_camt/camt053_001_02.xml",
                          "camt053_excel.xlsx")

hed = isotools.camt053_to_df("example_files/gs_camt/camt053_001_02.xml").head()
print(hed)
