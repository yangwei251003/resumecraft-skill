"""
匹配器 —— 执行三分组匹配逻辑：直接匹配 / 可强调关联 / 待补强

核心要求:
- 禁止输出"匹配度80%"这类单一数字结论
- 逐项匹配，每项都指向知识库具体条目
- 待补强项不进入简历正文
"""

from typing import Dict, List


class Matcher:
    """三分组匹配模块"""

    def match(self, profile: Dict, job_data: Dict) -> Dict:
        """执行知识库↔岗位三分组匹配"""
        result = {
            "direct_matches": [],
            "emphasizable_links": [],
            "gaps": [],
            "highlights": [],
            "deemphasize": [],
            "ats_advice": "",
            "interview_likes": [],
            "interview_concerns": [],
            "preparation_needed": [],
        }

        # 1. 直接匹配项
        result["direct_matches"] = self._find_direct_matches(profile, job_data)

        # 2. 可强调关联项
        result["emphasizable_links"] = self._find_emphasizable_links(profile, job_data)

        # 3. 待补强项
        result["gaps"] = self._find_gaps(profile, job_data)

        # 4. 重点展示/弱化建议
        result["highlights"] = self._recommend_highlights(profile, result)
        result["deemphasize"] = self._recommend_deemphasize(profile, job_data)

        # 5. ATS建议
        result["ats_advice"] = self._generate_ats_advice(job_data)

        # 6. 面试官视角
        result["interview_likes"] = self._predict_likes(result)
        result["interview_concerns"] = self._predict_concerns(result)
        result["preparation_needed"] = self._preparation_checklist(result)

        return result

    def _find_direct_matches(self, profile: Dict, job_data: Dict) -> List[Dict]:
        """查找知识库中可直接对应岗位需求的条目"""
        matches = []
        skills = profile.get("skills", [])
        internships = profile.get("internships_jobs", [])
        projects = profile.get("projects", [])
        education = profile.get("education", [])

        keywords = job_data.get("ats_keywords", [])
        requirements = job_data.get("requirements", {})
        all_requirements = (
            requirements.get("hard_requirements", [])
            + requirements.get("core_abilities", [])
        )

        # 技能匹配
        for skill in skills:
            skill_name = skill.get("name", "")
            skill_level = skill.get("level", "")
            for req in all_requirements:
                if skill_name.lower() in req.lower():
                    matches.append({
                        "type": "技能",
                        "requirement": req,
                        "profile_source": f"skills[{skill_name}]",
                        "evidence": f"{skill_name} - {skill_level}",
                        "strength": "强",
                        "detail": skill.get("evidence", ""),
                    })
                    break

        # 实习经历匹配
        for idx, job in enumerate(internships):
            responsibilities = job.get("responsibilities", "")
            for req in all_requirements:
                if any(w in responsibilities for w in ["数据", "分析", "报表", "运营"]):
                    if any(w in req for w in ["数据", "分析", "报表", "运营"]):
                        matches.append({
                            "type": "实习经历",
                            "requirement": req,
                            "profile_source": f"internships_jobs[{idx}] - {job.get('company', '')}",
                            "evidence": job.get("quantified_impact", job.get("deliverables", "")),
                            "strength": "强" if job.get("quantified_impact") else "中",
                            "detail": responsibilities,
                        })
                        break

        # 项目经历匹配
        for idx, proj in enumerate(projects):
            proj_name = proj.get("name", "")
            for req in all_requirements:
                # 简单关键词匹配
                if any(kw in proj_name for kw in ["数据", "分析", "预测", "模型"]):
                    if any(kw in req for kw in ["数据", "分析", "项目"]):
                        matches.append({
                            "type": "项目经历",
                            "requirement": req,
                            "profile_source": f"projects[{idx}] - {proj_name}",
                            "evidence": proj.get("quantified_metrics", proj.get("outcome", "")),
                            "strength": "中",
                            "detail": proj.get("my_role", ""),
                        })
                        break

        # 教育匹配
        for edu in education:
            if any(req_school_keyword in edu.get("school", "") + edu.get("major", "")
                   for req_school_keyword in ["本科", "硕士"]):
                matches.append({
                    "type": "学历",
                    "requirement": "学历要求",
                    "profile_source": f"education[{edu.get('school', '')}]",
                    "evidence": f"{edu.get('degree', '')} - {edu.get('major', '')}",
                    "strength": "强",
                    "detail": "",
                })
                break

        return matches

    def _find_emphasizable_links(self, profile: Dict, job_data: Dict) -> List[Dict]:
        """查找换个表达角度后能更贴合岗位的经历"""
        links = []
        projects = profile.get("projects", [])
        internships = profile.get("internships_jobs", [])
        core_exps = profile.get("core_experiences", [])
        certificates = profile.get("certificates_honors", [])

        # 检查项目经历中可强调的关联
        for idx, proj in enumerate(projects):
            proj_name = proj.get("name", "")
            # 即使项目名称不是直接匹配，但涉及到数据分析/问题解决
            if proj.get("quantified_metrics") or proj.get("highlights"):
                links.append({
                    "source": "project",
                    "index": idx,
                    "name": proj_name,
                    "original": proj.get("my_role", ""),
                    "reframing": f"建议突出：{proj.get('quantified_metrics', proj.get('highlights', ''))}，从技术实现角度改写为业务价值角度",
                    "reason": "体现数据驱动的业务分析能力",
                })

        # 检查实习经历中可强调的关联
        for idx, job in enumerate(internships):
            if job.get("quantified_impact") and "自动化" in job.get("responsibilities", ""):
                links.append({
                    "source": "internship",
                    "index": idx,
                    "name": f"{job.get('company', '')} - {job.get('role', '')}",
                    "original": job.get("responsibilities", ""),
                    "reframing": "建议突出：主动发现流程痛点→设计自动化方案→落地并量化成果，展示完整的'问题发现→解决→价值'链条",
                    "reason": "体现主动解决问题的能力和数据思维",
                })

        # 检查证书/荣誉可强调的关联
        for idx, cert in enumerate(certificates):
            cert_name = cert.get("name", "")
            if any(w in cert_name for w in ["建模", "竞赛", "数学"]):
                links.append({
                    "source": "certificate",
                    "index": idx,
                    "name": cert_name,
                    "original": cert_name,
                    "reframing": "不只是列一个奖项，而是强调背后的能力：快速学习、高强度分析、团队协作、数据建模",
                    "reason": "竞赛经历体现快速学习和抗压能力",
                })

        return links

    def _find_gaps(self, profile: Dict, job_data: Dict) -> List[Dict]:
        """查找岗位需要但知识库中确实没有的能力"""
        gaps = []
        skills = profile.get("skills", [])
        skill_names = [s.get("name", "").lower() for s in skills]

        must_have = job_data.get("must_have_skills", [])
        nice_have = job_data.get("nice_to_have_skills", [])

        # 检查必备技能的缺失
        for skill in must_have:
            if skill.lower() not in [s.lower() for s in skill_names]:
                importance = "必须补"
                # 检查用户是否在学习中
                is_learning = any(
                    s.get("name", "").lower() == skill.lower() and s.get("level") == "基础"
                    for s in skills
                )
                gaps.append({
                    "ability": skill,
                    "importance": importance,
                    "current_status": "正在学习中" if is_learning else "缺失",
                    "learning_suggestion": self._get_learning_suggestion(skill),
                    "estimated_time": self._get_learning_time(skill),
                    "mitigation_strategy": self._get_mitigation_strategy(skill, profile),
                })

        # 检查加分技能的缺失
        for skill in nice_have:
            if skill.lower() not in [s.lower() for s in skill_names]:
                if not any(g["ability"] == skill for g in gaps):
                    gaps.append({
                        "ability": skill,
                        "importance": "建议补",
                        "current_status": "缺失",
                        "learning_suggestion": self._get_learning_suggestion(skill),
                        "estimated_time": self._get_learning_time(skill),
                        "mitigation_strategy": self._get_mitigation_strategy(skill, profile),
                    })

        return gaps

    def _get_learning_suggestion(self, skill: str) -> str:
        """获取学习建议"""
        suggestions = {
            "SQL": "LeetCode SQL 50题 + 牛客网实战（3-5天）→ 进阶《高性能MySQL》（2周）",
            "Python": "官方文档 + 实战项目。已熟悉的可跳过基础，直接练数据处理和自动化",
            "Tableau": "Tableau Public 免费版 + 官方教程（3天入门）",
            "Power BI": "Power BI Desktop 免费 + 微软官方学习路径（1周入门）",
            "A/B测试": "Udacity免费课程 'A/B Testing'（2天了解）+ Kaggle实战",
            "机器学习": "吴恩达 Coursera 课程（4周系统学习）",
        }
        return suggestions.get(skill, f"搜索「{skill}入门教程」找一个评分高的免费课程开始学习")

    def _get_learning_time(self, skill: str) -> str:
        """获取预估学习时间"""
        times = {
            "SQL": "1-2周",
            "Python": "已掌握（或2-4周系统学习）",
            "Tableau": "1周",
            "Power BI": "1周",
            "A/B测试": "2-3天",
            "机器学习": "2-4周",
        }
        return times.get(skill, "1-2周")

    def _get_mitigation_strategy(self, skill: str, profile: Dict) -> str:
        """获取在当前简历中的应对策略"""
        skills = profile.get("skills", [])
        related = [s["name"] for s in skills if s.get("level") in ["熟悉", "熟练"]]

        if related:
            return f"不写「掌握{skill}」，但可以强调相关能力：{'、'.join(related[:3])}。面试诚实说自己正在学{skill}"
        return f"不写{skill}。在面试中诚实表达正在学习，并展示学习意愿和计划"

    def _recommend_highlights(self, profile: Dict, matches: Dict) -> List[str]:
        """推荐重点展示的经历"""
        highlights = []

        # 直接匹配度强的经历优先展示
        strong_matches = [m for m in matches.get("direct_matches", []) if m.get("strength") == "强"]
        for m in strong_matches[:3]:
            highlights.append(m.get("profile_source", ""))

        # 有量化成果的经历
        for job in profile.get("internships_jobs", []):
            if job.get("quantified_impact"):
                highlights.append(f"实习：{job.get('company', '')} - {job.get('quantified_impact', '')[:50]}")

        for proj in profile.get("projects", []):
            if proj.get("quantified_metrics"):
                highlights.append(f"项目：{proj.get('name', '')} - {proj.get('quantified_metrics', '')[:50]}")

        return highlights[:5]

    def _recommend_deemphasize(self, profile: Dict, job_data: Dict) -> List[str]:
        """推荐弱化或隐藏的经历"""
        deemphasize = []

        # 与目标岗位关联度低的经历
        title = job_data.get("job_info", {}).get("title", "")

        for proj in profile.get("projects", []):
            proj_name = proj.get("name", "")
            # 如果项目名称与岗位关键词都不相关
            if not any(kw in proj_name for kw in ["数据", "分析", "产品", "运营"]):
                deemphasize.append(f"项目「{proj_name}」与{title}岗位关联度低，建议弱化或删除")

        return deemphasize

    def _generate_ats_advice(self, job_data: Dict) -> str:
        """生成ATS关键词建议"""
        keywords = job_data.get("ats_keywords", [])
        if not keywords:
            return "建议在简历中自然嵌入岗位相关的技术/能力关键词"

        return f"建议在简历各模块自然嵌入以下关键词（不要堆砌）：\n{', '.join(keywords[:10])}"

    def _predict_likes(self, matches: Dict) -> List[str]:
        """预测面试官可能喜欢的点"""
        likes = []
        strong_count = len([m for m in matches.get("direct_matches", []) if m.get("strength") == "强"])

        if strong_count >= 2:
            likes.append("核心能力与岗位匹配度高")
        if matches.get("emphasizable_links"):
            likes.append("有主动解决问题的意识和成果")
        if any("实习" in m.get("type", "") for m in matches.get("direct_matches", [])):
            likes.append("有真实业务场景的实战经验")

        return likes + ["简历结构清晰、有量化成果"]

    def _predict_concerns(self, matches: Dict) -> List[str]:
        """预测面试官可能质疑的点"""
        concerns = []
        gaps = matches.get("gaps", [])

        must_fix = [g for g in gaps if g.get("importance") == "必须补"]
        for g in must_fix:
            concerns.append(f"{g['ability']} 水平可能不达标")

        return concerns + ["需要准备应对话术"]

    def _preparation_checklist(self, matches: Dict) -> List[str]:
        """列出需要提前准备的解释"""
        checklist = []

        must_fix = [g for g in matches.get("gaps", []) if g.get("importance") == "必须补"]
        for g in must_fix:
            checklist.append(f"准备 {g['ability']} 不足的解释话术：说明当前水平 + 学习进度 + 弥补方案")

        checklist.append("准备3个STAR故事（从知识库核心经历中提取）")
        checklist.append("练习1-2分钟自我介绍")

        return checklist

    def generate_report(self, matching_result: Dict) -> str:
        """生成匹配分析报告 Markdown"""
        lines = []
        lines.append("# 岗位匹配分析报告\n")

        # 直接匹配项
        lines.append("## 一、直接匹配项 ✅\n")
        for i, m in enumerate(matching_result.get("direct_matches", []), 1):
            lines.append(f"### ✅ 匹配项 #{i}：{m.get('requirement', '')}")
            lines.append(f"- **类型**：{m.get('type', '')}")
            lines.append(f"- **知识库依据**：{m.get('profile_source', '')}")
            lines.append(f"- **证据**：{m.get('evidence', '')}")
            lines.append(f"- **匹配强度**：{m.get('strength', '')}")
            lines.append("")

        # 可强调关联项
        lines.append("## 二、可强调关联项 🔗\n")
        for i, l in enumerate(matching_result.get("emphasizable_links", []), 1):
            lines.append(f"### 🔗 关联项 #{i}：{l.get('name', '')}")
            lines.append(f"- **原始表达**：{l.get('original', '')}")
            lines.append(f"- **换角度建议**：{l.get('reframing', '')}")
            lines.append(f"- **理由**：{l.get('reason', '')}")
            lines.append("")

        # 待补强项
        lines.append("## 三、待补强项 ⚠️\n")
        for i, g in enumerate(matching_result.get("gaps", []), 1):
            lines.append(f"### ⚠️ 待补强项 #{i}：{g.get('ability', '')}")
            lines.append(f"- **重要程度**：{g.get('importance', '')}")
            lines.append(f"- **当前状态**：{g.get('current_status', '')}")
            lines.append(f"- **学习建议**：{g.get('learning_suggestion', '')}")
            lines.append(f"- **预估时间**：{g.get('estimated_time', '')}")
            lines.append(f"- **应对策略**：{g.get('mitigation_strategy', '')}")
            lines.append("")

        # 面试官视角
        lines.append("## 四、面试官视角分析\n")
        lines.append("### 可能喜欢的点")
        for l in matching_result.get("interview_likes", []):
            lines.append(f"- {l}")
        lines.append("\n### 可能质疑的点")
        for c in matching_result.get("interview_concerns", []):
            lines.append(f"- {c}")
        lines.append("\n### 需提前准备的解释")
        for p in matching_result.get("preparation_needed", []):
            lines.append(f"- {p}")

        return "\n".join(lines)

    def format_result(self, matching_result: Dict) -> str:
        """格式化输出匹配结果摘要"""
        direct_count = len(matching_result.get("direct_matches", []))
        link_count = len(matching_result.get("emphasizable_links", []))
        gap_count = len(matching_result.get("gaps", []))

        lines = []
        lines.append(f"\n{'='*50}")
        lines.append(f"  📊 三分组匹配分析完成")
        lines.append(f"{'='*50}")
        lines.append(f"  ✅ 直接匹配项：{direct_count} 条")
        lines.append(f"  🔗 可强调关联项：{link_count} 条")
        lines.append(f"  ⚠️ 待补强项：{gap_count} 条")
        lines.append(f"{'='*50}")

        if gap_count > 0:
            must_fix = [g["ability"] for g in matching_result.get("gaps", [])
                       if g.get("importance") == "必须补"]
            if must_fix:
                lines.append(f"\n⚠️ 以下能力需要尽快补强：{'、'.join(must_fix)}")

        return "\n".join(lines)
