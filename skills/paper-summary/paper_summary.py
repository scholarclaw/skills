#!/usr/bin/env python3
"""
PDF Paper Summary Generator
Extracts text from PDF files and generates structured summaries using LLMs.
"""

import argparse
import os
import sys
from typing import Optional

import fitz  # PyMuPDF
import jinja2
import argparse
import sys
import os


def load_prompt_template(template_path: str = None) -> jinja2.Template:
    """Load the prompt template (embedded in code)."""
    # Embedded prompt template from get_file_summary.jinja
    template_content = """You are an Artificial Intelligence Assistant, and you are better at conversations in Chinese and English. You will provide users with safe, helpful and accurate answers. At the same time, you will reject all answers to questions that involve terrorism, racism, yellow violence, etc.
Your task is to perform an in-depth analysis of the provided as following, focusing on the following three core areas: Key Ideas, Main Contribution, and Experimental Results. Please read the document carefully and provide a concise and in-depth analysis.
{{ paper_text }}

Key Ideas:
The key idea should be the heart of an essay, and it should be clear in one sentence. Describe the core concept of the article in one concise sentence, no more than 20 words.
Main Contribution:
Analyse and clearly articulate the main contribution of this research to its field. This may include new methodologies, theoretical breakthroughs, technological innovations, or new insights into existing problems. Explain how these contributions have advanced the field and the potential impact they may have. Assess the originality and significance of these contributions.
Experimental Results:
Summarise the key experimental results presented in the document. Focus on results that directly support the main contribution or validate key ideas. Include a brief description of the experimental setup (if critical to understanding the results) and how these results support the author's argument or hypothesis. If there are any particularly significant or unexpected findings, point them out specifically.
Keep the following points in mind in your analysis:
Use language that is accurate and professional but easy to understand.

Remain objective, focus on the content of the document, and avoid adding personal speculation.
If information in a section is incomplete or unclear, explain this in your analysis.
Keep the total word count to 300 words to ensure dense but concise information.
You can answer in Chinese or English, depending on the language of the PDF document provided by the user.
Remember, as an AI assistant, your analyses should always be safe, helpful, and accurate. Your goal is to provide the reader with an overview of the core content of the document, highlighting its most important and innovative aspects, while ensuring that your answers do not contain any inappropriate or harmful content. Now, please begin your analysis.
The returned content must in markdown format, and you must generate in English. You only need to generate key ideas, main contributions and experimental results, and you don't need to generate anything else beyond that.
You must follow the markdown format below:

### Key Ideas
xxxxxxxxxxxxxxxxxxx

### Main Contribution
xxxxxxxxxxxxxxxxxxx

### Experimental Results
xxxxxxxxxxxxxxxxxxx"""
    
    try:
        return jinja2.Template(template_content)
    except Exception as e:
        print(f"Error loading prompt template: {e}")
        return None


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file using PyMuPDF (fitz)."""
    text = ""
    
    try:
        with fitz.open(pdf_path) as pdf:
            for page in pdf:
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"
    except FileNotFoundError:
        print(f"Error: File not found: {pdf_path}")
        return ""
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return ""
    
    return text


def generate_summary(text: str, template: jinja2.Template) -> str:
    """Generate summary using the prompt template."""
    # Limit text length to ~150,000 characters to avoid exceeding model limits
    if len(text) > 150000:
        text = text[:150000]
        print("Warning: Paper text is very long - content has been truncated")
    
    try:
        prompt = template.render(paper_text=text)
        return prompt
    except Exception as e:
        print(f"Error generating summary prompt: {e}")
        return ""


def main(pdf_path: str, template_path: str = None, output_path: str = None):
    """Main function for paper summary generation with OpenClaw integration"""
    
    # Check if PDF file exists
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return 1
    
    # Extract text from PDF
    print(f"Extracting text from: {pdf_path}")
    paper_text = extract_text_from_pdf(pdf_path)
    
    if not paper_text.strip():
        print("Error: No text could be extracted from the PDF file")
        return 1
    
    # Load prompt template
    print(f"Loading embedded prompt template")
    template = load_prompt_template()
    
    if template is None:
        return 1
    
    # Generate summary prompt
    print("Generating summary prompt...")
    summary_prompt = generate_summary(paper_text, template)
    
    if not summary_prompt:
        return 1
    
    # Output the result
    if output_path:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(summary_prompt)
            print(f"Summary prompt saved to: {output_path}")
        except Exception as e:
            print(f"Error writing to output file: {e}")
            return 1
    else:
        print("\nGenerated Summary Prompt:\n")
        print(summary_prompt)
    
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract text from PDF and generate paper summary"
    )
    
    parser.add_argument(
        "pdf_path",
        help="Path to the PDF file to summarize"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file to save the generated summary prompt"
    )
    
    args = parser.parse_args()
    
    sys.exit(main(args.pdf_path, None, args.output))
