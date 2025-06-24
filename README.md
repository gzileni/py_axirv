# Py-AXIRV

Py-AXIRV è un pacchetto Python installabile tramite pip che permette di scaricare e caricare articoli da arXiv direttamente su uno storage S3.

## Installazione

```bash
pip install py-axirv
```

## Utilizzo

Esempio di utilizzo per caricare articoli arXiv su S3:

```python
import urllib.request as libreq
import os
from py_axirv.axirv import ArxivLoader
import xml.etree.ElementTree as ET

documents = []

axirv = ArxivLoader(
    max_results=10000,
    start=0,
    type_storage='s3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
    bucket_name=os.getenv("AWS_BUCKET_NAME"),
    prefix='arxiv'
)

axirv.load()
```

Assicurati di impostare le variabili d'ambiente AWS (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_BUCKET_NAME`) prima di eseguire lo script.

Esempio di utlizzo per caricare articoli arXiv su un percorso locale:

```python
import urllib.request as libreq
import os
from py_axirv.axirv import ArxivLoader
import xml.etree.ElementTree as ET

documents = []

axirv = ArxivLoader(
    max_results=10000,
    start=0,
    type_storage='local',
    path_download='tmp'
)

# oppure configurare una cartella diversa di download
axirv.set_path_download('/downloads/axirv')

axirv.load()
```

## Licenza

Questo progetto è distribuito sotto licenza MIT.