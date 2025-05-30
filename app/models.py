from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import uuid

@dataclass
class Dataset:
    id: str
    name: str
    description: Optional[str] = None
    domainname: Optional[str] = None
    metatag1name: Optional[str] = None
    metatag2name: Optional[str] = None
    chunksize: int = 500
    chunkoverlap: int = 50
    status: str = 'created'
    createdat: Optional[datetime] = None

@dataclass
class Page:
    id: str
    datasetid: str
    url: str
    title: Optional[str] = None
    rawhtml: Optional[str] = None
    cleantext: Optional[str] = None
    wordcount: Optional[int] = None
    status: str = 'pending'
    errormessage: Optional[str] = None
    createdat: Optional[datetime] = None

@dataclass
class Chunk:
    id: str
    pageid: str
    text: str
    summary: Optional[str] = None
    contextretrieval: Optional[str] = None
    domainmeta1: Optional[str] = None
    domainmeta2: Optional[str] = None
    embedding: Optional[List[float]] = None
    tokencount: Optional[int] = None
    status: str = 'created'
    createdat: Optional[datetime] = None

@dataclass
class SearchResult:
    chunk_id: str
    text: str
    summary: Optional[str]
    contextretrieval: Optional[str]
    domainmeta1: Optional[str]
    domainmeta2: Optional[str]
    url: str
    title: Optional[str]
    similarity: float
