#!/usr/bin/env node
/**
 * build_resume.js
 * ResumeCraft Word 简历生成器
 *
 * 用 docx-js 将 resume_content.json 渲染为专业排版 .docx
 * 支持证件照嵌入、URL 自动识别、一页约束、紧凑降级模式
 *
 * 用法: node build_resume.js <content.json> [--photo <path>] [--compact]
 * 输入: resume_content.json (参考 assets/resume_content_schema.json)
 * 输出: 排版专业的一页 A4 Word 简历
 *
 * 设计理念：
 *   - AI 负责内容判断（删什么、留什么）
 *   - 脚本负责排版渲染（字体、间距、对齐、链接）
 *   - 一页是硬约束，--compact 是最后手段
 */

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel,
  AlignmentType, TabStopPosition, TabStopType,
  BorderStyle, LevelFormat, ExternalHyperlink, ImageRun,
  PageBreak
} = require("docx");

// ===== 常量 =====
// 字号系统（半磅 = half-points，1pt = 2 half-points）
const SIZE = {
  name: 36,           // 18pt
  nameCompact: 30,    // 15pt
  contact: 18,        // 9pt
  contactCompact: 16, // 8pt
  sectionTitle: 23,   // 11.5pt
  sectionTitleCompact: 20, // 10pt
  body: 21,           // 10.5pt
  bodyCompact: 18,    // 9pt
  subheading: 19,     // 9.5pt (比正文小1pt)
};

const FONT = "Microsoft YaHei";
const ACCENT_COLOR = "1F3864";   // 深蓝，专业低调
const GRAY_DARK   = "444444";    // 联系方式
const GRAY_MEDIUM  = "555555";    // 日期、副标题

// A4: 11906 x 16838 DXA (1 DXA = 1/20 pt = 1/1440 inch)
const PAGE = { width: 11906, height: 16838 };
const MARGIN = 720; // 0.5 inch = 720 DXA

// 间距表（DXA单位）
const SPACING = {
  afterName:         { normal: 70,  compact: 40 },
  afterContact:      { normal: 140, compact: 100 },
  beforeSection:     { normal: 190, compact: 140 },
  afterSectionTitle: { normal: 80,  compact: 60 },
  afterEntryHeading: { normal: 40,  compact: 20 },
  afterSubheading:   { normal: 30,  compact: 15 },
  afterBullet:       { normal: 50,  compact: 20 },
  afterEntry:        { normal: 110, compact: 60 },
};

// ===== 工具函数 =====

/** 防御性文本清洗：消除意外 tab/换行 */
function clean(text) {
  if (text === null || text === undefined) return "";
  return String(text)
    .replace(/[\t\r\n]+/g, " ")
    .replace(/ {2,}/g, " ")
    .trim();
}

/** URL自动识别正则（防邮箱误判、防分数误判） */
const URL_PATTERN = new RegExp(
  "(?<!@)\\b(?:" +
    "https?:\\/\\/[a-zA-Z0-9-]+(?:\\.[a-zA-Z0-9-]+)+(?:\\/[^\\s\\uFF0C\\uFF0C\\uFF1B\\uFF1B\\uFF08\\uFF09\\u300A\\u300B\\u201C\\u201D]*)" +
    "|" +
    "(?:www\\.)?(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\\.)+" +
    "(?:com|cn|net|org|io|me|co|cc|top|xyz|dev|app|so|ai|gg|sh|ly)" +
    "(?:\\/[^\\s\\uFF0C\\uFF1B\\uFF08\\uFF09\\u300A\\u300B\\u201C\\u201D]*)" +
  ")", "gi"
);

/** 将文本中的URL转为可点击超链接 */
function linkify(text, baseRunOpts = {}) {
  const parts = [];
  let lastIndex = 0;
  const str = clean(text);
  let match;

  while ((match = URL_PATTERN.exec(str)) !== null) {
    // 匹配前的普通文本
    if (match.index > lastIndex) {
      parts.push(new TextRun({
        ...baseRunOpts,
        text: str.slice(lastIndex, match.index),
      }));
    }
    // URL 部分
    let url = match[0];
    // 去掉末尾可能误抓的标点
    url = url.replace(/[.,;:!?，。；：！？、…]+$/, "");
    const href = url.startsWith("http") ? url : "https://" + url;
    parts.push(new ExternalHyperlink({
      children: [new TextRun({
        ...baseRunOpts,
        text: url,
        style: "Hyperlink",
        color: baseRunOpts.color || ACCENT_COLOR,
        underline: { color: baseRunOpts.color || ACCENT_COLOR },
      })],
      link: href,
    }));
    lastIndex = match.index + match[0].length;
  }

  // 剩余文本
  if (lastIndex < str.length) {
    parts.push(new TextRun({ ...baseRunOpts, text: str.slice(lastIndex) }));
  }

  return parts.length > 0 ? parts : [new TextRun({ ...baseRunOpts, text: str })];
}

// ===== 排版函数 =====

