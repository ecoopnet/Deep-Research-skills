---
user-invocable: true
description: 深堀り調査の結果をMarkdownレポートにまとめます。すべてのフィールドをカバーし、不確定な値はスキップします。
allowed-tools: Read, Write, Glob, Bash, AskUserQuestion
---

# Research Report - サマリーレポート

## トリガー
`/research-report`

## ワークフロー

### ステップ1: 結果ディレクトリを検索
現在の作業ディレクトリで`*/outline.yaml`を見つけ、topicとoutput_dir設定を読み込む。

### ステップ2: オプションのサマリーフィールドをスキャン
すべてのJSON結果を読み込み、目次表示に適したフィールド（数値、短いメトリクス）を抽出、例：
- github_stars
- google_scholar_cites
- swe_bench_score
- user_scale
- valuation
- release_date

AskUserQuestionでユーザーに確認：
- 項目名以外に目次に表示するフィールドは？
- 動的なオプションリストを提供（JSONの実際のフィールドに基づく）

### ステップ3: Python変換スクリプトを生成
`{topic}/`ディレクトリに`generate_report.py`を生成、スクリプト要件：
- output_dirからすべてのJSONを読み込む
- fields.yamlを読み込んでフィールド構造を取得
- 各JSONからすべてのフィールド値をカバー
- [uncertain]を含む値のフィールドをスキップ
- uncertain配列にリストされたフィールドをスキップ
- Markdownレポート形式を生成：目次（アンカーリンク + ユーザー選択のサマリーフィールド）+ 詳細コンテンツ（フィールドカテゴリ別）
- `{topic}/report.md`に保存

**目次フォーマット要件**:
- すべての項目を含める必要がある
- 各項目に表示：番号、名前（アンカーリンク）、ユーザー選択のサマリーフィールド
- 例：`1. [GitHub Copilot](#github-copilot) - Stars: 10k | Score: 85%`

#### スクリプト技術要件（必須）

**1. JSON構造の互換性**
2つのJSON構造をサポート：
- フラット構造：フィールドがトップレベルに直接 `{"name": "xxx", "release_date": "xxx"}`
- ネスト構造：フィールドがカテゴリサブ辞書内 `{"basic_info": {"name": "xxx"}, "technical_features": {...}}`

フィールド検索順序：トップレベル -> カテゴリマッピングキー -> すべてのネスト辞書を走査

**2. カテゴリの多言語マッピング**
fields.yamlのカテゴリ名とJSONキーは任意の組み合わせ（日-日、日-英、英-日、英-英）。双方向マッピングを確立する必要がある：
```python
CATEGORY_MAPPING = {
    "基本情報": ["basic_info", "基本情報", "Basic Info"],
    "技術的特徴": ["technical_features", "technical_characteristics", "技術的特徴", "Technical Features"],
    "性能指標": ["performance_metrics", "performance", "性能指標", "Performance Metrics"],
    "マイルストーン・重要性": ["milestone_significance", "milestones", "マイルストーン・重要性", "Milestone Significance"],
    "ビジネス情報": ["business_info", "commercial_info", "ビジネス情報", "Business Info"],
    "競合・エコシステム": ["competition_ecosystem", "competition", "競合・エコシステム", "Competition & Ecosystem"],
    "歴史": ["history", "歴史", "History"],
    "市場ポジショニング": ["market_positioning", "market", "市場ポジショニング", "Market Positioning"],
}
```

**3. 複雑な値のフォーマット**
- 辞書のリスト（例：key_events, funding_history）：各辞書を1行でフォーマット、kvを` | `で区切る
- 通常のリスト：短いリストはカンマで結合、長いリストは改行で表示
- ネストされた辞書：再帰的にフォーマット、セミコロンまたは改行で表示
- 長いテキスト文字列（100文字以上）：可読性のため改行`<br>`を追加、またはブロック引用形式を使用

**4. 追加フィールドの収集**
JSONに存在するがfields.yamlで定義されていないフィールドを収集し、「その他の情報」カテゴリに配置。フィルタリングに注意：
- 内部フィールド：`_source_file`、`uncertain`
- ネスト構造のトップレベルキー：`basic_info`、`technical_features`など
- `uncertain`配列：各フィールド名を別々の行に表示、1行に圧縮しない

**5. 不確定な値のスキップ**
スキップ条件：
- フィールド値に`[uncertain]`文字列が含まれる
- フィールド名が`uncertain`配列にある
- フィールド値がNoneまたは空文字列

### ステップ4: スクリプトを実行
`python {topic}/generate_report.py`を実行

## 出力
- `{topic}/generate_report.py` - 変換スクリプト
- `{topic}/report.md` - サマリーレポート
