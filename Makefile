.PHONY: serve clean

# ホットリロード付きプレビュー（Ruby不要。liquidjs + dart-sass による簡易レンダラー）
serve:
	cd preview && npm install --silent
	node preview/dev.mjs

clean:
	rm -rf _preview preview/node_modules
