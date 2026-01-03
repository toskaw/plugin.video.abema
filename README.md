# plugin.video.abema
# ABEMA プラグイン

ABEMAの配信コンテンツをkodiで視聴するためのプラグインです。
ライブ放送は未対応です。ライブ放送は[abema_m3uplaylist](https://github.com/toskaw/abema_m3uplaylist)をお使いください。
## インストール

  zipファイルをダウンロードして、システム>アドオン>ZIPファイルからインストール
  
## スクリーンショット
<img src="https://github.com/toskaw/plugin.video.abema/blob/master/screenshots/p1.png?raw=true" alt="screenshot 1" width="400"/>
<img src="https://github.com/toskaw/plugin.video.abema/blob/master/screenshots/p2.png?raw=true" alt="screenshot 1" width="400"/>
<img src="https://github.com/toskaw/plugin.video.abema/blob/master/screenshots/p3.png?raw=true" alt="screenshot 1" width="400"/>
<img src="https://github.com/toskaw/plugin.video.abema/blob/master/screenshots/p4.png?raw=true" alt="screenshot 1" width="400"/>


## 保存用スクリプトについて
リストを選択してコンテキストメニューの「ダウンロード用のスクリプトを保存する」でyt-dlpを使ったスクリプトを作成します。
事前にアドオン設定で保存フォルダを設定してください。
保存フォルダにコンテンツのタイトルでフォルダを作成し、dl.shファイルを作成します
保存フォルダに書き込み権限が必要です。
ホスト側で保存フォルダに以下のようなスクリプトを作っておいてcronで定期実行すれば便利だと思います

	#!/bin/sh
	find . -name dl.sh -execdir sh ./dl.sh \;

