# Message Generator

Generates classes to support message generation (for ISO 20022 payment messages)

## Create the message (just using the repo and not the package)

```bash
python -m pip install -r requirements.txt
./build_classes_from_xsds.py
python create_msg_1.py
```


## Message types?
Currently only supports PACS messages as well as HEAD (header documents for the PACS).
