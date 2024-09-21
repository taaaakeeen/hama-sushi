# PostgreSQL基本機能の学習  
回転寿司の座席案内->商品注文->会計システムを作成を通じてDBを学習します

## 目次
1. システム構成
    - 1-1. 構成図
    - 1-2. ER図
2. 環境構築
    - 2-1. 環境変数の設定
    - 2-2. クラスタの作成
    - 2-3. postgresql.confの設定
    - 2-4. サービスの起動
3. DB作成
    - 3-1. 本社DBの作成
        - 3-1-1. テーブルの作成
    - 3-2. 豊田高岡店DBの作成
        - 3-2-1. テーブルの作成
        - 3-2-2. 座席案内スクリプトの作成
        - 3-2-3. 注文スクリプトの作成
        - 3-2-4. 会計スクリプトの作成
    - 3-3. 豊田高岡店DBのレプリケーション設定
        - 3-3-1. Publication設定
        - 3-3-2. Subsucliction設定
    - 3-4. 豊田朝日店DBの作成
        - 3-4-1. テーブルの作成
        - 3-4-2. 座席案内スクリプトの作成
        - 3-4-3. 注文スクリプトの作成
        - 3-4-4. 会計スクリプトの作成
    - 3-5. 豊田朝日店DBのレプリケーション設定
        - 3-5-1. Publication設定
        - 3-5-2. Subsucliction設定
4. バックアップと修復
    - 4-1. dump
    - 4-2. restore
5. CRUD処理
    - 5-1. SELECT
    - 5-2. INSERT
    - 5-3. UPDATE
    - 5-4. DELETE
6. 実行計画
    - 6-1. 実行速度
    - 6-2. INDEX

## 1. システム構成

### 1-1. 構成図

1. 本社と支店のDB

<img src="data/images/2024-03-17 185623.png">

2. 支店は本社が管理するメニューと支払方法を使用します

<img src="data/images/2024-03-17 185713.png">

3. 支店はreplica DBを故障時のバックアップと本社からの参照用として運用します

<img src="data/images/2024-03-17 185733.png">

4. 本社は各支店のreplica DBを参照して売上データの解析に使用します

<img src="data/images/2024-03-17 185718.png">

### 1-2. ER図

1. 本社

<img src="data/images/2024-03-17 192501.png">

2. 支店

<img src="data/images/2024-03-17 192539.png">

- menues 商品テーブル
    - menu_id 商品ID
    - menu_classification 商品カテゴリ
    - menu_name 商品名
    - menu_price 商品価格
    - sale_flg 期間限定商品

- paypent_methods 支払方法テーブル
    - payment_method_id 支払方法ID
    - payment_method_name 支払方法

- seats 座席テーブル
    - seat_id 座席ID
    - vacant_seat_flg 空席フラグ
    - number_of_people 顧客人数
    - number_of_seats 座席数

- customers 顧客テーブル
    - customer_id 顧客ID
    - entry_time 入店日時
    - number_of_people 
    - seat_id 座席ID
    - exit_time 退店日時
    - payment_price 支払金額
    - payment_method 支払方法
    - check_time 支払日時

- orders 注文テーブル
    - order_time 注文日時
    - customer_id 顧客ID
    - menu_id 商品ID
    - menu_price 商品価格
    - number_of_orders 注文数量
    - seat_id 座席ID
    - distributed_flg 注文中フラグ
    - received_flg 提供済フラグ

## 2. 環境構築

### 2-1. 環境変数の設定
psqlコマンドのパスを通します

1. win+r key -> sysdm.cpl -> OK

<img src="data/images/2024-03-08 093211.png">

2. 詳細設定 -> 環境変数

<img src="data/images/2024-03-08 093840.png">

3. システム環境変数 -> Path -> 編集

<img src="data/images/2024-03-08 094225.png">

4. 新規 -> {psql.exe保存先のパス} -> OK

<img src="data/images/2024-03-08 094543.png">

5. バージョン確認コマンド実行 -> パスが通ることを確認

```
psql -V
```

<img src="data/images/2024-03-08 095048.png">

### 2-2. クラスタの作成
PC1台で複数のPostgreSQLサービスを稼働させます

1. クラスタ用のディレクトリを作成

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

<img src="data/images/2024-03-08 085815.png">

2. クラスタを作成

```
initdb -U postgres -D C:\PostgreSQL\server_01
initdb -U postgres -D C:\PostgreSQL\server_02
initdb -U postgres -D C:\PostgreSQL\server_03
initdb -U postgres -D C:\PostgreSQL\server_04
```

<img src="data/images/2024-03-08 101140.png">

