TABLE = ['CREATE TABLE IF NOT EXISTS "Пользователи" ( ' 
        '"ID"	serial primary key,' 
        '"id_messages"	TEXT,'
        '"Использованные промокоды" TEXT,'
        '"Баланс" INTEGER,'
        '"Статус" BOOlEAN)',

        'CREATE TABLE IF NOT EXISTS "Промокоды" ( ' 
        '"ID"	serial primary key,' 
        '"Промокод"	TEXT,'
        '"Баллы" INTEGER,'
        '"Статус" BOOlEAN)'
        ]