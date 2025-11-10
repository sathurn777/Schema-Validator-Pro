# 截图占位符说明

## 📸 需要创建的截图

请在此目录中放置以下截图文件：

### 1. screenshot-1-popup.png (必需)
**尺寸**: 1280x800 像素  
**内容**: Popup 界面展示 Schema 检测结果  
**说明**: 
- 打开扩展 Popup
- 显示检测到的 Schema 类型列表
- 展示验证状态（成功/警告/错误）

### 2. screenshot-2-validation.png (推荐)
**尺寸**: 1280x800 像素  
**内容**: Schema 验证详情界面  
**说明**:
- 显示 JSON-LD 代码
- 展示验证错误和警告
- 突出显示问题所在行

### 3. screenshot-3-options.png (推荐)
**尺寸**: 1280x800 像素  
**内容**: 设置页面  
**说明**:
- 显示扩展设置选项
- 展示自动检测开关
- 显示支持的 Schema 类型列表

### 4. screenshot-4-detection.png (可选)
**尺寸**: 1280x800 像素  
**内容**: 在真实网页上的检测效果  
**说明**:
- 在包含 Schema.org 标记的网页上
- 显示扩展图标的徽章（显示检测到的 Schema 数量）
- 展示实际使用场景

### 5. screenshot-5-results.png (可选)
**尺寸**: 1280x800 像素  
**内容**: 验证结果详情  
**说明**:
- 显示完整的验证报告
- 展示所有字段的验证状态
- 突出显示必需字段和推荐字段

---

## 🎯 创建步骤

### 方法 1: 手动截图（推荐）

1. **加载扩展**
   ```bash
   # 在 Chrome 中打开扩展管理页面
   chrome://extensions/
   
   # 启用"开发者模式"
   # 点击"加载已解压的扩展程序"
   # 选择 build/chrome-mv3-prod/ 目录
   ```

2. **访问测试页面**
   - 访问包含 Schema.org 标记的网页
   - 例如：https://schema.org/Article

3. **打开扩展并截图**
   - 点击扩展图标打开 Popup
   - 使用截图工具（macOS: Cmd+Shift+4, Windows: Win+Shift+S）
   - 截取整个浏览器窗口

4. **调整尺寸**
   - 使用图片编辑工具调整到 1280x800 像素
   - 确保内容清晰可读

### 方法 2: 使用占位符（快速测试）

如果你只是想测试发布流程，可以使用占位符：

```bash
# 使用 ImageMagick 创建占位符
convert -size 1280x800 xc:white \
  -gravity center \
  -pointsize 48 \
  -fill black \
  -annotate +0-100 "Schema Validator Pro" \
  -pointsize 32 \
  -annotate +0+0 "Popup Interface" \
  -pointsize 24 \
  -annotate +0+100 "Screenshot Placeholder" \
  screenshot-1-popup.png
```

或访问在线工具：
- https://placehold.co/1280x800/png?text=Schema+Validator+Pro+Popup

---

## ✅ 检查清单

创建截图后，请确认：

- [ ] 所有截图尺寸为 1280x800 像素
- [ ] 文件格式为 PNG 或 JPEG
- [ ] 文件大小 < 2MB
- [ ] 图片清晰，无模糊
- [ ] 没有包含敏感信息（个人数据、API 密钥等）
- [ ] 界面元素清晰可读
- [ ] 展示了扩展的核心功能

---

## 📝 文件命名规范

请使用以下命名格式：

```
screenshot-1-popup.png          # Popup 界面
screenshot-2-validation.png     # 验证界面
screenshot-3-options.png        # 设置页面
screenshot-4-detection.png      # 检测效果
screenshot-5-results.png        # 结果详情
```

---

**注意**: 至少需要 1 张截图才能发布到 Chrome Web Store。建议提供 3-5 张截图以更好地展示扩展功能。

