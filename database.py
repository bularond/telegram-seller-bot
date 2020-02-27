# -*- coding: utf-8 -*-
import sqlite3

from random import randint
from time import time

class database:

    def __init__(self):
        with sqlite3.connect('database.db') as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS keys"
                         "(`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `product` INTEGER, `key` TEXT)")
            conn.execute("CREATE TABLE IF NOT EXISTS products"\
                         "(`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `name` TEXT, `description` TEXT, `cost` INTEGER )")
            conn.execute("CREATE TABLE IF NOT EXISTS purchases"
                         "(`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `user_id` INTEGER, `product` INTEGER, `code` INTEGER, `datetime` INTEGER )")
            conn.execute("CREATE TABLE IF NOT EXISTS users_keys"
                         "(`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `key` TEXT, `user_id` INTEGER, `datetime` INTEGER, `product` INTEGER )")
            conn.commit()

    def has_key_on_product(self, product, conn):
        with sqlite3.connect('database.db') as conn:
            for key in conn.execute(f"SELECT * FROM keys "\
                                    f"WHERE product == {product}"):
                return True
            return False

    def get_catalog(self, offset=0, count=20):
        with sqlite3.connect('database.db') as conn:
            out = []
            for item in conn.execute(f"SELECT * FROM products "\
                                     f"ORDER BY id "\
                                     f"LIMIT {count} OFFSET {offset}"):
                if(self.has_key_on_product(item[0], conn)):
                    out.append(item)
            return out


    def get_product_by_id(self, id):
        with sqlite3.connect('database.db') as conn:
            for product in conn.execute(f"SELECT * FROM products "\
                                        f"WHERE id == {id}"):
                return product 
            return None


    def get_purchase_by_code(self, code):
        with sqlite3.connect('database.db') as conn:
            for purchase in conn.execute(f"SELECT * FROM purchases "\
                                         f"WHERE code == {code}"):
                return purchase  
            return None

    
    def has_purchase(self, user_id, product):
        with sqlite3.connect('database.db') as conn:
            for purchase in conn.execute(f"SELECT * FROM purchases "\
                                         f"WHERE user_id == {user_id} AND product == {product}"):
                return purchase[3]
            return None


    def add_purchase(self, user_id, product):
        with sqlite3.connect('database.db') as conn:
            code = randint(10000, 99999)
            while(self.get_purchase_by_code(code)):
                code = randint(10000, 99999)
            conn.execute(f"INSERT INTO purchases (user_id, product, code, datetime) "\
                         f"VALUES ({user_id}, {product}, {code}, {time()})")
            conn.commit()
            return code


    def get_key_by_product_id(self, product_id):
        with sqlite3.connect('database.db') as conn:
            for key in conn.execute(f"SELECT * FROM keys "\
                                    f"WHERE product == {product_id}"):
                return key
            return None


    def remove_purcases_by_code(self, code):
        with sqlite3.connect('database.db') as conn:
            conn.execute(f"DELETE FROM purchases "\
                         f"WHERE code == {code}")
            conn.commit()


    def remove_key(self, key):
        with sqlite3.connect('database.db') as conn:
            conn.execute(f"DELETE FROM keys "\
                         f"WHERE key == {key}")
            conn.commit()


    def add_key_to_user(self, key, user_id):
        with sqlite3.connect('database.db') as conn:
            conn.execute(f"INSERT INTO users_keys (key, user_id, datetime) "\
                         f"VALUES ({key}, {user_id}, {time()})")
            conn.commit()


    def get_users_keys(self, user_id):
        with sqlite3.connect('database.db') as conn:
            users_keys = []
            for user_key in conn.execute(f"SELECT * FROM users_keys "\
                                         f"WHERE user_id == {user_id}"):
                users_keys.append(user_key)
            return users_keys


if __name__ == "__main__":
    db = database()
    #  db.remove_key("123123")

