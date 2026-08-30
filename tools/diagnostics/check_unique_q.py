import fitz
import re
import pandas as pd

def check_unique_q():
    pdf_path = 'brenchmark/Correction 150 question.pdf'
    doc = fitz.open(pdf_path)
    full_text = [page.get_text() for page in doc]
    text = "\n".join(full_text)

    lines = text.split('\n')
    questions = []
    current_act = ""
    current_q_id = ""
    current_q_text = ""
    current_ans_text = ""
    state = "NONE"

    sec_heading_re = re.compile(r'^Section\s+\d+:\s*(.+)', re.IGNORECASE)
    q_start_re = re.compile(r'^Q(\d+):\s*(.*)', re.IGNORECASE)

    for line in lines:
        l_strip = line.strip()
        if not l_strip:
            continue
        
        m_sec = sec_heading_re.match(l_strip)
        if m_sec:
            current_act = m_sec.group(1).strip()
            continue

        m_q = q_start_re.match(l_strip)
        if m_q:
            if current_q_id and current_q_text:
                questions.append({
                    'act': current_act,
                    'q_id': current_q_id,
                    'question': current_q_text.strip(),
                    'answer': current_ans_text.strip()
                })
            current_q_id = m_q.group(1)
            current_q_text = m_q.group(2)
            current_ans_text = ""
            state = "Q"
            continue

        if l_strip.startswith("●") or l_strip.startswith("Answer Details:"):
            state = "ANS"
            current_ans_text += " " + re.sub(r'^[●\s]+', '', l_strip)
            continue

        if state == "Q":
            current_q_text += " " + l_strip
        elif state == "ANS":
            current_ans_text += " " + l_strip

    if current_q_id and current_q_text:
        questions.append({
            'act': current_act,
            'q_id': current_q_id,
            'question': current_q_text.strip(),
            'answer': current_ans_text.strip()
        })

    # Deduplicate by clean question text
    seen_q = set()
    dedup = []
    for q in questions:
        # clean question text slightly (remove extra spaces)
        clean_q = re.sub(r'\s+', ' ', q['question']).strip()
        if clean_q not in seen_q:
            seen_q.add(clean_q)
            dedup.append(q)

    with open('unique_check.txt', 'w', encoding='utf-8') as f:
        f.write(f"Total extracted: {len(questions)}\n")
        f.write(f"Total unique question texts: {len(dedup)}\n")
        f.write("\nUnique questions:\n")
        for idx, q in enumerate(dedup, 1):
            f.write(f"{idx:03d} | Orig Q{q['q_id']:>3} | Act: {q['act'][:30]:<30} | Q: {q['question']}\n")

if __name__ == '__main__':
    check_unique_q()
