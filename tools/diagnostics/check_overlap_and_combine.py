import fitz
import re
import pandas as pd

def check_overlap_and_combine():
    df_45 = pd.read_csv('brenchmark/justor benchmark verified 45.csv')
    print(f"df_45 rows: {len(df_45)}")
    print("df_45 columns:", list(df_45.columns))

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

    # Clean and deduplicate questions from Correction 150 question.pdf
    seen_q = set()
    clean_qs = []
    for q in questions:
        cq = re.sub(r'\s+', ' ', q['question']).strip().rstrip('●').strip()
        if cq not in seen_q:
            seen_q.add(cq)
            ca = re.sub(r'\s+', ' ', q['answer']).strip()
            if "Q37:" in ca:
                continue
            clean_qs.append({
                'act': q['act'],
                'orig_qid': q['q_id'],
                'question': cq,
                'answer': ca
            })

    # Check overlap with df_45
    df_45_qs = set(df_45['question'].apply(lambda x: re.sub(r'\s+', ' ', str(x)).strip().rstrip('●').strip()))
    overlap = seen_q.intersection(df_45_qs)
    print(f"Overlap count between df_45 and clean PDF questions: {len(overlap)}")
    if overlap:
        print("Overlapping questions:")
        for o in overlap:
            print(f"  - {o[:100]}")

if __name__ == '__main__':
    check_overlap_and_combine()
