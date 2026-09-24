# plugin.video.abema
# ABEMA プラグイン

ABEMAの配信コンテンツをkodiで視聴するためのプラグインです。

## インストール

  zipファイルをダウンロードして、システム>アドオン>ZIPファイルからインストール
  version 2からyt-dlpを分離しました
  [script.module.yt-dlp](https://github.com/lekma/script.module.yt-dlp)が必要です。
  
## スクリーンショット
<img src="https://github.com/toskaw/plugin.video.abema/blob/master/screenshots/p1.png?raw=true" alt="screenshot 1" width="400"/>
<img src="https://github.com/toskaw/plugin.video.abema/blob/master/screenshots/p2.png?raw=true" alt="screenshot 1" width="400"/>
<img src="https://github.com/toskaw/plugin.video.abema/blob/master/screenshots/p3.png?raw=true" alt="screenshot 1" width="400"/>
<img src="https://github.com/toskaw/plugin.video.abema/blob/master/screenshots/p4.png?raw=true" alt="screenshot 1" width="400"/>


## 保存用スクリプトについて
リストを選択してコンテキストメニューの「ダウンロード用のスクリプトを保存する」でyt-dlpを使ったスクリプトを作成します。<br>
事前にアドオン設定で保存フォルダを設定してください。<br>
保存フォルダにコンテンツのタイトルでフォルダを作成し、dl.shファイルを作成します<br>
保存フォルダに書き込み権限が必要です。<br>
ホスト側で保存フォルダに以下のようなスクリプトを作っておいてcronで定期実行すれば便利だと思います<br>

	#!/bin/sh
	find . -name dl.sh -execdir sh ./dl.sh \;

## スキップボタン
オープニング、エンディング時にスキップボタンが表示されます。<br>
設定で自動スキップを設定できます。

