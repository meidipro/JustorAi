import fitz
import re
import pandas as pd

def analyze_dups():
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

    by_id = {}
    for idx, q in enumerate(questions):
        by_id.setdefault(q['q_id'], []).append((idx, q))

    with open('dups_instances_detail.txt', 'w', encoding='utf-8') as f:
        for qid, insts in sorted(by_id.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999):
            if len(insts) > 1:
                f.write(f"\n=================== Q_ID {qid} ({len(insts)} instances) ===================\n")
                for idx, q in insts:
                    f.write(f"Index {idx} | Act: {q['act']}\n")
                    f.write(f"  Question: {q['question']}\n")
                    f.write(f"  Answer:   {q['answer']}\n")

if __name__ == '__main__':
    analyze_dups()
