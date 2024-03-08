1. James Madison
2. James Monroe
3. John Quincy Adams

---

1. James Madison
    - a
    - b
    - c
2. James Monroe
3. John Quincy Adams

```
cd /
mkdir PostgreSQL
cd PostgreSQL
mkdir server_01
mkdir server_02
mkdir server_03
mkdir server_04
dir
```

# PostgreSQL基本機能の学習
今までの開発はORMでCRUD処理を書いてたのでSQLやDBの機能エアプでした。  
回転寿司の座席案内->注文->退店を例にシステムを作成します。

## 目次
1. システム構成
    - 1-1. 構成図
    - 1-2. ER図
2. 環境構築
    - 2-1. 環境変数の設定
    - 2-2. クラスタの作成
    - 2-3. postgresql.confの設定
    - 2-4. サービスの起動
3. DBオブジェクト
    - 3-1. 基本操作
    - 3-2. 本社DBの作成
    - 3-3. 豊田高岡店DBの作成
    - 3-4. 豊田朝日店DBの作成
    - 3-5. 座席案内スクリプトの作成
    - 3-6. 注文スクリプトの作成
    - 3-7. 会計スクリプトの作成
4. レプリケーション
    - 4-1. Publicationの設定
    - 4-2. Subsuclictionの設定
5. CRUD処理
    - 5-1. SELECT
    - 5-2. INSERT
    - 5-3. UPDATE
    - 5-4. DELETE
6. バックアップと修復
    - 6-1. dump
    - 6-2. restore
7. パフォーマンス
    - 7-1. INDEX

## 1. システム構成

### 1-1. 構成図

### 1-2. ER図

## 2. 環境構築

### 2-1. 環境変数の設定
psqlコマンドのパスを通します。

#### win+r key -> sysdm.cpl -> OK

<img src="img\2024-03-08 093211.png">

#### 詳細設定 -> 環境変数　

<img src="img\2024-03-08 093840.png">

#### システム環境変数 -> Path -> 編集

<img src="img\2024-03-08 094225.png">

#### 新規 -> {"psql.exe"保存先のパス} -> OK

<img src="img\2024-03-08 094543.png">

#### バージョン確認コマンド実行 -> パスが通ることを確認

```
psql -V
```

<img src="img\2024-03-08 095048.png">

### 2-2. クラスタの作成
1台のPCで複数のPostgreSQLサービスを稼働させます。

#### クラスタ用のディレクトリを作成

```
cd /
mkdir PostgreSQL
cd PostgreSQL
mkdir server_01
mkdir server_02
mkdir server_03
mkdir server_04
dir
```

<img src="img\2024-03-08 085815.png">

#### クラスタを作成

```
initdb -U postgres -D C:\PostgreSQL\server_01
initdb -U postgres -D C:\PostgreSQL\server_02
initdb -U postgres -D C:\PostgreSQL\server_03
initdb -U postgres -D C:\PostgreSQL\server_04
```

<img src="img\2024-03-08 101140.png">

### 2-3. postgresql.confの設定
各クラスタのconfファイルを編集します

- C:\Program Files\PostgreSQL\13\data\postgresql.con\postgresql.conf
    - port = 5432
    - shared_preload_libraries = 'postgres_fdw'
- C:\PostgreSQL\server_01\postgresql.conf
    - port = 5433
    - shared_preload_libraries = 'postgres_fdw'
    - wal_level = logical
- C:\PostgreSQL\server_02\postgresql.conf
    - port = 5434
    - shared_preload_libraries = 'postgres_fdw'
- C:\PostgreSQL\server_03\postgresql.conf
    - port = 5435
    - shared_preload_libraries = 'postgres_fdw'
    - wal_level = logical
- C:\PostgreSQL\server_04\postgresql.conf
    - port = 5436
    - shared_preload_libraries = 'postgres_fdw'

#### ポート番号を設定

```
port = 5433
```

<img src="img\2024-03-08 101731.png">

#### FDWを有効にする

```
shared_preload_libraries = 'postgres_fdw'
```

<img src="img\2024-03-08 110013.png">

#### レプリケーションを有効にする

```
wal_level = logical
```

<img src="img\2024-03-08 151752.png">

### 2-4. サービスの起動
confファイルを変更したのでシステムを再起動します

#### win+r key -> services.msc -> OK

<img src="img\2024-03-08 120656.png">

