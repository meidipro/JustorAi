import fitz
import re
import pandas as pd

def inspect_details():
    pdf_path = 'brenchmark/Correction 150 question.pdf'
    doc = fitz.open(pdf_path)
    full_text = []
    for page in doc:
        full_text.append(page.get_text())
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

    print(f"Total extracted blocks: {len(questions)}")
    # Check distinct q_id values and if any are duplicates
    q_ids = [q['q_id'] for q in questions]
    print(f"Unique q_ids: {len(set(q_ids))}")
    
    # Print summary of acts and question numbers
    df_q = pd.DataFrame(questions)
    print("Q_IDs summary:")
    print(df_q['q_id'].tolist())
    
    # Let's see if there are missing numbers between 1 and 150 or what
    all_int_ids = sorted(list(set([int(x) for x in q_ids if x.isdigit()])))
    print(f"Min ID: {min(all_int_ids)}, Max ID: {max(all_int_ids)}, Count of unique integer IDs: {len(all_int_ids)}")
    missing = [i for i in range(1, max(all_int_ids)+1) if i not in all_int_ids]
    print(f"Missing IDs in range 1..{max(all_int_ids)}: {missing}")

    # Check duplicates
    dups = df_q[df_q.duplicated(subset=['q_id'], keep=False)]
    if not dups.empty:
        print(f"\nDuplicate Q_IDs ({len(dups)} entries):")
        for idx, row in dups.iterrows():
            print(f"Index {idx} | Q{row['q_id']} | Act: {row['act']} | Q: {row['question'][:60]}...")

if __name__ == '__main__':
    inspect_details()
