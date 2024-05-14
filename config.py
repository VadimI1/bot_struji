TABLE = ['CREATE TABLE IF NOT EXISTS "Пользователи" ( ' 
        '"ID"	serial primary key,' 
        '"id_messages"	TEXT,'
        '"Имя"	TEXT,'
        '"Номер телефона"	TEXT,'
        '"Использованные промокоды" TEXT,'
        '"Баланс" INTEGER,'
        '"Статус" BOOlEAN,'
        '"Ban" BOOlEAN)',

        'CREATE TABLE IF NOT EXISTS "Промокоды" ( ' 
        '"ID"	serial primary key,' 
        '"Название"	TEXT,' 
        '"Промокод"	TEXT,'
        '"Баллы" INTEGER,'
        '"Статус" BOOlEAN,'
        '"Активировавший" TEXT)'
        ]