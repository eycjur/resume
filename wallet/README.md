# デジタル名刺の Apple Wallet パス

`ja/card/` の名刺を Apple Wallet に入れ、相手に QR コード（名刺ページの URL）を見せるためのパスを生成します。
パスの表面には名刺ページと X の QR コードを並べた画像（`pass/strip*.png`）を表示します。
パスの内容は `pass.template.json`、画像は `pass/` にあります。画像はアバターや URL を変えたときに `make wallet-images`（要: `pip install "qrcode[pil]"`）で再生成します。

## 1. 証明書の準備（初回のみ・要 Apple Developer Program）

1. [Identifiers](https://developer.apple.com/account/resources/identifiers/list/passTypeId) で Pass Type ID を作成（例: `pass.io.github.eycjur.card`）
2. その Pass Type ID の証明書を作成（キーチェーンアクセスで CSR を作成してアップロード）し、`.cer` をダウンロードしてキーチェーンに追加
3. キーチェーンから証明書を `.p12` で書き出し、PEM に変換

```sh
openssl pkcs12 -in pass.p12 -clcerts -nokeys -out pass-cert.pem  # OpenSSL 3 でエラーになる場合は -legacy を付ける
openssl pkcs12 -in pass.p12 -nocerts -out pass-key.pem
```

証明書・鍵はリポジトリにコミットしないでください（`.gitignore` 済み）。

## 2. 生成

```sh
PASS_TYPE_ID=pass.io.github.eycjur.card \
TEAM_ID=XXXXXXXXXX \
PASS_CERT=pass-cert.pem \
PASS_KEY=pass-key.pem \
PASS_KEY_PASSWORD=... \
make wallet
```

`assets/card/kmuto.pkpass` が生成されます。Apple WWDR 中間証明書（G4）は自動でダウンロードされます（`WWDR_CERT` で指定も可）。

## 3. iPhone に追加

- AirDrop / メールで iPhone に送って開く
- またはコミットして GitHub Pages に公開し、Safari で `https://eycjur.github.io/resume/assets/card/kmuto.pkpass` を開く

Wallet でパスを開くと名刺ページ（`https://eycjur.github.io/resume/ja/card/`）と X（`https://x.com/eycjur`）の QR コードが並んで表示されます。
