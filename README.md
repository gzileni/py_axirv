# Py-AXIRV

Py-AXIRV is a Python package installable via pip that allows you to download and upload articles from arXiv directly to S3 storage.

## Installation

```bash
pip install py-axirv
```

## Usage

Example usage to upload arXiv articles to S3:

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

Make sure to set the AWS environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_BUCKET_NAME`) before running the script.

Example usage to upload arXiv articles to a local path:

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

# or configure a different download folder
axirv.set_path_download('/downloads/axirv')

axirv.load()
```

## License

This project is distributed under the MIT license.