/** 页头：姓名 + 联系方式 + 照片（可选） */
function buildHeader(name, contactLine, photoBuffer, isCompact) {
  const s = size(isCompact);
  const paragraphs = [];

  // 姓名行（居中、深蓝、加粗）
  const nameRun = new TextRun({
    text: clean(name), bold: true, size: s.name, font: FONT, color: ACCENT_COLOR,
  });
  paragraphs.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: SPACING.afterName[isCompact ? "compact" : "normal"] },
    children: [nameRun],
  }));

  // 联系方式行（居中、灰色）
  const contactRun = new TextRun({
    text: clean(contactLine), size: s.contact, font: FONT, color: GRAY_DARK,
  });
  paragraphs.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: SPACING.afterContact[isCompact ? "compact" : "normal"] },
    border: {
      bottom: { style: BorderStyle.SINGLE, size: 6, color: ACCENT_COLOR, space: 4 },
    },
    children: [contactRun],
  }));

  return paragraphs;
}

/** 节标题：深蓝粗体 + 底部细线 */
function sectionTitle(title, isCompact) {
  return new Paragraph({
    spacing: {
      before: SPACING.beforeSection[isCompact ? "compact" : "normal"],
      after: SPACING.afterSectionTitle[isCompact ? "compact" : "normal"],
    },
    border: {
      bottom: { style: BorderStyle.SINGLE, size: 4, color: ACCENT_COLOR, space: 2 },
    },
    children: [
      new TextRun({
        text: clean(title), bold: true,
        size: size(isCompact).sectionTitle, font: FONT, color: ACCENT_COLOR,
      }),
    ],
  });
}

/** 条目：标题行(左对齐) + 日期(右对齐Tab) + 可选副标题 + Bullets */
function buildEntry(entry, isCompact, isLastEntry) {
  const s = size(isCompact);
  const paragraphs = [];

  // === 标题行 ===
  const headingChildren = [];
  if (entry.heading) {
    headingChildren.push(new TextRun({
      text: clean(entry.heading), bold: true, size: s.body, font: FONT,
    }));
  }
  // 日期通过右对齐Tab定位到页面最右
  if (entry.date) {
    headingChildren.push(new TextRun({
      text: "\t" + clean(entry.date),
      size: s.body, font: FONT, color: GRAY_MEDIUM,
    }));
  }

  const hasSub = entry.subheading && entry.subheading.trim();
  const hasBullets = entry.bullets && entry.bullets.length > 0;
  const headingSpacing = (hasSub || hasBullets)
    ? SPACING.afterEntryHeading[isCompact ? "compact" : "normal"]
    : (isLastEntry ? 0 : SPACING.afterEntry[isCompact ? "compact" : "normal"]);

  paragraphs.push(new Paragraph({
    tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
    spacing: { after: headingSpacing },
    children: headingChildren,
  }));

  // === 副标题行（可选、斜体、灰色） ===
  if (hasSub) {
    const subSpacing = hasBullets
      ? SPACING.afterSubheading[isCompact ? "compact" : "normal"]
      : (isLastEntry ? 0 : SPACING.afterEntry[isCompact ? "compact" : "normal"]);

    paragraphs.push(new Paragraph({
      spacing: { after: subSpacing },
      children: linkify(entry.subheading, {
        size: s.subheading, font: FONT, italics: true, color: GRAY_MEDIUM,
      }),
    }));
  }

  // === Bullet列表 ===
  if (hasBullets) {
    entry.bullets.forEach((bullet, bi) => {
      const isLastBullet = bi === entry.bullets.length - 1;
      const bulletSpacing = isLastBullet
        ? (isLastEntry ? 0 : SPACING.afterEntry[isCompact ? "compact" : "normal"])
        : SPACING.afterBullet[isCompact ? "compact" : "normal"];

      paragraphs.push(new Paragraph({
        numbering: { reference: "resume-bullets", level: 0 },
        spacing: { after: bulletSpacing },
        children: linkify(bullet, { size: s.body, font: FONT }),
      }));
    });
  }

  return paragraphs;
}

/** 整个简历区块 */
function buildSection(section, isCompact, isLastSection) {
  const paragraphs = [];
  paragraphs.push(sectionTitle(section.title, isCompact));

  if (section.entries && section.entries.length > 0) {
    section.entries.forEach((entry, ei) => {
      const isLastEntry = ei === section.entries.length - 1;
      paragraphs.push(...buildEntry(entry, isCompact, isLastEntry));
    });
  }

  if (section.freeform_bullets && section.freeform_bullets.length > 0) {
    section.freeform_bullets.forEach((text) => {
      paragraphs.push(new Paragraph({
        numbering: { reference: "resume-bullets", level: 0 },
        spacing: { after: SPACING.afterBullet[isCompact ? "compact" : "normal"] },
        children: linkify(text, { size: size(isCompact).body, font: FONT }),
      }));
    });
  }

  return paragraphs;
}

