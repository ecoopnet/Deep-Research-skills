---
user-invocable: true
allowed-tools: Read, Write, Glob, WebSearch, Task, AskUserQuestion
description: トピックの予備調査を行い、リサーチアウトラインを生成します。学術研究、ベンチマーク調査、技術選定などに使用します。
---

# Research Skill - 予備調査

## トリガー
`/research <トピック>`

## ワークフロー

### ステップ1: モデルの知識から初期フレームワークを生成
トピックに基づき、モデルの既存知識を使用して生成：
- この分野の主要な調査対象/項目リスト
- 推奨される調査フィールドフレームワーク

{step1_output}を出力し、AskUserQuestionで確認：
- 項目を追加/削除する必要がありますか？
- フィールドフレームワークは要件を満たしていますか？

### ステップ2: Web検索で補完
AskUserQuestionで時間範囲を確認（例：過去6ヶ月、2024年以降、制限なし）。

**パラメータ取得**:
- `{topic}`: ユーザー入力のリサーチトピック
- `{YYYY-MM-DD}`: 現在の日付
- `{step1_output}`: ステップ1の完全な出力
- `{time_range}`: ユーザー指定の時間範囲

**厳守事項**: 以下のプロンプトは{xxx}の変数のみを置換し、構造や文言を変更してはいけません。

web-search-agentを1つ起動（バックグラウンド）、**プロンプトテンプレート**:
```python
prompt = f"""## タスク
リサーチトピック: {topic}
現在の日付: {YYYY-MM-DD}

以下の初期フレームワークに基づき、最新の項目と推奨調査フィールドを補完してください。

## 既存フレームワーク
{step1_output}

## 目標
1. 既存の項目に重要なオブジェクトが欠けていないか確認
2. 欠けているオブジェクトに基づいて項目を補完
3. {time_range}内の{topic}関連項目を検索して補完
4. 新しいフィールドを補完

## 出力要件
構造化された結果を直接返す（ファイルは書かない）：

### 補完項目
- item_name: 簡単な説明（なぜ追加すべきか）
...

### 推奨補完フィールド
- field_name: フィールドの説明（なぜこの観点が必要か）
...

### ソース
- [Source1](url1)
- [Source2](url2)
"""
```

**One-shot例**（AI Coding Historyを調査する場合）:
```
## タスク
リサーチトピック: AI Coding History
現在の日付: 2025-12-30

以下の初期フレームワークに基づき、最新の項目と推奨調査フィールドを補完してください。

## 既存フレームワーク
### 項目リスト
1. GitHub Copilot: Microsoft/GitHub開発、初のメインストリームAIコーディングアシスタント
2. Cursor: AIファーストIDE、VSCodeベース
...

### フィールドフレームワーク
- 基本情報: name, release_date, company
- 技術的特徴: underlying_model, context_window
...

## 目標
1. 既存の項目に重要なオブジェクトが欠けていないか確認
2. 欠けているオブジェクトに基づいて項目を補完
3. 2024年以降のAI Coding History関連項目を検索して補完
4. 新しいフィールドを補完

## 出力要件
構造化された結果を直接返す（ファイルは書かない）：

### 補完項目
- item_name: 簡単な説明（なぜ追加すべきか）
...

### 推奨補完フィールド
- field_name: フィールドの説明（なぜこの観点が必要か）
...

### ソース
- [Source1](url1)
- [Source2](url2)
```

### ステップ3: 既存フィールドについてユーザーに確認
AskUserQuestionで既存のフィールド定義ファイルがあるか確認し、あれば読み込んでマージ。

### ステップ4: アウトラインを生成（別ファイル）
{step1_output}、{step2_output}、ユーザーの既存フィールドをマージし、2つのファイルを生成：

**outline.yaml**（項目 + 設定）:
- topic: リサーチトピック
- items: 調査対象リスト
- execution:
  - batch_size: 並列エージェント数（AskUserQuestionで確認）
  - items_per_agent: エージェントあたりの項目数（AskUserQuestionで確認）
  - output_dir: 結果出力ディレクトリ（デフォルト: ./results）

**fields.yaml**（フィールド定義）:
- フィールドカテゴリと定義
- 各フィールドのname、description、detail_level
- detail_levelの階層: brief -> moderate -> detailed
- uncertain: 不確定フィールドリスト（予約フィールド、deepフェーズで自動記入）

### ステップ5: 出力と確認
- ディレクトリを作成: `./{topic_slug}/`
- 保存: `outline.yaml`と`fields.yaml`
- ユーザーに確認のため表示

## 出力パス
```
{current_working_directory}/{topic_slug}/
  ├── outline.yaml    # 項目リスト + 実行設定
  └── fields.yaml     # フィールド定義
```

## 後続コマンド
- `/research-add-items` - 項目を補完
- `/research-add-fields` - フィールドを補完
- `/research-deep` - 深堀り調査を開始
