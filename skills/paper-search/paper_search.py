#!/usr/bin/env python3
"""
OpenClaw Paper Search Skill - Core Functionality
This script implements the paper search functionality using scholar.club API
"""

import requests
import urllib.parse
import json
import sys
import argparse


class PaperSearch:
    """Class to handle paper search functionality"""
    
    API_BASE_URL = "https://scholar.club/api/v1/papers/search"
    DEFAULT_LIMIT = 10
    DEFAULT_OFFSET = 0
    
    @staticmethod
    def search_papers(query: str) -> dict:
        """
        Search for papers using the scholar.club API
        
        Args:
            query: Search keywords or question
            
        Returns:
            Dictionary containing search results
        """
        try:
            # URL encode the query
            encoded_query = urllib.parse.quote(query)
            url = f"{PaperSearch.API_BASE_URL}?query={encoded_query}&offset={PaperSearch.DEFAULT_OFFSET}&limit={PaperSearch.DEFAULT_LIMIT}"
            
            # Send API request
            response = requests.get(url, timeout=30)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            # Parse JSON response
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API 请求错误: {e}")
            return None
        except Exception as e:
            print(f"搜索过程中出错: {e}")
            return None
    
    @staticmethod
    def format_authors(authors: list) -> str:
        """
        Format authors list for display
        
        Args:
            authors: List of author dictionaries
            
        Returns:
            Formatted authors string
        """
        if not authors:
            return "Unknown"
            
        author_names = []
        for author in authors[:3]:  # Display first 3 authors
            if isinstance(author, dict) and 'name' in author:
                author_names.append(author['name'])
            elif isinstance(author, str):
                author_names.append(author)
        
        if len(authors) > 3:
            author_names.append(f"+{len(authors) - 3} 更多作者")
            
        return ", ".join(author_names)
    
    @staticmethod
    def format_paper_info(paper: dict) -> str:
        """
        Format single paper information for display
        
        Args:
            paper: Paper dictionary
            
        Returns:
            Formatted paper information string
        """
        lines = []
        
        # Paper number will be added later
        lines.append(f"### {paper.get('title', 'Unknown Title')}")
        
        # Authors
        authors = PaperSearch.format_authors(paper.get('authors', []))
        lines.append(f"**作者**: {authors}")
        
        # Year
        if 'year' in paper and paper['year']:
            lines.append(f"**年份**: {paper['year']}")
        
        # Journal
        if 'journal' in paper and paper['journal']:
            journal = paper['journal']
            if isinstance(journal, dict) and 'name' in journal:
                lines.append(f"**期刊**: {journal['name']}")
            elif isinstance(journal, str):
                lines.append(f"**期刊**: {journal}")
        
        # Citations
        if 'citationCount' in paper and paper['citationCount'] is not None:
            lines.append(f"**引用**: {paper['citationCount']}")
        
        # Abstract
        if 'abstract' in paper and paper['abstract']:
            lines.append(f"\n**摘要**: {paper['abstract']}")
        
        # Paper URL
        if 'url' in paper and paper['url']:
            lines.append(f"\n**链接**: {paper['url']}")
        
        # Open access PDF
        if 'isOpenAccess' in paper and paper['isOpenAccess'] and 'openAccessPdf' in paper and paper['openAccessPdf']:
            lines.append(f"**PDF访问**: {paper['openAccessPdf']}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_search_results(results: dict) -> str:
        """
        Format complete search results for display
        
        Args:
            results: Search results dictionary
            
        Returns:
            Formatted results string
        """
        if not results or 'papers' not in results:
            return "未找到相关论文。请尝试调整搜索关键词。"
            
        papers = results['papers']
        
        # Search summary
        total = results.get('total', len(papers))
        offset = results.get('offset', 0)
        query = results.get('query', '')
        
        lines = []
        lines.append(f"## 搜索结果: {query}")
        lines.append(f"找到 {total} 篇相关论文（显示前 {len(papers)} 篇）\n")
        
        # Format each paper
        for i, paper in enumerate(papers, 1):
            paper_info = PaperSearch.format_paper_info(paper)
            # Replace the ### header with numbered header
            paper_info = paper_info.replace("### ", f"### {i}. ", 1)
            lines.append(paper_info)
            lines.append("")  # Empty line between papers
        
        return "\n".join(lines)
    
    @staticmethod
    def main(query: str, output_file: str = None, raw: bool = False) -> int:
        """
        Main function to execute the paper search
        
        Args:
            query: Search query
            output_file: Optional output file path
            raw: Whether to return raw API response instead of formatted results
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        print(f"正在搜索: {query}")
        
        # Search for papers
        results = PaperSearch.search_papers(query)
        
        if not results:
            print("搜索失败，请稍后重试。")
            return 1
            
        # Output results
        if raw:
            # Output raw API response
            print(json.dumps(results, ensure_ascii=False, indent=2))
            output_content = json.dumps(results, ensure_ascii=False, indent=2)
        else:
            # Output formatted results
            formatted_results = PaperSearch.format_search_results(results)
            print(formatted_results)
            output_content = formatted_results
        
        # Save to file if specified
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(output_content)
                print(f"搜索结果已保存到: {output_file}")
            except Exception as e:
                print(f"保存结果到文件失败: {e}")
                return 1
                
        return 0


def main(query: str, output_file: str = None, raw: bool = False) -> int:
    """
    Main entry point function (compatibility wrapper)
    """
    return PaperSearch.main(query, output_file, raw)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Paper Search - Searches academic papers using scholar.club API"
    )
    parser.add_argument("query", help="Search query or keywords")
    parser.add_argument(
        "-o", "--output", 
        help="Output file to save the search results"
    )
    parser.add_argument(
        "-r", "--raw", 
        action="store_true",
        help="Output raw API response instead of formatted results"
    )
    
    args = parser.parse_args()
    sys.exit(PaperSearch.main(args.query, args.output, args.raw))
