"""
知识库收集器 —— 引导用户逐模块建立职业知识库

职责:
1. 按顺序引导9个模块
2. 执行通过标准检查
3. 强制追问模糊/空洞/无数据的回答
4. 整理用户混杂输入为结构化内容
"""

import json
from typing import Dict, List, Optional, Tuple


class ProfileCollector:
    """知识库收集模块"""

    MODULES = [
        "basic_info",
        "education",
        "core_experiences",
        "internships_jobs",
        "projects",
        "skills",
        "certificates_honors",
        "portfolio",
        "self_reflection",
    ]

    MODULE_NAMES = {
        "basic_info": "基本信息",
        "education": "教育经历",
        "core_experiences": "核心经历",
        "internships_jobs": "实习/工作经历",
        "projects": "项目经历",
        "skills": "技能清单",
        "certificates_honors": "证书/荣誉",
        "portfolio": "作品/案例",
        "self_reflection": "自我认知与职业偏好",
    }

    def __init__(self):
        self.current_module_index = 0
        self.profile: Dict = {}
        self._init_empty_profile()

    def _init_empty_profile(self) -> None:
        """初始化空知识库"""
        self.profile = {
            "basic_info": {},
            "education": [],
            "core_experiences": [],
            "internships_jobs": [],
            "projects": [],
            "skills": [],
            "certificates_honors": [],
            "portfolio": [],
            "self_reflection": {},
            "generated_resumes": [],
            "target_jobs": [],
        }

    def get_current_module(self) -> str:
        """获取当前正在收集的模块名"""
        if self.current_module_index < len(self.MODULES):
            return self.MODULES[self.current_module_index]
        return None

    def get_current_module_name(self) -> str:
        """获取当前模块中文名"""
        module = self.get_current_module()
        return self.MODULE_NAMES.get(module, module) if module else "全部完成"

    def get_prompt(self) -> str:
        """获取当前模块的引导问题"""
        module = self.get_current_module()
        if not module:
            return "所有模块已收集完毕！"

        prompts = {
            "basic_info": self._prompt_basic_info(),
            "education": self._prompt_education(),
            "core_experiences": self._prompt_core_experiences(),
            "internships_jobs": self._prompt_internships_jobs(),
            "projects": self._prompt_projects(),
            "skills": self._prompt_skills(),
            "certificates_honors": self._prompt_certificates(),
            "portfolio": self._prompt_portfolio(),
            "self_reflection": self._prompt_self_reflection(),
        }
        return prompts.get(module, "请提供相关信息：")

    def process_input(self, user_input: str) -> str:
        """处理用户输入，返回反馈信息"""
        module = self.get_current_module()
        if not module:
            return "所有模块已完成！"

        # 检查输入质量
        issues = self._check_input_quality(module, user_input)
        if issues:
            return f"⚠️ 还需要补充一些细节：\n" + "\n".join(f"  • {i}" for i in issues)

        # 解析并存储
        self._store_input(module, user_input)

        # 检查通过标准
        passed, feedback = self._check_pass_criteria(module)
        if not passed:
            return f"还差一点点～ {feedback}"

        # 推进到下一模块
        self.current_module_index += 1
        next_module = self.get_current_module()
        if next_module:
            return f"✅ {self.MODULE_NAMES[module]}已记录！\n\n接下来——{self.get_prompt()}"
        else:
            return "🎉 所有模块收集完毕！可以进行完整性自检了。"

    def _check_input_quality(self, module: str, user_input: str) -> List[str]:
        """检查输入质量，返回需要追问的问题列表"""
        issues = []
        text = user_input.strip()

        # 通用检查
        if len(text) < 10:
            issues.append("信息太简略了，能再多说一点吗？")
            return issues

        # 只有名词没有动作
        action_verbs = ["负责", "做", "写", "搭建", "设计", "开发", "分析", "管理",
                       "优化", "推动", "主导", "协调", "实施", "完成", "实现"]
        has_action = any(v in text for v in action_verbs)
        if module in ["core_experiences", "internships_jobs", "projects"] and not has_action:
            issues.append("你具体做了什么？不只是负责什么，而是你做了哪些具体的事情？")

        # 没有可衡量结果
        data_keywords = ["提升", "增长", "降低", "减少", "增加", "提高",
                        "%", "倍", "人", "个", "万", "千", "条", "次", "天"]
        has_data = any(k in text for k in data_keywords)
        if module in ["core_experiences", "internships_jobs", "projects"] and not has_data:
            issues.append("有没有可以量化的结果？大概的数字或比例也可以～")

        # 自我评价式空话
        empty_words = ["有责任心", "认真负责", "勤奋努力", "积极向上", "团队合作"]
        has_empty = sum(1 for w in empty_words if w in text)
        if has_empty >= 2:
            issues.append("能用具体的事例来说明吗？而不是用形容词～")

        return issues

    def _store_input(self, module: str, user_input: str) -> None:
        """将用户输入存储到知识库中"""
        # 根据模块类型解析存储
        if module == "basic_info":
            self._parse_basic_info(user_input)
        elif module == "education":
            self._parse_education(user_input)
        elif module == "core_experiences":
            self._parse_experience(user_input)
        elif module == "internships_jobs":
            self._parse_internship(user_input)
        elif module == "projects":
            self._parse_project(user_input)
        elif module == "skills":
            self._parse_skills(user_input)
        elif module == "certificates_honors":
            self._parse_certificates(user_input)
        elif module == "portfolio":
            self._parse_portfolio(user_input)
        elif module == "self_reflection":
            self._parse_self_reflection(user_input)

    def _check_pass_criteria(self, module: str) -> Tuple[bool, str]:
        """检查模块是否达到通过标准"""
        if module == "basic_info":
            info = self.profile.get("basic_info", {})
            required = ["name", "phone", "email", "target_direction"]
            missing = [r for r in required if not info.get(r)]
            if missing:
                return False, f"还需要补充：{', '.join(missing)}"
            return True, "基本信息完整 ✅"

        elif module == "education":
            edu_list = self.profile.get("education", [])
            if not edu_list:
                return False, "请至少提供一条教育经历"
            edu = edu_list[-1]
            if not edu.get("school") or not edu.get("major") or not edu.get("period"):
                return False, "学校、专业、时间必须填写完整"
            return True, "教育经历已记录 ✅"

        elif module == "core_experiences":
            exp_list = self.profile.get("core_experiences", [])
            if not exp_list:
                return False, "请至少分享一件最能代表你能力的事"
            exp = exp_list[-1]
            if not exp.get("actions") or not exp.get("results_with_data"):
                return False, "需要包含具体行动和可衡量的结果"
            return True, "核心经历已记录 ✅"

        elif module == "internships_jobs":
            jobs = self.profile.get("internships_jobs", [])
            # 允许为空（没有实习过）
            return True, "实习经历已记录 ✅"

        elif module == "projects":
            projects = self.profile.get("projects", [])
            if not projects:
                return False, "请至少提供一个项目经历（课设/比赛/自学项目都算）"
            proj = projects[-1]
            if not proj.get("my_role"):
                return False, "需要说明你在这个项目中具体负责的部分"
            return True, "项目经历已记录 ✅"

        elif module == "skills":
            skills = self.profile.get("skills", [])
            if not skills:
                return False, "请至少列出3项技能"
            # 检查是否有掌握程度标注
            missing_level = [s["name"] for s in skills if not s.get("level")]
            if missing_level:
                return False, f"以下技能需要标注掌握程度：{', '.join(missing_level)}"
            return True, "技能清单已记录 ✅"

        elif module == "certificates_honors":
            # 允许为空
            return True, "证书信息已记录 ✅"

        elif module == "portfolio":
            # 允许为空
            return True, "作品信息已记录 ✅"

        elif module == "self_reflection":
            reflection = self.profile.get("self_reflection", {})
            strengths = reflection.get("strengths", [])
            weaknesses = reflection.get("weaknesses", [])
            if len(strengths) < 2:
                return False, "请至少描述2条具体的优势"
            if len(weaknesses) < 2:
                return False, "请至少描述2条需要提升的地方"
            return True, "自我认知已记录 ✅"

        return True, "已记录 ✅"

    def get_missing_modules(self) -> List[str]:
        """获取未完成/信息不足的模块列表"""
        missing = []
        # 检查 profile 哪些模块信息不足
        if not self.profile.get("basic_info", {}).get("name"):
            missing.append("基本信息")
        if not self.profile.get("education"):
            missing.append("教育经历")
        if not self.profile.get("core_experiences"):
            missing.append("核心经历")
        if not self.profile.get("skills"):
            missing.append("技能清单")
        if not self.profile.get("projects"):
            missing.append("项目经历")
        return missing

    def is_complete(self) -> bool:
        """判断知识库是否基本完整（所有模块至少有一些内容）"""
        checks = [
            bool(self.profile.get("basic_info", {}).get("name")),
            bool(self.profile.get("education")),
            bool(self.profile.get("core_experiences")),
            bool(self.profile.get("skills")),
            bool(self.profile.get("projects") or self.profile.get("internships_jobs")),
            bool(self.profile.get("self_reflection", {}).get("strengths")),
        ]
        return all(checks)

    # ===== 解析方法 =====

    def _parse_basic_info(self, text: str) -> None:
        self.profile["basic_info"]["raw_input"] = text

    def _parse_education(self, text: str) -> None:
        edu = {"raw_input": text, "school": "", "major": "", "degree": "", "period": ""}
        self.profile.setdefault("education", []).append(edu)

    def _parse_experience(self, text: str) -> None:
        exp = {"title": "", "actions": text, "results_with_data": "", "tags": []}
        self.profile.setdefault("core_experiences", []).append(exp)

    def _parse_internship(self, text: str) -> None:
        job = {"company": "", "role": "", "responsibilities": text, "period": ""}
        self.profile.setdefault("internships_jobs", []).append(job)

    def _parse_project(self, text: str) -> None:
        proj = {"name": "", "my_role": text}
        self.profile.setdefault("projects", []).append(proj)

    def _parse_skills(self, text: str) -> None:
        skill = {"name": text, "category": "", "level": ""}
        self.profile.setdefault("skills", []).append(skill)

    def _parse_certificates(self, text: str) -> None:
        cert = {"name": text, "date": ""}
        self.profile.setdefault("certificates_honors", []).append(cert)

    def _parse_portfolio(self, text: str) -> None:
        item = {"name": text, "type": ""}
        self.profile.setdefault("portfolio", []).append(item)

    def _parse_self_reflection(self, text: str) -> None:
        self.profile["self_reflection"]["raw_input"] = text

    # ===== 引导问题生成 =====

    def _prompt_basic_info(self) -> str:
        return """先从基础信息开始吧～
- 你的姓名、手机号、邮箱？
- 目前是在职/应届/实习中？
- 意向岗位方向是什么？
- 希望在哪个城市工作？
- 📸 **请提供一张简历证件照**（正面、清晰、正式着装优先，支持 jpg/png 格式）

举个栗子🌰：
"我叫张三，手机138xxxx，邮箱zhang@email.com。2025届应届生，意向数据分析，希望在深圳。"
照片直接拖进来或粘贴即可～"""

    def _prompt_education(self) -> str:
        return """聊聊你的教育背景～
- 学校、专业、学历、就读时间？
- 有没有相关的核心课程值得一提？
- 毕设方向是什么？

举个栗子🌰：
"深圳大学，信息管理与信息系统，本科，2021-2025。核心课程：统计学、Python数据分析、数据库原理。毕设方向是用户行为数据分析。" """

    def _prompt_core_experiences(self) -> str:
        return """来说一件你觉得最能代表自己能力的事情——
- 这个事情的背景是什么？
- 你具体做了什么？（不是负责什么，而是你做了哪些事）
- 结果怎么样？有没有大概的数字？

举个栗子🌰：
好的回答：「我负责了学院公众号运营，3个月粉丝从500涨到2800，主要通过策划选题和同学投稿激励机制。」
需要补充的回答：「我负责过公众号运营。」（缺过程、缺结果）"""

    def _prompt_internships_jobs(self) -> str:
        return """有没有实习或工作经历？有的话——
- 公司、岗位、时间？
- 具体负责什么模块？
- 用了什么工具/方法？
- 产出/成果是什么？

没有的话直接说"没有"就好～"""

    def _prompt_projects(self) -> str:
        return """有没有做过一些项目？课设、比赛、自学项目都算～
- 项目名称和目标？
- 你具体负责哪部分？（不是你团队做了什么，而是你个人做了什么）
- 用了什么方法/工具？
- 结果和亮点？"""

    def _prompt_skills(self) -> str:
        return """最后梳理一下技能工具箱🧰 —— 请按类别列出，并诚实标注掌握程度：

类别参考：办公/数据分析/AI工具/编程技术/设计/语言/其他
掌握程度：了解 / 基础 / 熟悉 / 熟练 / 精通

⚠️ 重要：请诚实自评！把不熟的写成精通，面试很容易暴露。

举个栗子🌰：
"Python数据分析：熟悉（实习中独立做过自动化项目）
SQL：基础（会写简单查询，正在学习高级查询）
Excel：熟练（日常大量使用，包括透视表和VLOOKUP）" """

    def _prompt_certificates(self) -> str:
        return """有没有证书或拿过奖？
- 名称、时间、颁发机构？
- 什么级别（校级/省级/国家级）？
没有的话说"没有"就行～"""

    def _prompt_portfolio(self) -> str:
        return """有没有可以展示的作品/链接？
- GitHub、个人网站、设计作品集都可以
- 简单介绍一下背景和你负责的部分
没有的话说"没有"就行～"""

    def _prompt_self_reflection(self) -> str:
        return """最后来个自我认知小问卷 📝：
1. 你最擅长做什么？（至少2条具体描述，别只说形容词哦）
2. 最有成就感的一件事？
3. 短期职业目标？
4. 需要提升的地方？（至少2条具体描述）
5. 短期内愿意学什么来补强自己？"""