### 2-3. postgresql.confの設定
各クラスタのconfファイルを編集します

- C:\Program Files\PostgreSQL\13\data\postgresql.conf
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

1. ポート番号を設定

```
port = 5433
```

<img src="data/images/2024-03-08 101731.png">

2. FDWを有効にする

```
shared_preload_libraries = 'postgres_fdw'
```

<img src="data/images/2024-03-08 110013.png">

3. レプリケーションを有効にする

```
wal_level = logical
```

<img src="data/images/2024-03-08 151752.png">

### 2-4. サービスの起動
confファイルを変更したのでシステムを再起動します

1. win+r key -> services.msc -> OK

<img src="data/images/2024-03-08 120656.png">

2. postgresを再起動します

<img src="data/images/2024-03-08 120845.png">

3. クラスタのサービスを起動します

```
pg_ctl -D C:\PostgreSQL\server_01 -l C:\PostgreSQL\server_01\server_01.log start
pg_ctl -D C:\PostgreSQL\server_02 -l C:\PostgreSQL\server_02\server_02.log start
pg_ctl -D C:\PostgreSQL\server_03 -l C:\PostgreSQL\server_03\server_03.log start
pg_ctl -D C:\PostgreSQL\server_04 -l C:\PostgreSQL\server_04\server_04.log start
```

<img src="data/images/2024-03-08 102656.png">

4. サービスが起動していることを確認

```
netstat -ano -o | find "5433"
netstat -ano -o | find "5434"
netstat -ano -o | find "5435"
netstat -ano -o | find "5436"
```

<img src="data/images/2024-03-08 102803.png">

## 3. DB作成

### 3-1. 本社DBの作成

<img src="data/images/2024-03-17 185639.png">

#### 3-1-1. テーブルの作成

1. 本社DBサーバにアクセス

```
psql -h localhost -p 5432 -U postgres
```

2. 本社DBを作成

```
create database headquarters;
```

3. DB接続

```
\c headquarters
```

4. 本社の管理部門スキーマを作成

```
create schema management_system;
```

5. 商品テーブルを作成

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

6. 商品情報をINSERT

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

7. 全ての商品を確認

```
select * from management_system.menus;
```

<img src="data/images/2024-03-08 104133.png">

8. 支払方法テーブルを作成

```
create table management_system.payment_methods (
    payment_method_id SERIAL not null,
    payment_method_name varchar not null,
    primary key (payment_method_id)
);
```

9. 対応可能な支払方法をINSERT

```
INSERT INTO management_system.payment_methods (payment_method_name) VALUES 
('現金'),
('クレジットカード'),
('楽天ペイ');
```

10. 対応可能な支払方法を確認

```
select * from management_system.payment_methods;
```

<img src="data/images/2024-03-08 104616.png">

### 3-2. 豊田高岡店DBの作成

<img src="data/images/2024-03-17 185656.png">

#### 3-2-1. テーブルの作成

1. 高岡店のDBサーバにアクセス

```
psql -h localhost -p 5433 -U postgres
```

2. 高岡店のDBを作成

```
create database store_4316;
```

3. DB接続

```
\c store_4316
```

4. 注文スキーマ作成

```
create schema order_system;
```

5. postgres_fdw拡張機能を有効

```
CREATE EXTENSION postgres_fdw;
```

6. 外部DB接続用のサーバーを作成

```
CREATE SERVER headquarters_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host '127.0.0.1', port '5432', dbname 'headquarters');
```

7. 外部DBのマッピングを作成

```
CREATE USER MAPPING FOR postgres
SERVER headquarters_server
OPTIONS (user 'postgres', password 'hoge');
```

8. 外部DBの商品テーブルを参照するテーブルを作成します

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

> [!TIP]
> テーブル毎に参照対象設定するのではなくスキーマ全体を参照対象にすることも可能です
> ```
> IMPORT FOREIGN SCHEMA management_system
> FROM SERVER headquarters_server
> INTO order_system;
> ```

9. 全ての商品を確認

```
select * from order_system.menus;
```

10. 外部DBを参照する支払方法テーブルを作成

```
CREATE FOREIGN TABLE order_system.payment_methods (
    payment_method_id bigserial not null,
    payment_method_name varchar not null
)
SERVER headquarters_server
OPTIONS (schema_name 'management_system', table_name 'payment_methods');
```

11. 全ての支払方法を確認

```
select * from order_system.payment_methods;
```

12. 支店の座席テーブルを作成

```
create table order_system.seats(
    seat_id integer not null,
    vacant_seat_flg boolean not null default true,
    number_of_people integer not null default 0,
    number_of_seats integer not null,
    primary key (seat_id)
);
```

