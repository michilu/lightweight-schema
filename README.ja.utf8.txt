紹介

jsonschema はJSON文書がJSON Schema文書構造に従ってるかどうかを検証する
ライブラリです。JSON Schema Proposal Second Draftを仕様として基にされています。
JSON Schema Proposal Second Draft は以下のURLで参照することができます。

http://groups.google.com/group/json-schema/web/json-schema-proposal---second-draft

インストール

jsonschemaはsetuptoolsを使っていますので、adminユーザとして、以下のコマンドで
簡単にインストールすることが出来ます。

python setup.py install

そして、テストを行う場合は以下のコマンドで出来ます。

python setup.py test

使い方

JSON文書とSchema文書は検証する前にJSON解析ツールでPythonの
Dictオブジェクトに解析しないといけません。自分が好きな解析ツールを使っても
かまいませんが、例では、simplejsonを使います。

簡単なJSON文書を解析

>>> import jsonschema
>>> jsonschema.validate("simplejson", {"type":"string"})

より複雑なJSON文書を解析

>>> import simplejson
>>> import jsonschema
>>> 
>>> data = simplejson.loads('["foo", {"bar":["baz", null, 1.0, 2]}]')
>>> schema = {
...   "type":"array", 
...   "items":[
...     {"type":"string"},
...     {"type":"object",
...      "properties":{
...        "bar":{
...          "items":[
...            {"type":"string"},
...            {"type":"any"},
...            {"type":"number"},
...            {"type":"integer"}
...          ]
...        }
...      }
...    }
...   ]
... }
>>> jsonschema.validate(data,schema)

検証エラーを処理

検証エラーが発生する際に、ValueErrorと言う例外を上げる。

>>> import jsonschema
>>> try:
...     jsonschema.validate("simplejson", {"type":"string","minLength":15})
... except ValueError, e:
...     print e.message
... 
Length of 'simplejson' must be more than 15.000000

jsonschemaを拡張

simplejsonみたいにjsonschemaは拡張できるAPIが提供されています。
JSONSchemaValidatorと言うクラスを拡張すれば、JSON Schema プロパティや、
データ形式を追加することができます。examplesにある例を見てください。



スキーマレファレンスは対応されていません。
uniqueと言うプロパティは対応されていません。
