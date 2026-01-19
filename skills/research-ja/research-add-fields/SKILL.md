---
user-invocable: true
description: 既存のリサーチアウトラインにフィールド定義を追加します。
allowed-tools: Bash, Read, Write, Glob, WebSearch, Task, AskUserQuestion
---

# Research Add Fields - 調査フィールドを補完

## トリガー
`/research-add-fields`

## ワークフロー

### ステップ1: フィールドファイルを自動検索
現在の作業ディレクトリで`*/fields.yaml`ファイルを見つけ、既存のフィールド定義を自動的に読み込む。

### ステップ2: 補完ソースを取得
ユーザーに選択を依頼：
- **A. ユーザー直接入力**: フィールド名と説明を提供
- **B. Web検索**: エージェントを起動してこの分野の一般的なフィールドを検索

### ステップ3: 表示と確認
- 提案された新規フィールドリストを表示
- ユーザーがどのフィールドを追加するか確認
- ユーザーがフィールドカテゴリとdetail_levelを指定

### ステップ4: 更新を保存
確認されたフィールドをfields.yamlに追加し、ファイルを保存。

## 出力
更新された`{topic}/fields.yaml`ファイル（インプレース変更、ユーザー確認が必要）
