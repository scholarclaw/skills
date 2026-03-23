#!/usr/bin/env python3
"""
OpenClaw Paper Search Skill - Core Functionality
This script implements the paper search functionality using scholar.club API
"""

import requests
import urllib.parse
import json
import sys


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
    def main(query: str, output_file: str = None) -> int:
        """
        Main function to execute the paper search
        
        Args:
            query: Search query
            output_file: Optional output file path
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        print(f"正在搜索: {query}")
        
        # Search for papers
        results = PaperSearch.search_papers(query)
        
        if not results:
            print("搜索失败，请稍后重试。")
            return 1
            
        # Format results
        formatted_results = PaperSearch.format_search_results(results)
        
        # Print to stdout
        print(formatted_results)
        
        # Save to file if specified
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(formatted_results)
                print(f"搜索结果已保存到: {output_file}")
            except Exception as e:
                print(f"保存结果到文件失败: {e}")
                return 1
                
        return 0


def main(query: str, output_file: str = None) -> int:
    """
    Main entry point function (compatibility wrapper)
    """
    return PaperSearch.main(query, output_file)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python paper_search.py '搜索关键词' [输出文件名]")
        print("示例: python paper_search.py 'climate change impacts' results.md")
        sys.exit(1)
        
    query = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    sys.exit(PaperSearch.main(query, output_file))
