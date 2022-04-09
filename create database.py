import sqlite3 as sql

conn = sql.connect('db/data_base')
c = conn.cursor()

### create table customer
c.execute('''CREATE TABLE  customer 
            ( 'id' CHAR(20) PRIMARY KEY NOT NULL,
              'name' CHAR(30) NOT NULL,
              'address' TEXT,
              'acc_num' INTEGER,
              'phone_num' CHAR(11) NOT NULL)''' )

### create table goods
c.execute('''CREATE TABLE goods 
            ( 'price' INTEGER NOT NULL,
              'name' CHAR(30) PRIMARY KEY NOT NULL,
              'amount' INTEGER NOT NULL,
              'group_name' CHAR(15),
              'unit' CHAR(15),
              CONSTRAINT 'قیمت منفی است !' CHECK (price>=0),
              CONSTRAINT 'مقدار باید بیشتر از 0 باشد !' CHECK (amount>0),
              CHECK (group_name in ('ابزار','مصالح ساختمان','لوله و اتصالات')),
              CHECK (unit in ('متر','تناژ','عدد')) )''')

### create table sale
c.execute('''CREATE TABLE sale 
            ( 'tracking' CHAR(20),
              'time' TIMESTAMP,
              'amount' INTEGER NOT NULL,
              'invoice' INTEGER PRIMARY KEY NOT NULL,
              'discount' INTEGER,
              'total_price' INTEGER NOT NULL,
              'id' CHAR(20) NOT NULL,
              'name' CHAR(30) NOT NULL,
              FOREIGN KEY (id) REFERENCES customer(id),
              FOREIGN KEY (name) REFERENCES goods(name),
              CONSTRAINT 'مقدار باید بیشتر از 0 باشد !' CHECK (amount>0),
              CONSTRAINT 'تخفیف بیشتر از هزینه نهایی است !' CHECK (total_price>=discount),
              CONSTRAINT 'هزینه نهایی منفی میباشد !' CHECK (total_price>=0),
              CONSTRAINT 'تخفیف منفی میباشد !' CHECK (discount>=0) )''')

### triggers for sale
c.execute('''CREATE TRIGGER check_amount
            BEFORE INSERT ON sale
            BEGIN
            SELECT
            CASE
            WHEN (NEW.amount>(SELECT amount FROM goods WHERE name=NEW.name)) THEN
                RAISE (ABORT,'این مقدار در انبار موجود نمیباشد !') 
            END;
            END;''')

c.execute('''CREATE TRIGGER check_id
            BEFORE INSERT ON sale
            BEGIN
            SELECT
            CASE
            WHEN NEW.id NOT IN (SELECT id FROM customer) THEN 
                RAISE (ABORT,"مشتری با کد وارد شده موجود نیست !") 
            END;
            END; ''')

c.execute('''CREATE TRIGGER check_name
            BEFORE INSERT ON sale
            BEGIN
            SELECT
            CASE
            WHEN NEW.name NOT IN (SELECT name FROM goods) THEN 
                RAISE (ABORT,"کالا با نام وارد شده موجود نمیباشد") 
            END;
            END; ''')

c.execute('''CREATE TRIGGER update_goods 
            AFTER INSERT ON sale
            WHEN NEW.amount!=(SELECT amount FROM goods WHERE name=NEW.name)
                BEGIN
                UPDATE goods SET amount=((SELECT amount FROM goods WHERE name=NEW.name)-NEW.amount) WHERE name=NEW.name;
                END;''')

c.execute('''CREATE TRIGGER delete_goods 
            AFTER INSERT ON sale
            WHEN NEW.amount=(SELECT amount FROM goods WHERE name=NEW.name) 
            BEGIN
                DELETE FROM goods WHERE name=NEW.name;
            END;''')

conn.close()