.PHONY: serve wallet

# 静的ファイルをそのまま配信してプレビューする（ビルド不要）
serve:
	python3 -m http.server 4000

# デジタル名刺の Apple Wallet パスを生成する（wallet/README.md を参照）
wallet:
	python3 wallet/build.py
