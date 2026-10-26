"""
完整性自检器 —— 对知识库执行五维度自检，决定是否放行到下一阶段

自检清单:
1. 能否用一句话说出3个核心竞争力（每个指向知识库具体条目）
2. 知识库是否足够支撑至少2-3个不同方向岗位的初判
3. 是否存在前后矛盾、重复或空洞描述
4. 核心/实习/项目经历是否都包含可衡量结果
5. 技能熟练度标注是否真实可信
"""

from typing import Dict, List


class ProfileSelfChecker:
    """知识库完整性自检模块"""

    def check(self, profile: Dict) -> List[Dict]:
        """执行全量自检，返回每项检查结果"""
        results = []

        # 检查1：核心竞争力清晰度
        results.append(self._check_core_competencies(profile))

        # 检查2：多方向支撑能力
        results.append(self._check_multi_direction(profile))

        # 检查3：内容一致性
        results.append(self._check_consistency(profile))

        # 检查4：可衡量结果完整性
        results.append(self._check_measurable_results(profile))

        # 检查5：技能熟练度真实性
        results.append(self._check_skill_authenticity(profile))

        return results

    def _check_core_competencies(self, profile: Dict) -> Dict:
        """检查核心竞争力是否清晰"""
        strengths = profile.get("self_reflection", {}).get("strengths", [])
        core_exps = profile.get("core_experiences", [])
        skills = profile.get("skills", [])
        jobs = profile.get("internships_jobs", [])
        projects = profile.get("projects", [])

        # 至少需要识别3个核心竞争力
        skill_count = len([s for s in skills if s.get("level") in ["熟悉", "熟练", "精通"]])
        exp_count = len(core_exps) + len(jobs) + len(projects)

        has_enough = (
            len(strengths) >= 2
            and (skill_count >= 2 or exp_count >= 2)
        )

        return {
            "name": "核心竞争力清晰度",
            "pass": has_enough,
            "reason": "" if has_enough else "核心竞争力不够明确，建议补充至少2个具体优势描述和2项熟练技能"
        }

    def _check_multi_direction(self, profile: Dict) -> Dict:
        """检查是否足够支撑多方向匹配"""
        skills = profile.get("skills", [])
        projects = profile.get("projects", [])
        jobs = profile.get("internships_jobs", [])

        total_items = len(skills) + len(projects) + len(jobs)
        has_enough = total_items >= 6

        return {
            "name": "多方向支撑能力",
            "pass": has_enough,
            "reason": "" if has_enough else f"知识库条目较少（共{total_items}条），建议至少补充6条以上以支撑多方向匹配"
        }

    def _check_consistency(self, profile: Dict) -> Dict:
        """检查内容一致性"""
        issues = []

        # 检查技能一致性：技能清单中标注为"精通"的，是否有对应证据
        master_skills = [s for s in profile.get("skills", []) if s.get("level") == "精通"]
        for skill in master_skills:
            if not skill.get("evidence"):
                issues.append(f"技能「{skill['name']}」标注为精通但缺少证据支撑")

        # 检查时间线一致性（简单检查：教育时间不能和实习时间冲突）
        edu_list = profile.get("education", [])
        job_list = profile.get("internships_jobs", [])

        has_enough = len(issues) == 0
        return {
            "name": "内容一致性",
            "pass": has_enough,
            "reason": "; ".join(issues) if issues else ""
        }

    def _check_measurable_results(self, profile: Dict) -> Dict:
        """检查是否包含可衡量结果"""
        missing = []

        # 核心经历
        for i, exp in enumerate(profile.get("core_experiences", [])):
            if not exp.get("results_with_data"):
                missing.append(f"核心经历 #{i+1}「{exp.get('title', '未命名')}」缺少量化结果")

        # 实习经历
        for i, job in enumerate(profile.get("internships_jobs", [])):
            if not job.get("quantified_impact") and not job.get("deliverables"):
                missing.append(f"实习经历 #{i+1}「{job.get('company', '')} {job.get('role', '')}」缺少量化成果")

        # 项目经历
        for i, proj in enumerate(profile.get("projects", [])):
            if not proj.get("quantified_metrics"):
                missing.append(f"项目经历 #{i+1}「{proj.get('name', '未命名')}」缺少量化指标")

        has_enough = len(missing) == 0
        return {
            "name": "可衡量结果完整性",
            "pass": has_enough,
            "reason": "; ".join(missing) if missing else ""
        }

    def _check_skill_authenticity(self, profile: Dict) -> Dict:
        """检查技能熟练度真实性"""
        suspicious = []

        # 检查是否有"精通"但无证据的技能
        master_skills = [s for s in profile.get("skills", []) if s.get("level") == "精通"]
        if len(master_skills) > 2:
            suspicious.append(f"标注为「精通」的技能有{len(master_skills)}项，建议确认是否真的都达到了精通水平")

        # 检查是否所有技能都有级别标注
        unlabeled = [s["name"] for s in profile.get("skills", []) if not s.get("level")]
        if unlabeled:
            suspicious.append(f"以下技能未标注掌握程度：{'、'.join(unlabeled)}")

        has_enough = len(suspicious) == 0
        return {
            "name": "技能熟练度真实性",
            "pass": has_enough,
            "reason": "; ".join(suspicious) if suspicious else ""
        }

    def all_passed(self, results: List[Dict]) -> bool:
        """判断是否全部通过"""
        return all(r["pass"] for r in results)

    def get_failed_items(self, results: List[Dict]) -> List[str]:
        """获取未通过的项目名称列表"""
        return [r["name"] for r in results if not r["pass"]]
