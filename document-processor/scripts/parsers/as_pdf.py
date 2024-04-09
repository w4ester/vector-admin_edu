import os, fitz
from langchain.document_loaders import PyMuPDFLoader
from ..utils import guid, file_creation_time, move_source, tokenize
from unidecode import unidecode

# Process all text-related documents.
def as_pdf(**kwargs):
  parent_dir = kwargs.get('directory', 'hotdir')
  filename = kwargs.get('filename')
  ext = kwargs.get('ext', '.txt')
  remove = kwargs.get('remove_on_complete', False)
  fullpath = f"{parent_dir}/{filename}{ext}"

  print(f"-- Working {fullpath} --")
  loader = PyMuPDFLoader(fullpath)
  pages = loader.load()

  if len(pages) == 0:
    print(f"{fullpath} parsing resulted in no pages - nothing to do.")
    return []
  
  # Set doc to the first page so we can still get the metadata from PyMuPDF but without all the unicode issues.
  doc = pages[0]
  del loader
  del pages

  page_content = ''
  for page in fitz.open(fullpath):
    print(f"-- Parsing content from pg {page.number} --")
    page_content += unidecode(page.get_text('text'))

  if len(page_content) == 0:
    print("Resulting page content was empty - no text could be extracted from the document.")
    return []
  
  title = doc.metadata.get('title')
  author = doc.metadata.get('author')
  subject = doc.metadata.get('subject')
  metadata = {
    'id': guid(),
    'url': "file://"+os.path.abspath(f"{parent_dir}/processed/{filename}{ext}"),
    'title': title if title else f"{filename}{ext}",
    'docAuthor': author if author else 'No author found',
    'description': subject if subject else 'No description found.',
    'docSource': 'pdf file uploaded by the user.',
    'chunkSource': f"{filename}{ext}",
    'published': file_creation_time(fullpath),
    'wordCount': len(page_content), # Technically a letter count :p
    'pageContent': page_content,
    'token_count_estimate': len(tokenize(page_content))
  }

  move_source(parent_dir, f"{filename}{ext}", remove=remove)
  print(f"[SUCCESS]: {filename}{ext} converted & ready for embedding.\n")
  return [metadata]
