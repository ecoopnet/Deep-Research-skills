---
user-invocable: true
description: リサーチアウトラインを読み込み、各項目に対して独立したエージェントを起動して深堀り調査を行います。タスク出力は無効化されます。
allowed-tools: Bash, Read, Write, Glob, WebSearch, Task
---

# Research Deep - 深堀り調査

## トリガー
`/research-deep`

## ワークフロー

### ステップ1: アウトラインを自動検索
現在の作業ディレクトリで`*/outline.yaml`ファイルを見つけ、項目リストと実行設定（items_per_agentを含む）を読み込む。

### ステップ2: 再開チェック
- output_dir内の完了済みJSONファイルを確認
- 完了済み項目をスキップ

### ステップ3: バッチ実行
- batch_sizeごとにバッチ処理（次のバッチ前にユーザー承認が必要）
- 各エージェントはitems_per_agent個の項目を処理
- web-search-agentを起動（バックグラウンド並列、タスク出力無効）

**パラメータ取得**:
- `{topic}`: outline.yamlのtopicフィールド
- `{item_name}`: 項目のnameフィールド
- `{item_related_info}`: 項目の完全なyamlコンテンツ（name + category + descriptionなど）
- `{output_dir}`: outline.yamlのexecution.output_dir（デフォルト: ./results）
- `{fields_path}`: {topic}/fields.yamlへの絶対パス
- `{output_path}`: {output_dir}/{item_name_slug}.jsonへの絶対パス（item_nameをslugify：スペースを_に置換、特殊文字を削除）

**厳守事項**: 以下のプロンプトは{xxx}の変数のみを置換し、構造や文言を変更してはいけません。

**プロンプトテンプレート**:
```python
prompt = f"""## タスク
{item_related_info}を調査し、構造化JSONを{output_path}に出力

## フィールド定義
{fields_path}を読み込み、すべてのフィールド定義を取得

## 出力要件
1. fields.yamlで定義されたフィールドに従ってJSONを出力
2. 不確定なフィールド値は[uncertain]でマーク
3. JSONの最後にuncertain配列を追加し、すべての不確定フィールド名をリスト
4. すべてのフィールド値は英語で記述

## 出力パス
{output_path}

## 検証
JSON出力完了後、検証スクリプトを実行してフィールドカバレッジを確認：
python ~/.claude/skills/research/validate_json.py -f {fields_path} -j {output_path}
検証に合格して初めてタスク完了となります。
"""
```

**One-shot例**（GitHub Copilotを調査する場合）:
```
## タスク
調査対象 name: GitHub Copilot
category: 国際製品
description: Microsoft/GitHub開発、初のメインストリームAIコーディングアシスタント、市場シェア約40%、構造化JSONを/home/weizhena/AIcoding/aicoding-history/results/GitHub_Copilot.jsonに出力

## フィールド定義
/home/weizhena/AIcoding/aicoding-history/fields.yamlを読み込み、すべてのフィールド定義を取得

## 出力要件
1. fields.yamlで定義されたフィールドに従ってJSONを出力
2. 不確定なフィールド値は[uncertain]でマーク
3. JSONの最後にuncertain配列を追加し、すべての不確定フィールド名をリスト
4. すべてのフィールド値は英語で記述

## 出力パス
/home/weizhena/AIcoding/aicoding-history/results/GitHub_Copilot.json

## 検証
JSON出力完了後、検証スクリプトを実行してフィールドカバレッジを確認：
python ~/.claude/skills/research/validate_json.py -f /home/weizhena/AIcoding/aicoding-history/fields.yaml -j /home/weizhena/AIcoding/aicoding-history/results/GitHub_Copilot.json
検証に合格して初めてタスク完了となります。
```

### ステップ4: 待機と監視
- 現在のバッチの完了を待機
- 次のバッチを起動
- 進捗を表示

### ステップ5: サマリーレポート
すべて完了後、出力：
- 完了件数
- 失敗/uncertain マークされた項目
- 出力ディレクトリ

## エージェント設定
- バックグラウンド実行: Yes
- タスク出力: 無効（エージェントは完了時に明示的な出力ファイルを持つ）
- 再開サポート: Yes
