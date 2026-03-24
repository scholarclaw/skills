#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学术论文检索脚本
调用Semantic Scholar API进行多维度学术论文检索

使用方法：
    python paper_search.py --query "machine learning" --year-start 2020 --year-end 2024 --limit 20

参数说明：
    --query       检索关键词（必填）
    --year-start  起始年份（可选）
    --year-end    结束年份（可选）
    --venue       期刊/会议名称（可选）
    --author      作者姓名（可选）
    --limit       返回数量，默认20（可选）
    --fields      返回字段，逗号分隔（可选）
    --api-key     Semantic Scholar API Key（可选，无Key时使用公共额度）
"""

import argparse
import json
import sys
import os
from typing import Optional, Dict, List, Any
from urllib.parse import quote

# 导入requests库
# 优先使用标准库requests，当需要使用API Key认证时可选择性使用coze_workload_identity
import requests


# API配置
API_BASE_URL = "https://api.semanticscholar.org/graph/v1"
DEFAULT_FIELDS = "paperId,title,authors,abstract,venue,year,citationCount,referenceCount,url,openAccessPdf,publicationVenue,publicationDate"

# 默认返回数量
DEFAULT_LIMIT = 20


def search_papers(
    query: str,
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
    venue: Optional[str] = None,
    author: Optional[str] = None,
    limit: int = DEFAULT_LIMIT,
    fields: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    调用Semantic Scholar API检索学术论文

    Args:
        query: 检索关键词
        year_start: 起始年份
        year_end: 结束年份
        venue: 期刊/会议名称
        author: 作者姓名
        limit: 返回数量
        fields: 返回字段
        api_key: API密钥（可选）

    Returns:
        包含检索结果的字典
    """
    # 构建请求URL
    endpoint = f"{API_BASE_URL}/paper/search"

    # 构建查询参数
    params = {
        "query": query,
        "limit": limit,
        "fields": fields or DEFAULT_FIELDS
    }

    # P1 修复：年份范围过滤使用 Semantic Scholar 正确格式 "YYYY-YYYY"
    if year_start and year_end:
        params["year"] = f"{year_start}-{year_end}"
    elif year_start:
        params["year"] = f"{year_start}-"
    elif year_end:
        params["year"] = f"-{year_end}"

    # P2 修复：venue 过滤改为在 query 中使用引号包裹，提升匹配准确性
    if venue:
        params["query"] = f'{query} "{venue}"'

    # 构建请求头
    headers = {
        "Content-Type": "application/json"
    }

    # 如果有API Key，添加到请求头
    if api_key:
        headers["x-api-key"] = api_key

    try:
        # 发起请求
        response = requests.get(
            endpoint,
            params=params,
            headers=headers,
            timeout=30
        )

        # 检查HTTP状态码
        if response.status_code >= 400:
            return {
                "error": True,
                "status_code": response.status_code,
                "message": f"HTTP请求失败: {response.status_code}",
                "details": response.text
            }

        # 解析响应
        data = response.json()

        # 检查API错误
        if "error" in data:
            return {
                "error": True,
                "message": data.get("message", "API返回错误"),
                "details": data
            }

        # 格式化返回结果
        papers = data.get("data", [])
        total = data.get("total", len(papers))

        # P1 修复：author 过滤
        # Semantic Scholar /paper/search 不支持 author 直接过滤参数。
        # 策略：query 中已加入作者姓名（见 main()），此处做后过滤兜底，
        # 确保返回结果均含目标作者，避免 API 返回无关论文。
        if author:
            author_lower = author.lower()
            papers = [
                p for p in papers
                if any(author_lower in a.get("name", "").lower()
                       for a in p.get("authors", []))
            ]

        return {
            "error": False,
            "total": total,
            "returned": len(papers),
            "query": query,
            "filters": {
                "year_start": year_start,
                "year_end": year_end,
                "venue": venue,
                "author": author
            },
            "data": papers
        }

    except requests.exceptions.Timeout:
        return {
            "error": True,
            "message": "请求超时，请稍后重试"
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": True,
            "message": f"网络请求失败: {str(e)}"
        }
    except json.JSONDecodeError:
        return {
            "error": True,
            "message": "响应数据解析失败"
        }


