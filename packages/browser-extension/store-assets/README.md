# Chrome Web Store 商店资源

本目录包含发布到 Chrome Web Store 所需的所有资源文件。

## 📁 目录结构

```
store-assets/
├── icons/              # 扩展图标（已自动生成）
├── screenshots/        # 应用截图（需要手动创建）
├── promotional/        # 宣传图片（需要手动创建）
└── README.md          # 本文件
```

---

## ✅ 已准备的资源

### 1. 扩展图标 (icons/)

已从构建产物中复制，包含所有必需尺寸：

- ✅ `icon16.plasmo.*.png` - 16x16 像素
- ✅ `icon32.plasmo.*.png` - 32x32 像素
- ✅ `icon48.plasmo.*.png` - 48x48 像素
- ✅ `icon64.plasmo.*.png` - 64x64 像素
- ✅ `icon128.plasmo.*.png` - 128x128 像素

**用途**：
- 16x16: 浏览器工具栏图标
- 32x32: Windows 系统图标
- 48x48: 扩展管理页面
- 128x128: Chrome Web Store 列表页

---

## ⚠️ 需要创建的资源

### 2. 应用截图 (screenshots/)

**要求**：
- **数量**：至少 1 张，最多 5 张
- **尺寸**：1280x800 或 640x400 像素
- **格式**：PNG 或 JPEG
- **内容建议**：
  1. `screenshot-1-popup.png` - Popup 界面展示 Schema 检测结果
  2. `screenshot-2-validation.png` - Schema 验证界面，显示错误和警告
  3. `screenshot-3-options.png` - 设置页面
  4. `screenshot-4-detection.png` - 在真实网页上检测 Schema 的效果
  5. `screenshot-5-results.png` - 验证结果详情

**创建方法**：
1. 在 Chrome 中加载未打包的扩展（开发者模式）
2. 访问包含 Schema.org 标记的网页
3. 打开扩展 Popup 并截图
4. 使用截图工具调整到 1280x800 像素

### 3. 宣传图片 (promotional/)

#### 小型宣传图 (Small Promo Tile)
- **文件名**：`promo-small-440x280.png`
- **尺寸**：440x280 像素
- **格式**：PNG 或 JPEG
- **用途**：Chrome Web Store 搜索结果和详情页

#### 大型宣传图 (Large Promo Tile) - 可选
- **文件名**：`promo-large-920x680.png`
- **尺寸**：920x680 像素
- **格式**：PNG 或 JPEG
- **用途**：Chrome Web Store 精选展示

#### 侯爵宣传图 (Marquee Promo Tile) - 可选
- **文件名**：`promo-marquee-1400x560.png`
- **尺寸**：1400x560 像素
- **格式**：PNG 或 JPEG
- **用途**：Chrome Web Store 首页精选

**设计建议**：
- 使用扩展的主色调（蓝色/绿色）
- 包含扩展名称 "Schema Validator Pro"
- 展示核心功能图标或界面预览
- 添加简短的标语，如 "Validate & Generate Schema.org JSON-LD"

**创建工具**：
- Figma（推荐）
- Canva
- Adobe Photoshop
- GIMP（免费）

---

## 📝 资源创建优先级

### 必需（P0）
1. ✅ 扩展图标（已完成）
2. ⚠️ 至少 1 张应用截图
3. ⚠️ 小型宣传图 (440x280)

### 推荐（P1）
4. ⚠️ 3-5 张应用截图（展示不同功能）
5. ⚠️ 大型宣传图 (920x680)

### 可选（P2）
6. ⚠️ 侯爵宣传图 (1400x560)

---

## 🎨 设计指南

### 配色方案
- **主色**：#3B82F6（蓝色）
- **辅色**：#10B981（绿色）
- **背景**：#F9FAFB（浅灰）
- **文字**：#111827（深灰）

### 字体
- **标题**：Inter Bold / SF Pro Display Bold
- **正文**：Inter Regular / SF Pro Text Regular

### 截图建议
1. 使用真实的 Schema.org 数据示例
2. 确保界面清晰可读
3. 避免包含敏感信息
4. 使用高对比度，确保文字清晰

---

## 📋 检查清单

在提交到 Chrome Web Store 之前，请确认：

- [ ] 所有图标文件存在且尺寸正确
- [ ] 至少有 1 张应用截图（1280x800 或 640x400）
- [ ] 小型宣传图已创建（440x280）
- [ ] 所有图片格式为 PNG 或 JPEG
- [ ] 所有图片文件大小 < 2MB
- [ ] 截图中没有敏感信息
- [ ] 图片质量清晰，无模糊

---

## 🔗 相关资源

- [Chrome Web Store 图片要求](https://developer.chrome.com/docs/webstore/images/)
- [Chrome Web Store 发布指南](https://developer.chrome.com/docs/webstore/publish/)
- [Figma 设计模板](https://www.figma.com/community/search?model_type=files&q=chrome%20extension)

---

## 💡 快速创建截图

如果你需要快速创建占位符截图用于测试发布流程：

```bash
# 使用 ImageMagick 创建占位符（需要先安装 ImageMagick）
convert -size 1280x800 xc:white \
  -gravity center \
  -pointsize 48 \
  -annotate +0+0 "Screenshot Placeholder" \
  screenshot-placeholder.png
```

或者使用在线工具：
- [Placeholder.com](https://placeholder.com/)
- [Placehold.co](https://placehold.co/)

---

**注意**：这些资源文件不会包含在扩展包中，仅用于 Chrome Web Store 的商店列表展示。

