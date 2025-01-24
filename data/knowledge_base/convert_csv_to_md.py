import csv
import os
from pathlib import Path

def csv_to_md(csv_path, md_path):
    with open(csv_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        headers = next(reader)
        
        # Create RAG-compatible markdown content
        md_content = f"# {Path(csv_path).stem}\n\n"
        
        # Check if this is a Q&A format (question, answer columns)
        if "question" in headers and "answer" in headers:
            q_index = headers.index("question")
            a_index = headers.index("answer")
            
            # Format as Q&A pairs
            for row in reader:
                md_content += f"## {row[q_index]}\n"
                md_content += f"{row[a_index]}\n\n"
        else:
            # Format as table for other data
            md_content += "| " + " | ".join(headers) + " |\n"
            md_content += "| " + " | ".join(["---"] * len(headers)) + " |\n"
            for row in reader:
                md_content += "| " + " | ".join(row) + " |\n"
            
    # Write to markdown file
    with open(md_path, 'w', encoding='utf-8') as md_file:
        md_file.write(md_content)

def convert_all_csv_to_md(directory):
    knowledge_base = Path(directory)
    for csv_file in knowledge_base.glob("*.csv"):
        md_file = csv_file.with_suffix('.md')
        csv_to_md(csv_file, md_file)
        print(f"Converted {csv_file.name} to {md_file.name}")

if __name__ == "__main__":
    convert_all_csv_to_md("data/knowledge_base")
