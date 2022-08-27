# publish.py

記事の HTML を生成し、`index.html` に挿入する

## 動かし方

このリポジトリのディレクトリにいることが前提

```sh
$ ./publish.py

or

$ python3 publish.py
```

もちろん、vscode から実行することもできる

## 設定ファイル

`.draft` に次のように設定ファイルを置く

```
.draft
├── .body
├── .newstemplate
├── conf-template.json
└── conf.json
```

各設定ファイルは次の役割をもつ

- `.draft/.body`:
  - 記事の本文
- `.draft/.newstemplate`:
  - 記事のテンプレート (型)
  - このテンプレートから生成した記事を挿入する
  - [あとで解説](#draftnewstemplate)
- `.draft/conf-template.json`:
  - `conf.json` のテンプレート
  - 記事に最低限必要そうなキーを用意している
- `.draft/conf.json`:
  - ここで定義した値で、記事のテンプレートの任意の箇所を置換する
  - [あとで解説](#draftconfjson)

### .draft/.newstemplate

実際に使う、記事の基本テンプレートを例にして説明する

```
            <dt><span>${date}</span></dt>
            <details id="${date}">
              <summary>
                  <strong>${title}</strong>
              </summary>
              <dd>
                <div>
                  <p>
                    ${body}
                  </p>
                  <table style="table-layout: fixed; width: auto; border: none;">
                    <tr>
                      <td style="border: none;"><img src="${image_path}" style="width: 100%;"></td>
                    </tr>
                    <tr>
                      <td style="border: none;"><a href="${link}" style="width: 100%;">${link_name}</a></td>
                    </tr>
                  </table>
                </div>
              </dd>
            </details>
```
※ HTML に挿入したときのわかりやすさの観点から、インデントを入れている

ポイントは次の通り

- `${...}` は変数の感覚
  - たとえば、`<strong>${title}</strong>` の `${title}` は、変数 title の値で置換される
- 変数はどこで定義するか
  - `.draft/conf.json` で定義する
  - もし、`.draft/conf.json` に変数が定義されていなかった場合、そのままになる
- このテンプレートの `${...}` の箇所が変数の値で置換されたのち、`index.html` に挿入される
  - 記事のイベントがおこなわれた日付の降順になるように挿入される
  - 基本的にはこれだけ知っていれば十分だが、もっと詳しいことを知りたい場合は [こちら](#挿入時のルール) を参照
- テンプレートを編集することで挿入する記事の内容、見た目を柔軟に変更することができる
  - [この README の最後](#テンプレートの編集例) に例示

### .draft/conf.json

実際に使う、json ファイルを例にして説明する

```
{
  "date": "2022-06-15",
  "title": "📝日本電気(株)の宇都田賢一氏による研究室訪問(2022/06/15)",
  "body": ".draft/.body",
  "image_path": "./images/2022/nec-coming-00.png",
  "link": "https://jpn.nec.com/",
  "link_name": "日本電気(株)"
}
```

ポイントは次の通り

- `"X": "Y"` は変数定義の感覚
  - たとえば、`date: "2022-06-15` は、変数 `date` に `2022-06-15` を代入している感覚
- ここで定義した値で、記事のテンプレートの任意の箇所が置換される
  - たとえば、記事のテンプレートの `${date}` が `2022-06-15` に置換される
- `body` は編集しない
  - キー `body` の値が定義されているが、この行は編集しない (ことを勧める)
  - この `body` の値は、`publsh.py` を実行した場所から記事の本文のデータがあるファイルへのパス
  - このパスにしたがって、記事の本文を取得しにいく

## 挿入時のルール

`publish.py` の次の 2 つの変数の値で、比較時に記事のどこを見るかざっくりコントロールする

- `INSERT_SORT_KEY_PATTERN`
- `INSERT_SORT_KEY_CONVERT`

それぞれの変数の値がもつ意味は次の通り

- `INSERT_SORT_KEY_PATTERN`:
  - 挿入するときにどこの値どうしを比較するか、を正規表現で記述する
  - たとえば、`<dt><span>(.+?)</span></dt>` は、次の A と n 個の B_i をみて比較することを指定している
    - 「これから挿入する記事」の `<dt><span>A</span></dt>`
    - 挿入前の `index.html` の n 個の `<dt><span>B_i</span></dt>` (`1 ≦ i ≦ n`)
  - `A ≧ B_k (1 ≦ k ≦ n)` が成立した行を先頭に、「これから挿入する記事」を挿入する
  - この値を変えることで、挿入時にどこの値どうしを比較するか、を変えることができる
- `INSERT_SORT_KEY_CONVERT`
  - 値の型変換をおこなう関数を定義する
  - HTML は文字列なため、`INSERT_SORT_KEY_PATTERN` にマッチした値 A, B_i を比較するときに、必然的に文字列どうしの比較になる
  - たとえば、整数どうしの比較をしたいときや、日付どうしの比較をしたいときがくるかもしれない
    - 現に日付どうしの比較によって挿入箇所を決定している
    - (適切に 0 埋めされた日付どうしなら比較できるけど、日付の値が必ずしも 0 埋めされているとは限らない)
      - これからは見栄えの観点からも 0 埋めしてほしいけど...
  - そこで、意図した比較ができるように、`INSERT_SORT_KEY_CONVERT` に定義する関数で、適切な型に変換できるようにしている
    - たとえば、`lambda x: date(*map(int, x.split("-")))` は 0 埋めされていない日付も含めて date 型に変換するようにしている
  - 単純に文字列どうしの比較をしたい場合は `lambda x: x` にすればよい

他にも `publish.py` 内で大文字とアンダーバー (コンスタントケース) で定義されている変数の値を変更することで処理を柔軟にカスタマイズできる(はず)  
ただ、カスタマイズしたい場合は `publish.py` を直接編集するのではなく、
1. 新しく py ファイルを作る
2. `publish.py` をインポートする
3. `publish` モジュールの `INSERT_SORT_KEY_PATTERN` などを変更する
4. `publish` モジュールの main 関数を呼び出す

という流れがよい(と思う)

## テンプレートの編集例

次のように `.draft/.newstemplate` と `.draft/conf.json` を編集することで、2 枚の写真を横並びに表示することができる

`.draft/.newstemplate`
```
            <dt><span>${date}</span></dt>
            <details id="${date}">
              <summary>
                  <strong>${title}</strong>
              </summary>
              <dd>
                <div>
                  <p>
                    ${body}
                  </p>
                  <table style="table-layout: fixed; width: auto; border: none;">
                    <tr>
                      <td style="border: none;"><img src="${image_path}" style="width: 100%;"></td>
                      <td style="border: none;"><img src="${image_path_2}" style="width: 100%;"></td>
                    </tr>
                    <tr>
                      <td style="border: none;"><a href="${link}" style="width: 100%;">${link_name}</a></td>
                    </tr>
                  </table>
                </div>
              </dd>
            </details>
```

`./draft/conf.json`
```
{
  "date": "2022-06-15",
  "title": "📝日本電気(株)の宇都田賢一氏による研究室訪問(2022/06/15)",
  "body": ".draft/.body",
  "image_path": "./images/2022/nec-coming-00.png",
  "image_path_2": "./images/2022/2022-情報処理学会 第84回全国大会.png",
  "link": "https://jpn.nec.com/",
  "link_name": "日本電気(株)"
}
```

## 予告?

必要性を感じたら、`.draft/conf.json` で定義するキーのなかで、`body_1` のような形式のものは、いまの `body` と同じ挙動をするように更新する