#### postgresを再起動します

<img src="img\2024-03-08 120845.png">

#### クラスタのサービスを起動させます

```
pg_ctl -D C:\PostgreSQL\server_01 -l C:\PostgreSQL\server_01\server_01.log start
pg_ctl -D C:\PostgreSQL\server_02 -l C:\PostgreSQL\server_02\server_02.log start
pg_ctl -D C:\PostgreSQL\server_03 -l C:\PostgreSQL\server_03\server_03.log start
pg_ctl -D C:\PostgreSQL\server_04 -l C:\PostgreSQL\server_04\server_04.log start
```

<img src="img\2024-03-08 102656.png">

#### サービスが起動していることを確認

```
netstat -ano -o | find "5433"
netstat -ano -o | find "5434"
netstat -ano -o | find "5435"
netstat -ano -o | find "5436"
```

<img src="img\2024-03-08 102803.png">

## 3. DBオブジェクトの作成

本店DBサーバにアクセス
```
psql -h localhost -p 5432 -U postgres
```
本店のDBを作成
```
create database headquarters;
```

DB接続
```
\c headquarters
```

はま寿司本部の管理部門スキーマを作成
```
create schema management_system;
```

はま寿司本部が管理するメニューのテーブルを作成
```
create table management_system.menus(
    menu_id uuid not null default gen_random_uuid(),
    menu_classification varchar not null,
    menu_name varchar not null,
    menu_price integer not null,
    sale_flg boolean not null,
    primary key (menu_id)
);
```
メニュー情報をINSERT
```
insert into management_system.menus (menu_classification, menu_name, menu_price, sale_flg) values
('LIMITED MENU', 'みなみまぐろ中とろ', 100, true),
('LIMITED MENU', '広島県産牡蠣のカキフライつつみ（お好みソース）', 100, true),
('LIMITED MENU', 'まとうだいの天ぷら握り', 150, true),
('LIMITED MENU', '宮城県金華いわし', 150, true),
('LIMITED MENU', '一本穴子', 480, false),
('LIMITED MENU', '濃厚北海道味噌ラーメン', 380, true),
('NIGIRI', 'まぐろ', 100, true),
('NIGIRI', 'サーモン', 100, true),
('NIGIRI', '活〆ぶり(四国・九州産)', 120, true),
('ZEITAKU SANSYU', '真あじ', 150, true),
('SHIFUKU NO IKKAN', '富士山盛りサーモン軍艦', 290, true),
('SHIFUKU NO IKKAN', '富士山盛りまぐろ軍艦', 290, true),
('SHIFUKU NO IKKAN', '富士山盛りまかない軍艦', 290, true),
('SIDE MENU', 'あおさみそ汁', 100, true),
('SIDE MENU', '特製とん汁', 200, true),
('DESERT DRINK', 'フランス直輸入濃厚ガトーショコラ', 200, true),
('DESERT DRINK', '波照間黒糖のわらびもち', 100, true);
```
全ての商品を表示
```
select * from management_system.menus;
```
<img src="img\2024-03-08 104133.png">
支払方法テーブル作成

```
create table management_system.payment_methods (
    method_id SERIAL not null,
    method_name varchar not null,
    primary key (method_id)
);
```
対応可能な支払方法
```
INSERT INTO management_system.payment_methods (method_name) VALUES 
('現金'),
('クレジットカード'),
('楽天ペイ');
```

取り扱い支払方法一覧
```
select * from management_system.payment_methods;
```
<img src="img\2024-03-08 104616.png">

### FDW

FDWで外部DBのテーブルを参照します

高岡店のDBサーバにアクセス
```
psql -h localhost -p 5433 -U postgres
```
豊田高岡店のDBを作成
```
create database store_4316;
```

DB接続
```
\c store_4316
```

注文スキーマ作成
```
create schema order_system;
```

postgres_fdw拡張機能を有効
```
CREATE EXTENSION postgres_fdw;
```

外部データベースに接続するためのサーバーを作成
```
CREATE SERVER headquarters_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host '127.0.0.1', port '5432', dbname 'headquarters');
```

外部データベースへのユーザーマッピングを作成
```
CREATE USER MAPPING FOR postgres
SERVER headquarters_server
OPTIONS (user 'postgres', password 'hoge');
```