13. 支店の座席情報をINSERT

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
(10, 6),
(11, 6),
(12, 6);
```

14. 座席情報を確認

```
select * from order_system.seats
ORDER BY seat_id ASC;
```

15. 支店の顧客テーブルを作成

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
    primary key (customer_id),
    foreign key (seat_id) references order_system.seats(seat_id)
);
```

16. 支店の注文テーブルを作成

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
    foreign key (seat_id) references order_system.seats(seat_id),
    check (number_of_orders >= 1 AND number_of_orders <= 4)
)
PARTITION BY RANGE (order_time);
```

17. 支店の注文ひと月ごとのパーテションを作成

```
CREATE TABLE order_system.orders_partition_2024_03
PARTITION OF order_system.orders
FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');
```

#### 3-2-2. 座席案内スクリプトの作成

<img src="data/images/2024-03-17 192617.png">

1. 顧客テーブルに顧客IDと座席IDをINSERTするトリガ関数

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

2. 空席フラグがtrueからfalseになると発動するトリガ

```
CREATE TRIGGER welcome_trig
AFTER UPDATE OF vacant_seat_flg ON order_system.seats
FOR EACH ROW
WHEN (OLD.vacant_seat_flg = true AND NEW.vacant_seat_flg = false)
EXECUTE FUNCTION order_system.welcome_func();
```

3. 座席案内AppがseatsテーブルをUPDATE

```
update order_system.seats
SET vacant_seat_flg = false,
number_of_people = 4
where seat_id = 10;
```

4. 座席の状態を確認

```
select * from order_system.seats
ORDER BY seat_id ASC;
```

5. 顧客テーブルを確認
```
select * from order_system.customers
ORDER BY entry_time ASC;
```

#### 3-2-3. 注文スクリプトの作成

<img src="data/images/2024-03-17 192603.png">

1. 顧客IDから座席番号を取得する関数

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

2. 商品IDから金額を取得する関数

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

3. 注文可能な商品一覧

```
select * from order_system.menus
where sale_flg = true;
```

4. 商品注文Appで注文

```
insert into order_system.orders (customer_id, menu_id, menu_price, number_of_orders, seat_id) values(
    '{customer_id}',
    '{menu_id}',
    order_system.get_menu_price('{menu_id}'),
    2,
    order_system.get_seat_number('{customer_id}')
);
```

5. 注文状況を確認

```
select * from order_system.orders
ORDER BY seat_id ASC;
```

#### 3-2-4. 会計スクリプトの作成

<img src="data/images/2024-03-17 192609.png">

1. 注文金額合計を確認

```
SELECT SUM(o.number_of_orders * m.menu_price) AS total_order_amount
FROM order_system.orders o
JOIN order_system.menus m ON o.menu_id = m.menu_id
WHERE o.customer_id = '{customer_id}';
```

2. 注文金額を合計して顧客テーブルのpayment_priceをUPDATEするトリガ関数

```
CREATE OR REPLACE FUNCTION order_system.please_check_func()
RETURNS TRIGGER AS $$
BEGIN
    -- customer_idに関連する注文の合計金額を計算
    SELECT SUM(o.number_of_orders * m.menu_price) INTO NEW.payment_price
    FROM order_system.orders o
    JOIN order_system.menus m ON o.menu_id = m.menu_id
    WHERE o.customer_id = NEW.customer_id;

    -- 合計金額をorder_system.customersテーブルのpayment_price列に設定
    UPDATE order_system.customers
    SET payment_price = NEW.payment_price
    WHERE customer_id = NEW.customer_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

3. 顧客テーブルの退店時間がnullから更新されると発動するトリガ

```
CREATE TRIGGER please_check_trig
AFTER UPDATE OF exit_time ON order_system.customers
FOR EACH ROW
WHEN (OLD.exit_time IS NULL AND NEW.exit_time IS NOT NULL)
EXECUTE FUNCTION order_system.please_check_func();
```

4. 商品注文Appで会計ボタン押す

```
UPDATE order_system.customers
SET exit_time = CURRENT_TIMESTAMP
WHERE customer_id = '{customer_id}';
```

5. 顧客テーブルを確認

```
select * from order_system.customers
WHERE customer_id = '{customer_id}';
```

6. 楽天ペイで決済

```
UPDATE order_system.customers
SET check_time = CURRENT_TIMESTAMP,
payment_method = 3
WHERE customer_id = '{customer_id}';
```

### 3-3 豊田高岡店DBのレプリケーション設定

#### 3-3-1 Publication設定

1. パブリッシャ側のDBに接続

```
psql -h 127.0.0.1 -p 5433 -U postgres -d store_4316
```

