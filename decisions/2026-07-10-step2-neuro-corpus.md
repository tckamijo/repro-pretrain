# Step 2 — 神経 OA コーパス収集 provenance / spec

- 日付: 2026-07-10
- 端末: mac-mini（中枢 hub、macOS 26.5.2）
- repo: `~/projects/repro-pretrain`（HEAD 継承 `ff822e8`）
- 目的: repro-pretrain の実演台コーパス。神経/生物医学 OA 本文を byte-level で数百MB、
  `harness/train_scale.py --corpus corpus/data/neuro.bin`（uint8 memmap）が食える形にする。

## データ源

- **NCBI PMC Open Access subset** を E-utilities 経由で取得。
  - 探索: `esearch.fcgi?db=pmc&term=<query> AND open access[filter]`
  - 本文: `efetch.fcgi?db=pmc&id=<PMCID>&retmode=xml`（OA subset は full-text JATS を返す）
- 選定理由（empirical）: memory `project_lit_fetch_poc_2026-06-11` の教訓で
  **publisher 直叩きは anti-bot で全滅、PMC/API は素直**。E-utilities は anti-bot 無し・
  ライセンスが JATS `<permissions><license>` に埋まっており per-article gate 可能。
- politeness: API key 無しの NCBI 上限 **≤3 req/s** を順守（`sleep 0.35s`/request）、
  429/5xx は指数バックオフ retry。UA に contact 明記
  （`repro-pretrain-corpus-bot/0.1 (... contact: chuyo.km@gmail.com)`、grant-feed 流儀）。

## ライセンス方針（★release 可能性の要）

- **KEEP = permissive のみ**: CC0 / public-domain, CC-BY, CC-BY-SA。
- **REJECT = NC もしくは ND を含む全て**（CC-BY-NC, CC-BY-ND, CC-BY-NC-ND …）。
  - 理由: 最終成果を open release（Apache-2.0 code + corpus + weights, Tessera 流 full-open）
    するため、非商用/派生禁止条項は corpus に混入させない。ND は「学習=派生」解釈の risk も回避。
- gate は **efetch した実 XML の `<license>` href を authoritative に判定**（`corpus/collect_neuro.py:classify_license`）。
  - esearch 段階の license filter（`cc by[filter]` 等）は PMC 非対応で **0 hits**（2026-07-10 実測）→
    per-article gate が唯一の確実手段。
  - JATS の href 行折り返しアーティファクト（`by-\nnc-nd`）対策に空白除去して正規化。
- **rejected は全件 `corpus/data/rejected.jsonl` に理由付きで記録**（透明性・監査可能性）。

## 出力 / レイアウト（すべて gitignore、コードのみ tracked）

- `corpus/data/docs/<PMCID>.txt` — per-doc クリーン UTF-8 本文（表/図/参考文献/数式を除去、段落保持）。
- `corpus/data/manifest.jsonl` — provenance 1 doc 1 行:
  `{pmcid, title, license, chars, bytes, sha256, fetched, source}`。
- `corpus/data/rejected.jsonl` — 却下ログ `{pmcid, reason, license?}`。
- `corpus/data/neuro.bin` — **決定的組立**（`--assemble`）: PMCID を整数昇順ソートし
  `\n\n<|endoftext|>\n\n` 区切りで連結、全体 sha256 を stdout に記録。
  → コーパス自体が doc 集合から再現可能（本 PJ は再現性研究なのでコーパスも決定的に）。
- 品質フィルタ: 本文 < 2000 字は stub とみなし drop（`too_short`）。

## Smoke 実測（2026-07-10, 40 fetch）

- 40 fetch → **kept 29 / rejected 11**（reject 内訳: 全て `license_restricted` = NC/ND）。
  → **permissive 歩留まり ≈ 72%**。ライセンス gate が期待どおり NC/ND を弾いた。
- 29 docs = **1.40MB**（sha256 `bd139e90…97c1c`）、平均 ~48KB/doc。
  → 300MB 目標は **≈6,300 docs / ≈8,700 fetch** 見込み。
- 抽出品質: クリーン本文（例 13341307 = chronic pain 論文の Introduction）、参考文献・表除去確認。
- `train_scale.load_corpus("corpus/data/neuro.bin")` = uint8 / byte range 10–226（vocab256 内）/
  train 1,396,772・val 7,019 tokens に分割 ✓。→ harness 互換確認。

## 本 crawl

- コマンド: `python corpus/collect_neuro.py --query neuroscience --target-mb 300`
- 2026-07-10 mac-mini で nohup バックグラウンド起動、`corpus/data/crawl.log` に進捗。
- resumable: seen-set を manifest+rejected から復元、中断/再実行で続きから。
- 完了後: `--assemble` で neuro.bin 再生成 → sha256 を本 doc に追記 → seal 前提へ。

## 本 crawl 結果（2026-07-10 完了、確定）

- **kept 6,961 docs / rejected 3,025 / fetched 9,938**（permissive 歩留り ≈ 70%）。
- **kept license 内訳**: CC-BY 6,933 + CC0 28 = 6,961。**NC/ND 混入ゼロ**（gate 完全動作）。
- rejected 内訳: `license_restricted`(NC/ND) 2,933 / `too_short` 80 / `fetch_error` 8 / `license_unknown` 4。
- **neuro.bin = 300.12MB**、**sha256 `9d6b168e700a2a7b4bd2bbc609449ff6e74952819a0453c3ac0b82d93a5b0a27`**。
  - `train_scale.load_corpus`: train **298,619,798** + val **1,500,603** tokens、uint8、byte range 10–240（vocab256 内）✓。
- crawl 所要: 会話中に完走（当初「数時間」見積りは保守的すぎ、実測はより速い）。
  完了検知 → `--assemble` → iMessage 通知は watcher（scratchpad `watch_crawl.sh`, harness 追跡）が自動実行。
  - watcher 初版バグ: `pgrep -f "collect_neuro.py"` が起動ラッパーの echo にも誤マッチ → 永久待機。
    crawl argv に一意な `collect_neuro.py --query neuroscience --target-mb` に修正して解決。

## 次段（Step 2 後）

- 事前登録 seal（H: cross-backend 分岐は 50M/124M でも消えない / onset step のスケール方向）+
  anti-rescue ledger（`feedback_pre_registered_test_anti_rescue`）。
- overnight size-ladder run（honmaru RTX3060、`corpus/data/neuro.bin` を配置）。
