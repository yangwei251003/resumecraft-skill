# 本轮验证

2026-10-26，全部在独立副本执行，仅使用明确虚构资料。

- Node24实际冻结安装，Node排版脚本成功输出DOCX；依赖nanoid固定到官方修补5.1.16后重新安装、生成成功，npm audit0。依据：https://github.com/ai/nanoid/releases/tag/5.1.16 。
- Python3.12实际批量入口成功，输出Word、匹配报告、学习路径与面试准备建议；--output已实测写入指定目录。该路径是规则原型，没有请求模型或联网岗位服务。
- 两个Word都是可读取ZIP包，包含word/document.xml，XML/关系项没有机器个人路径，虚构联系邮箱为example.com；Node输出的公开示例保存在examples/demo-resume.docx。
- Python源码AST解析通过。没有声称在Word/WPS里核实了物理页数、字体一致性，也没有完成新的宿主模型对话验收。

原型仍包含待完善的可追溯修复检查；生成成功不证明职业匹配建议准确或材料符合某个真实岗位。原指南的设计目标以当前README和本记录解释。