2. レプリケーション対象テーブルと適用範囲を指定してパブリケーション作成

```
CREATE PUBLICATION publication_all_tbl FOR ALL TABLES;
```

3. レプリケーション対象テーブルの確認

```
SELECT * FROM pg_publication_tables;
```

4. レプリケーション対象操作の確認

```
SELECT * FROM pg_publication;
```

#### 3-3-2. Subsucliction設定

1. サブスクライバ側のDBに接続

```
psql -h 127.0.0.1 -p 5434 -U postgres
```

2. レプリケーション用のデータベース作成

```
create database store_4316_replica;
```

3. レプリケーション用のデータベースに接続

```
\c store_4316_replica
```

4. レプリケーション用のスキーマ作成

```
create schema order_system;
```

5. postgres_fdw拡張機能を有効

```
CREATE EXTENSION postgres_fdw;
```

6. 外部DB接続用のサーバーを作成

```
CREATE SERVER headquarters_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host '127.0.0.1', port '5432', dbname 'headquarters');
```

7. 外部DBのマッピングを作成

```
CREATE USER MAPPING FOR postgres
SERVER headquarters_server
OPTIONS (user 'postgres', password 'hoge');
```

8. 外部DBを参照する商品テーブルを作成

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

9. 外部DBを参照する支払方法テーブルを作成

```
CREATE FOREIGN TABLE order_system.payment_methods (
    payment_method_id bigserial not null,
    payment_method_name varchar not null
)
SERVER headquarters_server
OPTIONS (schema_name 'management_system', table_name 'payment_methods');
```

10. 支店の座席テーブルを作成

```
create table order_system.seats(
    seat_id integer not null,
    vacant_seat_flg boolean not null default true,
    number_of_people integer not null default 0,
    number_of_seats integer not null,
    primary key (seat_id)
);
```

11. 支店の顧客テーブルを作成

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
    primary key (customer_id),
    foreign key (seat_id) references order_system.seats(seat_id)
);
```

12. 支店の注文テーブルを作成

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
    foreign key (seat_id) references order_system.seats(seat_id),
    check (number_of_orders >= 1 AND number_of_orders <= 4)
)
PARTITION BY RANGE (order_time);
```

13. 支店の注文ひと月ごとのパーテションを作成

```
CREATE TABLE order_system.orders_partition_2024_03
PARTITION OF order_system.orders
FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');
```

14. パブリッシャーへの接続情報とパブリケーションを指定してサブスクリプション作成

```
CREATE SUBSCRIPTION subscriction_all_tbl 
CONNECTION 'host=localhost port=5433 user=postgres dbname=store_4316 password=hoge' 
PUBLICATION publication_all_tbl;
```

15. 座席テーブルがパブリッシャ側の座席テーブルと同じ状態になっていることを確認

```
select * from order_system.seats;
```

### 3-4. 豊田朝日店DBの作成

高岡店とオブジェクトの構造は同じです

<img src="data/images/2024-03-17 185701.png">

#### 3-4-1. テーブルの作成

1. 朝日店のDBサーバにアクセス

```
psql -h localhost -p 5435 -U postgres
```

2. 朝日店のDBを作成

```
create database store_4123;
```

3. DB接続

```
\c store_4123
```

4. 注文スキーマ作成

```
create schema order_system;
```

5. postgres_fdw拡張機能を有効

```
CREATE EXTENSION postgres_fdw;
```

6. 外部DB接続用のサーバーを作成

```
CREATE SERVER headquarters_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host '127.0.0.1', port '5432', dbname 'headquarters');
```

7. 外部DBのマッピングを作成

```
CREATE USER MAPPING FOR postgres
SERVER headquarters_server
OPTIONS (user 'postgres', password 'hoge');
```

8. 外部DBを参照する商品テーブルを作成

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

9. 外部DBを参照する支払方法テーブルを作成

```
CREATE FOREIGN TABLE order_system.payment_methods (
    payment_method_id bigserial not null,
    payment_method_name varchar not null
)
SERVER headquarters_server
OPTIONS (schema_name 'management_system', table_name 'payment_methods');
```

10. 支店の座席テーブルを作成
```
create table order_system.seats(
    seat_id integer not null,
    vacant_seat_flg boolean not null default true,
    number_of_people integer not null default 0,
    number_of_seats integer not null,
    primary key (seat_id)
);
```

11. 支店の座席情報をINSERT

```
insert into order_system.seats (seat_id, number_of_seats) values
(1, 1),
(2, 1),
(3, 1),
(4, 1),
(5, 1),
(6, 1),
(7, 6),
(8, 6),
(9, 6),
(10, 6),
(11, 6),
(12, 6);
```

