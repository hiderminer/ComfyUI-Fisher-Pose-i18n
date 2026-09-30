# i18n fork history — how the upstream code was changed

This memo records how this fork differs from the upstream plugin, so that future upstream updates can be merged and re-localized with minimal effort.

- Upstream: https://github.com/Work-Fisher/ComfyUI-Fisher-Pose (`origin` in this clone)
- Base commit: `d116451f25b1c9da36dd852fdc9df321068f4d98` ("Ship the body pack uncompressed; keep only the free-pose workflow")
- Fork work done: 2026-09-28, verified on ComfyUI 0.37.0 / comfyui-frontend-package 1.53.6
- Goal: show the UI in Simplified Chinese, Japanese and English (following ComfyUI's `Comfy.Locale`), without changing generation behavior.

## 1. Ground rules (apply these to any upstream change)

Every Chinese string in upstream falls into one of three classes. Classify first, then act:

| Class | Examples | Action |
|---|---|---|
| **UI text** (shown to the user) | button labels, headings, hints, toasts, confirm dialogs, editor error messages, node display names, output names, descriptions, tooltips | Move to dictionaries (editor: `web/editor/i18n/*.mjs`; node: `locales/*/nodeDefs.json`). Python error messages → **English only** (no dictionary). |
| **Prompt text** (sent to the model) | edit instructions built in `pose_core.py`, `qwen_bridge.py`, `prompt_format.py`, `pe_rewrite.py`, `state.mjs` `buildPrompt/personFacing/personConstraints/personDescription/cameraTerms`; `system_prompt_edit.txt`; `Draw character from image2` | **Never translate or change.** Output must stay byte-identical to upstream. |
| **Saved values / identifiers** (stored in workflows or scene JSON, compared in code) | `MODES = ["视角＋姿态","仅视角","仅姿态"]`, `["自动","图1","图2","图3"]`, `promptStyle: '中文编辑指令'`, `'Multiangle LoRA (<sks>)'` | **Keep the value.** Translate only the label (`options` in nodeDefs.json, `<option value="原值" data-i18n=...>` in HTML). |

Other rules used throughout:
- Python defaults (display names, `RETURN_NAMES`, `DESCRIPTION`, tooltips, `CATEGORY`, BOOLEAN `label_on/off`) are **English**; Chinese/Japanese come from `locales/`.
- Original Chinese text is left in the HTML as fallback content; `applyI18n()` replaces it at load time.
- Default names created by the UI (`人物 01`, `镜头 01`, `姿势 N`) are translated only for newly created items; existing saved data is not touched.
- Code comments that mention Chinese feature names (e.g. `我的姿势`) were left as they are.

## 2. Files added

| File | Purpose |
|---|---|
| `web/editor/i18n.mjs` | `resolveLang(code)` (zh / zh-TW → `zh`, `ja` → `ja`, anything else → `en`), `LANG` (from `?lang=` in the iframe URL, else `navigator.language`), `t(key, params)`, `translate(lang, key, params)`, `applyI18n(root)`. `{name}` placeholders. Fallback order: current language → en → zh → key. Guarded for Node (`location`/`navigator` may be undefined) so `tests/test_openpose_lift.mjs` still runs. |
| `web/editor/i18n/zh.mjs`, `ja.mjs`, `en.mjs` | Editor dictionaries, ~380 keys each, identical key sets. `zh.mjs` holds the **original upstream strings verbatim** — use it to find what a key replaced. |
| `locales/{en,ja,zh}/nodeDefs.json` | ComfyUI node translations: `display_name`, `description`, `inputs.<name>.{name,tooltip,options}`, `outputs.<index>.name`. `options` maps the saved Chinese combo values to labels. |
| `readme-cn.md`, `readme-jp.md` | Chinese (upstream README adapted to the fork) and Japanese README. `README.md` is now English. |
| `pose-images/README.md` | How to obtain the built-in skeleton images (not shipped). |
| README section “Where data is saved” | Added to `README.md` / `readme-cn.md` / `readme-jp.md` (before “UI language”): save locations of My poses, My library, built-in skeletons, node data, preview temp files, standalone localStorage. Paths are relative to the top of the ComfyUI repository — never write absolute local paths in repository docs. |
| `history.md` | This memo. |

Editor attribute conventions (handled by `applyI18n`):
- `data-i18n="key"` → `textContent`
- `data-i18n-lead="key"` → only the leading text node (keeps child `<input>`, `<output>`, `<select>`, `<span id=...>`; trailing whitespace is preserved). Used where wrapping text in a `<span>` would hit CSS such as `.shots h2 span`.
- `data-i18n-html="key"` → `innerHTML` (only for our own dictionary strings containing `<br>`)
- `data-i18n-title / -placeholder / -alt / -aria-label` → that attribute
- `<html data-i18n-title="...">` → `document.title`

Key prefixes: `common.*`, `kbd.*`/`act.*` (interaction bar), `cam.*` (view bins for display), `facing.*`, `mode.*`, `style.*`, `joint.*`, `preset.*`, `person.*`, `err.*` (state.mjs), `bind.*` (Qwen binding summary), `ref.*` (reference.mjs), `imp.*` (pose-import / openpose-lift), `cube.*`, `avatar.*`, `fp.*` (free-pose editor), `st.*` (multi-person studio), `node.*` (fisher_pose.js).

## 3. Changes per upstream file

### Web (editor / extension)
| File | Change |
|---|---|
| `web/fisher_pose.js` | Imports `resolveLang, translate` from `./editor/i18n.mjs`. `uiLang()` reads `Comfy.Locale` (`app.extensionManager.setting.get` → `app.ui.settings.getSettingValue` → `navigator.language`). `EDITORS.*.title` became a key and a `button` key was added; iframe `title` and the node button label use `translate()`. iframe URL gets `&lang=<lang>`. `version` strings bumped to `20260928-i18n` (cache busting). |
| `web/editor/freepose.html` | All visible text got `data-i18n*` attributes; label text wrapped in `<span data-i18n>` where needed; gallery-source buttons got `data-i18n`. Script query bumped to `?v=20260928-i18n`. |
| `web/editor/studio.html` | Same as above; `data-i18n-lead` for labels with inline controls and for headings with counters. `#output-mode` and `#prompt-style` `<option>`s got explicit `value="<original Chinese>"` (they previously had text only) plus `data-i18n` labels. Script query bumped. |
| `web/editor/freepose.mjs` | `import { t, applyI18n }` and `applyI18n()` at the top. `BODY_SLIDERS` / `PROPORTIONS` labels → `t('fp.body.*')` / `t('fp.prop.*')`. `SOURCE_NAMES` → `t()`. All toasts, statuses, confirms, prompts, innerHTML hints and errors → `t()`. Comment mentions `pose-images/`. |
| `web/editor/studio.mjs` | `import { t, applyI18n }`, `applyI18n()` at the top. Imports `cameraLabel`, `personFacingLabel` instead of `cameraTerms`, `personFacing`. `#camera-summary` uses `cameraLabel(state)`; `#actor-facing` uses `personFacingLabel()`. Mode/style help → `t()` keyed by the **Chinese mode/style value**. All toasts, hints, shot names, fit messages → `t()`. Mode values (`'视角＋姿态'` etc.) in logic are unchanged. |
| `web/editor/state.mjs` | `import {t}`. `PRESETS[].name`, `JOINT_NAMES` (built from `t('joint.'+key)`), `newPerson` default name, `migrate()` errors → `t()`. Refactor: `cameraBins()` extracted from `cameraTerms()` and new `cameraLabel()` (UI); `facingIndex()` extracted from `personFacing()` and new `personFacingLabel()` (UI). `cameraTerms()` / `personFacing()` return exactly the upstream strings. In `buildPrompt()` only the **`state.qwenBinding` summary branch** (an on-screen summary, not a model prompt) was localized; its per-person `personDescription()` text stays Chinese. All other `buildPrompt` branches are untouched. |
| `web/editor/reference.mjs` | `import {t}`; all strings → `ref.*`. |
| `web/editor/pose-import.mjs` | `import {t}`; thrown errors and `people.warnings` → `imp.*`. |
| `web/editor/openpose-lift.mjs` | `import { t }`; one thrown error → `imp.coincident`. |
| `web/editor/scene-cube.mjs` | `import {t}`; cube face labels → `cube.*`. |
| `web/editor/avatar.mjs` | `import {t}`; face texture text 前/后 → `avatar.front/back`. |

### Python
| File | Change |
|---|---|
| `__init__.py` | `NODE_DISPLAY_NAME_MAPPINGS` → English (`Fisher Camera & Pose`, `Fisher Qwen2.1 Person & Pose Encode`, `Fisher Qwen2.1 Free Pose`, `Fisher Qwen2.1 GGUF CLIP Loader`). |
| `nodes.py`, `free_pose.py`, `qwen_bridge.py` | `RETURN_NAMES` → English (`prompt`, `positive`, `negative`, `latent`, `actual_prompt`, `mannequin_pose_image`, `camera_preview`); `CATEGORY` → `Fisher/Pose & Camera`; `DESCRIPTION` → English; `thinking` `label_on/off` → `Thinking: on/off`; `use_default_template` tooltip → English; errors → English. Combo values unchanged. |
| `gguf_clip.py` | Errors and `vision_source` tooltip → English; `CATEGORY` → `Fisher/Loaders`. |
| `pe_rewrite.py` | Errors and the cache log line → English. Prompt/request strings unchanged. `system_prompt_edit.txt` is no longer shipped: new module constants `SYSTEM_PROMPT_FILE` and `SHORT_SYSTEM_PROMPT` (the upstream short template, moved out of `rewrite()` unchanged). With `use_default_template=True` the file is used **if the user placed it** next to `pe_rewrite.py`; otherwise the short template is used and `[Fisher PE] system_prompt_edit.txt not found; ...` is printed. Upstream always read the file (and would fail without it). |
| `tests/test_pe_rewrite.py` | `test_options_change_generation_and_cache` now patches `pe_rewrite.SYSTEM_PROMPT_FILE` with a temporary user-supplied template (upstream relied on the shipped file). New test `test_missing_template_falls_back_to_short_template`. |
| `pose_reference.py`, `saved_poses.py` | Errors / API error messages → English. |
| `pose_core.py` | Errors → English; `validate_vector` labels → English (`joint {name}`, `person position`, `camera target`); new `LIMB_NAMES_EN` for the zero-length-bone error; comment on `MODES`. Prompt code unchanged. |
| `openpose_library.py` | `BUILTIN_FOLDER` → `pose-images` (was `FISHER小彩蛋`); docstring. |

### Repository / docs
| Item | Change |
|---|---|
| `FISHER小彩蛋/` | Renamed to `pose-images/`. The 209 images were removed from the index (`git rm --cached`) and are git-ignored (`pose-images/*`, `!pose-images/README.md`). They still exist in upstream history. |
| `.gitignore` | Added the rules above, plus `/system_prompt_edit.txt` (a user-supplied copy stays local). |
| `LICENSE` | Unchanged from upstream (a temporary Qwen entry was added and removed again). |
| `README.md` | Rewritten in English; language links; fork notice; install section explains `pose-images/`; UI-language section; license section says `system_prompt_edit.txt` is not included and how to supply it. Same in `readme-cn.md` / `readme-jp.md`. |
| `system_prompt_edit.txt` | **Deleted** (`git rm`). It was a byte-identical copy of QwenLM's `prompt_rewrite/prompts/system_prompt_edit.txt` under the Qwen Research License (non-commercial only), which the upstream LICENSE did not declare. The `LICENSE-Qwen-Research.txt` / `NOTICE` files that were briefly added for it were removed as well. Upstream docs already call it "user-provided". |
| `use_default_template` tooltip | Python default and all three `nodeDefs.json` explain that the full template needs a user-supplied `system_prompt_edit.txt`. |
| Editor dictionary text `fp.builtinNeedsComfy` | Now also explains that images must be copied into `pose-images/`. |

## 4. Procedure for merging an upstream update

1. Fetch upstream and see what changed since the base:
   ```bash
   git fetch origin
   git diff --stat d116451 origin/main
   git log --oneline d116451..origin/main
   ```
2. Merge on a branch (`git merge origin/main`). Expected conflict hot spots: the files in §3, especially `studio.mjs`, `freepose.mjs`, `state.mjs`, the two HTML files, and every Python `raise`.
3. For each upstream hunk that touches a Chinese string, classify it (§1):
   - **New/changed UI string** → add or update the key in **all three** `web/editor/i18n/*.mjs` (put the upstream text verbatim in `zh.mjs`) or in `locales/*/nodeDefs.json`; replace the literal with `t('key')` / `data-i18n`.
   - **New/changed prompt text** → take upstream as-is.
   - **New saved value** (new mode, new combo choice) → keep the value; add an `options` label in all `nodeDefs.json` and `data-i18n` on the `<option>`.
   - **New Python error** → write it in English.
   - **New node / input / output** → English defaults in Python; add entries to all three `nodeDefs.json` (outputs are keyed by index — re-check indices if upstream reorders outputs).
4. If upstream touches `FISHER小彩蛋/`: keep images untracked; keep `BUILTIN_FOLDER = "pose-images"`.
5. If upstream changes its (Chinese) README: apply the change to `readme-cn.md`, then mirror it in `README.md` and `readme-jp.md`.
6. If upstream changes `system_prompt_edit.txt`: do **not** re-add it (keep it deleted / git-ignored). If upstream changes how `pe_rewrite.py` loads it, keep the optional-file + `SHORT_SYSTEM_PROMPT` fallback. If upstream changes the short template text, update `SHORT_SYSTEM_PROMPT` verbatim.
7. Bump `version` in `web/fisher_pose.js` and the `?v=` of the editor script tags.
8. Verify (see §5), then check in ComfyUI with Locale = 日本語 / English / 中文.

## 5. Verification tools

The helper scripts live outside this repository, in the owner's working folder next to the ComfyUI checkout (`../work/scripts/` relative to the top of the ComfyUI repository; copy them if the fork moves):

| Script | Use |
|---|---|
| `count_cjk.py <root> [--show FILE]` | Lists files/lines that still contain CJK text — run on changed files to find untranslated UI strings. Remaining hits should only be prompt text, saved values, `zh.mjs`/`ja.mjs`, comments. |
| `fisher-pose-i18n/check_i18n.py <root>` | Same key set in zh/ja/en, every used key defined, placeholders consistent, nodeDefs.json valid and covering the same nodes. |
| `fisher-pose-i18n/compare_prompts.mjs <upstream web/editor> <fork web/editor>` | Asserts `buildPrompt` / `personFacing` / `personConstraints` / `cameraTerms` produce identical output (2880 cases). Run with the new upstream `state.mjs` after merging. |
| `fisher-pose-i18n/replace_exact.py <file> <pairs.json>` | Exact-match replacement (each old string must occur once); `pairs_*.json` next to it are the replacement lists used for this fork — a concrete record of every string that was replaced. |

Also: `node --check` on all `web/**/*.mjs|js`, `python -m py_compile` on the Python files, and the upstream tests that do not need ComfyUI (`tests/test_pose.py`, `test_pose_semantics.py`, `test_saved_poses.py`, `test_pe_rewrite.py`, `test_gguf_clip.py`, `node tests/test_openpose_lift.mjs`). Tests only assert prompt text and exception types, so English error messages do not affect them.

## 6. Open items

- `tests/test_free_pose.py` and `tests/test_qwen_bridge.py` (need a ComfyUI checkout) were not run; the UI and existing functions were checked manually in ComfyUI instead (before the `pose-images` rename and the `system_prompt_edit.txt` removal — re-check the built-in skeleton list and PE rewrite in ComfyUI).

Decided to keep as is (owner's decision):
- `docs/自由视角详细说明.md` stays Chinese only.
- `CATEGORY` names (`Fisher/Pose & Camera`, `Fisher/Loaders`) and BOOLEAN `label_on/off` stay English for all locales.
- Commits are made manually by the owner.
