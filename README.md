# ResumeCraft · 简历工作流与Word排版

先整理有证据的职业材料，再匹配岗位要求、明确能力缺口，最后将核实后的内容输出为Word。仓库包含Agent工作流、提示模板、Python规则原型，以及独立可用的Node.js排版脚本。

![设计流程示意，不是Word截图](docs/workflow.svg)

## 最简运行：生成虚构示例Word

安装Node.js22+，在项目根目录运行：

```sh
npm ci --prefix scripts --ignore-scripts
node scripts/build_resume.js examples/render-content.json example-resume.docx
```

使用Word、WPS或兼容软件打开 `example-resume.docx`。输入结构见 `assets/resume_content_schema.json`，也可用 `--photo <本地照片>` 或 `--compact`。排版以A4一页为目标，实际页数受内容和字体环境影响，需要在文档软件复核；不保证任何长度都只有一页。

真实求职材料、照片、联系方式和输出存放在独立私有目录，不加入仓库。所有示例人物和经历均为虚构，不属于作者的履历。

[下载虚构示例Word](examples/demo-resume.docx)

## 作为Skill使用

把整个包放入支持 `SKILL.md` 的宿主用户技能目录，保持参考和脚本相对位置，按宿主方式调用 `resumecraft`。如已有同名技能，先区分版本与安装位置。完整四阶段对话依赖宿主模型、文档工具和经授权的岗位资料；安装不代表模型或检索服务已经提供。

## Python原型

`src/` 提供状态流转、规则解析、匹配和文档输出原型。Python3.12的实际批量运行通过，可按requirements安装后运行：

```sh
python -m pip install -r requirements.txt
python src/index.py --mode batch --profile examples/sample_profile.json --jd examples/sample_job_description.md --output output
```

它不等同于模型驱动的深度岗位判断；可追溯检查里仍有待实现的检查项。原设计记录见 [原指南](docs/original-guide.md)，实际运行范围与限制见 [本轮验证](docs/VERIFICATION.md)。

## 文件与协议

| 目录 | 用途 |
|---|---|
| `SKILL.md`、`references/`、`prompts/` | 工作流、方法和提示模板 |
| `templates/`、`assets/` | 结构化材料与排版Schema |
| `scripts/` | docx-js排版脚本、依赖锁定 |
| `src/` | Python规则原型 |
| `examples/` | 虚构的输入和输出示例 |

保留完整自有源码与模板，排除依赖缓存、实际个人知识库和真实输出。自有代码与文档使用 [MIT](LICENSE)，docx等依赖遵循各自原许可。

## 更新与计划

2026-10-26：公开归档、补充最简排版入口和虚构示例；Python命令的 `--output` 现在传递到格式化器。后续应补充真实文档渲染页数验收、未实现的可追溯检查和宿主会话测试，不把规则结果包装成已核实的职业建议。