外部テーブルを作成
```
create foreign table order_system.menus(
    menu_id uuid,
    menu_classification varchar,
    menu_name varchar,
    menu_price integer,
    sale_flg boolean
)
SERVER headquarters_server
OPTIONS (schema_name 'management_system', table_name 'menus');
```

全ての商品を表示
```
select * from order_system.menus;
```

支払方法を参照
```
CREATE FOREIGN TABLE order_system.payment_methods (
    method_id bigserial not null,
    method_name varchar not null
)
SERVER headquarters_server
OPTIONS (schema_name 'management_system', table_name 'payment_methods');
```

全ての支払方法を表示
select * from order_system.payment_methods;

### テーブル
支店の座席
```
create table order_system.seats(
    seat_id integer not null,
    vacant_seat_flg boolean not null default true,
    number_of_people integer not null default 0,
    number_of_seats integer not null,
    primary key (seat_id)
);
```

支店の顧客
```
create table order_system.customers(
    customer_id uuid not null default gen_random_uuid(),
    entry_time timestamp not null DEFAULT CURRENT_TIMESTAMP,
    number_of_people integer not null,
    seat_id integer not null,
    exit_time timestamp,
    payment_price integer,
    payment_method integer,
    check_time timestamp,
    primary key (customer_id)
);
```

### パーテション
支店の注文
```
create table order_system.orders(
    order_time timestamp not null default CURRENT_TIMESTAMP,
    customer_id uuid not null,
    menu_id uuid not null,
    menu_price integer not null,
    number_of_orders integer not null,
    seat_id integer not null,
    distributed_flg boolean not null default false,
    received_flg boolean not null default false,
    foreign key (customer_id) references order_system.customers(customer_id),
    check (number_of_orders >= 1 AND number_of_orders <= 4)
)
PARTITION BY RANGE (order_time);
```

```
/* 支店の注文ひと月ごとのパーテション */
CREATE TABLE order_system.orders_partition_2024_02
PARTITION OF order_system.orders
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

### インデックス
```
CREATE INDEX idx_customer_id ON order_system.orders(customer_id);
```

### トリガ関数
顧客テーブルに顧客IDと座席IDをINSERT
```
CREATE OR REPLACE FUNCTION order_system.welcome_func()
RETURNS TRIGGER AS $$
DECLARE
    arg1 INT;
    arg2 INT;
BEGIN
    arg1 := NEW.number_of_people; 
    arg2 := NEW.seat_id; 

    insert into order_system.customers (number_of_people, seat_id) values (arg1, arg2);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

選択した座席をFALSE
```
CREATE TRIGGER welcome_trig
AFTER UPDATE OF vacant_seat_flg ON order_system.seats
FOR EACH ROW
WHEN (OLD.vacant_seat_flg = true AND NEW.vacant_seat_flg = false)
EXECUTE FUNCTION order_system.welcome_func();
```

座席情報をINSERT
```
insert into order_system.seats (seat_id, number_of_seats) values
(1, 1),
(2, 1),
(3, 1),
(4, 1),
(5, 1),
(6, 1),
(7, 1),
(8, 1),
(9, 1),
(10, 1),
(11, 1),
(12, 1);
```

座席情報
```
select * from order_system.seats
ORDER BY seat_id ASC;
```

顧客情報
```
select * from order_system.customers
ORDER BY customer_id ASC;
```

座席と人数を変更
```
update order_system.seats
SET vacant_seat_flg = false,
number_of_people = 2
where seat_id = 3;
```

顧客IDから座席番号を取得
```
CREATE OR REPLACE FUNCTION order_system.get_seat_number(customer_id_in UUID)
RETURNS INTEGER AS $$
DECLARE
    seat_number INTEGER;
BEGIN
    SELECT seat_id INTO seat_number FROM order_system.customers WHERE customer_id = customer_id_in;
    RETURN seat_number;
END;
$$ LANGUAGE plpgsql;
```

商品IDから金額を取得
```
CREATE OR REPLACE FUNCTION order_system.get_menu_price(menu_id_in uuid)
RETURNS INTEGER AS $$
DECLARE
    menu_price_out INTEGER;
BEGIN
    SELECT menu_price INTO menu_price_out FROM order_system.menus WHERE menu_id = menu_id_in;
    RETURN menu_price_out;
END;
$$ LANGUAGE plpgsql;
```

注文情報
```
select * from order_system.orders
ORDER BY seat_id ASC;
```

商品情報
```
select * from order_system.menus
```

