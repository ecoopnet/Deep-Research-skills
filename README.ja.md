# Deep Research Skill for Claude Code / OpenCode

[English](README.md) | [中文](README.zh.md) | [日本語](README.ja.md)

> このプロジェクトが役に立ったら、スターをお願いします！ :star:

> [RhinoInsight: Improving Deep Research through Control Mechanisms for Model Behavior and Context](https://arxiv.org/abs/2511.18743) にインスパイアされました

Claude Code向けの構造化リサーチワークフロースキルです。アウトライン生成（拡張可能）と深堀り調査の2フェーズをサポート。Human-in-the-loop設計により、各段階で正確なコントロールが可能です。

![Deep Research Skills Workflow](workflow.png)

## ユースケース

- **学術研究**: 論文サーベイ、ベンチマークレビュー、文献分析
- **技術調査**: 技術比較、フレームワーク評価、ツール選定
- **市場調査**: 競合分析、業界トレンド、製品比較
- **デューデリジェンス**: 企業調査、投資分析、リスク評価

## インストール

### Claude Code
```bash
# 日本語版
cp -r skills/research-ja/* ~/.claude/skills/

# 必須: エージェントのインストール
cp agents/web-search-agent.md ~/.claude/agents/

# 必須: Python依存パッケージのインストール
pip install pyyaml
```

### OpenCode (デフォルト: gpt-5.2)
```bash
# スキル (Claude Codeと同様)
cp -r skills/research-ja/* ~/.claude/skills/

# 必須: エージェントのインストール
cp agents/web-search-opencode.md ~/.config/opencode/agent/web-search.md

# 必須: Python依存パッケージのインストール
pip install pyyaml
```

## コマンド

> **Claude Code 2.1.0+**: `/skill-name` で直接実行できるようになりました！
>
> **旧バージョン**: `run /skill-name` 形式を使用してください。

| コマンド (2.1.0+) | 説明 |
|------------------|------|
| `/research` | リサーチアウトラインを生成（項目とフィールドを含む） |
| `/research-add-items` | 既存アウトラインにリサーチ項目を追加 |
| `/research-add-fields` | 既存アウトラインにフィールド定義を追加 |
| `/research-deep` | 並列エージェントで各項目を深堀り調査 |
| `/research-report` | JSON結果からMarkdownレポートを生成 |

## ワークフローと例

> **例**: 「AI Agent Demo 2025」を調査する場合

### フェーズ1: アウトラインを生成
```
/research AI Agent Demo 2025
```
💡 **何が起きるか**: トピックを伝えると → リサーチリストを作成してくれます

**得られるもの**: 調査すべき17個のAIエージェントのリスト（ChatGPT Agent, Claude Computer Use, Cursorなど）+ 各項目で収集する情報

### （オプション）満足できない場合は追加
```
/research-add-items
/research-add-fields
```
💡 **何が起きるか**: リサーチ項目やフィールド定義を追加できます

### フェーズ2: 深堀り調査
```
/research-deep
```
💡 **何が起きるか**: AIが各項目について自動的にWeb検索を実行します

**得られるもの**: 各エージェントの詳細情報（企業、リリース日、価格、技術仕様、レビューなど）

### フェーズ3: レポート生成
```
/research-report
```
💡 **何が起きるか**: すべてのデータ → 整理されたレポートに変換

**得られるもの**: `report.md` - 目次付きの完全なMarkdownレポート、そのまま読んだり共有したりできます

## ヘルプが必要ですか？

質問がある場合は、Claude Codeにこのプロジェクトについて説明を求めてください：
```
このプロジェクトについて説明して: https://github.com/Weizhena/deep-research-skills
```

## 参考文献

- RhinoInsight: Improving Deep Research through Control Mechanisms for Model Behavior and Context

## ライセンス

MIT
