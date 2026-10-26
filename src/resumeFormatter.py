"""
简历格式化器 —— 生成一页式 Word 简历文档

依赖: python-docx 库
输出: .docx 文件，严格控制在一页 A4 内
"""

from typing import Dict
from pathlib import Path
import os

try:
    from docx import Document
    from docx.shared import Pt, Inches, Cm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.section import WD_ORIENT
    from docx.oxml.ns import qn
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


class ResumeFormatter:
    """简历 Word 格式化模块"""

    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def format(self, resume_content: Dict, filename: str = "简历.docx") -> str:
        """格式化简历为 Word 文档，返回文件路径"""
        if not HAS_DOCX:
            return self._format_fallback(resume_content, filename)

        doc = Document()

        # 页面设置：A4，窄边距以最大化空间
        section = doc.sections[0]
        section.page_width = Cm(21)
        section.page_height = Cm(29.7)
        section.top_margin = Cm(1.5)
        section.bottom_margin = Cm(1.5)
        section.left_margin = Cm(2)
        section.right_margin = Cm(2)

        # 设置默认字体
        style = doc.styles["Normal"]
        font = style.font
        font.name = "微软雅黑"
        font.size = Pt(10.5)
        # 设置中文字体
        style.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")

        # 按模块顺序写入
        module_order = resume_content.get("module_order", [])

        for module_name in module_order:
            if module_name == "personal_info":
                self._write_personal_info(doc, resume_content)
            elif module_name == "job_intention":
                self._write_job_intention(doc, resume_content)
            elif module_name == "education":
                self._write_education(doc, resume_content)
            elif module_name == "self_evaluation":
                self._write_self_evaluation(doc, resume_content)
            elif module_name == "skills":
                self._write_skills(doc, resume_content)
            elif module_name == "experiences":
                self._write_experiences(doc, resume_content)
            elif module_name == "projects":
                self._write_projects(doc, resume_content)
            elif module_name == "certificates":
                self._write_certificates(doc, resume_content)
            elif module_name == "portfolio":
                self._write_portfolio(doc, resume_content)

        # 保存
        output_path = self.output_dir / filename
        doc.save(str(output_path))

        return str(output_path)

    def _format_fallback(self, resume_content: Dict, filename: str) -> str:
        """无 python-docx 时的降级方案：保存为 Markdown"""
        md_path = self.output_dir / filename.replace(".docx", ".md")
        lines = []

        personal = resume_content.get("personal_info", {})
        lines.append(f"# {personal.get('name', '')}\n")
        lines.append(f"{personal.get('phone', '')} | {personal.get('email', '')} | {personal.get('city', '')}\n")

        # 求职意向
        intention = resume_content.get("job_intention", {})
        if intention:
            lines.append(f"## 求职意向")
            lines.append(f"**意向岗位**：{intention.get('target', '')}  \n")
            lines.append(f"**意向城市**：{intention.get('city', '')}\n")

        # 教育经历
        lines.append("## 教育经历")
        for edu in resume_content.get("education", []):
            lines.append(f"**{edu.get('school', '')}** | {edu.get('major', '')} | {edu.get('degree', '')} | {edu.get('period', '')}")
            if edu.get("gpa"):
                lines.append(f"- GPA: {edu['gpa']}")
            if edu.get("courses"):
                lines.append(f"- 核心课程：{edu['courses']}")
        lines.append("")

        # 自我评价
        eval_text = resume_content.get("self_evaluation", "")
        if eval_text:
            lines.append("## 核心优势")
            lines.append(f"{eval_text}\n")

        # 技能清单
        skills = resume_content.get("skills", {})
        if skills:
            lines.append("## 技能清单")
            for cat, skill_list in skills.items():
                names = [s["name"] for s in skill_list]
                lines.append(f"- **{cat}**：{'、'.join(names)}")
            lines.append("")

        # 实习经历
        experiences = resume_content.get("experiences", [])
        if experiences:
            lines.append("## 实习/工作经历")
            for exp in experiences:
                lines.append(f"**{exp.get('company', '')}** | {exp.get('role', '')} | {exp.get('period', '')}")
                for bullet in exp.get("bullets", []):
                    lines.append(f"- {bullet}")
                lines.append("")
            lines.append("")

        # 项目经历
        projects = resume_content.get("projects", [])
        if projects:
            lines.append("## 项目经历")
            for proj in projects:
                lines.append(f"**{proj.get('name', '')}**")
                for bullet in proj.get("bullets", []):
                    lines.append(f"- {bullet}")
                lines.append("")
            lines.append("")

        # 证书
        certs = resume_content.get("certificates", [])
        if certs:
            lines.append("## 荣誉奖项")
            for c in certs:
                lines.append(f"- {c.get('name', '')} | {c.get('issuer', '')} | {c.get('date', '')}")
            lines.append("")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print("⚠️ 未安装 python-docx，已生成 Markdown 版本。")
        print("💡 安装 python-docx 以获得 Word 格式：pip install python-docx")
        return str(md_path)

    def _write_personal_info(self, doc, resume):
        personal = resume.get("personal_info", {})
        name = personal.get("name", "")

        # 姓名（大号加粗居中）
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(name)
        run.bold = True
        run.font.size = Pt(18)
        run.font.name = "微软雅黑"

        # 联系方式
        contact = f"{personal.get('phone', '')} | {personal.get('email', '')}"
        if personal.get("city"):
            contact += f" | {personal.get('city', '')}"
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(contact)
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(100, 100, 100)

        # 链接
        links = personal.get("links", {})
        link_texts = []
        if links.get("github"):
            link_texts.append(f"github: {links['github']}")
        if links.get("portfolio"):
            link_texts.append(f"作品集: {links['portfolio']}")
        if link_texts:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(" | ".join(link_texts))
            run.font.size = Pt(8)
            run.font.color.rgb = RGBColor(80, 80, 80)

    def _write_job_intention(self, doc, resume):
        intention = resume.get("job_intention", {})
        if not intention.get("target"):
            return

        self._add_section_heading(doc, "求职意向")
        text = f"意向岗位：{intention.get('target', '')}"
        if intention.get("city"):
            text += f"  |  意向城市：{intention['city']}"
        if intention.get("status"):
            text += f"  |  到岗时间：{intention['status']}"
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.font.size = Pt(10.5)

    def _write_education(self, doc, resume):
        self._add_section_heading(doc, "教育经历")
        for edu in resume.get("education", []):
            # 学校信息行
            school_text = f"{edu.get('school', '')} | {edu.get('major', '')} | {edu.get('degree', '')}"
            if edu.get("period"):
                school_text += f" | {edu.get('period', '')}"
            p = doc.add_paragraph()
            run = p.add_run(school_text)
            run.bold = True
            run.font.size = Pt(10.5)

            # 补充信息
            details = []
            if edu.get("gpa"):
                details.append(f"GPA: {edu['gpa']}")
            if edu.get("courses"):
                details.append(f"核心课程：{edu['courses']}")
            for detail in details:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.5)
                run = p.add_run(detail)
                run.font.size = Pt(10)

    def _write_self_evaluation(self, doc, resume):
        text = resume.get("self_evaluation", "")
        if not text:
            return
        self._add_section_heading(doc, "核心优势")
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.font.size = Pt(10)
        p.paragraph_format.space_after = Pt(2)

    def _write_skills(self, doc, resume):
        skills = resume.get("skills", {})
        if not skills:
            return
        self._add_section_heading(doc, "技能清单")

        for cat, skill_list in skills.items():
            # 按熟练度排序展示
            skill_texts = []
            for s in skill_list:
                level = s.get("level", "")
                name = s.get("name", "")
                if level and level != "了解":
                    skill_texts.append(f"{name}（{level}）")
                else:
                    skill_texts.append(name)

            p = doc.add_paragraph()
            run = p.add_run(f"{cat}：")
            run.bold = True
            run.font.size = Pt(10)
            run = p.add_run("、".join(skill_texts))
            run.font.size = Pt(10)

    def _write_experiences(self, doc, resume):
        experiences = resume.get("experiences", [])
        if not experiences:
            return
        self._add_section_heading(doc, "实习/工作经历")

        for exp in experiences:
            # 公司+岗位
            header = f"{exp.get('company', '')}"
            if exp.get("role"):
                header += f" | {exp['role']}"
            if exp.get("period"):
                header += f" | {exp['period']}"
            p = doc.add_paragraph()
            run = p.add_run(header)
            run.bold = True
            run.font.size = Pt(10.5)

            # Bullets
            for bullet in exp.get("bullets", []):
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.5)
                run = p.add_run(f"• {bullet}")
                run.font.size = Pt(10)

    def _write_projects(self, doc, resume):
        projects = resume.get("projects", [])
        if not projects:
            return
        self._add_section_heading(doc, "项目经历")

        for proj in projects:
            header = proj.get("name", "")
            if proj.get("period"):
                header += f" | {proj['period']}"
            p = doc.add_paragraph()
            run = p.add_run(header)
            run.bold = True
            run.font.size = Pt(10.5)

            for bullet in proj.get("bullets", []):
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.5)
                run = p.add_run(f"• {bullet}")
                run.font.size = Pt(10)

    def _write_certificates(self, doc, resume):
        certs = resume.get("certificates", [])
        if not certs:
            return
        self._add_section_heading(doc, "荣誉奖项")

        for c in certs:
            text = f"{c.get('name', '')}"
            if c.get("date"):
                text += f" | {c['date']}"
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.5)
            run = p.add_run(f"• {text}")
            run.font.size = Pt(10)

    def _write_portfolio(self, doc, resume):
        portfolio = resume.get("portfolio", [])
        if not portfolio:
            return
        self._add_section_heading(doc, "作品链接")

        for item in portfolio:
            text = f"{item.get('name', '')}"
            if item.get("link"):
                text += f"：{item['link']}"
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.5)
            run = p.add_run(f"• {text}")
            run.font.size = Pt(10)

    def _add_section_heading(self, doc, text: str):
        """添加模块标题"""
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)

        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(30, 50, 100)

        # 添加底部分隔线
        p_border = p.paragraph_format
