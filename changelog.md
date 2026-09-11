## [Unreleased]

## [0.0.19] - 2026-09-11
### Changed
- 语言指纹检测重构为**基于语料词组**：新增共享分词器 `charset_mnbvc/langid_tokenizer.py`，
  采用「脚本门控 + presence 朴素贝叶斯」两阶段判别，输出 BCP-47 标签（zh-Hans/zh-Hant/ja/ko/...），
  证据不足返回 Unknown。
- 指纹构建脚本 `data/fingerprints_build.py` 改为语料驱动/流式，从平行多语语料构建 15 语种指纹，
  输出至包内 `charset_mnbvc/data/language_fingerprints.json`。
### Fixed
- 修复繁体中文被强制判为简体、标签命名不一致、简繁细分逻辑空转、指纹文件未随包分发等问题。
### Added
- `tests/test_language_fingerprints.py`（金标 15 语种 + 繁体回归 + Unknown 边界）。

## [0.0.16] - 2024-09-29
### Added
- 添加中英文检测的能力 api.check_zh_en()

## [0.0.17] - 2024-09-29
### Added
- 添加跨平台的 magic文件类型检测支持

## [0.0.18] - 2024-10-01
### Added
- 新增语言指纹检测工具