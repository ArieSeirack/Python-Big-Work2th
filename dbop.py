#!/usr/bin/python3

import pymysql


def sqlwrite(tablenum,list):
    db = pymysql.connect("localhost", "Aries", "aries", "pystadb")
    cursor = db.cursor()

    if tablenum == 1:
        table = "structure"
        for i in range(19):
            sql = "INSERT INTO " + table + "(year,total,young,mid,old) \
                       VALUES (%s,%s,%s,%s,%s)" % \
                  (list[i][0], list[i][1], list[i][2], list[i][3], list[i][4])
            try:
                # 执行sql语句
                cursor.execute(sql)
                # 提交到数据库执行
                db.commit()
            except:
                # 如果发生错误则回滚
                db.rollback()

    elif tablenum == 2:
        table = "consumption"
        for i in range(9):
            sql = "INSERT INTO " + table + "(year,allmoney,ruralmoney,urbanmoney,allindex,ruralindex,urbanindex) \
                                   VALUES (%s,%s,%s,%s,%s,%s,%s)" % \
                  (list[i][0], list[i][1], list[i][2], list[i][3], list[i][4],
                   list[i][5], list[i][6])
            try:
                # 执行sql语句
                cursor.execute(sql)
                # 提交到数据库执行
                db.commit()
            except:
                # 如果发生错误则回滚
                db.rollback()

    # 关闭数据库连接
    db.close()


def sqlread(table, name, info):
    db = pymysql.connect("localhost", "Aries", "aries", "pystadb")
    cursor = db.cursor()

    sql = "SELECT * FROM %s \
           WHERE %s = %s" % (table, name, info)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
    except:
        print("Error: unable to fetch data")

    db.close()
    return results


def sqlclear(table):
    db = pymysql.connect("localhost", "Aries", "aries", "pystadb")
    cursor = db.cursor()
    if table == 1:
        name = "structure"
    elif table == 2:
        name = "consumption"

    sql = "DELETE FROM "+name+" WHERE year > 0"
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()

    db.close()


