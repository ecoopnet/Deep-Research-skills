---
user-invocable: true
description: 既存のリサーチアウトラインに項目（調査対象）を追加します。
allowed-tools: Bash, Read, Write, Glob, WebSearch, Task, AskUserQuestion
---

# Research Add Items - 調査対象を補完

## トリガー
`/research-add-items`

## ワークフロー

### ステップ1: アウトラインを自動検索
現在の作業ディレクトリで`*/outline.yaml`ファイルを見つけ、自動的に読み込む。

### ステップ2: 補完ソースを並列で取得
同時に実行：
- **A. ユーザーに確認**: どの項目を補完しますか？具体的な名前はありますか？
- **B. Web検索の要否確認**: エージェントを起動してさらに項目を検索しますか？

### ステップ3: マージと更新
- 新しい項目をoutline.yamlに追加
- ユーザーに確認のため表示
- 重複を避ける
- 更新されたアウトラインを保存

## 出力
更新された`{topic}/outline.yaml`ファイル（インプレース変更）
