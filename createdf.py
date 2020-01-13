'''Use createdf.create_dataframe(nmax_rows) to create dataframe'''


import numpy as np
import pandas as pd
import csv
from datetime import datetime


# Создаем генератор строк
def generator_of_rows(filename):
    '''
    Generator of rows in csv file
    Returns row per call.
    
    '''
    # Открываем файл
    with open(filename, "r") as csvfile:
        datareader = csv.reader(csvfile)
        for row in datareader:
            yield row





# Создаем список функций которые хотим применять, для извлечения признаков
list_of_functions = [np.max, np.min, np.mean, np.median, np.std]


def create_feature(list_func,lists_of_feature):
    '''
    Create features by applying functions to list of features.
    Takes list of functions and apply them to lists of given features.
    Returns list with new generated features.
    
    '''
    result_list=[]
    for feature in lists_of_feature:
        # Если пусто заполняем нулем
        if feature==[]:
            feature=[0]
            
        for func in list_func:
            result_list.append(func(feature))
            
    return result_list




def inizialize_row(id_of_row, csv_row, start_row=None, last_row = None):
    '''
    Assign values to current and previos row.
    Takes id_of_row and row to update current row and previos row.
    Returns current row and previos row.
    
    '''
    if start_row==None:
        start_row=1
    # При первом запуске last_row = None
    if id_of_row==start_row:
        prev_row = csv_row
        curr_row = csv_row
    
    # После этого last_row = previos_row
    if id_of_row > start_row:
        prev_row = last_row
        curr_row = csv_row
    return curr_row, prev_row




def uptate_curr_check_feature(row, sum_product_unique,
                                sum_product_quantity, list_trn_sum_from_iss,
                                list_price_from_iss, list_trn_sum_from_red):
    
    '''
    Update info about current check due to next iteration.
    Takes arguments from last iteration and update it due to info in row.
    Returns updated features.
    
    '''
    #число уникальных товаров в чеке +1
    sum_product_unique += 1

    #общее число товаров в чеке
    if float(row[10])==0:
        quantity = 1.0
    else:
        quantity = float(row[10]) 
    sum_product_quantity += quantity

    #стоимость позиции в чеке
    trn_sum_from_iss = float(row[11])
    list_trn_sum_from_iss.append(trn_sum_from_iss)

    #стоимость товара в чеке
    price_from_iss = trn_sum_from_iss/quantity
    list_price_from_iss.append(price_from_iss)

    #стоимость позизии оплаченной бонусами в чеке
    if row[12]:
        trn_sum_from_red = float(row[12])
    else:
        trn_sum_from_red = 0 
    list_trn_sum_from_red.append(trn_sum_from_red)
    list_to_return = [sum_product_unique,
                      sum_product_quantity,
                      list_trn_sum_from_iss,
                      list_price_from_iss,
                      list_trn_sum_from_red
                     ]
    return list_to_return



def create_feat_from_days(client_visit_days):
    '''
    Uses list with dates of visits.
    Returns list with delays between visits in days.
    Also returns number of visits grouped by weekday. 

    '''
    weekday_list = [0,0,0,0,0,0,0]
    for date in client_visit_days:
        n_week_day = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').weekday()
        weekday_list[n_week_day]+=1

    list_delay_days = []
    if len(client_visit_days)==1:

        # Если у клиента только одно посещение помечаем его -1
        list_delay_days.append(-1)
    else:
        # Вычисляем дилэй между ближайшими посещениями
        for i in range(len(client_visit_days)-1):
            date_0 = datetime.strptime(client_visit_days[i], '%Y-%m-%d %H:%M:%S')
            date_1 = datetime.strptime(client_visit_days[i+1], '%Y-%m-%d %H:%M:%S')
            delay = (date_1 - date_0).days

            list_delay_days.append(delay)




    return list_delay_days, weekday_list



def summarize_last_visit(previos_row, prev_date, list_of_last_visit):
    '''
    Returns updated list with info about last visit.
    Takes previos row, previos date and list_of_last_visit 
    where:
    0 list_client_day,\
    1 list_regular_points_received,\
    2 list_express_points_received,\
    3 list_regular_points_spent,\
    4 list_express_points_spent,\
    5 list_purchase_sum,\
    6 list_sum_product_quantity,\
    7 list_sum_product_unique,\
    8 sum_product_unique,\
    9 sum_product_quantity = list_of_last_visit
    
    '''
    # Подводим итоги прошлого визита!
    # Добавляем день посещения
    list_of_last_visit[0].append(prev_date)

    # Добавляем информацию о бонусах за посещение
    list_of_last_visit[1].append(float(previos_row[3]))
    list_of_last_visit[2].append(float(previos_row[4]))
    list_of_last_visit[3].append(float(previos_row[5]))
    list_of_last_visit[4].append(float(previos_row[6]))

    # Добавляем информацию о количестве и качестве покупок
    list_of_last_visit[5].append(float(previos_row[7]))
    list_of_last_visit[6].append(float(list_of_last_visit[9]))
    list_of_last_visit[7].append(float(list_of_last_visit[8]))
    list_of_last_visit[8] , list_of_last_visit[9] = 0, 0

    return list_of_last_visit


