import fitz
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def inspect_qa_diff():
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

    seen_qa = set()
    clean_qa = []
    for q in questions:
        qa_key = (q['question'].strip(), q['answer'].strip())
        if qa_key not in seen_qa:
            seen_qa.add(qa_key)
            clean_qa.append(q)

    qid_counts = {}
    for q in clean_qa:
        qid_counts[q['q_id']] = qid_counts.get(q['q_id'], 0) + 1

    print("Q_IDs appearing multiple times in clean_qa:")
    for qid, c in sorted(qid_counts.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999):
        if c > 1:
            print(f"  Q_ID {qid}: {c} times")
            for q in clean_qa:
                if q['q_id'] == qid:
                    print(f"    Q: {q['question'][:80]}")
                    print(f"    A: {q['answer'][:80]}")

if __name__ == '__main__':
    inspect_qa_diff()