// ===== 辅助 =====
function size(isCompact) {
  return {
    name:          isCompact ? SIZE.nameCompact          : SIZE.name,
    contact:       isCompact ? SIZE.contactCompact       : SIZE.contact,
    sectionTitle:  isCompact ? SIZE.sectionTitleCompact  : SIZE.sectionTitle,
    body:          isCompact ? SIZE.bodyCompact          : SIZE.body,
    subheading:    isCompact ? SIZE.subheading           : SIZE.subheading,
  };
}

// ===== 主流程 =====

function main() {
  const args = process.argv.slice(2);
  const inputPath = args[0];
  let outputPath;
  let photoPath = null;
  let isCompact = false;

  // 解析参数
  for (let i = 1; i < args.length; i++) {
    if (args[i] === "--photo" && args[i + 1]) {
      photoPath = args[i + 1];
      i++;
    } else if (args[i] === "--compact") {
      isCompact = true;
    } else if (!args[i].startsWith("--")) {
      outputPath = args[i];
    }
  }

  if (!inputPath) {
    console.error("用法: node build_resume.js <content.json> [output.docx] [--photo <path>] [--compact]");
    console.error("  --photo <path>  嵌入证件照（支持 jpg/png）");
    console.error("  --compact       紧凑降级模式（字号缩小15%，仅内容过多时使用）");
    process.exit(1);
  }

  // 读取输入
  if (!fs.existsSync(inputPath)) {
    console.error(`输入文件不存在: ${inputPath}`);
    process.exit(1);
  }

  let content;
  try {
    content = JSON.parse(fs.readFileSync(inputPath, "utf-8"));
  } catch (e) {
    console.error(`JSON 解析失败: ${e.message}`);
    process.exit(1);
  }

  // 验证必填字段
  const errors = [];
  if (!content.name) errors.push("缺少 name 字段");
  if (!content.contact_line) errors.push("缺少 contact_line 字段");
  if (!content.sections || !Array.isArray(content.sections) || content.sections.length === 0) {
    errors.push("缺少 sections 字段（必须为非空数组）");
  }
  (content.sections || []).forEach((s, i) => {
    if (!s.title) errors.push(`section[${i}] 缺少 title`);
    if (!s.entries && !s.freeform_bullets) {
      errors.push(`section[${i}] 必须包含 entries 或 freeform_bullets`);
    }
  });

  if (errors.length > 0) {
    console.error("输入验证失败:");
    errors.forEach(e => console.error("  - " + e));
    process.exit(1);
  }

  // 读取照片（可选）
  let photoBuffer = null;
  if (photoPath && fs.existsSync(photoPath)) {
    photoBuffer = fs.readFileSync(photoPath);
    console.log("📸 照片已加载:", path.basename(photoPath));
  }

  // 构建文档
  const bodyChildren = [];

  // === 页头 ===
  const headerParas = buildHeader(content.name, content.contact_line, photoBuffer, isCompact);
  bodyChildren.push(...headerParas);

  // === 照片（放在header段落之后） ===
  if (photoBuffer) {
    // 照片放在页头后、第一个section前
    bodyChildren.push(new Paragraph({
      alignment: AlignmentType.RIGHT,
      spacing: { after: 100 },
      children: [
        new ImageRun({
          data: photoBuffer,
          transformation: { width: 105, height: 135 },
          floating: {
            horizontalPosition: { relative: "rightMargin", align: "right" },
            verticalPosition: { relative: "page", offset: 720 }, // below header
          },
        }),
      ],
    }));
  }

  // === 各区块 ===
  content.sections.forEach((section, si) => {
    const isLastSection = si === content.sections.length - 1;
    bodyChildren.push(...buildSection(section, isCompact, isLastSection));
  });

  // === 生成文档 ===
  const doc = new Document({
    numbering: {
      config: [{
        reference: "resume-bullets",
        levels: [{
          level: 0,
          format: LevelFormat.BULLET,
          text: "\u2022",
          alignment: AlignmentType.LEFT,
          style: {
            paragraph: { indent: { left: 260, hanging: 260 } },
          },
        }],
      }],
    },
    styles: {
      default: {
        document: {
          run: { font: FONT, size: SIZE.body },
        },
      },
    },
    sections: [{
      properties: {
        page: {
          size: { width: PAGE.width, height: PAGE.height },
          margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN },
        },
      },
      children: bodyChildren,
    }],
  });

  // 输出
  if (!outputPath) {
    const baseName = path.basename(inputPath, path.extname(inputPath));
    outputPath = baseName + "_resume.docx";
  }

  Packer.toBuffer(doc).then((buffer) => {
    fs.writeFileSync(outputPath, buffer);
    console.log(`✅ 简历已生成: ${outputPath}`);
    if (isCompact) {
      console.log("⚠️ 已启用紧凑模式（字号缩小）。请转PDF检查实际页数。");
    } else {
      console.log("📄 请转PDF检查实际页数。如超过一页，可尝试 --compact 或精简内容。");
    }
    if (photoBuffer) {
      console.log("📸 证件照已嵌入简历");
    }
  }).catch((err) => {
    console.error("生成失败:", err.message);
    process.exit(1);
  });
}

main();
