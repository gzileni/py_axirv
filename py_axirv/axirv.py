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
            app_root = os.path.dirname(os.path.abspath(__file__))
            self.path = os.path.join(app_root, self.path_download)
        
        query = "all" 
        if self.query:
            query = f"{query}:{self.query}"
        
        self.url += f"{query}&start={self.start}&max_results={self.max_results}"

    def set_path_download(self, path: str):
        """
        Set the path for downloading files.
        Args:
        
        """
        self.path_download = path

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
            if arxiv_id is None:
                continue
            else:
                pdf_filename = arxiv_id.replace('.', '_').replace('/', '_').replace(':', '').replace('http', '') + ".pdf"
                pdf_link : str | None = ""
                for link in entry.findall('atom:link', self.ns):
                    if link.attrib.get('title') == "pdf":
                        pdf_link = link.attrib.get('href')

                # Scarica PDF (se disponibile)
                pdf_path : str = ""
                
                if pdf_link is None:
                    print(f"No PDF link found for {arxiv_id}.")
                    continue
                
                if self.type_storage == 'local':
                    if self.path is None:
                        raise ValueError("Path for local storage is not set.")
                    pdf_path = os.path.join(self.path, pdf_filename)
                    if not os.path.exists(self.path):
                        print(f"Creating directory {self.path} for PDF storage.")
                        os.makedirs(self.path)
                        
                    try:
                        with libreq.urlopen(pdf_link) as pdf_url, open(pdf_path, 'wb') as f:
                            f.write(pdf_url.read())   
                        print(f"PDF {pdf_filename} downloaded to {self.path}.")
                    except Exception as e:
                        print(f"Errore nel download PDF {pdf_link}: {e}")
                        continue
                elif self.type_storage == 's3':
                    try:
                        with libreq.urlopen(pdf_link) as pdf_url:                        
                            buffer = pdf_url.read()
                            if self.type_storage == 'local':
                                pdf_url.write(buffer)
                            elif self.type_storage == 's3':
                                # Placeholder for S3 storage logic
                                # Assuming boto3 or similar library is used for S3 operations
                                # This part should be implemented based on the specific S3 client being used
                                object_name = f"{self.prefix}/{pdf_filename}"
                                self.s3.upload_bytes(bytes_data=buffer, object_name=object_name, format_file='pdf')
                                print(f"PDF {pdf_filename} uploaded to S3 bucket {self.bucket_name} with prefix {self.prefix}.")
                    except Exception as e:
                        print(f"Errore nel download PDF {pdf_link}: {e}")

    def _load_from_arxiv_api(self):
        """
        Load documents from the arXiv API.
        """
        with libreq.urlopen(self.url) as url:
            r = url.read()
        return ET.fromstring(r)    