商品注文
```
insert into order_system.orders (customer_id, menu_id, number_of_orders, seat_id) values
('51a40a00-eb7e-46c7-b349-6672eaba9923', 'f986ccbb-0893-422d-8100-b095b040d7e2', 2, order_system.get_seat_number('51a40a00-eb7e-46c7-b349-6672eaba9923'));
```

{顧客ID}の注文金額合計
```
SELECT SUM(o.number_of_orders * m.menu_price) AS total_order_amount
FROM order_system.orders o
JOIN order_system.menus m ON o.menu_id = m.menu_id
WHERE o.customer_id = '51a40a00-eb7e-46c7-b349-6672eaba9923';
```

会計ボタン押す→exit_time→orderテーブルの注文金額合計をcustomerテーブルのpayment_priceに
```
CREATE OR REPLACE FUNCTION order_system.please_check_func()
RETURNS TRIGGER AS $$
BEGIN
    -- 指定されたcustomer_idに関連する注文の合計金額を計算
    SELECT SUM(o.number_of_orders * m.menu_price) INTO NEW.payment_price
    FROM order_system.orders o
    JOIN order_system.menus m ON o.menu_id = m.menu_id
    WHERE o.customer_id = NEW.customer_id;

    -- 新しい合計金額をorder_system.customersテーブルのpayment_price列に設定
    UPDATE order_system.customers
    SET payment_price = NEW.payment_price
    WHERE customer_id = NEW.customer_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

```
CREATE TRIGGER please_check_trig
AFTER UPDATE OF exit_time ON order_system.customers
FOR EACH ROW
WHEN (OLD.exit_time IS NULL AND NEW.exit_time IS NOT NULL) -- exit_timeが更新されたかどうかを確認
EXECUTE FUNCTION order_system.please_check_func();
```

会計ボタン押す→exit_time
```
UPDATE order_system.customers
SET exit_time = CURRENT_TIMESTAMP
WHERE customer_id = '51a40a00-eb7e-46c7-b349-6672eaba9923';
```

レジでの支払
```
UPDATE order_system.customers
SET check_time = CURRENT_TIMESTAMP,
payment_method = 3
WHERE customer_id = '51a40a00-eb7e-46c7-b349-6672eaba9923';
```

### VIEW
```
create view user_list as select user_id, user_name from table_a;
```

```
select * from user_list;
```

```
create view user_level_avg as select avg(user_level) from table_a;
```

```
select * from user_level_avg;
```

```
select avg(user_level) from table_a;
```

```
select max(user_level), min(user_level) from table_a; 
```

### プロシージャ
```
create table items(
    user_id uuid not null,
    item_name varchar not null,
    item_level integer not null,
    foreign key (user_id) references table_a(user_id)
);
```

```
CREATE PROCEDURE add_item(user_id uuid, item_name varchar, item_level integer)
LANGUAGE SQL
AS $$
INSERT INTO items VALUES (user_id, item_name, item_level);
$$;
```

```
CALL add_item('9c398f32-e088-4b0a-bf6e-b4a623b516ed', '肉まん', 14);
```

```
select * from items;
```

## 4. ロジカルレプリケーション

### Publication側の設定
postgresql.conf
```
wal_level = logical
```

<img src="img\2024-03-08 151752.png">

パブリケーション作成時にレプリケーション対象テーブル
```
CREATE PUBLICATION my_publication FOR ALL TABLES;
```

レプリケーション対象テーブルの確認
```
SELECT * FROM pg_publication_tables;
```

レプリケーション対象操作の確認
```
SELECT * FROM pg_publication;
```

### Subsucliction側の設定

```
create database store_4316_replica
```

```
\d store_4316_replica
```

```
create schema order_system;
```

```
create table order_system.seats(
    seat_id integer not null,
    vacant_seat_flg boolean not null default true,
    number_of_people integer not null default 0,
    number_of_seats integer not null,
    primary key (seat_id)
);
```

サブスクリプション作成時にパブリッシャーへの接続情報とパブリケーションを指定
```
CREATE SUBSCRIPTION my_subscriction CONNECTION 'host=localhost port=5433 user=postgres dbname=store_4316 password=hoge' PUBLICATION my_publication;
```

```
```












## 5. CRUD処理

### SELECT

### INSERT

### UPDATE

### DELETE

## 6. バックアップと修復

### dump

### restore