# Ищем стартовую строку для start_user
def get_start_row(start_user, filename='Data/purchases.csv'):
    '''
    Finds number of row which contains info about start_user.
    start_user = {1,2,3,...}
    Return number of row in csv file (starts from 0)
    '''
    if start_user!=None:
        if start_user>0: 
            n_of_row = 0
            n_of_user = 0
            for row in generator_of_rows(filename):
                if n_of_row==0:
                    current_user = row[0]
                    previos_user = row[0]

                current_user = row[0]
                if current_user==previos_user:
                    n_of_row+=1
                    continue
                else:
                    previos_user=current_user
                    n_of_user+=1
                    n_of_row+=1
                    if n_of_user==start_user:
                        break
    return n_of_row-1




def create_data_for_df(nmax_rows=None, nmax_users=None, start_row=None, start_user=None,
                       step_rows = 10_000, filename='Data/purchases.csv'):    
    '''
    This is the kernal function (main) in purcing csv file.
    Running rows in given csv file and create list with final features.
    Returns lists with info about each person.
    '''
    
    # Если не указана начальная строка
    if start_row==None:
        start_row=1
    
    # Если указан номер начального пользователя
    if start_user!=None:
        start_row = get_start_row(start_user)
    
    id_of_row = 0
    
    purchase=[]
    
    n_of_user = 0
    for row in generator_of_rows(filename):
        # пропускаем header
        if id_of_row==0:
            id_of_row = 1
            continue
        
        if id_of_row < start_row:
            id_of_row+=1
            continue       
        
        if id_of_row==start_row:
                # инициализируем количество визитов в магазин единицей
                n_visits=1

                # инициализируем строку для функции inizialize_row
                current_row = None

                # инициализируем количество визитов в магазин со скидкой
                n_red_visits=0

                # инициализируем стоимость отдельной позиции и количество товаров в чеке 
                sum_trn_sum_from_iss = 0
                sum_trn_sum_from_red = 0

                sum_product_quantity = 0
                sum_product_unique = 0

                # инициализируем листы фичей
                list_client_day = []                #дни посещений
                list_delay_days = []                #промужуток дней между посещений

                list_regular_points_received = []   #список полученных "регулярных"  баллов
                list_express_points_received = []   #список полученных "экспресс" баллов
                list_regular_points_spent = []      #список потраченных "регулярных"  баллов
                list_express_points_spent = []      #список потраченных "регулярных"  баллов

                list_purchase_sum = []              #список потраченных денег на покупки
                list_sum_product_quantity = []      #список числа купленных товаров
                list_sum_product_unique = []        #список числа уникальных купленных товаров

                list_trn_sum_from_iss = []          #список цен купленных позиций
                list_trn_sum_from_red = []          #список цен оплаченных бонусами
                list_price_from_iss = []            #список цен за одну единицу товара


        # Инициализируем текущую строку и предыдущую
        current_row, previos_row = inizialize_row(id_of_row, row,start_row, last_row=current_row)

        # Инициализируем текущие и прошлые значения id_клиента, транзакции, даты
        curr_client_id, prev_client_id = current_row[0], previos_row[0]
        curr_trans, prev_trans = current_row[1], previos_row[1]
        curr_date, prev_date = current_row[2], previos_row[2]

        # Если текущий чек продолжается
        if curr_trans==prev_trans:
            # Это тот же чек, того же клиента!

            #Обновляем признаки для текущего чека 
            # число уникальных товаров в чеке
            # число всех товаров в чеке
            # список цен за позицию для клиента по всем чекам   
            # список цен за уникальный товар, за позицию без скидки
            sum_product_unique,   \
            sum_product_quantity, \
            list_trn_sum_from_iss,\
            list_price_from_iss,  \
            list_trn_sum_from_red =  uptate_curr_check_feature(row,           
                                                              sum_product_unique,
                                                              sum_product_quantity, 
                                                              list_trn_sum_from_iss,
                                                              list_price_from_iss, 
                                                              list_trn_sum_from_red)

        # Если клиент тот же
        elif curr_client_id==prev_client_id:
            # Это новый чек, того же клиента! 

            list_of_last_visit= [list_client_day,
                                 list_regular_points_received,
                                 list_express_points_received,
                                 list_regular_points_spent,
                                 list_express_points_spent,

                                 list_purchase_sum,
                                 list_sum_product_quantity,
                                 list_sum_product_unique,

                                 sum_product_unique,
                                 sum_product_quantity
                                ]


            list_of_last_visit = summarize_last_visit(previos_row, prev_date, list_of_last_visit)

            sum_product_unique = list_of_last_visit[-2]
            sum_product_quantity = list_of_last_visit[-1]

            #Обновляем признаки для нового чека 
            # число уникальных товаров в чеке
            # число всех товаров в чеке
            # список цен за позицию для клиента по всем чекам   
            # список цен за уникальный товар, за позицию без скидки
            sum_product_unique,   \
            sum_product_quantity, \
            list_trn_sum_from_iss,\
            list_price_from_iss,  \
            list_trn_sum_from_red =  uptate_curr_check_feature(row,           
                                                              sum_product_unique,
                                                              sum_product_quantity, 
                                                              list_trn_sum_from_iss,
                                                              list_price_from_iss, 
                                                              list_trn_sum_from_red)

            # Число посещений +1
            n_visits+=1

            # Если нужно добавляем в число "красных" визитов 
            # Если нет нулей в списке, то покупка оплачена бонусами 
            if 0 not in list_trn_sum_from_red:
                n_red_visits+=1


        # Если клиент другой   curr_client_id!=prev_client_id
        elif curr_client_id!=prev_client_id:
            # Это другой клиент! 
            # Подводим итоги прошлого клиента!



            # Подводим итоги прошлого визита!
            list_of_last_visit= [list_client_day,
                                 list_regular_points_received,
                                 list_express_points_received,
                                 list_regular_points_spent,
                                 list_express_points_spent,

                                 list_purchase_sum,
                                 list_sum_product_quantity,
                                 list_sum_product_unique,

                                 sum_product_unique,
                                 sum_product_quantity
                                ]


            list_of_last_visit = summarize_last_visit(previos_row, prev_date, list_of_last_visit)
            sum_product_unique = list_of_last_visit[-2]
            sum_product_quantity = list_of_last_visit[-1]



            # Добавляем информацию о частоте посещения магазина

            list_delay_days, week_day_list = create_feat_from_days(list_client_day)

            # Собираем список из списков фичей - 11 штук !
            lists_of_feature = [list_delay_days, 
                                *list_of_last_visit[1:8], 
                                list_trn_sum_from_iss,
                                list_trn_sum_from_red,
                                list_price_from_iss
                               ]


            # Собираем итоговые признаки клиента
            # Инициалзируем лист который описывает клиента
            push=[]

            # Добавляем id, количество посещений, количество "красных" посещений
            push.extend([prev_client_id, n_visits, n_red_visits, *week_day_list])

            # Создаем фичи для каждого листа с помощью 
            # ряда функций  
            # list_func = [np.max, np.min, np.mean, np.median, np.std]
            for feature in create_feature(list_of_functions,lists_of_feature):
                push.append(feature)
            
            purchase.append(push)


            # Опустошаем использованные списки
            list_client_day = []
            list_regular_points_received = []
            list_express_points_received = []
            list_regular_points_spent = []
            list_express_points_spent = []
            list_purchase_sum = []
            list_sum_product_quantity = []
            list_sum_product_unique = []
            sum_product_unique = 0
            sum_product_quantity = 0
            
            list_trn_sum_from_iss = []
            list_trn_sum_from_red = []
            list_price_from_iss = []
            list_delay_days=[]
            list_client_day=[]
            
            # Обновляем индикаторы
            n_visits = 1
            n_red_visits = 0
            
            n_of_user += 1


        id_of_row += 1
        
        if nmax_users!=None:
            if n_of_user>=nmax_users:
                break
                
        if nmax_rows!=None:
            if id_of_row-start_row>=nmax_rows:
                break
        
   
    return purchase




