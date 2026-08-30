import fitz
import re
import pandas as pd

def inspect_pdf():
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

    print(f"Extracted exactly {len(questions)} questions from {pdf_path}.")
    if len(questions) > 0:
        print("First question extracted:")
        print(questions[0])
        print("Last question extracted:")
        print(questions[-1])

    # Let's also check old 45 questions
    df_45 = pd.read_csv('brenchmark/justor benchmark verified 45.csv')
    print(f"\nOld 45 questions CSV has exactly {len(df_45)} rows.")

if __name__ == '__main__':
    inspect_pdf()
