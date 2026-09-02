.PHONY: serve jekyll clean

# ホットリロード付きプレビュー（Ruby不要。liquidjs + dart-sass による簡易レンダラー）
serve:
	cd preview && npm install --silent
	node preview/dev.mjs

# 本物のJekyllでプレビュー（要Ruby環境。本番と同一のビルド）
jekyll:
	bundle exec jekyll serve --livereload

clean:
	rm -rf _preview preview/node_modules
