# repro-pretrain 論文 — NotebookLM 読み方ガイド

NotebookLM の音声概要（日本語）で誤読しやすい固有名詞・略語・技術用語・記号の読み一覧。
**原則: TTS は読み注記を無視するので、気になる語はカナ直書きで指定する**（本文やカスタム指示に直接カナを入れる）。

## 著者・所属（最重要）
- **上條 中庸 / Tadanobu C. Kamijo → 「かみじょう ただのぶ」**
  - ⚠️「ちゅうよう」「なかよう」は誤り。中庸=ただのぶ。英語表記は Tadanobu Kamijo。
- University of the Ryukyus → **りゅうきゅうだいがく**（琉球大学）
- Graduate School of Medicine, Department of Systems Physiology → 医学研究科 システム生理学

## 略語（カナ直書き）
| 表記 | 読み |
|---|---|
| CUDA | クーダ |
| MPS (Metal Performance Shaders) | エムピーエス（メタル） |
| CPU / GPU | シーピーユー / ジーピーユー |
| TMLR | ティーエムエルアール |
| PMC | ピーエムシー |
| OA (open access) | オープンアクセス |
| CC-BY / CC-BY-SA / CC0 | シーシー・ビーワイ / シーシー・ビーワイ・エスエー / シーシー・ゼロ |
| SHA-256 | シャ にごーろく |
| fp32 / bf16 / fp16 | エフピー さんじゅうに / ビーエフ じゅうろく / エフピー じゅうろく |
| AdamW | アダム・ダブリュー |
| NVIDIA / RTX 3060 | エヌビディア / アールティーエックス さんまるろくまる |
| PyTorch | パイトーチ |
| API | エーピーアイ |
| JATS (XML) | ジャッツ |

## 技術用語（日本語 or カナ）
| 英語 | 読み / 訳 |
|---|---|
| pretraining | 事前学習（じぜんがくしゅう） |
| byte-level | バイトレベル |
| Transformer | トランスフォーマー |
| seed | シード |
| prediction disagreement | 予測不一致（よそくふいっち） |
| validation loss | 検証ロス（バリデーションロス） |
| determinism / non-determinism | 決定性 / 非決定性 |
| reproducibility | 再現性（さいげんせい） |
| bit-identical | ビット完全一致 |
| pre-registration | 事前登録（じぜんとうろく） |
| anti-rescue ledger | アンチレスキュー・レジャー（後付け防止の台帳） |
| onset | オンセット（発現点） |
| floating-point non-associativity | 浮動小数点の非結合性（ひけつごうせい） |
| heterogeneous fleet | 異種混成の計算機群 |
| backend | バックエンド |

## 記号・数値の読み下し（TTS が崩しやすい）
- **13.2% → じゅうさんてん に パーセント** / 0.2% → れいてん に パーセント / 0.07% → れいてん れいなな パーセント
- **|Δ| = 0.012 → 「デルタの絶対値は れいてん れいいちに」**
- **± 1.0% → プラスマイナス いってん れい パーセント**
- **10M / 50M / 124M → 1000万 / 5000万 / 1億2400万（パラメータ）**（"M" は「ミリオン」でも可）
- **↔（例 CUDA↔CPU）→ 「クーダ と シーピーユー の対（比較）」**
- 4,000 steps → よんせん ステップ / 50/100/…/4000 step → ステップ数はそのまま数字読み
- step 800 → ステップ はっぴゃく

## キーフレーズ（意味を保った読み）
- "same recipe, different model" → 「同じレシピ、違うモデル」
- "equally-good-but-different" → 「同じくらい優秀だけど別物（べつもの）」
- "holds at 10M but fails at 50M" → 「1000万では保たれるが5000万では崩れる」
- "scale-dependence / emerges with scale" → 「規模依存 / 規模とともに現れる」

## 参考文献の主な著者（英語読み、要注意のみ）
- Srivastava, Arora, Boneh → スリヴァスタヴァ、アローラ、ボネ
- Goldberg → ゴールドバーグ / Bouthillier → ブティリエ / Shanmugavelu → シャンムガヴェル
- （その他の英語名は NotebookLM が概ね正しく読むので個別指定不要）

## NotebookLM 運用メモ
- 音声概要の**言語を日本語**に設定。カスタム指示に「著者名は『かみじょう ただのぶ』と読む」等を明記すると安定。
- **カナ直書き原則**（TTS は furigana 的注記を無視 → 気になる語は本文/指示に直接カナ）。関連: memory `user_name_reading`。
- 深掘りには 5-prompt 型（用語多層 / 逆質問 / 反論あぶり出し / 音声概要 / 構造化ノート）が有効。関連: memory `reference_notebooklm_5prompts`。
- ソースには **PDF（`main.pdf`）本体**＋本ガイドの両方を入れると読みが安定。
