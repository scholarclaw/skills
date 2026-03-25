#!/usr/bin/env python3
"""
PDF Paper Questions Generator
Extracts text from PDF files and generates 3 thought-provoking questions using LLMs.
"""

import argparse
import os
import sys
from typing import Optional

import fitz  # PyMuPDF
import jinja2


def load_prompt_template(template_path: str = None) -> jinja2.Template:
    """Load the prompt template (embedded in code)."""
    template_content = """You are an Artificial Intelligence Assistant. You are fluent in both Chinese and English and always provide answers that are safe, helpful, accurate, and free from any content involving terrorism, racism, pornography, violence, or other harmful topics.

Your task is to perform a thorough analysis of the provided academic content (e.g., research paper excerpt). Based on this analysis, please generate exactly 3 thought-provoking questions that explore the study in depth.

Each question must:

Be related to technical details, applications, comparisons with existing methods, or future directions
Contain between 10 and 20 words
End with a question mark (?)
Be concise, clear, and logically sound
Please output your response using the following Markdown format:

Recommended Questions
1. [Question 1]
2. [Question 2]
3. [Question 3]
Do not include any additional text, explanations, or formatting beyond the list of questions.

Now, begin your analysis based on the following content:

{{ paper_text }}

for example, you can output like this:
### Recommended Questions
1. How does the sparse attention mechanism reduce computational costs compared to GPT-4?
2. Can this method maintain robustness when applied to medical diagnosis scenarios?
3. What hardware limitations must be overcome for real-time deployment on edge devices?"""
    
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


def generate_questions_prompt(text: str, template: jinja2.Template) -> str:
    """Generate questions prompt using the prompt template."""
    if len(text) > 150000:
        text = text[:150000]
        print("Warning: Paper text is very long - content has been truncated")
    
    try:
        prompt = template.render(paper_text=text)
        return prompt
    except Exception as e:
        print(f"Error generating questions prompt: {e}")
        return ""


def main(pdf_path: str, template_path: str = None, output_path: str = None):
    """Main function for paper questions generation with OpenClaw integration"""
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return 1
    
    print(f"Extracting text from: {pdf_path}")
    paper_text = extract_text_from_pdf(pdf_path)
    
    if not paper_text.strip():
        print("Error: No text could be extracted from the PDF file")
        return 1
    
    print(f"Loading embedded prompt template")
    template = load_prompt_template()
    
    if template is None:
        return 1
    
    print("Generating questions prompt...")
    questions_prompt = generate_questions_prompt(paper_text, template)
    
    if not questions_prompt:
        return 1
    
    if output_path:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(questions_prompt)
            print(f"Questions prompt saved to: {output_path}")
        except Exception as e:
            print(f"Error writing to output file: {e}")
            return 1
    else:
        print("\nGenerated Questions Prompt:\n")
        print(questions_prompt)
    
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract text from PDF and generate 3 recommended questions"
    )
    
    parser.add_argument(
        "pdf_path",
        help="Path to the PDF file to generate questions for"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file to save the generated questions prompt"
    )
    
    args = parser.parse_args()
    
    sys.exit(main(args.pdf_path, None, args.output))
