.PHONY: serve

# 静的ファイルをそのまま配信してプレビューする（ビルド不要）
serve:
	python3 -m http.server 4000
