import fitz
import re

def check_pdf_pages():
    doc = fitz.open('brenchmark/Correction 150 question.pdf')
    print(f"Total pages in Correction 150 question.pdf: {len(doc)}")
    
    q_start_re = re.compile(r'^Q(\d+):\s*(.*)', re.IGNORECASE)
    for pno in range(len(doc)):
        text = doc[pno].get_text()
        qs = []
        for line in text.split('\n'):
            m = q_start_re.match(line.strip())
            if m:
                qs.append(f"Q{m.group(1)}")
        print(f"Page {pno+1:2d}: {len(qs):2d} questions -> {qs}")

if __name__ == '__main__':
    check_pdf_pages()
