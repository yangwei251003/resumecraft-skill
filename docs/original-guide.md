# ResumeCraft —— 原设计与目标记录

> 这是原始设计记录，部分目标尚未实现或核验。实际使用请从[当前README](../README.md)和[验证记录](VERIFICATION.md)开始。命令从仓库根目录执行。

> 一个分四阶段运行的状态机式 AI 简历生成技能。先引导用户建立结构化、可追溯的个人职业知识库；通过完整性自检后，针对目标岗位 JD 做深度拆解与三分组匹配；最终生成一页式、排版精美、内容可信的中文 Word 简历，并同步输出匹配分析报告、学习提升路径与面试准备建议。

---

## 快速开始

### 在 WorkBuddy 中使用

直接说以下触发词即可激活：
- "帮我写简历"
- "帮我匹配这个岗位"
- "我想更新知识库"
- "帮我分析这个 JD"

### 命令行运行

```bash
# 交互式模式
python src/index.py --mode interactive

# 批量模式（需提供知识库和JD文件）
python src/index.py --mode batch --profile examples/sample_profile.json --jd examples/sample_job_description.md
```

---

## 四阶段流程

```
collecting → self_check → job_matching → generating
    ↑            ↓               ↓               ↓
  知识库收集 → 完整性自检 → 岗位解析匹配 → 简历生成输出
```

### 阶段一：知识库收集（collecting）
逐模块引导用户建立 9 大模块的个人职业知识库，对模糊/空洞/无数据的回答强制追问。

### 阶段二：完整性自检（self_check）
五维度自检：核心竞争力、多方向支撑、内容一致性、可衡量结果、技能真实性。

### 阶段三：岗位解析与匹配（job_matching）
- 三分组匹配：直接匹配项 + 可强调关联项 + 待补强项
- 岗位客观评价：优点/缺点/成长空间/AI风险/投递建议

### 阶段四：简历生成（generating）
- 一页式 Word 简历 + 纯文本版本
- 匹配分析报告
- 学习提升路径（7天+30天）
- 面试准备建议
- 可追溯性自查

---

## 核心原则（不可覆盖）

1. **真实性**：简历内容必须来自知识库中真实存在的经历
2. **诚实差距披露**：不会的技能不伪装，放在学习路径中
3. **流程不可跳过**：必须通过自检才能进入简历生成
4. **可追溯性**：简历每句话都能在知识库中找到依据
5. **不鼓励求职欺诈**：帮助但不协助造假

---

## 项目结构

```
resumecraft-skill/
├── SKILL.md                    # WorkBuddy 技能主定义
├── README.md                   # 本文件
├── prompts/                    # AI 提示词文件
│   ├── system_prompt.md        # 核心系统提示词
│   ├── profile_collector_prompt.md
│   ├── job_parser_prompt.md
│   ├── matcher_prompt.md
│   ├── resume_writer_prompt.md
│   ├── learning_advisor_prompt.md
│   ├── interview_coach_prompt.md
│   └── ethics_guard_prompt.md
├── templates/                  # 模板文件
│   ├── profile_schema.json     # 知识库 JSON Schema
│   ├── job_schema.json         # 岗位信息 Schema
│   ├── matching_report_template.md
│   ├── resume_template.md
│   ├── learning_path_template.md
│   └── self_check_template.md
├── src/                        # Python 源码
│   ├── index.py                # 主入口
│   ├── stateManager.py         # 状态机管理器
│   ├── profileCollector.py     # 知识库收集器
│   ├── profileSelfChecker.py   # 完整性自检器
│   ├── profileAnalyzer.py      # 职业画像分析器
│   ├── jobParser.py            # 岗位解析器
│   ├── jobResearcher.py        # 岗位研究员
│   ├── matcher.py              # 匹配器（三分组）
│   ├── resumeWriter.py         # 简历内容生成器
│   ├── resumeFormatter.py      # Word 格式化器
│   ├── traceabilityChecker.py  # 可追溯性检查器
│   ├── learningAdvisor.py      # 学习顾问
│   ├── interviewCoach.py       # 面试教练
│   └── ethicsGuard.py          # 伦理守护者
├── examples/                   # 示例文件
│   ├── sample_profile.json     # 示例知识库
│   ├── sample_job_description.md  # 示例 JD
│   ├── sample_matching_report.md  # 示例匹配报告
│   ├── sample_resume_output.md    # 示例简历
│   └── sample_learning_path.md    # 示例学习路径
└── antigravity/                # Antigravity IDE 格式
    └── resumecraft.skill.md
```

---

## 验收标准

| # | 测试场景 | 预期行为 |
|---|---------|---------|
| 1 | 模糊输入（"我负责过运营"） | AI 主动追问细节和量化结果 |
| 2 | 知识库不完整 | 拒绝进入简历生成 |
| 3 | 给定岗位 | 输出三分组匹配，非"匹配度80%" |
| 4 | 简历每句话 | 能在知识库找到依据 |
| 5 | 待补强项 | 隔离在学习路径中 |
| 6 | Word 文件 | 一页、ATS友好 |
| 7 | JD 截图 | 正确识别解析 |
| 8 | 降级例外 | 明确标注质量受限模块 |
| 9 | 知识库更新 | 状态正确回退 collecting |

---

## 环境依赖

- Python 3.8+
- python-docx（用于生成 Word 简历，可选）

```bash
pip install python-docx
```

---

## License

MIT
