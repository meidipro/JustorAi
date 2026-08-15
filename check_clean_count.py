import fitz
import re
import pandas as pd

def check_clean():
    doc = fitz.open('brenchmark/Correction 150 question.pdf')
    text = "\n".join([page.get_text() for page in doc])
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

    # Method 1: Remove exact duplicate (question, answer) pairs
    seen_qa = set()
    clean_qa = []
    for q in questions:
        qa_key = (q['question'].strip(), q['answer'].strip())
        if qa_key not in seen_qa:
            seen_qa.add(qa_key)
            clean_qa.append(q)

    # Method 2: Remove exact duplicate (q_id, question, answer) pairs
    seen_id_qa = set()
    clean_id_qa = []
    for q in questions:
        id_qa_key = (q['q_id'].strip(), q['question'].strip(), q['answer'].strip())
        if id_qa_key not in seen_id_qa:
            seen_id_qa.add(id_qa_key)
            clean_id_qa.append(q)

    # Method 3: Group by q_id and take first occurrence of each q_id
    seen_id = set()
    clean_id = []
    for q in questions:
        qid = q['q_id'].strip()
        if qid not in seen_id:
            seen_id.add(qid)
            clean_id.append(q)

    # Method 4: Group by question text only and take first occurrence
    seen_q_text = set()
    clean_q_text = []
    for q in questions:
        qt = q['question'].strip()
        if qt not in seen_q_text:
            seen_q_text.add(qt)
            clean_q_text.append(q)

    print(f"Total extracted blocks: {len(questions)}")
    print(f"Method 1 (unique question+answer): {len(clean_qa)}")
    print(f"Method 2 (unique q_id+question+answer): {len(clean_id_qa)}")
    print(f"Method 3 (unique q_id): {len(clean_id)}")
    print(f"Method 4 (unique question text): {len(clean_q_text)}")

if __name__ == '__main__':
    check_clean()
