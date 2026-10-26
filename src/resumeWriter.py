"""
简历写作器 —— 基于匹配结果生成一页式简历内容

规则:
1. 仅使用直接匹配项+可强调关联项
2. 自我评价包含：胜任理由+能力对应+待提升方向
3. 模块顺序按岗位优先级动态排列
4. 润色规则：专业化、结果导向、不新增事实
"""

from typing import Dict, List


class ResumeWriter:
    """简历内容生成模块"""

    def write(self, profile: Dict, matching_result: Dict) -> Dict:
        """生成简历各模块内容"""
        resume = {
            "personal_info": self._write_personal_info(profile),
            "job_intention": self._write_job_intention(profile, matching_result),
            "education": self._write_education(profile),
            "self_evaluation": self._write_self_evaluation(profile, matching_result),
            "skills": self._write_skills(profile),
            "experiences": self._write_experiences(profile, matching_result),
            "projects": self._write_projects(profile, matching_result),
            "certificates": self._write_certificates(profile),
            "portfolio": self._write_portfolio(profile),
            "module_order": self._determine_module_order(profile, matching_result),
        }

        return resume

    def _write_personal_info(self, profile: Dict) -> Dict:
        """写个人信息"""
        basic = profile.get("basic_info", {})
        return {
            "name": basic.get("name", ""),
            "phone": basic.get("phone", ""),
            "email": basic.get("email", ""),
            "city": basic.get("current_city", ""),
            "links": basic.get("links", {}),
        }

    def _write_job_intention(self, profile: Dict, matching_result: Dict) -> Dict:
        """写求职意向"""
        # 从匹配结果推断
        direct_matches = matching_result.get("direct_matches", [])
        # 简单推断
        if direct_matches:
            return {
                "target": profile.get("basic_info", {}).get("target_direction", ""),
                "city": profile.get("basic_info", {}).get("target_city", ""),
                "status": "随时到岗",
            }
        return {
            "target": profile.get("basic_info", {}).get("target_direction", ""),
            "city": profile.get("basic_info", {}).get("target_city", ""),
        }

    def _write_education(self, profile: Dict) -> List[Dict]:
        """写教育经历"""
        edu_list = profile.get("education", [])
        result = []
        for edu in edu_list:
            result.append({
                "school": edu.get("school", ""),
                "major": edu.get("major", ""),
                "degree": edu.get("degree", ""),
                "period": edu.get("period", ""),
                "gpa": edu.get("gpa_rank", ""),
                "courses": edu.get("core_courses", ""),
                "thesis": edu.get("thesis_direction", ""),
            })
        return result

    def _write_self_evaluation(self, profile: Dict, matching_result: Dict) -> str:
        """写自我评价（三段式：胜任理由+能力对应+待提升方向）"""
        parts = []

        # (a) 基于真实匹配点说明胜任理由
        direct_matches = matching_result.get("direct_matches", [])
        strong_matches = [m for m in direct_matches if m.get("strength") == "强"]

        if strong_matches:
            parts.append(f"具备{len(strong_matches)}项与岗位要求直接匹配的核心能力，包括{'、'.join(m['requirement'][:20] for m in strong_matches[:3])}。")

        # 补充具体经历
        internships = profile.get("internships_jobs", [])
        for job in internships:
            if job.get("quantified_impact"):
                parts.append(f"曾在{job.get('company', '')}担任{job.get('role', '')}，{job.get('quantified_impact', '')}。")
                break

        # (b) 已有能力与岗位需求的对应关系
        skills = profile.get("skills", [])
        familiar = [s["name"] for s in skills if s.get("level") in ["熟悉", "熟练"]]
        if familiar:
            parts.append(f"熟练掌握{'、'.join(familiar[:5])}，能够满足岗位对核心技能的要求。")

        # (c) 坦诚的待提升方向
        gaps = matching_result.get("gaps", [])
        must_learn = [g for g in gaps if g.get("importance") == "必须补"]
        if must_learn:
            skill_names = [g["ability"] for g in must_learn[:2]]
            parts.append(f"目前正在系统学习{'和'.join(skill_names)}，预计{gaps[0].get('estimated_time', '1-2周')}内达到独立工作水平。")
        else:
            # 即使没有必须补的，也展示一个成长方向
            parts.append("持续关注行业前沿技术，正在深入学习数据驱动决策方法论，力求将分析能力与业务理解深度结合。")

        return " ".join(parts)

    def _write_skills(self, profile: Dict) -> List[Dict]:
        """写技能清单"""
        skills = profile.get("skills", [])
        result = []

        # 按类别分组
        categorized = {}
        for s in skills:
            cat = s.get("category", "其他")
            if cat not in categorized:
                categorized[cat] = []
            categorized[cat].append(s)

        # 排序：熟悉的技能优先
        level_order = {"精通": 0, "熟练": 1, "熟悉": 2, "基础": 3, "了解": 4}
        for cat, skill_list in categorized.items():
            skill_list.sort(key=lambda s: level_order.get(s.get("level", "了解"), 5))

        return categorized

    def _write_experiences(self, profile: Dict, matching_result: Dict) -> List[Dict]:
        """写实习/工作经历（润色后）"""
        internships = profile.get("internships_jobs", [])
        result = []

        for job in internships:
            bullets = []

            # 职责 → 行动+结果
            responsibilities = job.get("responsibilities", "")
            if responsibilities:
                bullets.append(self._polish_bullet(responsibilities, job))

            # 量化成果
            if job.get("quantified_impact"):
                bullets.append(self._polish_bullet(job["quantified_impact"], job))

            # 问题-方案
            if job.get("problems_faced") and job.get("solutions"):
                bullets.append(self._polish_bullet(
                    f"面对{job['problems_faced']}的问题，采用{job['solutions']}解决",
                    job
                ))

            # 限制 2-4 条
            bullets = bullets[:4]

            result.append({
                "company": job.get("company", ""),
                "role": job.get("role", ""),
                "period": job.get("period", ""),
                "bullets": bullets,
            })

        return result

    def _write_projects(self, profile: Dict, matching_result: Dict) -> List[Dict]:
        """写项目经历（润色后）"""
        projects = profile.get("projects", [])
        result = []

        for proj in projects:
            bullets = []

            # 我的角色+做了什么
            role = proj.get("my_role", "")
            if role:
                bullets.append(self._polish_bullet(role, proj))

            # 量化指标
            if proj.get("quantified_metrics"):
                bullets.append(self._polish_bullet(proj["quantified_metrics"], proj))

            # 亮点
            if proj.get("highlights"):
                bullets.append(self._polish_bullet(proj["highlights"], proj))

            bullets = bullets[:3]

            result.append({
                "name": proj.get("name", ""),
                "period": proj.get("period", ""),
                "bullets": bullets,
            })

        return result

    def _write_certificates(self, profile: Dict) -> List[Dict]:
        """写证书/荣誉"""
        return [
            {
                "name": c.get("name", ""),
                "issuer": c.get("issuer", ""),
                "date": c.get("date", ""),
                "level": c.get("level", ""),
            }
            for c in profile.get("certificates_honors", [])
        ]

    def _write_portfolio(self, profile: Dict) -> List[Dict]:
        """写作品链接"""
        return profile.get("portfolio", [])

    def _determine_module_order(self, profile: Dict, matching_result: Dict) -> List[str]:
        """按岗位优先级动态确定模块顺序"""
        # 默认顺序
        default_order = [
            "personal_info",
            "job_intention",
            "education",
            "self_evaluation",
            "experiences",
            "projects",
            "skills",
            "certificates",
            "portfolio",
        ]

        # 有实习经验的优先展示实习
        if profile.get("internships_jobs"):
            # 实习经历提前到自我评价之后
            return default_order

        # 有项目的优先展示项目
        if profile.get("projects") and len(profile.get("projects", [])) >= 2:
            # 项目经历提前
            reordered = default_order.copy()
            reordered.remove("projects")
            reordered.insert(reordered.index("education") + 1, "projects")
            return reordered

        return default_order

    def _polish_bullet(self, text: str, source: Dict) -> str:
        """润色 bullet point：专业化表达，结果导向"""
        # 添加动词前缀
        if not any(text.startswith(v) for v in ["负责", "独立", "主导", "协助", "参与", "设计", "搭建"]):
            text = f"负责{text}"

        # 确保有结果导向
        if not any(w in text for w in ["提升", "增长", "降低", "减少", "增加", "优化", "改善", "缩短", "完成"]):
            text += "，形成可复用成果"

        return text
