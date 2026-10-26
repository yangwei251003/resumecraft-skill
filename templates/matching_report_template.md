# 岗位匹配分析报告

> 生成时间：{date}
> 岗位：{job_title} @ {company}
> 基于知识库版本：{profile_version}

---

## 一、岗位理解与拆解

### 1.1 基本信息

| 项目 | 内容 |
|------|------|
| 岗位名称 | {job_title} |
| 公司/行业 | {company} / {industry} |
| 工作地点 | {location} |
| 薪资范围 | {salary_range} |
| 经验要求 | {experience_required} |
| 学历要求 | {education_required} |

### 1.2 岗位核心职责

{core_responsibilities_list}

### 1.3 硬性要求（门槛项）

{hard_requirements_list}

### 1.4 核心能力要求

{core_abilities_list}

### 1.5 隐性偏好

{hidden_preferences_list}

### 1.6 高频关键词（ATS 优化）

`{keyword1}` `{keyword2}` `{keyword3}` ...

### 1.7 必备技能 vs 加分技能

| 必备技能 | 加分技能 |
|----------|----------|
| {must1} | {nice1} |

### 1.8 该岗位真正看重的能力

{real_requirements_text}

### 1.9 面试官筛选简历的关键信号

{resume_signals_list}

### 1.10 岗位人才画像

- **适合**：{suitable_traits}
- **不适合**：{unsuitable_traits}

---

## 二、三分组匹配分析

### 2.1 第一组：直接匹配项 ✅

以下经历/技能可直接对应岗位需求，作为简历正文主力来源：

{for each direct_match:}
#### ✅ 匹配项 #{index}：{requirement_name}

- **岗位要求**：{requirement_description}
- **知识库依据**：{profile_source_path}
- **具体证据**：{evidence_detail}
- **匹配强度**：{强/中}

---

### 2.2 第二组：可强调关联项 🔗

以下经历换个表达角度后能更贴合该岗位：

{for each emphasizable_link:}
#### 🔗 关联项 #{index}：{original_experience}

- **原始经历**：{original_text}
- **岗位需要**：{required_ability}
- **换角度建议**：{reframing_suggestion}
- **建议改写为**：{rewritten_version}
- **改写理由**：{reason}

---

### 2.3 第三组：待补强项 ⚠️

以下能力岗位需要但知识库中确实欠缺，不写入简历正文：

{for each gap:}
#### ⚠️ 待补强项 #{index}：{ability_name}

- **缺失能力**：{ability_description}
- **重要程度**：{必须补 / 建议补 / 可选补}
- **当前状态**：{current_status}
- **速成学习建议**：{learning_suggestion}
- **预估时间**：{estimated_time}
- **在当前简历中的应对方式**：{mitigation_strategy}

---

## 三、简历优化策略

### 3.1 重点展示的经历

{highlight_experiences}

### 3.2 建议弱化或隐藏的经历

{deemphasize_experiences}

### 3.3 ATS 关键词匹配建议

{ats_keyword_advice}

### 3.4 面试官可能喜欢的点

{liked_points}

### 3.5 面试官可能质疑的点

{questioned_points}

### 3.6 需要提前准备的解释

{preparation_needed}

---

## 四、岗位客观评价

### 4.1 综合评价

| 维度 | 评价 |
|------|------|
| 优点 | {pros} |
| 缺点 | {cons} |
| 成长空间 | {growth} |
| 薪资发展潜力 | {salary_potential} |
| 工作强度/压力 | {workload} |
| AI替代风险 | {ai_risk} |
| 新人友好度 | {newcomer_friendliness} |
| 长期发展 | {long_term} |
| 行业风险 | {industry_risk} |

### 4.2 用户适配判断

{user_fit_analysis}

### 4.3 投递建议

**建议：{强烈推荐 / 可以尝试 / 谨慎投递 / 不建议}**

理由：{reason}

---

## 五、匹配分析总结

{summary}
