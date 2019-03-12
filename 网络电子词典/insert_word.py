import pymysql

f=open('dict.txt')
db=pymysql.connect('localhost','root','123456','dict')

cursor=db.cursor()

for line in f:
    tmp=line.split(' ')
    word=tmp[0]
    mean=' '.join(tmp[1:]).strip()#strip 去两边空格

    sql='insert into words(word,mean) values("%s","%s")'%(word,mean)

    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.commit()
f.close()