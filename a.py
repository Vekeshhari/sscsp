from docx import Document
from docxcompose.composer import Composer

master = Document("ENDSEM_LAB_SSE.docx")
addition = Document("phase11_secure_build.docx")

composer = Composer(master)
composer.append(addition)
composer.save("ENDSEM_LAB_SSE.docx")

print("[OK] Merged into ENDSEM_LAB_SSE.docx")