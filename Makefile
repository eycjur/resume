.PHONY: serve wallet wallet-images

# 静的ファイルをそのまま配信してプレビューする（ビルド不要）
serve:
	python3 -m http.server 4000

# デジタル名刺の Apple Wallet パスを生成する（wallet/README.md を参照）
wallet:
	python3 wallet/build.py

# Wallet パスの画像（アバター・QR）を再生成する（要: pip install "qrcode[pil]"）
wallet-images:
	python3 wallet/make_images.py