def get_paper_by_id(
    paper_id: str,
    fields: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    根据论文ID获取论文详情

    Args:
        paper_id: 论文ID（Semantic Scholar ID或DOI）
        fields: 返回字段
        api_key: API密钥（可选）

    Returns:
        论文详情字典
    """
    endpoint = f"{API_BASE_URL}/paper/{paper_id}"

    params = {
        "fields": fields or DEFAULT_FIELDS
    }

    headers = {
        "Content-Type": "application/json"
    }

    if api_key:
        headers["x-api-key"] = api_key

    try:
        response = requests.get(
            endpoint,
            params=params,
            headers=headers,
            timeout=30
        )

        if response.status_code == 404:
            return {
                "error": True,
                "message": f"未找到论文: {paper_id}"
            }

        if response.status_code >= 400:
            return {
                "error": True,
                "status_code": response.status_code,
                "message": f"HTTP请求失败: {response.status_code}"
            }

        data = response.json()

        return {
            "error": False,
            "data": data
        }

    except requests.exceptions.RequestException as e:
        return {
            "error": True,
            "message": f"网络请求失败: {str(e)}"
        }


def format_paper_summary(paper: Dict[str, Any]) -> str:
    """
    格式化单篇论文摘要信息

    Args:
        paper: 论文数据字典

    Returns:
        格式化的摘要字符串
    """
    title = paper.get("title", "N/A")
    year = paper.get("year", "N/A")
    venue = paper.get("venue", "N/A")
    citation_count = paper.get("citationCount", 0)
    authors = paper.get("authors", [])
    author_names = ", ".join([a.get("name", "") for a in authors[:3]])
    if len(authors) > 3:
        author_names += " et al."

    abstract = paper.get("abstract", "")
    abstract_short = abstract[:200] + "..." if abstract and len(abstract) > 200 else (abstract or "无摘要")

    url = paper.get("url", "")

    return f"""
标题: {title}
作者: {author_names}
年份: {year}
期刊/会议: {venue}
引用数: {citation_count}
摘要: {abstract_short}
链接: {url}
"""


def main():
    """主函数：解析命令行参数并执行检索"""
    parser = argparse.ArgumentParser(
        description="学术论文检索脚本 - 基于Semantic Scholar API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础检索
  python paper_search.py --query "deep learning"

  # 带时间范围
  python paper_search.py --query "machine learning" --year-start 2020 --year-end 2024

  # 指定期刊
  python paper_search.py --query "natural language processing" --venue "ACL"

  # 使用API Key
  python paper_search.py --query "transformer" --api-key "YOUR_API_KEY"
        """
    )

    parser.add_argument(
        "--query", "-q",
        type=str,
        required=True,
        help="检索关键词（必填）"
    )

    parser.add_argument(
        "--year-start",
        type=int,
        default=None,
        help="起始年份"
    )

    parser.add_argument(
        "--year-end",
        type=int,
        default=None,
        help="结束年份"
    )

    parser.add_argument(
        "--venue",
        type=str,
        default=None,
        help="期刊/会议名称"
    )

    parser.add_argument(
        "--author",
        type=str,
        default=None,
        help="作者姓名"
    )

    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"返回数量，默认{DEFAULT_LIMIT}"
    )

    parser.add_argument(
        "--fields", "-f",
        type=str,
        default=None,
        help="返回字段，逗号分隔"
    )

    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Semantic Scholar API Key（可选）"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出文件路径（JSON格式）"
    )

    parser.add_argument(
        "--summary",
        action="store_true",
        help="打印论文摘要信息"
    )

    args = parser.parse_args()

    # P1 修复：author 检索增强
    # Semantic Scholar /paper/search 不支持独立的 author 过滤参数。
    # 将作者姓名加入 query，大幅提升召回率（后过滤仅在 limit 内兜底）。
    effective_query = args.query
    if args.author:
        effective_query = f'"{args.author}" {args.query}'

    # 打印检索信息
    print(f"正在检索: {effective_query}")
    if args.year_start or args.year_end:
        print(f"年份范围: {args.year_start or '不限'} - {args.year_end or '不限'}")
    if args.venue:
        print(f"期刊/会议: {args.venue}")
    if args.author:
        print(f"作者: {args.author}")
    print(f"返回数量: {args.limit}")
    print("-" * 50)

    # 执行检索
    result = search_papers(
        query=effective_query,
        year_start=args.year_start,
        year_end=args.year_end,
        venue=args.venue,
        author=args.author,
        limit=args.limit,
        fields=args.fields,
        api_key=args.api_key
    )

    # 处理错误
    if result.get("error"):
        print(f"检索失败: {result.get('message', '未知错误')}")
        if result.get("details"):
            print(f"详细信息: {result.get('details')}")
        sys.exit(1)

    # 打印结果统计
    print(f"检索完成: 找到 {result['total']} 篇论文，返回 {result['returned']} 篇")
    print("-" * 50)

    # 打印摘要信息
    if args.summary:
        for i, paper in enumerate(result.get("data", []), 1):
            print(f"\n[{i}]")
            print(format_paper_summary(paper))

    # 保存到文件
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存至: {args.output}")

    # 返回JSON格式结果
    print("\n=== JSON结果 ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
