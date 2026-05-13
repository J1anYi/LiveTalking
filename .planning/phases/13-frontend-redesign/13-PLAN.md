# Phase 13: Frontend Redesign - Context & Plan

**Requirements:** UI-05, UI-06, UI-07, UI-08, UI-09

## Design System (from UI/UX Pro Max)

### Color Palette
| Role | Hex | Usage |
|------|-----|-------|
| Background | `#F5F0EB` | 页面主背景（暖白） |
| Card/Surface | `#FFFFFF` | 视频卡片、对话框卡片 |
| Primary | `#8B8CF8` | 品牌色、按钮、链接（柔和紫） |
| On Primary | `#FFFFFF` | 品牌色上的文字 |
| User Bubble | `#8B8CF8` + 15% opacity | 用户消息气泡 |
| Assistant Bubble | `#F0EEF5` | 数字人消息气泡 |
| Text Primary | `#2D3436` | 正文文字 |
| Text Secondary | `#636E72` | 辅助文字 |
| Border | `#E8E4E0` | 卡片边框 |

### Typography
- System font stack (`-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif`)
- 保持现有字体即可，无需额外加载

### Layout
- 顶部导航栏：连接状态 + RAG 模式切换 + 设置
- 主内容：视频卡片（左）+ 对话卡片（右），6:6 分栏
- 统一圆角 16px，卡片阴影 `0 2px 12px rgba(0,0,0,0.06)`

## Plan

### Task 1: Color System Rewrite
- Replace all `--primary-color: #4361ee` with `#8B8CF8`
- Update background, card, border, shadow variables
- Ensure WCAG 4.5:1 contrast on all text

### Task 2: Layout Restructure
- Top bar: connection status + RAG mode toggle + settings
- Video card: uniform container matching chat card style
- Chat card: doubled height, 6/12 column width
- Remove side panel (move RAG toggle to top bar)

### Task 3: Bubble Redesign
- User: right-aligned, soft purple bg `#8B8CF8`, white text
- Assistant: left-aligned, warm gray bg `#F0EEF5`, dark text
- Larger padding (12px 16px), rounded 16px
- Spacing between bubbles: 12px

### Task 4: Responsive
- Desktop: side-by-side 6:6
- Tablet < 768px: stacked (video above chat)