12. 支店の顧客テーブルを作成

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
    primary key (customer_id),
    foreign key (seat_id) references order_system.seats(seat_id)
);
```

13. 支店の注文テーブルを作成

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
    foreign key (seat_id) references order_system.seats(seat_id),
    check (number_of_orders >= 1 AND number_of_orders <= 4)
)
PARTITION BY RANGE (order_time);
```

14. 支店の注文ひと月ごとのパーテションを作成

```
CREATE TABLE order_system.orders_partition_2024_03
PARTITION OF order_system.orders
FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');
```

#### 3-4-2. 座席案内スクリプトの作成

1. 顧客テーブルに顧客IDと座席IDをINSERTするトリガ関数

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

2. 空席フラグがtrueからfalseになると発動するトリガ

```
CREATE TRIGGER welcome_trig
AFTER UPDATE OF vacant_seat_flg ON order_system.seats
FOR EACH ROW
WHEN (OLD.vacant_seat_flg = true AND NEW.vacant_seat_flg = false)
EXECUTE FUNCTION order_system.welcome_func();
```

#### 3-4-3. 注文スクリプトの作成

1. 顧客IDから座席番号を取得する関数

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

2. 商品IDから金額を取得する関数

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

#### 3-4-4. 会計スクリプトの作成

1. 注文金額を合計して顧客テーブルのpayment_priceをUPDATEするトリガ関数

```
CREATE OR REPLACE FUNCTION order_system.please_check_func()
RETURNS TRIGGER AS $$
BEGIN
    -- customer_idに関連する注文の合計金額を計算
    SELECT SUM(o.number_of_orders * m.menu_price) INTO NEW.payment_price
    FROM order_system.orders o
    JOIN order_system.menus m ON o.menu_id = m.menu_id
    WHERE o.customer_id = NEW.customer_id;

    -- 合計金額をorder_system.customersテーブルのpayment_price列に設定
    UPDATE order_system.customers
    SET payment_price = NEW.payment_price
    WHERE customer_id = NEW.customer_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

2. 顧客テーブルの退店時間がnullから更新されると発動するトリガ

```
CREATE TRIGGER please_check_trig
AFTER UPDATE OF exit_time ON order_system.customers
FOR EACH ROW
WHEN (OLD.exit_time IS NULL AND NEW.exit_time IS NOT NULL)
EXECUTE FUNCTION order_system.please_check_func();
```

### 3-5. 豊田朝日店DBのレプリケーション設定

#### 3-5-1. Publication設定

1. パブリッシャ側のDBに接続

```
psql -h 127.0.0.1 -p 5435 -U postgres -d store_4123
```

2. レプリケーション対象テーブルと適用範囲を指定してパブリケーション作成

```
CREATE PUBLICATION publication_all_tbl FOR ALL TABLES;
```

3. レプリケーション対象テーブルの確認

```
SELECT * FROM pg_publication_tables;
```

4. レプリケーション対象操作の確認

```
SELECT * FROM pg_publication;
```

#### 3-5-2. Subsucliction設定

1. サブスクライバ側のDBに接続

```
psql -h 127.0.0.1 -p 5436 -U postgres
```

2. レプリケーション用のデータベース作成

```
create database store_4123_replica;
```

3. レプリケーション用のデータベースに接続

```
\c store_4123_replica
```

4. レプリケーション用のスキーマ作成

```
create schema order_system;
```

5. postgres_fdw拡張機能を有効

```
CREATE EXTENSION postgres_fdw;
```

6. 外部DB接続用のサーバーを作成

```
CREATE SERVER headquarters_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host '127.0.0.1', port '5432', dbname 'headquarters');
```

7. 外部DBのマッピングを作成

```
CREATE USER MAPPING FOR postgres
SERVER headquarters_server
OPTIONS (user 'postgres', password 'hoge');
```

8. 外部DBを参照する商品テーブルを作成

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

9. 外部DBを参照する支払方法テーブルを作成

```
CREATE FOREIGN TABLE order_system.payment_methods (
    payment_method_id bigserial not null,
    payment_method_name varchar not null
)
SERVER headquarters_server
OPTIONS (schema_name 'management_system', table_name 'payment_methods');
```

10. 支店の座席テーブルを作成

```
create table order_system.seats(
    seat_id integer not null,
    vacant_seat_flg boolean not null default true,
    number_of_people integer not null default 0,
    number_of_seats integer not null,
    primary key (seat_id)
);
```

11. 支店の顧客テーブルを作成

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
    primary key (customer_id),
    foreign key (seat_id) references order_system.seats(seat_id)
);
```

