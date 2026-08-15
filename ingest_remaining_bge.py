import pathlib
import logging
from ingest_all_bge import ingest_file

REMAINING_FILES = [
    "knowledge/pdr_1913_sections_corrected.json",
    "knowledge/Penal_Code_1860_structured_2_corrected.json",
    "knowledge/Specific_Relief_Act_1877_structured_corrected.json",
    "knowledge/Stamp_Act_1899_structured_corrected.json",
    "knowledge/state_acquisition_tenancy_act_1950_corrected.json",
    "knowledge/Trademarks_Act_2009_structured_corrected.json",
    "knowledge/Transfer_of_Property_Act_1882_structured_corrected.json",
]

def main():
    total = 0
    print(f"Resuming ingestion for {len(REMAINING_FILES)} remaining Acts using OpenRouter baai/bge-m3...")
    for f in REMAINING_FILES:
        fpath = pathlib.Path(f)
        if fpath.exists():
            try:
                n = ingest_file(fpath)
                total += n
            except Exception as e:
                print(f"ERROR on {fpath.name}: {e}")
        else:
            print(f"Missing: {f}")
    print(f"\n=== Successfully ingested {total} chunks across remaining Acts ===")

if __name__ == "__main__":
    main()
