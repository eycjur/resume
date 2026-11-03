#!/usr/bin/env python3
"""デジタル名刺の Apple Wallet パス (.pkpass) を生成する。

必要な環境変数:
  PASS_TYPE_ID  Pass Type ID (例: pass.io.github.eycjur.card)
  TEAM_ID       Apple Developer の Team ID
  PASS_CERT     Pass Type ID 証明書 (PEM)
  PASS_KEY      秘密鍵 (PEM)
任意:
  PASS_KEY_PASSWORD  秘密鍵のパスフレーズ
  WWDR_CERT          Apple WWDR 中間証明書 (PEM)。未指定なら G4 をダウンロードする
  PASS_OUT           出力先 (既定: assets/card/kmuto.pkpass)
"""
import hashlib
import json
import os
import string
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WWDR_URL = "https://www.apple.com/certificateauthority/AppleWWDRCAG4.cer"


def env(name, required=True):
    value = os.environ.get(name)
    if required and not value:
        sys.exit(f"環境変数 {name} が未設定です（wallet/README.md を参照）")
    return value


def fetch_wwdr(tmp):
    der = Path(tmp, "wwdr.cer")
    pem = Path(tmp, "wwdr.pem")
    urllib.request.urlretrieve(WWDR_URL, der)
    subprocess.run(["openssl", "x509", "-inform", "DER", "-in", der, "-out", pem], check=True)
    return pem


def main():
    pass_type_id = env("PASS_TYPE_ID")
    team_id = env("TEAM_ID")
    cert = env("PASS_CERT")
    key = env("PASS_KEY")
    password = env("PASS_KEY_PASSWORD", required=False)
    out = Path(env("PASS_OUT", required=False) or ROOT.parent / "assets/card/kmuto.pkpass")

    template = string.Template((ROOT / "pass.template.json").read_text(encoding="utf-8"))
    pass_json = template.substitute(PASS_TYPE_ID=pass_type_id, TEAM_ID=team_id).encode("utf-8")
    json.loads(pass_json)

    files = {"pass.json": pass_json}
    for image in sorted((ROOT / "pass").glob("*.png")):
        files[image.name] = image.read_bytes()
    manifest = json.dumps(
        {name: hashlib.sha1(data).hexdigest() for name, data in files.items()}, indent=2
    ).encode("utf-8")

    with tempfile.TemporaryDirectory() as tmp:
        wwdr = env("WWDR_CERT", required=False) or fetch_wwdr(tmp)
        manifest_path = Path(tmp, "manifest.json")
        signature_path = Path(tmp, "signature")
        manifest_path.write_bytes(manifest)
        cmd = [
            "openssl", "smime", "-binary", "-sign",
            "-certfile", wwdr, "-signer", cert, "-inkey", key,
            "-in", manifest_path, "-out", signature_path, "-outform", "DER",
        ]
        if password:
            cmd += ["-passin", "env:PASS_KEY_PASSWORD"]
        subprocess.run(cmd, check=True)
        signature = signature_path.read_bytes()

    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in files.items():
            zf.writestr(name, data)
        zf.writestr("manifest.json", manifest)
        zf.writestr("signature", signature)
    print(f"生成しました: {out}")


if __name__ == "__main__":
    main()