12. 支店の注文テーブルを作成

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
    foreign key (seat_id) references order_system.seats(seat_id),
    check (number_of_orders >= 1 AND number_of_orders <= 4)
)
PARTITION BY RANGE (order_time);
```

13. 支店の注文ひと月ごとのパーテションを作成

```
CREATE TABLE order_system.orders_partition_2024_03
PARTITION OF order_system.orders
FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');
```

14. パブリッシャーへの接続情報とパブリケーションを指定してサブスクリプション作成

```
CREATE SUBSCRIPTION subscriction_all_tbl 
CONNECTION 'host=localhost port=5435 user=postgres dbname=store_4123 password=hoge' 
PUBLICATION publication_all_tbl;
```

## 4. バックアップと修復

### 4-1. dump

1. DBをarciveでdump

```
pg_dump -h 127.0.0.1 -p 5433 -U postgres -d store_4316 -Fc -f C:\PostgreSQL\2024-03-15_store_4316_database.dump
```

2. DBをscriptでdump

```
pg_dump -h 127.0.0.1 -p 5433 -U postgres -d store_4316 -f C:\PostgreSQL\2024-03-15_store_4316_database.sql
```

3. クラスタ全体をscriptでdump

```
pg_dumpall -h 127.0.0.1 -p 5433 -U postgres -f C:\PostgreSQL\2024-03-15_server_01.sql
```

### 4-2. restore

1. restore用のクラスタを作成

```
mkdir C:\PostgreSQL\server_05
initdb -U postgres -D C:\PostgreSQL\server_05
```

2. confファイルを編集します

- C:\PostgreSQL\server_04\postgresql.conf
    - port = 5437
    - shared_preload_libraries = 'postgres_fdw'
    - wal_level = logical

3. サービス起動済みの場合プロセスを殺します

```
taskkill /PID {PID} /F
```

4. クラスタのサービスを起動します

```
pg_ctl -D C:\PostgreSQL\server_05 -l C:\PostgreSQL\server_05\server_05.log start
```

5. サービスが起動していることを確認

```
netstat -ano -o | find "5437"
```

6. restoreを実行

```
pg_restore -C -h 127.0.0.1 -p 5437 -U postgres -d postgres C:\PostgreSQL\2024-03-15_store_4316_database.dump
```

7. restoreしたDBに接続

```
psql -h localhost -p 5437 -U postgres -d store_4316
```

8. order_systemスキーマのテーブル一覧

```
\dt order_system.*
```

<img src="data/images/2024-03-15 162803.png">

9. ordersテーブルを確認

```
select * from order_system.orders;
```

<img src="data/images/2024-03-15 162739.png">

## 5. CRUD処理

私の部屋のセンサ値を使用します

[sensor_values.csv](https://github.com/taaaakeeen/hama-sushi/blob/main/data/sensor_values.csv)

1. サーバに接続

```
psql -h localhost -p 5432 -U postgres
```

2. DB作成

```
create database measurement_data;
```

3. DB接続

```
\c measurement_data
```

4. スキーマ作成

```
create schema room;
```

5. テーブル作成

```
create table room.sensor_machines(
    machine_id integer,
    location_name varchar,
    PRIMARY KEY (machine_id)
);
```

```
create table room.sensor_values(
    machine_id integer,
    timestamp timestamp,
    temperature double precision,
    humidity double precision,
    barometric_pressure double precision,
    FOREIGN KEY (machine_id)
    REFERENCES room.sensor_machines(machine_id)
    ON DELETE CASCADE
);
```

6. 測定装置を登録

```
INSERT INTO room.sensor_machines (machine_id, location_name)
VALUES (1, '豊田市');
```

7. CSVをインポート

```
COPY room.sensor_values(machine_id, timestamp, temperature, humidity, barometric_pressure)
FROM 'C:\PostgreSQL\sensor_values.csv' DELIMITER ',' CSV HEADER;
```

8. 結果を確認

```
SELECT *
FROM room.sensor_machines AS sm
JOIN room.sensor_values AS sv ON sm.machine_id = sv.machine_id
WHERE sm.machine_id = 1
limit 10;
```

### 5-1. SELECT

1. テーブルのレコード数

```
SELECT COUNT(*)
FROM room.sensor_values;
```

2. 月ごとの最高気温と最低気温

```
SELECT EXTRACT(YEAR FROM timestamp) AS year,
EXTRACT(MONTH FROM timestamp) AS month,
MAX(temperature) AS max_temperature,
MIN(temperature) AS min_temperature
FROM room.sensor_values
GROUP BY EXTRACT(YEAR FROM timestamp), EXTRACT(MONTH FROM timestamp)
ORDER BY EXTRACT(YEAR FROM timestamp), EXTRACT(MONTH FROM timestamp);
```

3. 月ごとの最高気温と最低気温のVIEWを作成

```
CREATE VIEW room.monthly_temperature_stats AS
SELECT 
EXTRACT(YEAR FROM timestamp) AS "年",
EXTRACT(MONTH FROM timestamp) AS "月",
MAX(temperature) AS "最高気温",
MIN(temperature) AS "最低気温"
FROM room.sensor_values
GROUP BY EXTRACT(YEAR FROM timestamp), EXTRACT(MONTH FROM timestamp)
ORDER BY EXTRACT(YEAR FROM timestamp), EXTRACT(MONTH FROM timestamp);
```

4. VIEWの呼び出し

```
SELECT * FROM room.monthly_temperature_stats;
```

### 5-2. INSERT

1. 集計データ用のテーブルを作成

```
CREATE TABLE room.daily_summary (
date DATE,
machine_id integer,
max_temperature double precision,
min_temperature double precision,
max_humidity double precision,
min_humidity double precision,
max_barometric_pressure double precision,
min_barometric_pressure double precision,
PRIMARY KEY (date, machine_id),
FOREIGN KEY (machine_id)
REFERENCES room.sensor_machines(machine_id)
ON DELETE CASCADE
);
```

2. select結果をINSERT

```
INSERT INTO room.daily_summary (date, machine_id, max_temperature, min_temperature, max_humidity, min_humidity, max_barometric_pressure, min_barometric_pressure)
SELECT
DATE(timestamp) AS date,
machine_id,
MAX(temperature) AS max_temperature,
MIN(temperature) AS min_temperature,
MAX(humidity) AS max_humidity,
MIN(humidity) AS min_humidity,
MAX(barometric_pressure) AS max_barometric_pressure,
MIN(barometric_pressure) AS min_barometric_pressure
FROM room.sensor_values
GROUP BY DATE(timestamp), machine_id;
```

3. 集計データの確認

```
SELECT * FROM room.daily_summary;
```

### 5-3. UPDATE

1. 集計テーブルを更新するトリガ関数の作成

```
CREATE OR REPLACE FUNCTION room.update_daily_summary()
RETURNS TRIGGER AS $$
BEGIN
    -- 更新された日付と machine_id の組み合わせに対応する行を更新する
    UPDATE room.daily_summary
    SET
        max_temperature = (SELECT MAX(temperature) FROM room.sensor_values WHERE DATE(timestamp) = NEW.timestamp::DATE AND machine_id = NEW.machine_id),
        min_temperature = (SELECT MIN(temperature) FROM room.sensor_values WHERE DATE(timestamp) = NEW.timestamp::DATE AND machine_id = NEW.machine_id),
        max_humidity = (SELECT MAX(humidity) FROM room.sensor_values WHERE DATE(timestamp) = NEW.timestamp::DATE AND machine_id = NEW.machine_id),
        min_humidity = (SELECT MIN(humidity) FROM room.sensor_values WHERE DATE(timestamp) = NEW.timestamp::DATE AND machine_id = NEW.machine_id),
        max_barometric_pressure = (SELECT MAX(barometric_pressure) FROM room.sensor_values WHERE DATE(timestamp) = NEW.timestamp::DATE AND machine_id = NEW.machine_id),
        min_barometric_pressure = (SELECT MIN(barometric_pressure) FROM room.sensor_values WHERE DATE(timestamp) = NEW.timestamp::DATE AND machine_id = NEW.machine_id)
    WHERE date = NEW.timestamp::DATE AND machine_id = NEW.machine_id;
    
    -- 更新された日付と machine_id の組み合わせが存在しない場合は新しい行を挿入する
    IF NOT FOUND THEN
        INSERT INTO room.daily_summary (date, machine_id, max_temperature, min_temperature, max_humidity, min_humidity, max_barometric_pressure, min_barometric_pressure)
        VALUES (NEW.timestamp::DATE, NEW.machine_id,
            (SELECT MAX(temperature) FROM room.sensor_values WHERE DATE(timestamp) = NEW.timestamp::DATE AND machine_id = NEW.machine_id),
            (SELECT MIN(temperature) FROM room.sensor_values WHERE DATE(timestamp) = NEW.timestamp::DATE AND machine_id = NEW.machine_id),
            (SELECT MAX(humidity) FROM room.sensor_values WHERE DATE(timestamp) = NEW.timestamp::DATE AND machine_id = NEW.machine_id),
            (SELECT MIN(humidity) FROM room.sensor_values WHERE DATE(timestamp) = NEW.timestamp::DATE AND machine_id = NEW.machine_id),
            (SELECT MAX(barometric_pressure) FROM room.sensor_values WHERE DATE(timestamp) = NEW.timestamp::DATE AND machine_id = NEW.machine_id),
            (SELECT MIN(barometric_pressure) FROM room.sensor_values WHERE DATE(timestamp) = NEW.timestamp::DATE AND machine_id = NEW.machine_id)
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

2. sensor_valuesテーブルのinsert/updateで発動するトリガ

```
CREATE TRIGGER update_summary_trigger
AFTER INSERT OR UPDATE ON room.sensor_values
FOR EACH ROW
EXECUTE FUNCTION room.update_daily_summary();
```

3. machine_idが1の2022-06-12の最高気温のレコードを確認

```
SELECT *
FROM room.sensor_values
WHERE machine_id = 1
AND DATE(timestamp) = '2022-06-12'
ORDER BY temperature DESC
LIMIT 1;
```

4. 2022-06-12の最高気温のレコードを38.3に更新

```
UPDATE room.sensor_values
SET temperature = 38.3
WHERE machine_id = 1
AND DATE(timestamp) = '2022-06-12'
AND temperature = (SELECT MAX(temperature) FROM room.sensor_values WHERE machine_id = 1 AND DATE(timestamp) = '2022-06-12');
```

5. 集計テーブルの2022-06-12のレコードの最高気温が更新されていることを確認

```
select * from room.daily_summary
where date = '2022-06-12';
```

### 5-4. DELETE

1. 測定装置を追加するプロシージャを作成

```
CREATE OR REPLACE PROCEDURE room.add_sensor_machine(
    IN new_machine_id INTEGER,
    IN new_location_name VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    
    -- 指定された location_name がすでに存在するかチェック
    IF EXISTS (SELECT 1 FROM room.sensor_machines WHERE location_name = new_location_name) THEN
        RAISE EXCEPTION 'location_name % already exists', new_location_name;
    END IF;

    -- 新しい測定装置を追加
    INSERT INTO room.sensor_machines (machine_id, location_name) VALUES (new_machine_id, new_location_name);
END;
$$;
```

2. プロシージャでtest装置を追加

```
CALL room.add_sensor_machine(2, '名古屋');
```

3. 追加した装置のtestデータをinsert

```
INSERT INTO room.sensor_values (machine_id, timestamp, temperature, humidity, barometric_pressure)
VALUES
(2, '2024-01-01 12:00:00', 25.0, 60.0, 1005.0),
(2, '2024-01-02 12:00:00', 24.5, 58.0, 1003.0),
(2, '2024-01-03 12:00:00', 26.0, 62.0, 1007.0),
(2, '2024-01-04 12:00:00', 24.0, 55.0, 1002.0);
```

4. testデータを確認

```
SELECT *
FROM room.sensor_machines AS sm
JOIN room.sensor_values AS sv ON sm.machine_id = sv.machine_id
WHERE sm.machine_id = 2;
```

5. 集計テーブルも確認

```
SELECT *
FROM room.sensor_machines AS sm
JOIN room.daily_summary AS ds ON sm.machine_id = ds.machine_id
WHERE sm.machine_id = 2;
```

6. idが2の装置を削除

```
DELETE FROM room.sensor_machines
WHERE machine_id = 2;
```

7. センサ値テーブルと集計テーブルからtestデータが削除されていることを確認

```
SELECT
(SELECT COUNT(*) FROM room.sensor_values WHERE machine_id = 2) AS sensor_values_count,
(SELECT COUNT(*) FROM room.daily_summary WHERE machine_id = 2) AS daily_summary_count;
```

## 6. 実行計画

### 6-1. 実行速度

1. インデックスを作成する前に実行速度を確認します

```
EXPLAIN ANALYZE SELECT * 
FROM room.sensor_values 
WHERE timestamp >= '2023-01-01' AND timestamp < '2023-02-01';
```

2. Seq Scan -> テーブル全体をスキャンして条件に一致する行を検索

<img src="data/images/2024-03-17 173426.png">

### 6-2. INDEX

1. timestamp列にindexを設定します

```
CREATE INDEX idx_sensor_values_timestamp ON room.sensor_values (timestamp);
```

2. 再度実行速度を確認します

```
EXPLAIN ANALYZE SELECT * 
FROM room.sensor_values 
WHERE timestamp >= '2023-01-01' AND timestamp < '2023-02-01';
```

3. Index Scan -> インデックスによって行の順番が決定され、条件に一致する行を効率的に検索

<img src="data/images/2024-03-17 173704.png">
