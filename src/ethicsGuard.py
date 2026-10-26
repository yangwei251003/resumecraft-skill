"""
伦理守护者 —— 防止生成虚假信息，确保简历内容真实可信

红线清单:
- 不虚构学历、证书、公司、职位、获奖
- 不编造不可验证的项目成果或数据
- 不把用户不会的技能写成精通
- 不鼓励求职欺诈
"""

from typing import Dict, List


class EthicsGuard:
    """伦理底线守护模块"""

    def check(self, profile: Dict, matching_result: Dict) -> List[str]:
        """在简历生成前检查潜在违规，返回问题列表"""
        issues = []

        # 检查是否有明显的缺失（可能被编造的风险）
        if not profile.get("education"):
            issues.append("⚠️ 知识库缺少教育经历 —— 简历中不得编造学历信息")

        if not profile.get("internships_jobs") and not profile.get("projects"):
            issues.append("⚠️ 知识库缺少实习/项目经历 —— 简历中不得编造工作经历")

        if not profile.get("skills"):
            issues.append("⚠️ 知识库缺少技能清单 —— 简历中不得编造不掌握的技能")

        # 检查技能掌握程度
        for skill in profile.get("skills", []):
            if skill.get("level") == "精通" and not skill.get("evidence"):
                issues.append(
                    f"⚠️ 技能「{skill.get('name', '')}」标注为精通但缺少证据 —— 建议降级或补充证据"
                )

        return issues

    def validate_resume(self, resume_content: Dict, profile: Dict) -> List[Dict]:
        """验证已生成的简历内容（更严格的检查）"""
        violations = []

        # 1. 学历检查
        resume_edu = resume_content.get("education", [])
        profile_edu = profile.get("education", [])
        if len(resume_edu) > len(profile_edu):
            violations.append({
                "type": "虚假学历",
                "detail": "简历中学历条目多于知识库，可能存在编造",
                "severity": "CRITICAL",
            })

        # 2. 公司检查
        resume_companies = [e.get("company") for e in resume_content.get("experiences", [])]
        profile_companies = [j.get("company") for j in profile.get("internships_jobs", [])]
        for company in resume_companies:
            if company and company not in profile_companies:
                violations.append({
                    "type": "虚假工作单位",
                    "detail": f"「{company}」不在知识库中",
                    "severity": "CRITICAL",
                })

        # 3. 技能夸大检查
        resume_skills = resume_content.get("skills", {})
        profile_skills = {s.get("name", ""): s for s in profile.get("skills", [])}

        for cat, skill_list in resume_skills.items():
            for s in skill_list:
                name = s.get("name", "")
                if name in profile_skills:
                    profile_level = profile_skills[name].get("level", "了解")
                    resume_level = s.get("level", "")
                    if resume_level == "精通" and profile_level != "精通":
                        violations.append({
                            "type": "技能夸大",
                            "detail": f"技能「{name}」知识库为「{profile_level}」，简历中写成「精通」",
                            "severity": "HIGH",
                        })

        # 4. 证书检查
        resume_certs = [c.get("name") for c in resume_content.get("certificates", [])]
        profile_certs = [c.get("name") for c in profile.get("certificates_honors", [])]
        for cert in resume_certs:
            if cert and cert not in profile_certs:
                violations.append({
                    "type": "虚假证书",
                    "detail": f"证书「{cert}」不在知识库中",
                    "severity": "CRITICAL",
                })

        return violations

    def is_allowed_operation(self, operation: str) -> bool:
        """检查某个操作是否在允许范围内（绿灯清单）"""
        allowed = [
            "专业化表达",
            "结果导向改写",
            "关联性强化",
            "诚实分级表达",
            "可迁移能力挖掘",
            "亮点提取放大",
        ]
        return operation in allowed

    def get_refusal_message(self, violation_type: str) -> str:
        """获取违规操作的拒绝话术"""
        messages = {
            "编造经历": (
                "我理解你希望简历更有竞争力，但编造经历可能在背调或面试中暴露，"
                "反而得不偿失。不如我们看看你现有的经历里，有哪些可以通过换个表达角度来凸显你的能力？"
            ),
            "夸大技能": (
                "把尚未掌握的技能写成精通，面试时被追问到很容易露馅。"
                "我建议写成「正在系统学习」或者标注真实水平。"
                "我可以帮你在学习提升路径里给出最快的补强方法。"
            ),
            "美化职位": (
                "美化职位名称可能在背调中出现问题。"
                "我们可以通过描述你实际负责的工作内容和成果来体现你的能力，"
                "这比一个漂亮的头衔更有说服力。"
            ),
            "虚假学历": (
                "学历信息非常容易被背调查证，绝对不能编造。"
                "如果学历是短板，我们可以通过强调实践经验和项目成果来弥补。"
            ),
        }
        return messages.get(violation_type, "这个操作不符合诚信求职原则，我不能协助。")

    def green_light_examples(self) -> Dict[str, str]:
        """返回绿灯操作示例（帮助理解允许范围）"""
        return {
            "专业化表达": {
                "before": "做报表",
                "after": "负责数据报表的自动化生成与日常维护",
            },
            "结果导向改写": {
                "before": "整理数据",
                "after": "完成数据清洗与结构化整理，支撑团队决策分析",
            },
            "关联性强化": {
                "before": "管理过社团公众号",
                "after": "独立运营校园媒体账号，策划选题并产出内容，培养用户分析与内容策划能力",
            },
            "诚实分级表达": {
                "before": "（不在简历中写SQL）",
                "after": "了解基础 SQL，正在系统学习高级查询与性能优化",
            },
            "可迁移能力挖掘": {
                "before": "担任班级学习委员",
                "after": "统筹班级学习资源分配与信息传达，协调30+人学习进度管理",
            },
        }