def generate_column_names(names_pure_feature=None, names_gen_feature=None, name_of_func=None):
    '''
    Generate names of columns for DataFrame.
    Takes names of pure features, names of generated features and names of functions.
    Return list of strings with column names.
    '''
    if names_pure_feature==None:
        names_pure_feature = ['client_id',
                              'n_visits',
                              'n_red_visits',
                              'weekday_1', 
                              'weekday_2',
                              'weekday_3',
                              'weekday_4',
                              'weekday_5',
                              'weekday_6',
                              'weekday_7',]
        
    if names_gen_feature==None:
        names_gen_feature = ['delay_days',       
                            'regular_points_received',
                            'express_points_received',
                            'regular_points_spent',
                            'express_points_spent',

                            'purchase_sum',
                            'sum_product_quantity',
                            'sum_product_unique',

                            'trn_sum_from_iss',
                            'trn_sum_from_red',
                            'price_from_iss'
                           ]
        
    if name_of_func==None:
        name_of_func = ['max', 'min', 'mean', 'median', 'std']
    
    

    columns=[]
    for name in names_pure_feature:
        columns.append(name)
    for feature in names_gen_feature:
            for func in name_of_func:
                columns.append(func + '_' + feature)
   
    return columns


def create_dataframe(nmax_rows=None, nmax_users=None, start_row=None, start_user=None, 
                     filename='Data/purchases.csv'):
    '''
    Creates DataFrame from csv file with parcing maximum of nmax_rows, or nmax_users.
    Starts from start_row or start_user.
    
    '''
    data = create_data_for_df(nmax_rows, nmax_users, start_row, start_user, filename)
    columns = generate_column_names()
    
    dataframe=pd.DataFrame(data=data, columns=columns)
    return dataframe


