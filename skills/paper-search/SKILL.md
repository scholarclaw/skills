---
name: "paper-search"
description: "Searches academic papers using scholar.club API with query keywords. Returns structured results with 10 papers including title, abstract, authors, year, and links. Invoke when user asks to search academic papers or query research topics."
author: "qi"
version: "1.0.0"
---

# Paper Search

## 功能说明
This skill searches for academic papers using the scholar.club API with user-provided query keywords. It retrieves and structures the top 10 paper results including detailed information such as paper title, abstract, authors, publication year, journal, and access links. The results are formatted for easy reading and analysis in Feishu conversations.

## 使用方法
@openclaw paper-search [QUERY_KEYWORDS]

### 必选参数
- **QUERY_KEYWORDS**: 搜索关键词或问题（支持中文和英文）

### 示例
@openclaw paper-search climate change impacts on infectious diseases
@openclaw paper-search 人工智能在医疗诊断中的应用
@openclaw paper-search "machine learning for protein structure prediction"

## Input Requirements
- 提供有效的搜索关键词或查询问题
- 关键词应与学术研究相关
- 支持中文和英文查询

## Output Format
The skill will generate a structured response in markdown format with the following sections for each paper:

```markdown
### [Paper Number]. [Paper Title]
**Authors**: [Author List]
**Year**: [Publication Year]
**Journal**: [Journal Name]
**Citations**: [Citation Count]

**Abstract**: [Paper Abstract]

**Link**: [Semantic Scholar URL]
{% if openAccessPdf %}
**PDF Access**: [Open Access PDF Link]
{% endif %}
```

### 输出示例
```markdown
### 1. Climate change & infectious diseases in India: Implications for health care providers
**Authors**: V. R. Dhara, P. Schramm, G. Luber
**Year**: 2013
**Journal**: The Indian Journal of Medical Research
**Citations**: 67

**Abstract**: Climate change has the potential to influence the earth's biological systems, however, its effects on human health are not well defined. Developing nations with limited resources are expected to face a host of health effects due to climate change, including vector-borne and water-borne diseases such as malaria, cholera, and dengue. This article reviews common and prevalent infectious diseases in India, their links to climate change, and how health care providers might discuss preventive health care strategies with their patients.

**Link**: https://www.semanticscholar.org/paper/b0b901ebe9464c17ab186fe7235989c9afbf0669
```

## Implementation Details

### API Integration
The skill uses the scholar.club API for paper search:
- **API Endpoint**: https://scholar.club/api/v1/papers/search
- **Request Parameters**: 
  - query: URL-encoded search keywords
  - offset: 0 (fixed)
  - limit: 10 (fixed, returns 10 results per request)

### Results Processing
The skill processes the API response to extract and structure:
- Paper title and metadata
- Authors list with affiliations
- Publication information (year, journal, volume, pages)
- Paper abstract and TLDR summary
- Citations count and influential citations
- Open access PDF links (when available)
- Semantic Scholar paper links

### Error Handling
The skill includes error handling for:
- API connection failures
- Invalid API responses
- Network timeouts
- Empty search results

## Dependencies
- requests>=2.31.0: HTTP requests library for API calls
- urllib3>=2.0.7: HTTP client library
