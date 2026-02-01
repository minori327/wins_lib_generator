# Success Story / Wins Library System
## 离线 Agentic Workflow 需求文档 v1.0

**文档版本**: 1.0
**创建日期**: 2026-02-01
**项目状态**: 需求定义阶段

---

## 目录

1. [项目概述](#1-项目概述)
   1.1 [项目背景](#11-项目背景)
   1.2 [项目目标](#12-项目目标)
   1.3 [核心约束](#13-核心约束)
2. [系统架构](#2-系统架构)
   2.1 [高层架构](#21-高层架构)
   2.2 [核心设计原则](#22-核心设计原则)
3. [输入设计](#3-输入设计)
   3.1 [支持的原始数据类型](#31-支持的原始数据类型)
   3.2 [数据收集方式](#32-数据收集方式)
4. [数据标准化](#4-数据标准化)
   4.1 [标准化目标](#41-标准化目标)
   4.2 [标准化数据模型](#42-标准化数据模型)
   4.3 [处理方式](#43-处理方式)
5. [核心业务对象](#5-核心业务对象)
   5.1 [Success Story 定义](#51-success-story-定义)
   5.2 [数据结构](#52-数据结构)
6. [Agentic Workflow 设计](#6-agentic-workflow-设计)
   6.1 [Agent 类型](#61-agent-类型)
   6.2 [Agent 协作流程](#62-agent-协作流程)
7. [每周更新流程](#7-每周更新流程)
8. [输出设计](#8-输出设计)
   8.1 [输出版本](#81-输出版本)
   8.2 [输出存储](#82-输出存储)
9. [Obsidian 集成](#9-obsidian-集成)
10. [技术选型](#10-技术选型)
11. [项目结构](#11-项目结构)
12. [功能范围](#12-功能范围)
    12.1 [包含功能](#121-包含功能)
    12.2 [不包含功能](#122-不包含功能-v1)
13. [成功标准](#13-成功标准)
14. [实施优先级](#14-实施优先级)

---

## 1. 项目概述

### 1.1 项目背景

业务团队在每个月、每个国家都会产生大量分散的成功案例（Success Stories / Wins），这些信息来源多样，包括：

- **PDF 报告**：月度案例研究报告、客户分析报告
- **邮件**：销售团队分享的成功案例邮件
- **Microsoft Teams 消息**：团队沟通中分享的成功故事
- **图片**：截图、照片等可视化资料

**当前痛点**：

| 问题 | 影响 |
|------|------|
| 信息分散 | 难以查找和复用 |
| 格式不统一 | 无法自动化处理 |
| 缺乏结构化 | 难以进行趋势分析 |
| 手动整理 | 效率低下，易出错 |
| 受众单一 | 无法针对不同受众快速生成定制版本 |

### 1.2 项目目标

构建一套**完全离线、本地运行**的 Agentic Workflow 系统，实现：

1. **统一管理**：收集并统一管理 Success Story 的原始资料
2. **自动抽取**：自动抽取、维护一个结构化的 Wins / Success Story Library
3. **定期更新**：支持每周更新（weekly update）
4. **多版本输出**：基于同一份素材，生成多种受众版本的英文输出
5. **知识集成**：通过 Obsidian 作为知识库与阅读界面

### 1.3 核心约束

系统必须满足以下核心约束：

| 约束维度 | 要求 | 说明 |
|----------|------|------|
| **运行方式** | 完全离线 | 不依赖任何云服务 |
| **模型** | 本地模型 | 使用 Ollama + GLM-4 开源模型 |
| **网络** | 零依赖 | 不依赖任何云 API |
| **处理语言** | 英文 | 所有内部处理使用英文 |
| **输出语言** | 英文 | 所有输出为英文 |
| **触发方式** | 手动或定时 | 非实时触发 |
| **知识库** | Obsidian | 使用 Markdown 格式 |

---

## 2. 系统架构

### 2.1 高层架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Raw Inputs Layer                          │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐                        │
│  │ PDF  │  │Email │  │Teams │  │Image │                        │
│  └──────┘  └──────┘  └──────┘  └──────┘                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   1. Data Collection Layer                       │
│                   (文件扫描与发现)                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  2. Data Normalization Layer                     │
│                  (PDF解析/邮件解析/OCR - 非LLM)                  │
│                  输出: RawItem 对象                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              3. Success Story Extraction Agent                   │
│                   (LLM: GLM-4)                                   │
│              输入: RawItem 集合                                   │
│              输出: SuccessStory 对象                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              4. Wins / Success Story Library                     │
│                   (JSON 持久化存储)                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              5. Multi-Version Output Agents                      │
│  ┌──────────────────┐           ┌──────────────────┐           │
│  │  Executive Agent │           │  Marketing Agent │           │
│  │  (高管版本)       │           │  (市场版本)       │           │
│  └──────────────────┘           └──────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Obsidian Knowledge Base                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Success Story│  │Weekly Summary│  │  Outputs     │          │
│  │    Notes     │  │              │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 核心设计原则

1. **Success Story 是一等公民**
   - Success Story 是核心业务对象
   - 原始数据只是"证据"（evidence）
   - 系统围绕 Success Story 生命周期构建

2. **智能与计算分离**
   - 所有智能行为由 Agent 完成
   - Obsidian 只用于阅读与思考，不参与计算

3. **可审计性**
   - 每个 Success Story 必须可追溯到原始数据
   - 所有处理过程可人工检查

4. **可重复性**
   - 相同输入必须产生相同输出
   - 支持手动重复执行

---

## 3. 输入设计

### 3.1 支持的原始数据类型

| 数据类型 | 格式 | 说明 | 示例 |
|----------|------|------|------|
| **PDF** | `.pdf` | 案例研究报告、客户分析文档 | `case_study_acme.pdf` |
| **邮件** | `.eml` | 导出的原始邮件文件 | `success_story.eml` |
| **Teams 消息** | `.txt` | 手动复制的聊天文本 | `teams_chat_0101.txt` |
| **图片** | `.png`, `.jpg` | 截图、照片（需 OCR 处理） | `screenshot.png` |

### 3.2 数据收集方式

**v1 阶段采用手动文件投放方式**，不实现自动抓取 API。

#### 目录结构规范

```
vault/00_sources/
└── YYYY-MM/                    # 按月组织
    └── COUNTRY/                # 按国家组织
        ├── pdf/               # PDF 文件
        ├── email/             # 邮件文件
        ├── teams/             # Teams 文本
        └── images/            # 图片文件
```

#### 命名规范

- **文件命名**: `{type}_{description}_{date}.{ext}`
- **示例**: `pdf_acme_case_20260115.pdf`

#### 完整示例

```
vault/00_sources/
└── 2026-01/
    ├── US/
    │   ├── email/
    │   │   ├── email_acme_0123.eml
    │   │   └── email_techcorp_0125.eml
    │   ├── pdf/
    │   │   └── case_study_q1.pdf
    │   ├── teams/
    │   │   └── teams_success_jan.txt
    │   └── images/
    │       └── screenshot_dashboard.png
    ├── UK/
    │   └── email/
    │       └── email_bbc_0110.eml
    └── CN/
        └── pdf/
            └── report_alibaba.pdf
```

---

## 4. 数据标准化

### 4.1 标准化目标

将所有原始输入转换为统一、可被 Agent 处理的文本对象。

**重要**: 本阶段不使用 LLM，仅使用传统解析工具。

### 4.2 标准化数据模型 (RawItem)

```json
{
  "id": "raw-uuid-v4",
  "text": "Extracted English text content...",
  "source_type": "pdf | email | teams | image",
  "filename": "original filename with extension",
  "country": "US | UK | CN | ...",
  "month": "YYYY-MM",
  "created_at": "2026-01-15T10:30:00Z",
  "metadata": {
    "file_path": "/path/to/original/file",
    "file_size": 1024000,
    "language_detected": "en",
    "encoding": "utf-8"
  }
}
```

#### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 唯一标识符 (UUID v4) |
| `text` | string | ✅ | 提取的英文文本内容 |
| `source_type` | enum | ✅ | 原始数据类型 |
| `filename` | string | ✅ | 原始文件名 |
| `country` | string | ✅ | 国家代码 (ISO 3166-1 alpha-2) |
| `month` | string | ✅ | 月份 (YYYY-MM 格式) |
| `created_at` | string | ✅ | 创建时间 (ISO-8601) |
| `metadata` | object | ❌ | 额外元数据 |

### 4.3 处理方式

| 源类型 | 处理工具 | 输出处理逻辑 |
|--------|----------|--------------|
| **PDF** | `unstructured` / `pdfplumber` | 提取所有文本，保留段落结构 |
| **Email** | `mailparser` | 提取主题、发件人、正文、时间 |
| **Teams 文本** | 原样读取 | 清理格式，统一编码 |
| **图片** | `Tesseract OCR` | 提取图片中的文字 |

---

## 5. 核心业务对象

### 5.1 Success Story 定义

**Success Story** 是一个结构化的业务成功事件，代表一个完整的客户成功案例，包含以下核心要素：

- **客户** (Customer)
- **背景** (Context): 业务问题或情境
- **行动** (Action): 采取的措施
- **结果** (Outcome): 达成的业务成果
- **指标** (Metrics): 可量化的影响

### 5.2 数据结构 (SuccessStory)

```json
{
  "id": "win-2026-01-us-001",
  "country": "US",
  "month": "2026-01",
  "customer": "ACME Corporation",
  "context": "Customer was struggling with inefficient legacy systems causing 40% downtime.",
  "action": "Implemented our cloud solution with migration team over 6 weeks.",
  "outcome": "Achieved 99.9% uptime and reduced operational costs by 25%.",
  "metrics": [
    "+15% revenue increase",
    "-40% downtime",
    "+200 employee hours saved/month"
  ],
  "confidence": "high | medium | low",
  "internal_only": false,
  "raw_sources": [
    "email_acme_0123.eml",
    "case_study.pdf"
  ],
  "last_updated": "2026-01-15T14:30:00Z",
  "tags": ["cloud-migration", "efficiency", "cost-reduction"],
  "industry": "Manufacturing",
  "team_size": "Enterprise"
}
```

#### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 唯一标识符，格式: `win-YYYY-MM-{country}-{seq}` |
| `country` | string | ✅ | 国家代码 |
| `month` | string | ✅ | 月份 (YYYY-MM) |
| `customer` | string | ✅ | 客户名称 |
| `context` | string | ✅ | 业务背景/问题 |
| `action` | string | ✅ | 采取的行动 |
| `outcome` | string | ✅ | 达成的结果 |
| `metrics` | array | ✅ | 量化指标列表 |
| `confidence` | enum | ✅ | 信息可信度: `high`/`medium`/`low` |
| `internal_only` | boolean | ✅ | 是否仅内部使用 |
| `raw_sources` | array | ✅ | 原始数据来源文件名列表 |
| `last_updated` | string | ✅ | 最后更新时间 (ISO-8601) |
| `tags` | array | ❌ | 业务标签 |
| `industry` | string | ❌ | 客户行业 |
| `team_size` | string | ❌ | 团队规模分类 |

---

## 6. Agentic Workflow 设计

### 6.1 Agent 类型

#### 6.1.1 Ingest Agent (非 LLM)

**职责**：
- 扫描源目录，发现新文件
- 根据文件类型选择合适的解析器
- 生成 RawItem 对象
- 记录处理状态

**输入**：
- 文件系统路径

**输出**：
- RawItem 对象列表

**技术**：
- Python 文件系统操作
- 无需 LLM

---

#### 6.1.2 Success Story Extraction Agent (LLM)

**职责**：系统的智能核心

1. **识别客户**: 从文本中识别客户名称
2. **判断有效性**: 判断是否为成功案例
3. **信息抽取**: 抽取 Context、Action、Outcome
4. **量化指标**: 提取或推断可量化指标
5. **敏感信息判断**: 判断是否可对外使用

**输入**：
- 一组 RawItem（按国家/时间窗口过滤）

**输出**：
- 一个或多个 SuccessStory 对象

**提示词设计原则**：
```
You are a business analyst extracting success stories from raw data.

For each set of raw items:
1. Identify if this represents a success story
2. Extract customer name
3. Extract context (business problem)
4. Extract action (what was done)
5. Extract outcome (results achieved)
6. Extract or infer metrics (quantifiable impact)
7. Assess confidence level
8. Determine if internal-only

Output as JSON array of SuccessStory objects.
```

---

#### 6.1.3 Planner Agent (轻量 LLM)

**职责**：
- 分析当前状态
- 决定本次运行需要执行的任务
- 生成执行计划

**输入**：
- 上次运行时间
- 新增 RawItem 数量
- 用户命令参数

**输出**：
```json
{
  "tasks": [
    "weekly_update",
    "executive_output",
    "marketing_output"
  ],
  "scope": {
    "countries": ["US", "UK"],
    "from_month": "2026-01",
    "to_month": "2026-01"
  }
}
```

---

#### 6.1.4 Output Agents (LLM)

每种输出类型对应一个专门的 Agent。

**(a) Executive Output Agent**

**目标受众**: 公司高管

**风格要求**:
- 极度精简
- 强调影响和数据
- 仅内部使用
- Bullet points 优先

**(b) Marketing Output Agent**

**目标受众**: 外部客户/市场

**风格要求**:
- 故事化叙述
- 自动规避敏感信息
- 引用可信来源
- 适合公开发布

---

### 6.2 Agent 协作流程

```
┌─────────────┐
│ User Trigger│  (手动 CLI 或定时任务)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Planner Agent│  决定执行哪些任务
└──────┬──────┘
       │
       ├──────────────┐
       │              │
       ▼              ▼
┌─────────────┐  ┌──────────────┐
│Ingest Agent │  │Load Existing │  扫描新文件 + 加载已有数据
└──────┬──────┘  │SuccessStories│
       │         └──────┬───────┘
       ▼                │
   RawItems             │
       │                │
       └──────┬─────────┘
              │
              ▼
┌─────────────────────────┐
│Extraction Agent         │  抽取/更新 Success Stories
│ (LLM: GLM-4)            │
└──────────┬──────────────┘
           │
           ▼
   SuccessStories
           │
           ├─────────────────┐
           │                 │
           ▼                 ▼
┌──────────────┐  ┌──────────────────┐
│ Save Library │  │ Output Agents     │  持久化 + 生成输出
│   (JSON)     │  │  - Executive      │
└──────────────┘  │  - Marketing      │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌─────────────────┐
                  │ Write to Obsidian│  写入 Markdown
                  └─────────────────┘
```

---

## 7. 每周更新流程

### 7.1 触发方式

**手动 CLI 触发**：

```bash
# 更新所有国家
python run.py --mode weekly

# 更新特定国家
python run.py --mode weekly --country US

# 指定月份范围
python run.py --mode weekly --from 2026-01 --to 2026-01
```

### 7.2 执行步骤

| 步骤 | 操作 | 输出 |
|------|------|------|
| **1** | 查找自上次运行后的新增 Raw Data | 新文件列表 |
| **2** | 标准化处理 → 生成 RawItem | RawItem 集合 |
| **3** | Success Story 抽取/更新 | SuccessStory 对象 |
| **4** | 去重（基于客户 + 行为） | 唯一 SuccessStory 集合 |
| **5** | 更新 Wins Library (JSON) | 持久化数据 |
| **6** | 生成每周总结 | Weekly Summary |
| **7** | 写入 Obsidian | Markdown 文件 |

### 7.3 去重策略

**去重规则**：
- 相同 `customer` + 相似 `action` → 视为同一 Success Story
- 保留最新版本
- 合并 `raw_sources`（保留所有来源）

**相似度计算**：
- 使用字符串相似度算法 (如 Levenshtein distance)
- 阈值：85% 相似度

---

## 8. 输出设计

### 8.1 输出版本

#### (a) Executive Version

**目标**: 公司高管

**特点**:
- 极度精简 (每个 Story < 100 词)
- 强调业务影响和数据
- 仅内部使用
- Bullet points 格式

**模板**:
```markdown
## ACME Corporation - US

**Impact**:
- +15% revenue
- -40% operational cost

**What Happened**:
- Implemented cloud migration in 6 weeks
- Achieved 99.9% uptime
- Saved 200+ employee hours/month

**Date**: Jan 2026
```

---

#### (b) Marketing Version

**目标**: 外部客户/市场

**特点**:
- 故事化叙述
- 自动规避敏感信息（基于 `internal_only` 标志）
- 适合公开发布
- 可添加客户logo/图片占位符

**模板**:
```markdown
# How ACME Corporation Transformed Their Operations

## The Challenge

ACME Corporation, a leading manufacturing company, was struggling with legacy systems...

## The Solution

Working together, we implemented a comprehensive cloud migration strategy...

## The Results

Within just 6 weeks, ACME achieved remarkable results:
- Revenue increased by 15%
- Operational costs reduced by 40%
- System uptime improved to 99.9%

*"This transformation has been game-changing for our business."*
— Jane Doe, CTO at ACME Corporation

---

*Published: January 2026 | Industry: Manufacturing*
```

---

### 8.2 输出存储

| 输出类型 | 存储位置 | 格式 |
|----------|----------|------|
| **Success Story JSON** | `wins/*.json` | JSON |
| **Obsidian 笔记** | `vault/20_notes/wins/*.md` | Markdown |
| **Weekly Summary** | `vault/30_weekly/YYYY-WW.md` | Markdown |
| **Executive Output** | `vault/40_outputs/executive/YYYY-MM.md` | Markdown |
| **Marketing Output** | `vault/40_outputs/marketing/YYYY-MM.md` | Markdown |

---

## 9. Obsidian 集成

### 9.1 角色定位

Obsidian **仅**作为：
- 阅读界面
- 知识组织工具
- 笔记管理平台

Obsidian **不承担**：
- 计算逻辑
- 数据处理
- Agent 运行

### 9.2 Markdown 模板

#### Success Story Note 模板

```markdown
---
id: win-2026-01-us-003
country: US
month: 2026-01
type: success-story
customer: ACME Corporation
internal_only: false
created: 2026-01-15
tags: [cloud-migration, efficiency, cost-reduction]
---

# ACME Corporation

## 📊 Metrics
- +15% revenue
- -40% operational cost
- +200 employee hours saved/month

## 🎯 Context
Customer was struggling with inefficient legacy systems causing 40% downtime.

## ⚡ Action
Implemented our cloud solution with migration team over 6 weeks.

## 🎉 Outcome
Achieved 99.9% uptime and reduced operational costs by 25%.

## 📎 Sources
- [[email_acme_0123]]
- [[case_study_q1]]

---
**Last Updated**: 2026-01-15
**Confidence**: High
```

#### Weekly Summary 模板

```markdown
---
type: weekly-summary
week: 2026-W03
date_range: 2026-01-15 to 2026-01-21
countries: [US, UK, CN]
---

# Weekly Wins Summary - Week 03

## 📈 Overview
- **New Success Stories**: 5
- **Countries**: US (3), UK (1), CN (1)
- **Total Impact**: +$1.2M revenue identified

## 🏆 Top Stories

### 1. ACME Corporation (US)
- +15% revenue through cloud migration
- [[win-2026-01-us-003|View Details]]

### 2. BBC Studios (UK)
- Improved content delivery by 40%
- [[win-2026-01-uk-001|View Details]]

## 📊 Trends
- Cloud migration: 60% of wins
- Cost reduction: Avg 35%
- Customer satisfaction: Avg 4.8/5

---
*Generated on 2026-01-21*
```

---

## 10. 技术选型

| 模块 | 技术选择 | 版本/说明 |
|------|----------|-----------|
| **编程语言** | Python | 3.10+ |
| **LLM 运行时** | Ollama | 最新版 |
| **LLM 模型** | GLM-4 | 开源版本 |
| **OCR** | Tesseract | v5+ |
| **PDF 解析** | unstructured | 或 pdfplumber |
| **邮件解析** | mailparser | |
| **存储** | 本地文件系统 | JSON + Markdown |
| **配置管理** | YAML | |
| **CLI** | argparse / click | |
| **UI** | Obsidian | 知识管理界面 |

---

## 11. 项目结构

```
wins_lib_generator/
├── run.py                      # 主入口
├── config.yaml                 # 配置文件
├── README.md                   # 项目文档
├── requirements.txt            # Python 依赖
│
├── workflow/                   # 工作流模块
│   ├── __init__.py
│   ├── ingest.py              # 数据收集 (Ingest Agent)
│   ├── normalize.py           # 数据标准化
│   ├── planner.py             # 规划 Agent
│   ├── extract_story.py       # Success Story 抽取 Agent
│   ├── deduplicate.py         # 去重逻辑
│   │
│   ├── outputs/               # 输出 Agents
│   │   ├── __init__.py
│   │   ├── executive.py       # 高管版本
│   │   └── marketing.py       # 市场版本
│   │
│   └── writer.py              # Obsidian 写入器
│
├── models/                    # 数据模型
│   ├── __init__.py
│   ├── raw_item.py            # RawItem 模型
│   ├── success_story.py       # SuccessStory 模型
│   └── library.py             # Wins Library 管理器
│
├── processors/                # 数据处理器
│   ├── __init__.py
│   ├── pdf_processor.py       # PDF 处理
│   ├── email_processor.py     # 邮件处理
│   ├── image_processor.py     # 图片/OCR 处理
│   └── text_processor.py      # 文本处理
│
├── agents/                    # Agent 实现
│   ├── __init__.py
│   ├── base.py                # Agent 基类
│   ├── extraction_agent.py    # 抽取 Agent
│   ├── planner_agent.py       # 规划 Agent
│   └── output_agent.py        # 输出 Agent 基类
│
├── utils/                     # 工具函数
│   ├── __init__.py
│   ├── file_utils.py          # 文件操作
│   ├── date_utils.py          # 日期处理
│   ├── llm_utils.py           # LLM 调用
│   └── similarity.py          # 相似度计算
│
├── templates/                 # Markdown 模板
│   ├── success_story.md       # Success Story 模板
│   ├── weekly_summary.md      # Weekly Summary 模板
│   ├── executive_output.md    # Executive 输出模板
│   └── marketing_output.md    # Marketing 输出模板
│
├── config/                    # 配置
│   ├── prompts.yaml           # Agent 提示词
│   └── settings.yaml          # 系统设置
│
├── wins/                      # Success Story Library (JSON)
│   └── *.json
│
└── vault/                     # Obsidian Vault
    ├── 00_sources/            # 原始数据源
    │   └── YYYY-MM/
    │       └── COUNTRY/
    │           ├── pdf/
    │           ├── email/
    │           ├── teams/
    │           └── images/
    │
    ├── 20_notes/              # Success Story 笔记
    │   └── wins/
    │       └── *.md
    │
    ├── 30_weekly/             # Weekly Summary
    │   └── YYYY-WW.md
    │
    └── 40_outputs/            # 输出文档
        ├── executive/
        │   └── YYYY-MM.md
        └── marketing/
            └── YYYY-MM.md
```

---

## 12. 功能范围

### 12.1 包含功能 (v1)

| 功能 | 优先级 | 说明 |
|------|--------|------|
| ✅ 项目结构与数据模型 | P0 | 基础架构 |
| ✅ Raw Data 标准化 | P0 | PDF/Email/OCR |
| ✅ Success Story 抽取 | P0 | 核心智能 |
| ✅ Wins Library 持久化 | P0 | JSON 存储 |
| ✅ Executive 输出 | P1 | 高管版本 |
| ✅ Marketing 输出 | P1 | 市场版本 |
| ✅ Weekly Runner | P1 | 定期更新流程 |
| ✅ Obsidian 写入 | P1 | Markdown 输出 |
| ✅ 去重逻辑 | P2 | 防止重复 |

### 12.2 不包含功能 (v1)

| 功能 | 原因 | 未来版本 |
|------|------|----------|
| ❌ 自动邮箱/Teams API | 离线约束 | v2 |
| ❌ 向量数据库 | 非必需，增加复杂度 | v2 |
| ❌ 云模型支持 | 离线约束 | - |
| ❌ 实时触发 | 手动触发足够 | v2 |
| ❌ Web UI | Obsidian 作为 UI | v2 |
| ❌ 多语言支持 | 英文优先 | v2 |
| ❌ 高级去重 (embedding) | 字符串相似度足够 | v2 |

---

## 13. 成功标准

系统满足以下条件即视为 **v1 成功**：

| 标准 | 验证方式 |
|------|----------|
| ✅ **全流程离线运行** | 无网络连接情况下完成端到端流程 |
| ✅ **稳定生成每周 Success Story** | 连续 4 周无故障运行 |
| ✅ **同一 Story 生成不同受众版本** | Executive 和 Marketing 版本风格差异明显 |
| ✅ **Obsidian 自动更新** | 运行后 vault/ 目录下生成正确 Markdown 文件 |
| ✅ **可手动重复执行** | 多次运行相同输入，结果一致 |
| ✅ **可人工检查** | 所有中间产物可查看和审计 |

---

## 14. 实施优先级

### Phase 1: 基础架构 (Week 1)
- [x] 项目结构搭建
- [x] 数据模型定义 (RawItem, SuccessStory)
- [x] 配置文件设计

### Phase 2: 数据处理 (Week 1-2)
- [x] Ingest Agent (文件扫描)
- [x] 标准化处理器 (PDF/Email/OCR)
- [x] RawItem 生成

### Phase 3: 核心智能 (Week 2-3)
- [x] Success Story 抽取 Agent
- [x] Planner Agent
- [x] LLM 集成 (Ollama + GLM-4)

### Phase 4: 数据管理 (Week 3)
- [x] Wins Library 持久化
- [x] 去重逻辑
- [x] JSON 存储

### Phase 5: 输出生成 (Week 4)
- [x] Executive Output Agent
- [x] Marketing Output Agent
- [x] Obsidian Writer

### Phase 6: 集成与测试 (Week 4-5)
- [x] Weekly Runner CLI
- [x] 端到端测试
- [x] 文档完善

---

## 15. 给 AI Coding Agent 的最终指示

### 开发原则

1. **可读性优先**
   - 代码清晰、注释充分
   - 模块职责单一
   - 命名规范统一

2. **可复跑**
   - 相同输入 → 相同输出
   - 无隐藏状态
   - 失败可恢复

3. **可审计**
   - 所有中间产物可查看
   - 日志完整
   - 决策可追溯

4. **简单优于复杂**
   - 不追求"黑魔法自动化"
   - 明确的错误处理
   - 人工可干预

### 质量要求

- ✅ 所有输出必须可人工检查
- ✅ 每个模块可独立测试
- ✅ 配置与代码分离
- ✅ 错误信息清晰可操作

### 技术债务策略

- **v1 不做**: 向量数据库、高级去重、自动 API
- **可预留**: 接口抽象，便于未来扩展
- **不预留**: 不为不确定的功能设计复杂接口

---

## 附录

### A. 配置文件示例 (config.yaml)

```yaml
# 系统配置
system:
  offline_mode: true
  llm_backend: ollama
  model: glm-4:9b

# 目录配置
paths:
  vault_root: ./vault
  sources_dir: ./vault/00_sources
  wins_library: ./wins
  notes_dir: ./vault/20_notes/wins
  weekly_dir: ./vault/30_weekly
  outputs_dir: ./vault/40_outputs

# Agent 配置
agents:
  extraction:
    model: glm-4:9b
    temperature: 0.3
    max_tokens: 2000

  planner:
    model: glm-4:9b
    temperature: 0.1

  output:
    model: glm-4:9b
    temperature: 0.7

# 去重配置
deduplication:
  similarity_threshold: 0.85
  algorithm: levenshtein

# Obsidian 配置
obsidian:
  vault_name: Wins Library
  create_frontmatter: true
  link_sources: true
```

### B. CLI 使用示例

```bash
# 每周更新 - 所有国家
python run.py --mode weekly

# 每周更新 - 特定国家
python run.py --mode weekly --country US --country UK

# 仅生成输出（不抽取新数据）
python run.py --mode output --type executive

# 指定月份范围
python run.py --mode weekly --from 2026-01 --to 2026-01

# 查看当前库状态
python run.py --mode status

# 强制重新抽取所有数据
python run.py --mode reindex
```

### C. 数据流示例

**输入**: `vault/00_sources/2026-01/US/email/acme_success.eml`

**处理流程**:
1. Ingest Agent → 发现文件
2. Normalize → 生成 `raw-uuid-123`
3. Extraction Agent → 生成 `win-2026-01-us-001`
4. Save → `wins/win-2026-01-us-001.json`
5. Output → `vault/20_notes/wins/win-2026-01-us-001.md`
6. Output → `vault/40_outputs/executive/2026-01.md`

---

**文档结束**

*本需求文档遵循以下原则:*
- *完整性: 覆盖所有核心功能*
- *可实施性: 技术选型明确*
- *可验证性: 成功标准清晰*
- *可维护性: 架构设计清晰*