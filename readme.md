# CNT-Controller
卒研用のプログラムです．
ごちゃついてますが，今から見る必要があるのは`controller_gui`フォルダ内の`cnt-maker.pyw`というファイルです．
他のファイルはこれを作るために使った実験用ファイルなので見なくてもok．

吸光度測定機から出力されたcsvファイルを整形する`result_extractor_gui.pyw`などもこのリポジトリにおいてあります．

## ファイル解説
### controller_gui/cnt-maker.pyw
メインプログラム．これを実行するとGUIが開くのでよしなに．．．

### controller_gui/cnt-pump_factory.py
周辺機器制御用のプログラム．pump_factoryといいつつLEDの点灯管理もやっている．Windows環境で実行するとき周辺機器がつながっておらず，デバッグがしにくかったので勝手に環境を判別してダミーのポンプを渡すようにしている．

### result_extractor_gui.pyw
吸光度測定機から出力されたcsvファイルを整形する．（GUI版）
CUI版との違いはGUIで操作するかコマンドラインから実行するかという点しかない．
使い方のマニュアルは`ソフトの使い方`ディレクトリに置いておいた．

### result_extractor.py
吸光度測定機から出力されたcsvファイルを整形する．（CUI版）




2022/02/13 @MunoLike