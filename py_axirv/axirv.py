import urllib.request as libreq
import os
from langchain_core.documents import Document
import xml.etree.ElementTree as ET
from typing import Literal
from pyaws_s3 import S3Client

TypeStorage = Literal['local', 's3']

class ArxivLoader:
    """Loader for arXiv API XML data."""
    
    max_results: int = 1000
    start : int = 0
    query: str = ''
    url : str = 'http://export.arxiv.org/api/query?search_query='
    path_download: str = '.arxiv'
    path : str | None = None
    type_storage: TypeStorage = 's3'
    
    aws_access_key_id : str | None = None
    aws_secret_access_key : str | None = None
    region_name : str | None = None
    bucket_name : str | None = None
    prefix: str = 'arxiv'
    s3 : S3Client
    
    ns = {
        'atom': 'http://www.w3.org/2005/Atom',
        'arxiv': 'http://arxiv.org/schemas/atom',
        'opensearch': 'http://a9.com/-/spec/opensearch/1.1/'
    }

    def __init__(self, **kwargs):
        """
        Initialize the ArxivLoader with optional parameters.
        Args:
            **kwargs: Optional parameters to configure the loader.
        """
        self.max_results = kwargs.get('max_results', self.max_results)
        self.start = kwargs.get('start', self.start)
        self.query = kwargs.get('query', self.query)
        
        self.type_storage = kwargs.get('type_storage', self.type_storage)
        
        if self.type_storage not in ['local', 's3']:
            raise ValueError("type_storage must be either 'local' or 's3'")
        
        if self.type_storage == 's3':
            self.aws_access_key_id = kwargs.get("aws_access_key_id", os.getenv("AWS_ACCESS_KEY_ID"))
            self.aws_secret_access_key = kwargs.get("aws_secret_access_key", os.getenv("AWS_SECRET_ACCESS_KEY"))
            self.region_name = kwargs.get("region_name", os.getenv("AWS_REGION"))
            self.bucket_name = kwargs.get("bucket_name", os.getenv("AWS_BUCKET_NAME"))
            self.prefix = kwargs.get("prefix", self.prefix)
            if not all([kwargs.get("aws_access_key_id"), kwargs.get("aws_secret_access_key"), 
                        kwargs.get("region_name"), kwargs.get("bucket_name")]):
                raise ValueError("For S3 storage, aws_access_key_id, aws_secret_access_key, region_name, and bucket_name must be provided.")
            
            self.s3 = S3Client(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            )
            
        if self.type_storage == 'local':
            self.path_download = kwargs.get('path_download', self.path_download)
            if not self.path_download:
                raise ValueError("For local storage, path_download must be provided.")
            self.path = self.set_path_download(self.path_download)
        
        query = "all" 
        if self.query:
            query = f"{query}:{self.query}"
        
        self.url += f"{query}&start={self.start}&max_results={self.max_results}"

    def set_path_download(self, path: str):
        """
        Set the path for downloading files.
        Args:
        
        """
        app_root = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(app_root, path)

    def load(self):
        """
        Load documents from the arXiv API and download PDFs if available.
        Returns:
            None
        """
        root = self._load_from_arxiv_api()

        for entry in root.findall('atom:entry', self.ns):
            # Ricava i dati principali
            atom_it = entry.find('atom:id', self.ns)
            
            if atom_it is None:
                arxiv_id = ""
            else:
                arxiv_id = atom_it.text if atom_it is not None else ""
                
            # PDF link
            pdf_link = ""
            for link in entry.findall('atom:link', self.ns):
                if link.attrib.get('title') == "pdf":
                    pdf_link = link.attrib.get('href')

            if arxiv_id is not None:
                # Scarica PDF (se disponibile)
                pdf_path : str = ""
                if pdf_link:
                    pdf_filename = arxiv_id.replace('.', '_').replace('/', '_').replace(':', '').replace('http', '') + ".pdf"
                    if self.type_storage == 'local':
                        
                        if self.path is None:
                            raise ValueError("Path for local storage is not set.")
                        
                        pdf_path = os.path.join(self.path, pdf_filename)
                        
                        if not os.path.exists(self.path):
                            os.makedirs(self.path)
                        try:
                            with libreq.urlopen(pdf_link) as pdf_url, open(pdf_path, 'wb') as f:
                                buffer = pdf_url.read()
                                if self.type_storage == 'local':
                                    f.write(buffer)
                                elif self.type_storage == 's3':
                                    # Placeholder for S3 storage logic
                                    # Assuming boto3 or similar library is used for S3 operations
                                    # This part should be implemented based on the specific S3 client being used
                                    pass
                        except Exception as e:
                            print(f"Errore nel download PDF {pdf_link}: {e}")
                            pdf_path = ""
                else:   
                    raise ValueError(f"PDF link not found for arXiv ID: {arxiv_id}")

    def _load_from_arxiv_api(self):
        """
        Load documents from the arXiv API.
        """
        with libreq.urlopen(self.url) as url:
            r = url.read()
        return ET.fromstring(r)    




