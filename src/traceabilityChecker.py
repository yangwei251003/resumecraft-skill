"""
可追溯性检查器 —— 逐句核对简历内容在知识库中的溯源依据

核心原则4: 简历中每一句话必须能在知识库中找到具体依据
找不到依据 → 标记为违规 → 删除或改写
"""

from typing import Dict, List, Tuple


class TraceabilityChecker:
    """简历可追溯性检查模块"""

    def check(self, resume_content: Dict, profile: Dict) -> List[Dict]:
        """检查简历内容是否可追溯，返回问题列表"""
        issues = []

        # 检查个人信息
        issues += self._check_personal_info(resume_content, profile)

        # 检查教育经历
        issues += self._check_education(resume_content, profile)

        # 检查自我评价
        issues += self._check_self_evaluation(resume_content, profile)

        # 检查技能
        issues += self._check_skills(resume_content, profile)

        # 检查经历
        issues += self._check_experiences(resume_content, profile)

        # 检查项目
        issues += self._check_projects(resume_content, profile)

        # 检查证书
        issues += self._check_certificates(resume_content, profile)

        return issues

    def fix(self, resume_content: Dict, profile: Dict) -> Dict:
        """自动修正可追溯性问题"""
        issues = self.check(resume_content, profile)

        for issue in issues:
            location = issue.get("location", "")
            problem = issue.get("problem", "")
            action = issue.get("action", "")

            if action == "delete":
                # 找到并删除对应内容
                self._delete_content(resume_content, location)
            elif action == "rewrite":
                # 改写为有依据的表达
                self._rewrite_content(resume_content, location, profile)

        return resume_content

    def _check_personal_info(self, resume: Dict, profile: Dict) -> List[Dict]:
        """检查个人信息可追溯性"""
        issues = []
        pi = resume.get("personal_info", {})
        bi = profile.get("basic_info", {})

        if pi.get("name") and pi["name"] != bi.get("name"):
            issues.append({
                "location": "personal_info.name",
                "problem": f"姓名不一致：简历「{pi['name']}」vs 知识库「{bi.get('name', '')}」",
                "action": "rewrite",
            })

        if pi.get("email") and pi["email"] != bi.get("email"):
            issues.append({
                "location": "personal_info.email",
                "problem": f"邮箱不一致",
                "action": "rewrite",
            })

        return issues

    def _check_education(self, resume: Dict, profile: Dict) -> List[Dict]:
        """检查教育经历"""
        issues = []
        resume_edu = resume.get("education", [])
        profile_edu = profile.get("education", [])

        for i, edu in enumerate(resume_edu):
            if i >= len(profile_edu):
                issues.append({
                    "location": f"education[{i}]",
                    "problem": "简历中有知识库不存在的教育经历",
                    "action": "delete",
                })
                continue

            pe = profile_edu[i]
            if edu.get("school") and edu["school"] != pe.get("school"):
                issues.append({
                    "location": f"education[{i}].school",
                    "problem": f"学校名称不一致",
                    "action": "rewrite",
                })
            if edu.get("degree") and edu["degree"] != pe.get("degree"):
                issues.append({
                    "location": f"education[{i}].degree",
                    "problem": "学历描述不一致",
                    "action": "rewrite",
                })

        return issues

    def _check_self_evaluation(self, resume: Dict, profile: Dict) -> List[Dict]:
        """检查自我评价"""
        issues = []
        text = resume.get("self_evaluation", "")

        # 检查是否有声称"精通"的技能但知识库中不是精通
        skills = profile.get("skills", [])
        for skill in skills:
            name = skill.get("name", "")
            level = skill.get("level", "")
            if level != "精通" and name and f"精通{name}" in text:
                issues.append({
                    "location": "self_evaluation",
                    "problem": f"自称「精通{name}」但知识库中标注为「{level}」",
                    "action": "rewrite",
                })

        return issues

    def _check_skills(self, resume: Dict, profile: Dict) -> List[Dict]:
        """检查技能清单"""
        issues = []
        resume_skills = resume.get("skills", {})
        profile_skills = {s.get("name", ""): s for s in profile.get("skills", [])}

        for cat, skill_list in resume_skills.items():
            for s in skill_list:
                name = s.get("name", "")
                if name and name not in profile_skills:
                    issues.append({
                        "location": f"skills.{cat}.{name}",
                        "problem": f"技能「{name}」不在知识库中",
                        "action": "delete",
                    })

                # 检查掌握程度是否夸大
                if name in profile_skills:
                    profile_level = profile_skills[name].get("level", "了解")
                    resume_level = s.get("level", "")
                    if resume_level == "精通" and profile_level != "精通":
                        issues.append({
                            "location": f"skills.{cat}.{name}",
                            "problem": f"技能「{name}」知识库中为「{profile_level}」，不可写为「精通」",
                            "action": "rewrite",
                        })

        return issues

    def _check_experiences(self, resume: Dict, profile: Dict) -> List[Dict]:
        """检查实习/工作经历"""
        issues = []
        resume_exps = resume.get("experiences", [])
        profile_jobs = profile.get("internships_jobs", [])

        for i, exp in enumerate(resume_exps):
            if i >= len(profile_jobs):
                issues.append({
                    "location": f"experiences[{i}]",
                    "problem": "简历中有知识库不存在的工作经历",
                    "action": "delete",
                })
                continue

            pj = profile_jobs[i]
            if exp.get("company") and exp["company"] != pj.get("company"):
                issues.append({
                    "location": f"experiences[{i}].company",
                    "problem": f"公司名称不一致",
                    "action": "rewrite",
                })

            # 检查 bullet 中是否有编造的数字
            for j, bullet in enumerate(exp.get("bullets", [])):
                numbers_in_bullet = self._extract_numbers(bullet)
                known_numbers = self._extract_numbers(
                    str(pj.get("quantified_impact", ""))
                    + str(pj.get("deliverables", ""))
                )
                # 如果 bullet 中有数字但知识库中没有对应的
                for num in numbers_in_bullet:
                    if num not in known_numbers and num > 1:  # 忽略小数字
                        issues.append({
                            "location": f"experiences[{i}].bullets[{j}]",
                            "problem": f"数字「{num}」在知识库中无依据",
                            "action": "rewrite",
                        })

        return issues

    def _check_projects(self, resume: Dict, profile: Dict) -> List[Dict]:
        """检查项目经历"""
        issues = []
        resume_projs = resume.get("projects", [])
        profile_projs = profile.get("projects", [])

        for i, proj in enumerate(resume_projs):
            if i >= len(profile_projs):
                issues.append({
                    "location": f"projects[{i}]",
                    "problem": "简历中有知识库不存在的项目",
                    "action": "delete",
                })

        return issues

    def _check_certificates(self, resume: Dict, profile: Dict) -> List[Dict]:
        """检查证书"""
        issues = []
        resume_certs = resume.get("certificates", [])
        profile_certs = profile.get("certificates_honors", [])
        profile_cert_names = [c.get("name", "") for c in profile_certs]

        for i, cert in enumerate(resume_certs):
            name = cert.get("name", "")
            if name and name not in profile_cert_names:
                issues.append({
                    "location": f"certificates[{i}]",
                    "problem": f"证书「{name}」不在知识库中",
                    "action": "delete",
                })

        return issues

    def _extract_numbers(self, text: str) -> List[int]:
        """从文本中提取数字"""
        import re
        numbers = re.findall(r'\d+', text)
        return [int(n) for n in numbers]

    def _delete_content(self, resume: Dict, location: str) -> None:
        """从简历中删除指定位置的内容"""
        parts = location.split(".")
        # 简化实现：标记为需要删除
        # 实际应用中可以递归定位并删除
        pass

    def _rewrite_content(self, resume: Dict, location: str, profile: Dict) -> None:
        """重写简历中指定位置的内容"""
        # 简化实现：标记为需要改写
        pass
