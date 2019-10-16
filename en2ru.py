#!/usr/bin/env python
# coding: utf-8

# # Зачем всё это?

# Есть машинный перевод и есть автоматизированный перевод. 
# 
# Машинный перевод дает 100% автоматизации и не позволяет вмешиваться в процесс перевода (только в результат). Конечно у многих машинных переводчиков есть функция "предложить перевод", но я не понимаю, как она работает, и работает ли хоть как-то вообще. Однажды я всё-таки заметил, как это работает: в яндекс-переводчике предложил перевод слова (уже не помню какого), и через сутки до него дошло, как надо переводить это слово. Через сутки, Карл!
# 
# Автоматизированный перевод дает где-то 15-20% автоматизации. Помимо словарей, глоссариев и прочей справочной информации, самая продвинутая (известная мне) технология - это память переводов, когда человек вручную переводит предложения, а система запоминает эти переводы, и если встречается предложение, которое было переведено раньше (или _похожее_ на него), его перевод подставляется автоматически. Но какова вероятность встретить в тексте 2 одинаковых предложения, если в них больше трёх слов?
# 
# Целью данного переводчика является автоматизация 90%. Не 100 и не 20. А также мгновенное вступление изменений в силу. Ну и возможность залезть в код.
# 
# -----
# 
# Любая система перевода состоит из двух аспектов:
# * используемые структуры данных и алгоритмы
# * способ заполнения базы данных
# 
# Есть следующие способы заполнения базы данных:
# * статистический: у статистического перевода и у нейросетевого
# * ручной: у перевода основанного на пправилах и у памяти переводов
# 
# Какими бы умными ни были нейросетевые системы, системы с ручным заполнением базы данных всегда будут оставаться актуальными.

# # Основной принцип

# ```
# p_паттерн парсит текст (str, pos), 
#     вызывая другие паттерны, возвращающие древовидные структуры
#     эти древовидные структуры передает одному из правил, сопоставленных данному паттерну
#     и возвращает (pos, результат этого правила), помещенный в массив
#     
#     если ничего не удалось распарсить, возвращаемый массив будет пустым
#     если удалось распарсить несколько вариантов - в массиве будет насколько вариантов
#         сначала парсятся все обычные варианты
#         и если есть хоть один обычный результат, 
#             то парсятся все исключения
#             в массиве результатов исключения замещают результаты, если их длины совпадают
# ```
# 
# ```
# r_правило получает список древовидных структур
#     обрабатывает их по определенному правилу
#         т.е. меняет параметры аргументов
#     возвращает древовидную структуру
#         т.е. создает структуру, содержащую в себе аргументы
#     если в группе правил все правила отключены, то результатом будет 0 или ссылка на эту группу правил
#     отключать все правила допустимо только в исключениях
# ```
# 
# ```
# древовидная структура - объект определенного класса, соответствующего части речи, который содержит
#     постоянные параметры (для сущ.: род, число)
#     переменные параметры (для сущ.: падеж)
#         при изменении этих параметров автоматически менются параметры дочерних древовидных структур
#     talk: массив древовидных структур
#         или пар (тип, структура), где тип - main/dep/other
#     и др.
# ```
# 
# ```
# str(древовидная структура)
#     превращает древовидную структуру в строку
# ```

# # Что с этим делать дальше

# ```
# В дальнейшем предполагается, что паттерны и правила будут писать пользователи
# грамматика не преобразовывается в LL(1) или какой-то другой промежуточный формат,
# а парсится как есть, с возвратами (LL(*)), поэтому результаты нетерминалов кэшируются.
# Также стоит защита от зацикливания.
# Никто не обещал, что грамматика будет однозначной, 
# поэтому каждый нетерминал возвращает массив результатов.
# Но в конечном итоге таких результатов должно быть немного.
# Ситуация, когда получаются одинаковые результаты явлется нежелательной.
# 
# Уточним терминологию:
# нетерминал - набор альтернатив паттернов
# паттерн - последовательность терминалов/нетерминалов
# 
# В дальнейшем предполагается, что будет центральная грамматика, 
# а у ее правил пользователи будут создавать исключения и расширения.
# Фишка в том, что при редактировании грамматики этим способом 
#     поведение грамматики для уже имеющихся тестов/текстов не изменится.
# Возможно периодически для оптимизации грамматики будет требоваться полная ее переработка,
# но чисто математическая (т.е. не требующая тестов/текстов) и довольно вычислительно-сложная задача.
# Впрочем и без оптимизации производительность ухудшается не сильно.
# 
# Паттерн A является исключением паттерна B, если 
# всё что может разобрать паттерн A может разобрать паттерн B,
# т.е. A задает подъязык языка B, 
# т.е. A является частным случаем B (но связано с другим правилом).
# Сначала парсится B, и если это оказалось удачным, парсится A.
# Если А распарсилось неудачно, то результатом станосится результат B,
# а если удачно - то результат B отбрасывается и результатом станосится результат A.
# 
# т.к. исключения являются обычными нетерминалами, то внутри них тоже можно делать исключения
# 
# Расширения просто добавляются в список альтернатив.
# Можно было бы просто в нетерминалы добавлять новые альтернативы, 
# но это может привести к появлению разных вариантов разбора.
# В этих случаях можно было бы создавать исклчения, разрешающие неоднозначность,
# но чтобы всё происходило автоматически для уже переведенных текстов
# надо чтобы результат помечался датой, которая является максимумом 
#     из дат результатов (которые разобрал паттерн-последовательность) и даты создания этого паттерна.
# Если в альтернативу попадают результаты одинаковой длины, то 
#     новые отбрасываются и остается только старый.
# 
# В дальнейшем предполагается возможность каждый паттерн связывать с 
# набором правил, а точнее с одним правилом из заданного набора.
# А также возможность эти наборы пополнять и легко менять вариант перевода.
# Одним из правил перевода исключения будет вариант, когда
# результат исключения отбрасывается а результатом становится 
# результат правила регулярного паттерна.
# Это дает возможность отключать исключения, т.к. они всё же вносят изменения в регулярный перевод.
# 
# Семантически возникают разные варианты использования наборов правил:
# - смысловой
#     в этом случае как правило смысл паттерна не меняется на протяжении всего текста
# - указательный (контекстный): it, this, that, you
#     ...
# - эстетический
#     его решать лучше за счет более крупных исключений (?)
# 
# Вопрос дефолтного связывания паттернов с правилами допускает множество решений
# и остается открытым.
# В любом случае пользователь сможет создавать исключения паттернов и дополнительные правила,
# тем самым пополняя базу данных переводчика,
# а также менять связи паттернов с правилами для своего текста, сохранять эти связи,
# и применять к другим текстам.
# 
# набор правил - набор правил + номер дефолтного правила
# 		или просто правило
# 
# ```

# # Организация кода

# * parse_system.py - низкоуровневые классы, токенезация и базовые функции парсинга
# * classes.py - классы частей речи
# * ru_dictionary.py - функции отображения, русские слова и функции их добавления
# * en_dictionary.py - словарь
# 
# 
# * en2ru.ipynb .py - описание всего, грамматика, маленькие тесты, todo
# * tests.ipynb - тесты уже имеющихся переводов
# * utils.ipynb - прочее

# In[1]:


'''англо-русский переводчик, основанный на правилах, с простым добавлением паттернов и правил

en2ru(s) -> str - переводит строку, возвращает строку
d_en2ru(s) -> str - дополнительно печатает отладочный вывод
pr_l_repr(s) - печатает строку в тройных кавычках
decline(s,pads=['ip','rp','dp','vp','tp','pp']) - возвращает список склонений переведенной фразы
parse_pat(patt,s) -> Struct - парсит строку паттерном, возвращает нестрингифицированный объект
d_parse_pat(patt,s) -> Struct - дополнительно печатает отладочный вывод
scheme(s) - печатает схему разбора строки

паттерны:
p_text
p_sentence
p_phrase
p_verb
...
p_noun
...
''';


# In[2]:


import parse_system
from parse_system import S, SAttrs, ParseInfo, tokenize,                        ch_title, ch_sentence, ch_anti_sentence, ch_open, ch_prefix, ch_anti_prefix,                        seq, alt, p_alt, ELSE, W, D,                        warning, debug_pp, reset_globals, global_cache,                         RuleVars, RuleContext, repr_rule, rez_checker

import classes
from classes import StC, StNum, StNoun, StAdj, StVerb, I

import ru_dictionary
from ru_dictionary import ruwords, CW, add_runoun2, add_skl2, make_skl2, add_skl1, make_skl

import en_dictionary
from en_dictionary import dict_adj, dict_adv, dict_noun, dict_pronoun_ip, dict_pronoun_dp,                         dict_numeral, dict_verb_simple, dict_verb_komu, r_adj_noun, dict_other,                        add_ennoun2, add_ennoun1, add_dict_variant
from importlib import reload
from copy import copy, deepcopy

def dict_funs(*funs):
    return {fun.__name__:fun for fun in funs}


# # Паттерны и правила: Составные

# ## FAQ

# паттерн - функция, которая принимает s,p(токенизированную строку и позицию в ней)   
# и возвращает список результатов, а именно список пар (позиция окончания разбора, результат)  
# токены - объекты типа S - нормализованные (т.е. в нижнем регистре) строки с дополнительными атрибутами, а именно префикс из пробельных символов, модификаторы, восстанавливающие исходный регистр слова, тэги, в которые обёрнуто это слово (тэги пока не реализованы)  
# если `f` - паттерн, то `f(s,p)` - его вызов, или его результат  
# длиной результата будем называть разность позиции окончания разбора и стартовой позиции.
# 
# Терминальные паттерны:  
# `W('строка')` - считывает 1 токен, который должен совпадать со сторокой, возвращает его в непреобразованном виде, а именно объект класса S
# 
# `D(dict_smth)` - считывает 1 токен, ищет его в словаре `dict_smth`, и если находит, возвращает то, что ему сопоставлено.  
# список доступных словарей можно посмотреть в en_dictionary.py
# 
# Нетерминальные паттрны:  
# `alt(patt1,patt2,ELSE,patt3,patt4)` - список альтернатив, объединяет результаты паттернов. `ELSE` - ключевое слово-разделитель. Паттрены слева от ELSE являются исключениями паттернов справа, регулярных паттернов. Исключения могут отсутствовать, в этом случае `ELSE` указывать не нужно. Если ни один из регулярных паттернов не разобран, паттерны-исключения парсится не будут. Результаты паттернов исключений замещают результаты регулярных паттернов, но только той же самой длины прочтения. Если результат исключения не может заместить ни один из регулярных результатов, генерируется предупреждение.  
# `p_alt(s,p,patt1,patt2,ELSE,patt3,patt4)` эквивалентен `alt(patt1,patt2,ELSE,patt3,patt4)(s,p)`
# 
# `seq([patt1,patt2,patt3],rule)`(где `def rule(rez1,rez2,rez3)`) - последовательность паттернов. Генерируются все возможные комбинации результатов, и каждая последовательность передается в правило, и из этих результатов составляется окончательный результат.  
# Если нужно применить правило к результату одного паттерна, то для этого его надо поместить в последовательность из дного этого паттерна `seq([patt1],rule)` (где `rule(rez1)`)
# 
# Правила:  
# правило получает результаты последовательно разобранных паттернов, и формирует из них единый объект, возможно предварительно проведя некоторые проверки, и сообщив их результаты warning-ом  
# 
# объект должен быть класса (или подкласса Struct)  
# вот типичный синтаксис:  
# ```
# return StSmth([
#     I(tag = rez1),
#     I(tag = rez2),
#     I(tag = rez3),
# ],struct_params...)
# ```
# -- это структура, состоящая из последовательности rez1, rez2, rez3  
# доступные типы структур, а также их синтаксис (`tag`, `struct_params`) можно посмотреть в classes.py  
# `tag` задает тип взаимодействия между родительской и дочерней структурой
# 
# входные результаты можно указывать в любом порядке  
# можно менять их параметры: `I(dep = rez1, param1=new_val_1, param2 = new_val_2...)`  
# можно менять их атрибуты:  
# *    добавлять атрибуты с более правого объекта `I(dep = rez1, attrs_from_right=rez2.attrs)`  
# *    добавлять атрибуты с более левого объекта `I(dep = rez2, attrs_from_left=rez1.attrs)` 
# 
# можно использовать фиксированные слова `I(nodep = S('строка', rez3.attrs))`, при этом снабжая (или не снабжая) их атрибутами одного из входных результатов.  
# можно использовать фиксированные объекты из словаря `I(dep = CW('кошка',rez3))`, при этом снабжая (или не снабжая) их атрибутами одного из входных результатов (в данном случае это rez3).  
# не обязательно все входящие результаты должны присутствовать в итоговом объекте. Чтобы их атрибуты не потерялись, их атрибуты можно добавлять к другим результатам, как показано выше.
# 
# Может быть так, что чтруктура конструируется из нескольких фиксированных слов и одного результата. В этом случае мы часто хотим атрибуты этого результата распространить на всю структуру. Для этого в параметры структуры нужно добавить `pull_attrs=N`, где `N` - номер этого результата (нумерация с 0).
# Например
# ```
# I(nodep=StC([
#         I(nodep=S('у')),
#         I(nodep=_n1_,   pad='rp', npad='n' )# у Него
# ]), pull_attrs=1 )
# ```
# Если указать `pull_attrs=1`, то '__Kate__' будет переведено как '__у Кати__'  
# Если не указать `pull_attrs=1`, то '__Kate__' будет переведено как 'у __Кати__'
# 
# Если требуется вернуть всего лишь один входной результат, изменив его параметры, он всё равно должен быть обёрнут в новую структуру
# 
# Ну и, само собой, можно создавать структуры внутри которых содержатся структуры.
# 
# ------
# можно менять параметры входных объектов, но т.к. объекты кэшируются, их нельзя изменять, но можно указать, какие параметры будут изменены перед преобразованием объекта в строку, но для этого объект должен быть помещен в 
# 
# 
# -Когда в правилах использовать S а когда один из классов Struct ?
# 
# -S используется для неизменяемых узлов-листьев. Во всех остальных случаях используется один из классов Struct
# 
# pull_attrs - если имеющуюся структуру надо расширить константами и распространить attrs структуры на расширенную структуру - смотри пример в как в r_U_noun_EST_noun
# значение pull_attrs задается равным исходной структуры в расширенной
# 
# attrs_from_left/attrs_from_right - если в правиле один из аргументов пропадает, то его атрибуты желательно добавить к другому аргументу. 
# Синтаксис `I(tag=remain_arg, ... , attrs_from_left=lost_arg.attrs)`
# 
# 

# In[3]:


W('cat')(tokenize('cat'),0)


# ## en_dictionary

# ###### dict_noun
# ###### dict_pronoun_ip
# ###### dict_pronoun_dp
# ###### dict_adj
# ###### dict_numeral
# ###### dict_verb_simple
# ###### dict_verb_komu
# r_adj_noun

# ## Other

# ###### p_numeral

# In[4]:


@debug_pp
def p_numeral(s,p):
    return D(dict_numeral)(s,p)


# ###### p_adj

# In[5]:


#2->
@debug_pp
def p_adj(s,p): return p_alt(s,p,
    D(dict_adj),
    seq([D(dict_adv),p_adj],r_adv_adj)
)
def r_adv_adj(_adv,_adj): return StAdj([
    I(nodep=_adv),
    I(maindep=_adj)
])
    


# ## Noun-like

# ###### p_adj_noun3
# r_A_noun, r_THE_noun, r_GOOD_MORNING

# In[6]:


@debug_pp
def p_adj_noun3(s,p): return p_alt(s,p,
    seq([ alt(W('an'),W('a')), p_noun3 ],r_A_noun),
    seq([ W('the')           , p_noun3 ],r_THE_noun),
    seq([ W('good'), W('morning') ],r_GOOD_MORNING),             
ELSE,
    seq([ p_adj, p_noun3 ],r_adj_noun)
)
# r_adj_noun определен в en_dictionary.py


# In[7]:


# исключения
def r_A_noun(_a,_n): return StNoun([
    I(maindep=_n,         attrs_from_left=_a.attrs)
])
def r_THE_noun(_a,_n): return StNoun([
    I(maindep=_n,         attrs_from_left=_a.attrs)
])

def r_GOOD_MORNING(_g,_m):  return r_adj_noun(
    CW('добрый',_g),
    CW('утро',_m)
)


# ###### p_noun3

# In[8]:


@debug_pp
def p_noun3(s,p): return p_alt(s,p,
    p_adj_noun3, #ELSE, # переход к следующему уровню
    p_adj, #ELSE, # переход к следующему уровню
    p_numeral,
    D(dict_noun)
)


# ###### p_noun2_1
# r_noun_dops

# In[9]:


@debug_pp
def p_noun2_1(s,p): return p_alt(s,p,
    seq([ p_noun3, p_dops ], r_noun_dops), #ELSE, # переход к следующему уровню
    p_noun3
)
def r_noun_dops(n,d): return StNoun([
    I(maindep=n),
    I(nodep=d)
])


# ###### p_noun2
# ###### p_dop_noun2
# r_noun_numeral

# In[10]:


@debug_pp
def p_noun2(s,p): return p_alt(s,p,
    seq([ p_noun2_1, p_numeral ], r_noun_numeral), #ELSE, # переход к следующему уровню
    p_noun2_1
)
@debug_pp
def p_dop_noun2(s,p): return p_alt(s,p,
    seq([ p_noun3, p_numeral ], r_noun_numeral), #ELSE, # переход к следующему уровню
    p_noun3
)
def r_noun_numeral(n,num): return StNoun([
    I(maindep=n),
    I(nomer=num)
])


# ###### p_noun1
# ###### p_dop_noun1
# ###### p_noun1_ip
# r_numeral_noun

# In[11]:


@debug_pp
def p_noun1(s,p): return p_alt(s,p,
    seq([ p_numeral, p_noun2 ], r_numeral_noun), #ELSE, # переход к следующему уровню
    p_noun2,
    D(dict_pronoun_dp)
)
@debug_pp
def p_dop_noun1(s,p): return p_alt(s,p,
    seq([ p_numeral, p_dop_noun2 ], r_numeral_noun), #ELSE, # переход к следующему уровню
    p_dop_noun2,
    D(dict_pronoun_dp)
)
@debug_pp
def p_noun1_ip(s,p): return p_alt(s,p,
    seq([ p_numeral, p_noun2 ], r_numeral_noun), #ELSE, # переход к следующему уровню
    p_noun2,
    D(dict_pronoun_ip)
)
def r_numeral_noun(num,n):
    #if num.chis!=n.chis :
    #    warning('не совпадают числа числ. и сущ.:'+str(num)+'('+num.chis+') '+
    #            str(n)+'('+n.chis+') ')
    return StNum([
        I(quantity=num,            chis=n.chis, rod=n.rod, odush=n.odush ),
        I(maindep=n)
    ],quantity=num.quantity)


# ###### p_noun
# ###### p_dop_noun
# ###### p_noun_ip
# r_noun_and_noun, r_noun_comma_noun, r_noun_ILI_noun

# In[12]:


@debug_pp
def p_noun(s,p):
    return p_alt(s,p,
        seq([ p_noun1, W('and'), p_noun ],r_noun_and_noun  ),
        seq([ p_noun1, W('or'), p_noun ],r_noun_ILI_noun  ),
        seq([ p_noun1, W(',')  , p_noun ],r_noun_comma_noun),
                 #ELSE, # переход к следующему уровню
                 # идет конфликт с and-ом из глаголов
        p_noun1
    )
@debug_pp
def p_dop_noun(s,p):
    return p_alt(s,p,
        seq([ p_dop_noun1, W('and'), p_dop_noun ],r_noun_and_noun  ),
        seq([ p_dop_noun1, W(',')  , p_dop_noun ],r_noun_comma_noun),
                 #ELSE, # переход к следующему уровню
                 # идет конфликт с and-ом из глаголов
        p_dop_noun1
    )
@debug_pp
def p_noun_ip(s,p):
    return p_alt(s,p,
        seq([ p_noun1_ip, W('and'), p_noun_ip ],r_noun_and_noun  ),
        seq([ p_noun1_ip, W(',')  , p_noun_ip ],r_noun_comma_noun),
                 #ELSE, # переход к следующему уровню
                 # идет конфликт с and-ом из глаголов
        p_noun1_ip
    )
def r_noun_and_noun(sn,a,n):    return StNoun([
    I(dep=sn),
    I(nodep=S('и',a.attrs)),
    I(dep=n)
],c='mn', p='ip',o=False,r='m')
def r_noun_ILI_noun(sn,o,n):    return StNoun([
    I(dep=sn),
    I(nodep=S('или',o.attrs)),
    I(dep=n)
],c='mn', p='ip',o=False,r='m')
def r_noun_comma_noun(sn,c,n):    return StNoun([
    I(dep=sn),
    I(punct=S(',',c.attrs)),
    I(dep=n)
],c='mn', p='ip',o=False,r='m')


# ## Существительные в разных формах

# ###### p_noun_dp
# r_noun_dp, r_TO_noun_dp

# In[13]:


@debug_pp
def p_noun_dp(s,p): return p_alt(s,p,
    seq([D(dict_pronoun_dp)],r_noun_dp), 
    seq([ W('to'), p_noun ],r_TO_noun_dp)
)
def r_noun_dp(_n): return StNoun([
    I(maindep=_n,         pad='dp')
])

def r_TO_noun_dp(_t,_n): return StNoun([
    I(maindep=_n,         pad='dp', attrs_from_left=_t.attrs)
])


# ###### pe_IN_THE_STREET
# r_NA_X_ULITSE

# In[14]:


# на (определенной) улице
@debug_pp
def pe_IN_THE_STREET(s,p): return p_alt(s,p,
    seq([W('in'), W('the'), W('street') ],r_NA_X_ULITSE),
)
def r_NA_X_ULITSE(v,_a,_U): return StC([
    I(nodep=S('на',v.attrs)),
    I(nodep=CW('улица',_U),pad='pp')
])


# ###### pe_IN_adj_STREET
# r_NA_adj_ULITSE

# In[15]:


# на какой-то улице
@debug_pp
def pe_IN_adj_STREET(s,p): return p_alt(s,p,
    pe_IN_THE_STREET,
    ELSE,
    seq([W('in'), p_adj, W('street') ],r_NA_adj_ULITSE),
)
def r_NA_adj_ULITSE(v,_a,_U): return StC([
    I(nodep=S('на',v.attrs)),
    I(nodep = StNoun([
        I(dep=_a,
            rod='g',
            chis='ed',
            pad='ip'),
        I(maindep=CW('улица',_U))
    ]),pad='pp')
])


# ###### pe_IN_THE_GARDEN
# r_V_X_SADU

# In[16]:


# на (определенной) улице
@debug_pp
def pe_IN_THE_GARDEN(s,p): return p_alt(s,p,
    seq([W('in'), W('the'), W('garden') ],r_V_X_SADU),
)
def r_V_X_SADU(v,_a,_U): return StC([
    I(nodep=S('в',v.attrs)),
    I(nodep=CW('сад',_U),pad='dp')
])


# ###### pe_IN_adj_GARDEN
# r_V_adj_SADU

# In[17]:


# на какой-то улице
@debug_pp
def pe_IN_adj_GARDEN(s,p): return p_alt(s,p,
    pe_IN_THE_GARDEN,
    ELSE,
    seq([W('in'), p_adj, W('garden') ],r_V_adj_SADU),
)
def r_V_adj_SADU(v,_a,_U): return StC([
    I(nodep=S('в',v.attrs)),
    I(nodep=_a,
        rod='m',
        chis='ed',
        pad='pp'),
    I(nodep=CW('сад',_U),pad='dp')
])


# ###### p_where
# r_V_noun_pp, r_NA_noun_pp

# In[18]:


# где
@debug_pp
def p_where(s,p): return p_alt(s,p,
    pe_IN_adj_STREET,
    pe_IN_adj_GARDEN,
    ELSE,
    seq([W('in'), p_dop_noun ],r_V_noun_pp),
    seq([W('on'), p_dop_noun ],r_NA_noun_pp),
    seq([W('under'), p_dop_noun ],r_POD_noun_pp),
)
def r_V_noun_pp(v,_n): return StC([
    I(nodep=S('в',v.attrs)),
    I(nodep=_n,  pad='pp'),
])
def r_NA_noun_pp(v,_n): return StC([
    I(nodep=S('на',v.attrs)),
    I(nodep=_n,  pad='pp'),
])
def r_POD_noun_pp(v,_n): return StC([
    I(nodep=S('под',v.attrs)),
    I(nodep=_n,  pad='tp'),
])


# ###### p_dop
# r_X_noun_dp, r_IZ_noun, r_S_noun_tp

# In[19]:


# одно дополнение
@debug_pp
def p_dop(s,p): return p_alt(s,p,
    seq([W('to'), p_dop_noun ],r_X_noun_dp),
    seq([W('from'),p_dop_noun],r_IZ_noun),
    seq([W('with'),p_dop_noun],r_S_noun_tp),
    p_where
)
def r_X_noun_dp(x,n): return StNoun([
    I(maindep=n,  pad='dp',         attrs_from_left=x.attrs)
])
def r_IZ_noun(iz,n): return StNoun([
    I(nodep=S('из',iz.attrs)),
    I(maindep=n,  pad='rp')
])
def r_S_noun_tp(s,n): return StNoun([
    I(nodep=S('с',s.attrs)),
    I(maindep=n,  pad='tp')
])


# ###### p_dops
# r_seq_dops

# In[20]:


# последовательность дополнений
@debug_pp
def p_dops(s,p): return p_alt(s,p,
    p_dop,
    seq([p_dop, p_dops], r_seq_dops)
)
def r_seq_dops(d1,d2): return StC([
    I(nodep=d1),
    I(nodep=d2)
])


# ## have/has

# In[21]:


px_HAVE_HAS = alt( W('have'), W('has') )


# ###### p_have_question
# r_have_question, rv_HOW_MANY_noun_HAVE_noun(r_SKOLKO_noun_U_noun, r_SKOLKO_U_noun_noun)

# In[22]:


@debug_pp
def p_have_question(s,p):
    return p_alt(s,p,
        seq([px_HAVE_HAS,p_noun_ip,p_noun],r_have_question),
        seq([W('how'), W('many'), p_noun, px_HAVE_HAS, p_noun_ip], rv_HOW_MANY_noun_HAVE_noun)
    )

def r_have_question(_h,_n1,_n2):    return StC([
    I(nodep=StC([
        I(nodep=S('у')),
        I(nodep=_n1,   pad='rp', npad='n' )# у Него
    ]), pull_attrs=1 ),
    I(nodep=S('есть',_h.attrs)),
    I(nodep=_n2)
])
def r_SKOLKO_noun_U_noun(how,many,_n1,have,_n2):  return StC([
    I(nodep=S('сколько',how.attrs), attrs_from_right=many.attrs),
    I(nodep=_n1, pad='rp'),
    I(nodep=S('у')),
    I(nodep=_n2,   pad='rp', npad='n' )# у Него
])
def r_SKOLKO_U_noun_noun(how,many,_n1,have,_n2):  return StC([
    I(nodep=S('сколько',how.attrs), attrs_from_right=many.attrs),
    I(nodep=S('у')),
    I(nodep=_n2,   pad='rp', npad='n' ),# у Него
    I(nodep=_n1, pad='rp'),
])
rv_HOW_MANY_noun_HAVE_noun = RuleVars('r_SKOLKO_U_noun_noun',
                                      dict_funs(r_SKOLKO_noun_U_noun,r_SKOLKO_U_noun_noun))


# ###### pe_noun_HAVE_noun
# rv_noun_HAVE_noun(r_U_noun_EST_noun, r_U_noun_noun), r_U_noun_NET_noun

# In[23]:


@debug_pp
def pe_noun_HAVE_noun(s,p):
    return p_alt(s,p,
        seq([ p_noun_ip, px_HAVE_HAS,          p_noun ],rv_noun_HAVE_noun),
        seq([ p_noun_ip, px_HAVE_HAS, W('no'), p_noun ],r_U_noun_NET_noun)
#        seq([ p_noun, p_HAVE_HAS,          p_pronoun_dp ],r_noun_EST_U_noun),
#        seq([ p_noun, p_HAVE_HAS, W('no'), p_pronoun_dp ],r_noun_NET_U_noun)
    )
def r_U_noun_EST_noun(_n1_,_h_,_n2_):    return StC([
    I(nodep=StC([
        I(nodep=S('у')),
        I(nodep=_n1_,   pad='rp', npad='n' )# у Него
    ]), pull_attrs=1 ),
    I(nodep=S('есть',_h_.attrs)),
    I(nodep=_n2_)
])
def r_U_noun_noun(_n1_,_h_,_n2_):    return StC([
    I(nodep=StC([
        I(nodep=S('у')),
        I(nodep=_n1_,   pad='rp', npad='n' )# у Него
    ]), pull_attrs=1, attrs_from_right = _h_.attrs ),
    I(nodep=_n2_)
])
rv_noun_HAVE_noun = RuleVars('r_U_noun_EST_noun',dict_funs(r_U_noun_noun, r_U_noun_EST_noun))

def r_U_noun_NET_noun(_n1_,_h_,_no_,_n2_):    return StC([
    I(nodep=StC([
        I(nodep=S('у')),
        I(nodep=_n1_,   pad='rp', npad='n' )# у Него
    ]), pull_attrs=1 ),
    I(nodep=S('нет',_h_.attrs)),
    I(nodep=_n2_,        pad='rp')
])


# ###### pe_noun_HAVE
# r_U_noun_EST, r_U_noun_NET

# In[24]:


@debug_pp
def pe_noun_HAVE(s,p):
    return p_alt(s,p,
        seq([ p_noun_ip, px_HAVE_HAS          ],r_U_noun_EST),
        seq([ p_noun_ip, px_HAVE_HAS, alt(W('no'),W('not')) ],r_U_noun_NET)
#        seq([ p_noun, p_HAVE_HAS,          p_pronoun_dp ],r_noun_EST_U_noun),
#        seq([ p_noun, p_HAVE_HAS, W('no'), p_pronoun_dp ],r_noun_NET_U_noun)
    )
def r_U_noun_EST(_n1_,_h_):    return StC([
    I(nodep=StC([
        I(nodep=S('у')),
        I(nodep=_n1_,   pad='rp', npad='n' )# у Него
    ]), pull_attrs=1 ),
    I(nodep=S('есть',_h_.attrs))
])

def r_U_noun_NET(_n1_,_h_,_no_):    return StC([
    I(nodep=StC([
        I(nodep=S('у')),
        I(nodep=_n1_,   pad='rp', npad='n' )# у Него
    ]), pull_attrs=1 ),
    I(nodep=S('нет',_h_.attrs))
])


# ###### p_HAVE_noun
# r_IMET_noun_vp, r_NE_IMET_noun_vp, r_IMET, r_NE_IMET

# In[25]:


@debug_pp
def p_HAVE_noun(s,p): 
    return p_alt(s,p,
        seq([px_HAVE_HAS,          p_noun], r_IMET_noun_vp),
        seq([px_HAVE_HAS, W('no'), p_noun], r_NE_IMET_noun_vp),
        seq([px_HAVE_HAS],r_IMET),
        seq([px_HAVE_HAS,alt(W('no'),W('not'))],r_NE_IMET)
    )
def r_NE_IMET_noun_vp(_v,no,_n): return StVerb([
    I(nodep=S('не',no.attrs)),
    I(maindep=CW('иметь',_v)),
    I(vp=_n,   pad='vp')
])
def r_IMET_noun_vp(_v,_n): return StVerb([
    I(maindep=CW('иметь',_v)),
    I(vp=_n,   pad='vp')
])
def r_IMET(_v): return StVerb([
    I(maindep=CW('иметь',_v)),
])
def r_NE_IMET(_v,no): return StVerb([
    I(nodep=S('не',no.attrs)),
    I(maindep=CW('иметь',_v)),
])


# ## to_be

# ###### pe_noun_TOBE_where
# re_ETO_X_where, re_TO_X_where, r_noun_X_where

# In[26]:


@debug_pp
def pe_noun_TOBE_where(s,p): return p_alt(s,p,
    seq([W('this'),p_TOBE,p_where],re_ETO_X_where),
    seq([W('that'),p_TOBE,p_where],re_TO_X_where),
    ELSE,
    seq([p_noun_ip,p_TOBE,p_where],r_noun_X_where)
)

def r_noun_X_where(_n,x,_w): return StC([
    I(nodep=_n),
    I(nodep=_w, attrs_from_left=x.attrs)
])
def re_ETO_X_where(_n,x,_w): return StC([
    I(nodep=CW('этот',_n), rod='s'),
    I(nodep=_w, attrs_from_left=x.attrs)
])
def re_TO_X_where(_n,x,_w): return StC([
    I(nodep=CW('тот',_n, rod='s')),
    I(nodep=_w, attrs_from_left=x.attrs)
])


# ###### pe_noun_TOBE_where_TOO
# re_ETO_X_TOJE_where, re_TO_X_TOJE_where, r_noun_X_TOJE_where

# In[27]:


@debug_pp
def pe_noun_TOBE_where_TOO(s,p): return p_alt(s,p,
    seq([W('this'),p_TOBE,p_where,W('too')],re_ETO_X_TOJE_where),
    seq([W('that'),p_TOBE,p_where,W('too')],re_TO_X_TOJE_where),
    ELSE,
    seq([p_noun_ip,p_TOBE,p_where,W('too')],r_noun_X_TOJE_where)
)

def r_noun_X_TOJE_where(_n,x,_w,too): return StC([
    I(nodep=_n),
    I(nodep=S('тоже',too.attrs)),
    I(nodep=_w, attrs_from_left=x.attrs)
])
def re_ETO_X_TOJE_where(_n,x,_w,too): return StC([
    I(nodep=CW('этот',_n), rod='s'),
    I(nodep=S('тоже',too.attrs)),
    I(nodep=_w, attrs_from_left=x.attrs)
])
def re_TO_X_TOJE_where(_n,x,_w,too): return StC([
    I(nodep=CW('тот',_n, rod='s')),
    I(nodep=S('тоже',too.attrs)),
    I(nodep=_w, attrs_from_left=x.attrs)
])


# ###### pe_noun_TOBE_noun
# re_ETO_X_noun, re_TO_X_noun, r_noun_X_noun, r_noun_X_NE_noun

# In[79]:


@debug_pp
def pe_noun_TOBE_noun(s,p): return p_alt(s,p,
    seq([W('it'),p_TOBE,p_noun],re_ETO_X_noun),
    seq([W('this'),p_TOBE,p_noun],re_ETO_X_noun),
    seq([W('that'),p_TOBE,p_noun],re_TO_X_noun),
    ELSE,
    seq([p_noun_ip,p_TOBE,p_noun],r_noun_X_noun),
    seq([p_noun_ip,p_TOBE,W('not'),p_noun],r_noun_X_NE_noun)
)

def r_noun_X_noun(_n1,_tobe,_n2): return StC([
    I(nodep=_n1),
    I(nodep=S('--',_tobe.attrs)),
    I(nodep=_n2, rod=_n1.rod)
])
def r_noun_X_NE_noun(_n1,_tobe,_not,_n2): return StC([
    I(nodep=_n1),
    I(nodep=S('--',_tobe.attrs)),
    I(nodep=S('не',_not.attrs)),
    I(nodep=_n2, rod=_n1.rod)
])
def re_ETO_X_noun(_n1,_tobe,_n2): return StC([
    I(nodep=CW('этот',_n1), rod='s'),
    I(nodep=_n2, attrs_from_left = _tobe.attrs)
])
def re_TO_X_noun(_n1,_tobe,_n2): return StC([
    I(nodep=CW('тот',_n1), rod='s'),
    I(nodep=_n2, attrs_from_left = _tobe.attrs)
])


# ###### pe_noun_TOBE_noun_TOO
# re_ETO_X_TOJE_noun, re_TO_X_TOJE_noun, r_noun_X_TOJE_noun, r_noun_X_TOJE_NE_noun

# In[29]:


@debug_pp
def pe_noun_TOBE_noun_TOO(s,p): return p_alt(s,p,
    seq([W('this'),p_TOBE,p_noun,W('too')],re_ETO_X_TOJE_noun),
    seq([W('that'),p_TOBE,p_noun,W('too')],re_TO_X_TOJE_noun),
    ELSE,
    seq([p_noun_ip,p_TOBE,p_noun,W('too')],r_noun_X_TOJE_noun),
    seq([p_noun_ip,p_TOBE,W('not'),p_noun,W('too')],r_noun_X_TOJE_NE_noun)
)

def r_noun_X_TOJE_noun(_n1,_tobe,_n2,_too): return StC([
    I(nodep=_n1),
    I(nodep=S('--',_tobe.attrs)),
    I(nodep=S('тоже',_too.attrs)),
    I(nodep=_n2, rod=_n1.rod)
])
def r_noun_X_TOJE_NE_noun(_n1,_tobe,_not,_n2,_too): return StC([
    I(nodep=_n1),
    I(nodep=S('--',_tobe.attrs)),
    I(nodep=S('тоже',_too.attrs)),
    I(nodep=S('не',_not.attrs)),
    I(nodep=_n2, rod=_n1.rod)
])
def re_ETO_X_TOJE_noun(_n1,_tobe,_n2,_too): return StC([
    I(nodep=CW('этот',_n1), rod='s'),
    I(nodep=S('тоже',_too.attrs)),
    I(nodep=_n2, attrs_from_left = _tobe.attrs)
])
def re_TO_X_TOJE_noun(_n1,_tobe,_n2,_too): return StC([
    I(nodep=CW('тот',_n1), rod='s'),
    I(nodep=S('тоже',_too.attrs)),
    I(nodep=_n2, attrs_from_left = _tobe.attrs)
])


# ###### p_TOBE
# r_EST

# In[30]:


@debug_pp
def p_TOBE(s,p): return p_alt(s,p,
    seq([W('be')],r_EST),
    seq([W('am')],r_EST),
    seq([W('is')],r_EST),
    seq([W('are')],r_EST)
)
def r_EST(_v): return StVerb([
    I(maindep=CW('есть (быть)',_v)),
])


# ###### p_TOBE_noun
# rv_TOBE_noun(r_EST_noun_ip, r_JAVLYATSA_noun_tp)

# In[31]:


@debug_pp
def p_TOBE_noun(s,p): return p_alt(s,p,
    seq([p_TOBE, p_noun], rv_TOBE_noun),
#    seq([p_tobe, W('no'), alt(p_noun,D(dict_pronoun_dp))], r_NE_IMET_noun_vp),
    p_TOBE
)
def r_EST_noun_ip(_v,_n): return StVerb([
    I(maindep=CW('есть (быть)',_v)),
    I(ip=_n,   pad='ip')
])
def r_JAVLYATSA_noun_tp(_v,_n): return StVerb([
    I(maindep=CW('являться',_v)),
    I(tp=_n,   pad='tp')
])
rv_TOBE_noun = RuleVars('r_EST_noun_ip',dict_funs(r_EST_noun_ip, r_JAVLYATSA_noun_tp))


# ###### p_tobe_question
# r_GDE_noun_ip, r_noun_noun_question, r_noun_question, r_noun_adj_question, r_noun_where_TOO_question, r_CHTO_ETO, r_CHTO_TAKOE_noun_ip

# In[32]:


@debug_pp
def p_tobe_question(s,p): return p_alt(s,p,
    seq([p_TOBE,p_noun_ip],r_noun_question),
    seq([p_TOBE,p_noun_ip,p_adj],r_noun_adj_question),
    seq([W('what'),p_TOBE,W('this')],r_CHTO_ETO),
    ELSE,
    seq([W('what'),p_TOBE,p_noun_ip],r_CHTO_TAKOE_noun_ip),
    seq([W('where'),p_TOBE,p_noun_ip],r_GDE_noun_ip),
    seq([W('what'),W('colour'),p_TOBE,p_noun_ip],r_KAKOGO_TSVETA_noun_ip),
    seq([p_TOBE,p_noun_ip,p_noun],r_noun_noun_question),
    seq([p_TOBE,p_noun_ip,p_where,W('too')],r_noun_where_TOO_question)
)
def r_CHTO_ETO(what,_v,this): return StC([
    I(nodep=S('что',what.attrs), attrs_from_right=_v.attrs),
    I(nodep=S('это',this.attrs))
])
def r_CHTO_TAKOE_noun_ip(what,_v,_n): return StC([
    I(nodep=S('что',what.attrs)),
    I(nodep=S('такое',what.attrs), attrs_from_right=_v.attrs),
    I(nodep=_n, pad='ip')
])
def r_GDE_noun_ip(where,_v,_n): return StC([
    I(nodep=S('где',where.attrs), attrs_from_right=_v.attrs),
    I(nodep=_n, pad='ip')
])
def r_KAKOGO_TSVETA_noun_ip(what,color,_v,_n): return StC([
    I(nodep=S('какого',what.attrs)),
    I(nodep=S('цвета',color.attrs), attrs_from_right=_v.attrs),
    I(nodep=_n, pad='ip')
])
def r_noun_noun_question(_v,_n1,_n2): return StC([
    I(nodep=_n1, pad='ip'),
    I(nodep=S('--')),
    I(nodep=_n2, pad='ip')
])
def r_noun_adj_question(_v,_n,_a): return StC([
    I(nodep=_n, pad='ip'),
    I(nodep=S('--')),
    I(nodep=_a, pad='ip', rod=_n.rod)
])
def r_noun_question(_v,_n): return StC([
    I(nodep=_n, pad='ip'),
])
def r_noun_where_TOO_question(_v,_n,_wh,too): return StC([
    I(nodep=_n, pad='ip'),
    I(nodep=S('тоже', too.attrs)),
    I(nodep=_wh),
])


# ## Глагол с дополнениями

# ###### разделяемые правила
# r_verb_noun_vp, r_verb_noun_dp

# In[33]:


# разделяемые правила
def r_verb_noun_vp(_v,_p): return StVerb([
    I(maindep= _v),
    I(vp=_p,   pad='vp')
])
def r_verb_noun_dp(_v,_p): return StVerb([
    I(maindep= _v),
    I(dp=_p,   pad='dp')
])


# ###### p_verb3_komu

# In[34]:


# сделать кому-то
@debug_pp
def p_verb3_komu(s,p): return p_alt(s,p,
    seq([D(dict_verb_komu), p_noun_dp], r_verb_noun_dp),
    D(dict_verb_komu)
)
# r_verb_noun_dp - разделяемое


# ###### p_verb3_komu_chto
# r_verb_c_phrase, r_verb_q_text, r_verb_c_q_text

# In[35]:


# сделать кому-то что-то
@debug_pp
def p_verb3_komu_chto(s,p): return p_alt(s,p,
    seq([p_verb3_komu,                D(dict_pronoun_dp)], r_verb_noun_dp),
    ELSE,
    seq([ p_verb3_komu,                 p_noun        ], r_verb_noun_vp),
    seq([ p_verb3_komu, W(':'),         p_phrase      ], r_verb_c_phrase),
    seq([ p_verb3_komu,         W('"'), p_text, W('"')], r_verb_q_text),
    seq([ p_verb3_komu, W(':'), W('"'), p_text, W('"')], r_verb_c_q_text), 
    p_verb3_komu
)
# r_verb_noun_vp - разделяемое
# r_verb_noun_dp - разделяемое
def r_verb_c_phrase(_v,c,_p): return StVerb([
    I(maindep=_v),
    I(punct=c),
    I(nodep=_p)
])
def r_verb_q_text(_v,q1,_p,q2): return StVerb([
    I(maindep=_v),
    I(punct=q1, add_changers={ch_open}),
    I(nodep=_p),
    I(punct=q2),
])
def r_verb_c_q_text(_v,c,q1,_p,q2): return StVerb([
    I(maindep=_v),
    I(punct=c),
    I(punct=q1, add_changers={ch_open}),
    I(nodep=_p),
    I(punct=q2),
])


# ###### p_verb2
# re_verb_OT_noun_DO_noun, r_verb_dops

# In[36]:


# глагол с дополнением
@debug_pp
def p_verb2(s,p): return p_alt(s,p,
    seq([D(dict_verb_simple),W('from'),p_noun,W('to'), p_noun],re_verb_OT_noun_DO_noun),
    ELSE,
    seq([D(dict_verb_simple), p_dops],r_verb_dops),
    D(dict_verb_simple)
)

def r_verb_dops(_v,_d): return StVerb([
    I(maindep=_v),
    I(nodep=_d)
])
def re_verb_OT_noun_DO_noun(_v,ot,_n1,do,_n2): return StVerb([
    I(maindep=_v),
    I(nodep=S('от',ot.attrs)),
    I(nodep=_n1,  pad='rp'),
    I(nodep=S('до',do.attrs)),
    I(nodep=_n2,  pad='rp')
])


# ###### p_verb3_simple

# In[37]:


# сделать что-то
@debug_pp
def p_verb3_simple(s,p): return p_alt(s,p,
    seq([p_verb2, p_noun], r_verb_noun_vp),
    p_verb2
)
# r_verb_noun_vp - разделяемое


# ###### p_verb3_1

# In[38]:


# сделать (кому-то что-то)
@debug_pp
def p_verb3_1(s,p): return p_alt(s,p,
    p_verb3_simple,
    p_verb3_komu_chto,
    p_HAVE_noun,
    p_TOBE_noun,
)


# ###### p_verb3
# r_CAN_verb

# In[39]:


# могу сделать
@debug_pp
def p_verb3(s,p): return p_alt(s,p,
    seq([W('can'), p_verb3_1],r_CAN_verb),
    p_verb3_1
)
def r_CAN_verb(c,v): return StVerb([
    I(maindep=CW('мочь',c)),
    I(nodep=v,   form='neopr')
])


# ## Глагол(ы) с подлежащим, или другой формы

# ###### p_noun_verb1
# r_noun_verb, r_noun_TOZHE_verb

# In[40]:


# некто делает
@debug_pp
def p_noun_verb1(s,p): return p_alt(s,p,
    pe_noun_HAVE_noun,
    pe_noun_HAVE,
    pe_noun_TOBE_noun,
    pe_noun_TOBE_noun_TOO,
ELSE,
    pe_noun_TOBE_where,
    pe_noun_TOBE_where_TOO,
    seq([p_noun_ip,p_TOBE,W('not'),p_noun],r_noun_X_NE_noun),
    seq([ p_noun_ip , p_verb3 ],r_noun_verb),
    seq([ p_noun_ip, p_verb3, W('too') ],r_noun_TOZHE_verb), #ELSE, # переход к следующему уровню
)

def r_noun_verb(n,v): return StVerb([
    I(ip=n),
    I(main=v,   form='nast', pers=n.pers, chis=n.chis, rod=n.rod)
])
def r_noun_TOZHE_verb(_n, _v, _t): return StVerb([
    I(ip=_n),
    I(nodep=S('тоже',_t.attrs)),
    I(main=_v,   form='nast', pers=_n.pers, chis=_n.chis, rod=_n.rod)
])


# ###### p_verb1
# r_to_verb, rv_rule_povel_verb(r_povel_verb_ed, r_povel_verb_mn)

# In[41]:


# некто делает/ делать/ делай
@debug_pp
def p_verb1(s,p): return p_alt(s,p,
    p_noun_verb1,
    seq([ W('to'), p_verb3 ],r_to_verb),   #ELSE, # переход к следующему уровню
    seq([ p_verb3 ],rv_rule_povel_verb)
)
def r_to_verb(_t,_v): return StVerb([
    I(maindep=_v,         form='neopr', attrs_from_left=_t.attrs)
])

def r_povel_verb_ed(_v): return StVerb([
    I(maindep=_v, asp='sov', form='povel',chis='ed') #
])
def r_povel_verb_mn(_v): return StVerb([
    I(maindep=_v, asp='sov', form='povel',chis='mn') # asp='sov',
])
rv_rule_povel_verb = RuleVars('r_povel_verb_ed',dict_funs(r_povel_verb_ed,r_povel_verb_mn))


# ###### p_verb
# r_verb_NO_verb, r_verb_c_verb, r_verb_I_verb, re_U_noun_EST_noun_C_noun_I_verb

# In[42]:


# сделать одно и/но сделать сдругое
@debug_pp
def p_verb(s,p): return p_alt(s,p,
    seq([ p_noun_ip, px_HAVE_HAS, p_noun1, W(',')  , p_noun,  W('and'), p_verb1 ],re_U_noun_EST_noun_C_noun_I_verb),
    ELSE,
    seq([ p_verb1, W(','), p_verb1 ]          ,r_verb_c_verb),   
    seq([ p_verb1, W(','), W('but'), p_verb1 ],r_verb_NO_verb),   
    seq([ p_verb1, W('and'), p_verb1 ]        ,r_verb_I_verb),
    #ELSE, # переход к следующему уровню
    p_verb1
)

def r_verb_NO_verb(_v1_,_c_,_but_,_v2_):    return StC([
    I(nodep=_v1_),
    I(nodep=_c_),
    I(nodep=S('но',_c_.attrs)),
    I(nodep=_v2_)
])

def r_verb_c_verb(_v1_,_c_,_v2_):    return StC([
    I(nodep=_v1_),
    I(nodep=_c_),
    I(nodep=_v2_)
])

def r_verb_I_verb(_v1_,_i_,_v2_):    return StC([
    I(nodep=_v1_),
    I(nodep=S('и',_i_.attrs)),
    I(nodep=_v2_)
])

def re_U_noun_EST_noun_C_noun_I_verb(_n1_,_h_,sn,c,n,_i_,_v2_):    return StC([
    I(nodep=StC([
        I(nodep=StC([
            I(nodep=S('у')),
            I(nodep=_n1_,   pad='rp', npad='n' )# у Него
        ]), pull_attrs=1 ),
        I(nodep=S('есть',_h_.attrs)),
        I(nodep=StNoun([
            I(dep=sn),
            I(punct=S(',',c.attrs)),
            I(dep=n)
        ],c='mn', p='ip',o=False,r='m'))
    ])),
    I(nodep=S('и',_i_.attrs)),
    I(nodep=_v2_)
])


# ## Фразы, предложения, текст

# ###### p_phrase
# r_DA_ETO_TAK, r_NET_ETO_NE_TAK, r_DA_COMMA_verb, r_NET_COMMA_verb, r_noun_COMMA_verb, r_SPASIBO

# In[43]:


@debug_pp
def p_phrase(s,p): 
    return p_alt(s,p,
        seq([W('yes'),W(','),D(dict_pronoun_ip),p_TOBE],r_DA_ETO_TAK),
        ELSE,
        seq([W('no'),W(','),D(dict_pronoun_ip),p_TOBE,W('not')],r_NET_ETO_NE_TAK),
        p_verb,    #ELSE,
        p_noun_ip,    #ELSE,
        p_noun_dp, #ELSE,
        p_dop,
        D(dict_other),
        seq([W('yes'),W(','),p_verb],r_DA_COMMA_verb),
        seq([W('no') ,W(','),p_verb],r_NET_COMMA_verb),
        seq([p_noun  ,W(','),p_verb],r_noun_COMMA_verb),
        seq([W('thank'),W('you')],r_SPASIBO),
    )

def r_SPASIBO(th,you):  return S('спасибо',th.attrs)

def r_DA_ETO_TAK(yes,comma,_pn,_be):    return StC([
    I(nodep=S('да',yes.attrs)),
    I(nodep=comma),
    I(nodep=S('это',_pn.attrs)),
    I(nodep=S('так',_be.attrs))
])

def r_NET_ETO_NE_TAK(no,comma,_pn,_be,_not):    return StC([
    I(nodep=S('нет',no.attrs)),
    I(nodep=comma),
    I(nodep=S('это',_pn.attrs)),
    I(nodep=S('не',_not.attrs)),
    I(nodep=S('так',_be.attrs))
])

def r_DA_COMMA_verb(yes,comma,_v):    return StC([
    I(nodep=S('да',yes.attrs)),
    I(nodep=comma),
    I(nodep=_v)
])

def r_NET_COMMA_verb(no,comma,_v):    return StC([
    I(nodep=S('нет',no.attrs)),
    I(nodep=comma),
    I(nodep=_v)
])

def r_noun_COMMA_verb(_n,comma,_v):    return StC([
    # обращение
    I(nodep=_n),
    I(nodep=comma),
    I(nodep=_v)
])


# ###### p_question_phrase
# r_noun_COMMA_tobe_question, r_have_question_COMMA_noun, r_verb_COMMA_tobehave_question

# In[44]:


@debug_pp
def p_question_phrase(s,p): return p_alt(s,p,
    seq([alt(p_tobe_question,p_have_question),W(','),p_noun_ip],r_tobehave_question_COMMA_noun),
    ELSE,
    p_have_question,
    p_tobe_question,
    seq([p_noun_ip,W(','),alt(p_tobe_question,p_have_question)],r_noun_COMMA_tobehave_question),
    seq([p_verb1,W(','),alt(p_tobe_question,p_have_question)],r_verb_COMMA_tobehave_question)
)
def r_noun_COMMA_tobehave_question(_n,comma,_q): return StC([
    I(nodep=_n),
    I(nodep=comma),
    I(nodep=_q)
])
def r_verb_COMMA_tobehave_question(_v,comma,_q): return StC([
    I(nodep=_v),
    I(nodep=comma),
    I(nodep=_q)
])
def r_tobehave_question_COMMA_noun(_q,comma,_n): return StC([
    I(nodep=_q),
    I(nodep=comma),
    I(nodep=_n)
])


# ###### p_sentence

# In[45]:


dict_proper={}# имена собственные


# In[46]:


@debug_pp
def p_sentence(s,p):
    first_capital = s[p]=='I' or ch_title in s[p].attrs.changers
    def r_sentence(ph,d):
        rez=StC([I(nodep=ph),I(punct=d)])
        if first_capital: rez.attrs.changers|={ch_sentence}
        rez.attrs.pre = prefix + rez.attrs.pre
        rez.attrs.changers|={ch_prefix}
        return rez
    restore_title=False
    if ch_title in s[p].attrs.changers and s[p] not in dict_proper:
        s[p].attrs.changers-={ch_title}
        s[p].attrs.changers|={ch_anti_sentence}# хак, реализованный в SAttrs.join()
        restore_title=True
    prefix = s[p].attrs.pre
    s[p].attrs.changers |= {ch_anti_prefix}
    try:
        rezs=p_alt(s,p,
            seq([p_phrase,alt(W('.'),W('!'),W(';'))],r_sentence),
            seq([p_question_phrase,W('?')],r_sentence)
        )
    finally:# не работает, т.к. всё закешировалось
        if restore_title:
            s[p].attrs.changers|={ch_title}
            s[p].attrs.changers-={ch_anti_sentence}
        s[p].attrs.pre = prefix
    return rezs


# ###### p_text

# In[47]:


CONTEXT_DEBUGGING = False

import bisect

def context_fetch_1(s,sentence_points,first,next_,default_variants):
    '''преобразует узел next_ в соотетствии с контекстом first

    first - указатель на первый узел
    next_ - указатель на текущий узел'''
    #global CONTEXT_DEBUGGING

    def current_rule(rule_group):
        '''превращает rule_group в строку - для отладки'''
        return '<'+str(id(rule_group))+'>'+            str(rule_group.default)+            '('+repr_rule(rule_group.vars[rule_group.default])+')'

    def update_cache(oldrez,newrez):
        '''в кэше oldrez заменяет на newrez'''
        if hasattr(oldrez.parse_info,'patterns'):
            for pat in oldrez.parse_info.patterns:
                if callable(pat):
                    cache = parse_system.global_cache
                    fn = (oldrez.parse_info.p_start,pat.__name__)
                    if fn in cache:
                        yes = False
                        for i in range(len(cache[fn])):
                            if cache[fn][i][1] is oldrez:
                                if yes: raise TextError('в кэше дублируется результат')
                                yes = True
                                cache[fn][i] = (cache[fn][i][0],newrez,cache[fn][i][2])
                        if not yes:  raise TextError('в кэше не найден результат')

    if first is next_: # дошли до контекстного узла
        assert first.context_info.context, first
        rule_group = first.context_info.context
        # находим номер текущего предложения
        ns = bisect.bisect_right(sentence_points,first.context_info.pos)-1
        if CONTEXT_DEBUGGING: print('на входе',current_rule(rule_group))
        # выбираем правило

    # ----------
        def tmp_rez_checker(rez):
            assert isinstance(rez,classes.Struct) or type(rez)==S or type(rez)==str, (type(rez),rez)
            return rez

        old_checker = parse_system.rez_checker
        parse_system.rez_checker = tmp_rez_checker
        old_context_enabled = parse_system.ContextInfo.enabled
        parse_system.ContextInfo.enabled = False
        try:
            # по всем селекторам
            for start, stop, p_selector in rule_group.selectors:
                if ns+start<0 or ns+stop>len(sentence_points):
                    continue
                # запускаем с нужной позиции
                tmp = p_selector(s,sentence_points[ns+start])
                # проверяем позицию всех результатов
                assert all([p1==(
                    len(s) if ns+stop==len(sentence_points) else sentence_points[ns+stop]
                    ) for p1,r1 in tmp])
                # отбрасываем None, если результатов нет, идем дальше
                tmp = [(p1,r1) for p1,r1 in tmp if r1!=None]
                # берем первый результат
                if len(tmp):
                    if CONTEXT_DEBUGGING and len(tmp)>1: 
                        print('больше одного варианта контекста')
                    rez = tmp[0][1]
                    break
            else:
                if CONTEXT_DEBUGGING: print('выбираем вариант по умолчанию')
                rez = rule_group.default
        finally:
            parse_system.rez_checker = old_checker
            parse_system.ContextInfo.enabled = old_context_enabled
        if CONTEXT_DEBUGGING: 
            print('выбрали ',rez)
            
        #  если строка - запоминаем его, получаем результат
        if type(rez)==str:
            if not id(rule_group) in default_variants:
                default_variants[id(rule_group)] = (rule_group,rule_group.default)
            rule_group.select(rez)
            if CONTEXT_DEBUGGING: print('selected',id(rule_group),rez)
            rez = rule_group.vars[rez]
        # если есть аргументы - применяем его и получаем результат
        if first.context_info.args:
            newrez = rez(*first.context_info.args)
        else:
            newrez = deepcopy(rez)
        # подготавливаем и возвращаем результат
        rule_group = copy(rule_group) # для parse_info
        assert len(first.context_info.first_context)==0
        newrez.parse_info = copy(first.parse_info)
        if ParseInfo.enabled:
            newrez.parse_info.rule_group = rule_group
        update_cache(first,newrez)
        return rez_checker(newrez)
    # ----------
        go_break = False
        for k in range(1,len(rule_group)): # по всем правилам
            j = 0
            for n,test in rule_group[k][1]: # по всем тестам данного правила
                if ns+n>=0 and test(s,first.context_info.pos,sentence_points[ns+n]):
                    tmp = rule_group[0]
                    rule_group[0] = k
                    if CONTEXT_DEBUGGING: print('set',id(rule_group),k)
                    if not id(rule_group) in default_variants:
                        default_variants[id(rule_group)] = (rule_group,tmp)
                    old_rule_group = rule_group
                    rule_group = copy(rule_group) # для parse_info
                    if CONTEXT_DEBUGGING:
                        print('at',first.context_info.pos,
                              'найдено правило',current_rule(old_rule_group),#current_rule(rule_group),
                              'по тесту',j,'('+str(sentence_points[ns+n])+')')
                    go_break = True
                    break
                j+=1
            if go_break: break
        else:
            if CONTEXT_DEBUGGING:
                print('at',first.context_info.pos,
                      'используем правило',current_rule(rule_group),
                      'т.к. ни один вариант не подходит')
        rule = rule_group[rule_group[0]][0]
        #if CONTEXT_DEBUGGING: print('итого',current_rule(rule_group))
        # применяем правило
        if first.context_info.args:
            newrez = rule(*args)
        else:
            newrez = deepcopy(rule)
        assert len(first.context_info.first_context)==0
        newrez.parse_info = copy(first.parse_info)
        if ParseInfo.enabled:
            newrez.parse_info.rule_group = rule_group
        update_cache(first,newrez)
        return newrez

    else: #шаг рекурсии
        first_context = next_.context_info.first_context
        for i in range(len(first_context)):
            if first_context[i][0]==first: break
        else: raise TextError('обрыв пути к контексту')
        n = first_context[i][1]
        del first_context[i]
        next_.context_info.args[n] =             context_fetch_1(s,sentence_points,first,next_.context_info.args[n],default_variants)
        newrez = next_.context_info.rule(*next_.context_info.args)
        newrez.context_info = next_.context_info
        if ParseInfo.enabled:
            newrez.parse_info = next_.parse_info
        update_cache(next_,newrez)
        return rez_checker(newrez)

def context_fetch(s,sentence_points,rez,default_variants):
    '''преобразует узел rez в соотетствии со всеми контекстами, которые указаны в узле'''
    # global parse_system.rez_checker
    while len(rez.context_info.first_context): # по всем контекстам
        # ищем независимый контекстный узел
        for first ,n in rez.context_info.first_context:
            if len(first.context_info.first_context)==0:
                break
        else:
            raise TextError('не могу выбрать подходящий контекстный узел',rez.context_info.first_context)
        rez = context_fetch_1(s,sentence_points,first,rez,default_variants)
    return rez


@debug_pp
def p_text(s,p):
    '''или последовательность предложений или 1 фраза
    p_text::= p_sentence* | p_phrase
    '''
    default_variants = {} # сюда замыкается context_fetch_1

    # p_text(s,p):
    rez=[]
    sentence_points = []
    pie = ParseInfo.enabled
    ParseInfo.enabled = True
    try:
        while p<len(s):
            sentence_points.append(p)
            rezs=maxlen_filter(p_sentence(s,p))
            if len(rezs)==0: break
            p1,r1=rezs[0] # отбрасываем остальные результаты
            p=p1
            rez.append(r1)

        if len(rez)>0:
            global CONTEXT_DEBUGGING
            if CONTEXT_DEBUGGING:
                print('--- text start ---')
                for isp in range(len(sentence_points)-1):
                    sp = sentence_points[isp]
                    nsp =sentence_points[isp+1]
                    print(sp,':',SAttrs().join(s[sp:nsp]))
                sp = sentence_points[-1]
                print(sp,':',SAttrs().join(s[sp:]))
                print('--- text end ---')
        #    rezs2 =  [(p,StC([ I(nodep=r1) for r1 in rez ]))]
            rezs2 =  [(p,StC([
                I(nodep=context_fetch(s,sentence_points,r1,default_variants)) for r1 in rez
            ]))]
        else:
            rez = maxlen_filter(alt(p_phrase,p_question_phrase)(s,p))
        #    rezs2 = [] if len(rez)==0 else [(rez[0][0],rez[0][1])]
            rezs2 = [] if len(rez)==0 else                 [(rez[0][0],context_fetch(s,sentence_points,rez[0][1],default_variants))]
    finally:
        ParseInfo.enabled = pie
        for idd,(r,n) in default_variants.items():
            #print(k)
            r.select(n)
    return rezs2
        


# In[48]:


def maxlen_filter(rezs):
    '''находит самые длинные результаты, а остальные отбрасывает
    
    если самых длинных несколько - warning
    '''
    #rezs=patt(s,p)
    m=0 # самая длинная длина
    im=set() # множество номеров результатаов с самой длинной длиной
    for i in range(len(rezs)):
        if rezs[i][0]>m:
            m=rezs[i][0]
            im={i}
        elif rezs[i][0]==m:
            im.add(i)
    long_rezs= [rezs[i] for i in im]
    if len(long_rezs)>1:
        #print(p,m,s[p:m],SAttrs().join(s))
        warning('multiple results:\n'+
            #SAttrs().join(s[p:m])+'\n'+
            '\n'.join(r.tostr() for void,r in long_rezs)
        )
            
    return [] if len(long_rezs)==0 else long_rezs


# ## Контекстные паттерны

# In[49]:


def rc_collect_all(*args):
    return StC([
            I(nodep=r1) for r1 in args
        ])
def rc_10_5(x1,x2,x3,x4,x5,x6,x7,x8,x9,x10):
    return x5
def rc_10_4(x1,x2,x3,x4,x5,x6,x7,x8,x9,x10):
    return x4
def rc_9_4(x1,x2,x3,x4,x5,x6,x7,x8,x9):
    return x4
def rc_9_3(x1,x2,x3,x4,x5,x6,x7,x8,x9):
    return x3
def rc_11_3(x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11):
    return x3
def rc_8_3(x1,x2,x3,x4,x5,x6,x7,x8):
    return x3


# In[50]:


# pc - parse context
# arc - abstract rule context
def arc_IT(rule):
    def rc_IT(*args):
        rez = rule(*args)
        assert isinstance(rez,classes.StDeclinable)
        if rez.chis=='mn': return None
        if   rez.rod=='m': return 'он'
        elif rez.rod=='g': return 'она'
        elif rez.rod=='s': return 'оно'
        else: raise TextError('wrong rod')
    return rc_IT

pc_IT_1 = alt(
            seq([W('how'), W('many'), p_noun, px_HAVE_HAS, p_noun_ip, W('?'), 
                   p_noun_ip, px_HAVE_HAS,  p_noun, W('.')
            ],arc_IT(rc_10_5)),
            seq([p_noun_ip, alt(px_HAVE_HAS,p_TOBE), p_noun, W(';'), 
                   p_noun_ip, p_TOBE,  alt(p_noun,p_where), W('.')
            ],arc_IT(rc_8_3)),
            seq([W('where'), p_TOBE, p_noun_ip, W('?'), 
                   p_noun_ip, p_TOBE,  p_where, W('.')
            ],arc_IT(rc_8_3)),
            seq([p_noun_ip,W(','),W('where'), p_TOBE, p_noun_ip, W('?'), 
                   p_noun_ip, p_TOBE,  p_where, W('.')
            ],arc_IT(rc_10_5)),
            seq([W('where'), p_TOBE, p_noun_ip, W('?'), 
                   p_noun_ip, p_TOBE,  p_where, W('too'), W('.')
            ],arc_IT(rc_9_3)),
            seq([W('what'),W('colour'),p_TOBE,p_noun_ip, W('?'), 
                   p_noun_ip, p_TOBE,  p_noun, W('.')
            ],arc_IT(rc_9_4))
)
pc_IT_2 = alt(
            seq([px_HAVE_HAS, p_noun_ip, p_noun, W(','), p_noun_ip, W('?'), 
                 p_sentence,
                 W('where'), p_TOBE, p_noun_ip, W('?')
            ],arc_IT(rc_11_3)),
            seq([px_HAVE_HAS, p_noun_ip, p_noun, W('?'), 
                 p_sentence,
                 W('where'), p_TOBE, p_noun_ip, W('?')
            ],arc_IT(rc_9_3)),
        )

dict_pronoun_ip['it'] = RuleContext('оно',dict_pronoun_ip['it'].vars,selectors = [
    (-1,1,pc_IT_1),(-2,1,pc_IT_2)
])


# ## Запуск и отладка
# 
# * `en2ru(s)` - переводит строку, возвращает строку
# * `d_en2ru(s)` - переводит строку, возвращает строку, дополнительно печатает процесс разбора
# * `pr_l_repr(s)` - печатает строку в тройных кавычках
# * `with_variants(variants,fun,s)` - устанавливает варианты, и потом вызывает fun(s).
# `variants` - список пар (RuleVars,n)
# * `decline(s,pads=['ip','rp','dp','vp','tp','pp'])` - переводит строку и выводит ее в разных падежах. Строка должна быть существительным
# * `parse_pat(patt,s)` == `patt(tokenize(s),0)`
# * `d_parse_pat(patt,s)` - дополнительно печатает процесс разбора
# * `scheme(s,detailed=1,nohtml = False)` - печатает схему разбора
#     
#     есть дополнительный аргумент datailed
#         0 - не печатает сквозные паттерны (которые без правил)
#         1 - дефолтный вывод
#         2 - дополнительно печатает нестрингифицированные объекты
# 

# In[51]:


def _en2ru(s): # main
    ''' (text|.)* + warning-и
    '''
    s=tokenize(s)
    if len(s)==0:
        warning('no tokens')
        return ''
    
    ret_s = ''
    p=0
    while p<len(s):
        #print('ITERATION',p)
        rezs= p_text(s,p)
        if len(rezs)==0:
            warning("CAN'T TRANSLATE: "+s[p])
            ret_s += (' | ' if p>0 else '')+ s[p]
            p+=1
        else:
            assert len(rezs)==1
            p1,r1 = rezs[0]
            #print(p,p1,r1)
            s1 = r1.tostr()
            #print(p,p1,r1)
            ret_s += (' | ' if p>0 else '')+ s1
            if p>0:
                warning('TRANSLATION BREAKS')
            assert p1>p, rezs
            p=p1
    return ret_s

def en2ru(s):
    '''переводит строку, возвращает строку'''
    parse_system.DEBUGGING=False
    return _en2ru(s)

def d_en2ru(s):
    '''переводит строку, возвращает строку
    
    дополнительно пишет отладочный вывод разбора'''
    l_d = parse_system.DEBUGGING
    parse_system.DEBUGGING=True
    try:
        r=_en2ru(s)
    finally:
        parse_system.DEBUGGING=l_d
    return r

def c_en2ru(s):
    '''переводит строку, возвращает строку
    
    дополнительно пишет отладочный вывод поиска контекстов'''
    global CONTEXT_DEBUGGING
    l_d = CONTEXT_DEBUGGING
    CONTEXT_DEBUGGING=True
    try:
        r=_en2ru(s)
    finally:
        CONTEXT_DEBUGGING=l_d
    return r

def pr_l_repr(s):
    """печатает строку в тройных кавычках"""
    print("'''"+s+"'''")
    


# In[52]:


def with_variants(variants,fun,s):
    '''variants - список пар (RuleVars,n)'''
    saves = {}
    for k,v in variants:
        saves[id(k)]=k.default
        k.select(v)
    try:
        s = fun(s)
    finally:
        for k,v in variants:
            k.select(saves[id(k)])
    return s


# In[53]:


def decline(s,pads=['ip','rp','dp','vp','tp','pp']):
    s=tokenize(s)
    # добавить дочитывание точки и остаточных пробелов
    rezs=[res for pos,res in p_noun(s,0) if pos==len(s)]
    if len(rezs)!=1:
        raise TextError(rezs)
    tmp=rezs[0]
    
    m=[]
    for p in pads:
        #print(str(tmp))
        prompt=             '' if p=='ip' else            'нет ' if p=='rp' else            'дать ' if p=='dp' else            'вижу ' if p=='vp' else            'творю ' if p=='tp' else            'думаю о ' if p=='pp' else            throw(ValueError('bad pad: '+p))
        #rez=deepcopy(tmp)
        tmp.pad=p
        m.append(prompt+tmp.tostr())#        print(prompt+str(tmp))
    return m


# In[54]:


def _parse_pat(patt,s):
    s=tokenize(s)
    return patt(s,0)

def parse_pat(patt,s):
    '''парсит строку паттерном, и возвращает не стрингифицированный объект'''
    parse_system.DEBUGGING=False
    return _parse_pat(patt,s)

def d_parse_pat(patt,s):
    '''парсит строку паттерном, и возвращает не стрингифицированный объект
    
    дополнительно пишет отладочный вывод'''
    l_d = parse_system.DEBUGGING
    parse_system.DEBUGGING=True
    try:
        r=_parse_pat(patt,s)
    finally:
        parse_system.DEBUGGING=l_d
    return r


# In[55]:


from IPython.core.display import HTML

def sch_print_rez0(rez,depth,s,detailed):
    '''выводит исходное дерево слева направо'''
    info = rez.parse_info
    if hasattr(info,'p_start'):
        print('  '*depth+' '+SAttrs().join( s[info.p_start : info.p_end] ))
    if hasattr(info,'patterns') or hasattr(info,'rule_group'):
        if hasattr(info,'patterns'):
            #'<'+str(id(info.patterns))+'>'+
            patterns = ' '.join(info.patterns2str()) if detailed>=1 else info.patterns2str()[0]
        else:
            patterns = ''
        if hasattr(info,'rule_group'):
            if type(info.rule_group)==list:
                n = info.rule_group[0] if info.rule_group[0]!=0 else 1
                rule = info.rule_group[n]
                rules = str(n)+'/'+str(len(info.rule_group)-1)+' '
            else:
                rule = info.rule_group
                rules = ''
            rules += (rule.__name__ if callable(rule) else str(rule))
        else:
            rules = ''
        print('  '*depth +' '+ patterns+' -> '+rules)
    print('  '*depth+'*'+str(rez))
    print('  '*depth+'*'+repr(rez))

    if hasattr(rez,'talk'):
        for x in rez.talk:
            sch_print_rez0(x[1],depth+1,s,detailed)

# создание узлов (+ преобразование rule_group)
# ! - было исключение
# ? - есть отключенные исключения
class Node:
    __slots__ = ['childs','p_start','p_end','patterns','rule','rez','str','html']
    def make_html(self,cols,DISTANCE):
        l = '_'*(cols[self.p_end]-cols[self.p_start]-DISTANCE)
        
        patts=[]
        elseflag = False
        disabled_exc = False
        for p in self.rez.parse_info.patterns:
            if p=='__ELSE__':
                elseflag = True
            elif type(p)==RuleVars:
                disabled_exc = True
            else:
                s = ''
                if disabled_exc:
                    disabled_exc = False
                    s+='?'
                if elseflag:
                    elseflag = False
                    s+='!'
                if len(s)!=0: s+=' '
                ps = p.__name__ if callable(p) else p['__name__']
                if len(patts)==0:
                    s+='<a href="#'+ps+'">'+ps+'</a>'
                else:
                    s+='(<a href="#'+ps+'">'+ps+'</a>)'
                patts.append(s)
        
        p0 = patts[0]
        r = self.rule
        s = self.str
        pp = '<br>'.join(patts[1:])
        
        self.html = l+'<br>'+p0+'<br>'+r+'<br>'+s+'<br>'+pp
        
def sch_make_tree(struct):
    '''возвращает пару (глубина, [Node-ы])'''
    if hasattr(struct,'talk'):
        if hasattr(struct.parse_info,'p_start'):
            info = struct.parse_info
            node = Node()
            node.p_start = info.p_start
            node.p_end = info.p_end
            node.patterns = info.patterns2str()
            if hasattr(info,'rule_group'):
                if isinstance(info.rule_group,RuleVars):
                    assert info.rule_group.default!=None, info.rule_group
                    rule = info.rule_group.get_default()
                    rules= ('c-' if type(info.rule_group)==RuleContext else '')+                        str(info.rule_group.default)+'/'+str(len(info.rule_group.vars))+' '
                else:
                    rule = info.rule_group
                    rules = ''
                node.rule = rules + (rule.__name__ if callable(rule) else str(rule))
            else:
                node.rule = ''
            node.rez = struct
            node.childs = []
            depth = 0
            for tup in struct.talk:
                d,m = sch_make_tree(tup[1])
                if d>depth: depth = d
                node.childs+=m
            node.childs.sort(key=lambda node:node.p_start)
            return (depth+1,[node])
        else:
            mm = []
            depth = 0
            for tup in struct.talk:
                d,m = sch_make_tree(tup[1])
                if d>depth: depth = d
                mm+=m
            return (depth,mm)
    elif hasattr(struct.parse_info,'p_start'):
        # получется, всё, что не является структурой - обязано содержать parse_info ?
        info = struct.parse_info
        node = Node()
        node.p_start = info.p_start
        node.p_end = info.p_end
        node.patterns = info.patterns2str()
        if hasattr(info,'rule_group'):
            if isinstance(info.rule_group,RuleVars):
                rule = info.rule_group.get_default()
                rules= ('c-' if type(info.rule_group)==RuleContext else '')+                    str(info.rule_group.default)+'/'+str(len(info.rule_group.vars))+' '
            else:
                rule = info.rule_group
                rules = ''
            node.rule = rules + (rule.__name__ if callable(rule) else str(rule))
        else:
            node.rule = ''
        node.rez = struct
        node.childs = []
        return (1,[node])
    else:
        return (0,[])

def sch_print_rez1(info,depth,s):
    '''выводит преобразованное дерево слева направо'''
    if hasattr(info,'p_start'):
        print('  '*depth+' '+SAttrs().join( s[info.p_start : info.p_end] ))
    patterns = ' '.join(info.patterns) if full else info.patterns[0]
    print('  '*depth +' '+ patterns+' -> '+info.rule)
    print('  '*depth+'*'+str(info.rez))

    if hasattr(info,'childs'):
        for x in info.childs:
            sch_print_rez1(x,depth+1,s)

def sch_make_lines(node,lines,cols,DISTANCE):
    '''преобразует дерево в таблицу'''
    dd=0 # уровень, номер Лайна. У детей меньше чем у родителей.
    for c in node.childs:
        d = sch_make_lines(c,lines,cols,DISTANCE)
        if d>dd: dd = d

    # приводим результат к текстовой форме
    node.str = repr(node.rez.tostr())[1:-1]
    # приводим паттерны в надлежащий вид
    for i in range(1,len(node.patterns)):
        node.patterns[i] = '('+node.patterns[i]+')'

    # вычисляем кол-во строк в Лайне
    if len(node.patterns)>lines[dd].h: lines[dd].h = len(node.patterns)

    # длина строки в символах
    maxlen = max(len(node.rule),len(node.str),max([len(i) for i in node.patterns]))
    dlen = (maxlen+DISTANCE) - (cols[node.p_end]-cols[node.p_start])
    #print(node.str,maxlen,dlen)
    # модифицируем позиции столбцов
    if dlen>0:
        for i in range(node.p_end,len(cols)):
            cols[i]+=dlen

    # присваиваем объект в таблицу
    lines[dd].line[node.p_start] = node
    return dd+1

def sch_print_table(s,cols,lines,DISTANCE,detailed):
    def inde(s,p_start,p_end):
        '''дополняет строку пробелами, чтобы заполнить нужные ячейки'''
        return s+' '*(cols[p_end]-cols[p_start]-len(s))

    # выводим исходную строку
    for i in range(len(s)):
        print(inde(s[i],i,i+1),end='')
    print()

    for line_ in lines:
        line=line_.line

        # _______
        i=0
        l=''
        while i<len(s):
            if line[i]==None:
                l+=inde('',i,i+1)
                i+=1
            else:
                l+='_'*(cols[line[i].p_end]-cols[line[i].p_start]-DISTANCE)+' '*DISTANCE
                i=line[i].p_end
        print(l)

        # patterns[0]
        i=0
        l=''
        while i<len(s):
            if line[i]==None:
                l+=inde('',i,i+1)
                i+=1
            else:
                l+=inde(line[i].patterns[0],line[i].p_start,line[i].p_end)
                i=line[i].p_end
        print(l)

        # rule
        i=0
        l=''
        while i<len(s):
            if line[i]==None:
                l+=inde('',i,i+1)
                i+=1
            else:
                l+=inde(line[i].rule,line[i].p_start,line[i].p_end)
                i=line[i].p_end
        print(l)

        # rez
        i=0
        l=''
        while i<len(s):
            if line[i]==None:
                l+=inde('',i,i+1)
                i+=1
            else:
                l+=inde(line[i].str,line[i].p_start,line[i].p_end)
                i=line[i].p_end
        print(l)

        # patterns[j]
        if detailed>=1:
            for j in range(1,line_.h):
                i=0
                l=''
                while i<len(s):
                    if line[i]==None or j>=len(line[i].patterns):
                        l+=inde('',i,i+1)
                        i+=1
                    else:
                        l+=inde(line[i].patterns[j],line[i].p_start,line[i].p_end)
                        i=line[i].p_end
                print(l)

def scheme_pat(patt,s,detailed=1,nohtml = False):
    '''печатает схему разбора
    
    есть дополнительный аргумент datailed
        0 - не печатает сквозные паттерны (которые без правил)
        1 - дефолтный вывод
        2 - дополнительно печатает нестрингифицированные объекты
    '''
    # токенизируем строку
    s=tokenize(s)
    
    # парсим строку
    ParseInfo.enabled = True
    try:
        rezs=debug_pp(patt)(s,0)
    finally:
        ParseInfo.enabled = False
        
    return scheme_print(s,rezs,detailed,nohtml)
        
def scheme(s,detailed=1,nohtml = False):
    '''печатает схему разбора
    
    есть дополнительный аргумент datailed
        0 - не печатает сквозные паттерны (которые без правил)
        1 - дефолтный вывод
        2 - дополнительно печатает нестрингифицированные объекты
    '''
    # токенизируем строку
    s=tokenize(s)
    
    # парсим строку
    ParseInfo.enabled = True
    try:
        rezs=maxlen_filter(alt(p_sentence,p_phrase,p_question_phrase)(s,0))
    finally:
        ParseInfo.enabled = False
        
    return scheme_print(s,rezs,detailed,nohtml)
        
def scheme_print(s,rezs,detailed=1,nohtml = False):
    '''печатает схему разбора
    
    есть дополнительный аргумент datailed
        0 - не печатает сквозные паттерны (которые без правил)
        1 - дефолтный вывод
        2 - дополнительно печатает нестрингифицированные объекты
    '''
    hstr = '' # html_str
    def h_print(s=''):
        nonlocal nohtml
        if nohtml:
            print(s)
        else:
            nonlocal hstr
            hstr+=s+'\n'
        
    h_print(str(len(rezs))+' результатов')
    # анализируем каждый результат
    for end,rez in rezs:
        h_print()
        # простой построчный вывод узлов результата
        if detailed==2:
            rez.pull_deferred()
            sch_print_rez0(rez,0,s,detailed)
        
        # простой вывод узлов
        if 0:
            rez.pull_deferred()
            
        # создание дерева
        depth,mm = sch_make_tree(rez)
        assert len(mm)==1, mm
        tree=mm[0]
        
        # простой вывод узлов
        if 0:
            print('depth=',depth)
            sch_print_rez1(tree,0,s)
        
        DISTANCE = 2
        cols = [] # позиции столбцов - кол-во символов от начала строки до начала столбца
        pos=0
        for word in s:
            cols.append(pos)
            pos+=len(word)+DISTANCE
        cols.append(pos)
        
        class Line:
            __slots__=['h','line']
            def __init__(self,h,l):
                self.h = h      # количество строчек в чинии
                self.line = l   # список объектов (Node-ов) по столбцам
                
        lines = [Line(0,[None for i in range(len(s))]) for j in range(depth)]
        dd = sch_make_lines(tree,lines,cols,DISTANCE)
        assert dd==depth
        
        if nohtml:
            sch_print_table(s,cols,lines,DISTANCE,detailed)
        
        else:
            def make_html(n):
                n.make_html(cols,DISTANCE)
                for i in n.childs:
                    make_html(i)
            make_html(tree)

            ss = '<tr>'+''.join(['<td>'+si+'</td>' for si in s])+'</tr>\n'
            for ll in lines:
                sl = '<tr>\n'
                p_end=0
                for l in ll.line:
                    if l!=None:
                        sl+='<td></td>'*(l.p_start-p_end)
                        sl+='<td colspan="'+str(l.p_end-l.p_start)+'">'+l.html+'</td>\n'
                        p_end = l.p_end
                ss+=sl+'</tr>\n\n'

            h_print('<table>'+ss+'\n</table>\n')

    if not nohtml:
        return HTML(hstr)
           


# In[56]:


def cache_stat():
    stat = {}
    for (pos,fun),v in parse_system.global_cache.items():
        if pos in stat:
            stat[pos]+=1
        else:
            stat[pos]=1
    {k:(
        [(d[0],str(d[1])) for d in v] \
        #len(v)\
        if type(v)==list 
        else v
    ) for k,v in parse_system.global_cache.items() }
    if len(stat)>0:
        print(sum(stat)/len(stat))
    return stat
cache_stat()


# # Тесты

# In[57]:


en2ru('I see jam and one cup.')


# In[58]:


import inspect
lines = inspect.getsource(en2ru)
print(lines)


# In[59]:


import tests
tests = reload(tests)
tests.init(parse_system,en_dictionary,
           en2ru,with_variants,decline,scheme,d_en2ru,pr_l_repr,
           p_noun,p_noun1,r_noun_comma_noun,rv_noun_HAVE_noun,
          1,False)
tests.test1()
tests.test2()
tests.test3()
tests.test4()
tests.test5and6()
tests.test7()
tests.test8()
tests.test8_1()
tests.test9()
tests.test10()
tests.test11()
tests.test12()
tests.test13()
tests.test14()
tests.finalize()
tests.TEST_ERRORS


# In[60]:


add_skl2('m',False,make_skl2(
'цветок'   ,'цветы',
'цветка'   ,'цветов',
'цветку'   ,'цветам',
'цветок'   ,'цветы',
'цветком'  ,'цветами',
'цветке'   ,'цветах'))
add_ennoun2('flower'  ,'flowers' ,"цветок"		,"цветы"	  ,'m',False)
add_ennoun2('rose'  ,'roses' ,"роза"		,"розы"	  ,'g',False)
add_ennoun2('violet'  ,'violets' ,"фиалка"		,"фиалки"	  ,'g',False)
add_ennoun2('bird'  ,'birds' ,"птица"		,"птицы"	  ,'g',True)
add_ennoun2('cage'  ,'cages' ,"клетка"		,"клетки"	  ,'g',False)
add_ennoun2('umbrella'  ,'umbrellas' ,"зонт"		,"зонты"	  ,'m',False)
add_ennoun2('umbrella'  ,'umbrellas' ,"зонт"		,"зонты"	  ,'m',False)


# In[61]:


add_ennoun1('trousers'				  ,"брюки"  ,'mn'		,'g',False,2)


# In[62]:


en2ru('what is this?')


# In[80]:


scheme('It is a flower.')


# In[81]:


en2ru('''Look, what is this? It is a flower.
These flowers are red and those flowers
are blue.''')


# In[64]:


pr_l_repr(en2ru('''What is this? It is
a rose.
What is this? It is
a violet.
Is this	a	violet	or
a	rose? It	is	a rose.
Is this	a rose too?
No, it is not.'''))


# In[65]:


pr_l_repr(en2ru('''That girl has many violets in her garden. She has
many red roses too. She
has many flowers in her
garden.'''))


# In[66]:


pr_l_repr(en2ru('''Is this a chicken?
No, it is not. What
is this? It is a bird.
Where is the bird?
It is in the cage.
Is this bird big or
little? It is little.'''))


# In[67]:


pr_l_repr(en2ru('''Is this a stick? No, it is
not. What is this? It is
an umbrella. What colour is
the umbrella? It is black.
How many umbrellas
have you? I have two umbrellas.
Give me one umbrella!'''))


# In[68]:


pr_l_repr(en2ru('''This bird is in the cage.
This girl is in the room.
That rose is red.
That flower is yellow.
This book is on the table.
This kitten is in the box.
This spoon is in the cup.
That violet is little.
That rose is good.'''))


# In[69]:


pr_l_repr(en2ru('''These birds are in the tree.
These girls are in the garden.
Those roses are red.
Those flowers are not yellow.
These books are on the table.
These kittens are under the bed.
These spoons are on the dish.
Those violets are very big.
Those roses are little.'''))


# In[70]:


pr_l_repr(en2ru('''I have good trousers. What colour are
they?
They are grey. These trousers are not
bad.'''))


# In[71]:


pr_l_repr(en2ru('''What has that girl in
her garden?
Has she many flowers
in her garden?
Where is this book?
Where are these birds?
Where is that kitten?
What colour are those
roses?
Are these trousers bad?
Is that violet big?'''))


# In[ ]:





# In[ ]:





# In[76]:


get_ipython().system('jupyter nbconvert --to script en2ru.ipynb')


# # todo

# ## составляем основную грамматику

# ```
# выбираем варианты вручную
# пока в одном тексте не начнут требоваться разные варианты одного правила
# 
# на боевое применение не выходим
# пока не будут пройдены времена глаголов
# 
# КОДИТЬ И ДЕБАЖИТЬ ТЕКУЩЕЕ
# 13) где?
# 14) какого цвета?
# 15) посмотри
# 16) что у тебя есть?
# 17) что это за <животное>?
# 18) Polly's quail
# 19) как тебя зовут?
# 20) 
# 21) сколько тебе лет?
# 22) take, give...
# 23) can
# 24) may, must
# 25) must
# 26) there is
# 27) is there?
# 28)
# 29) когда? тогда
# 30) рифма
# 31) сравнительны прилагательные
# 32) другая рифма
# 33) скороговорка
# 34) 
# 35)
# 36)
# 37)
# 38) мой, твой
# 39)
# стандартные фразы
# 3 рассказа
# 
# автовыбор склонений/спряжений прилагательных и глаголов
# сделать устранение конфликтов исключений
# 
# 
# два рыжих кота
# вижу двух рыжих котов
# вижу два горячих утюга
# два пирожных
# 
# add_skl_suffix
# ```

# In[73]:


#decline('two watches')


# In[74]:


pr_l_repr(en2ru('''
Boy: Where is your doll?
Girl: My doll is on the bed.
Boy: Where is your ball?
Girl: It is under the table.
Boy: Have you red ribbons?
Girl: Yes, I have.
Boy: Where are your red ribbons:
Girl: They are in the box.
Boy: Show me your ribbons! Thank you.
'''))


# In[75]:


en2ru('It \nis black.')


# ## придумываем способ выборов вариантов (контекстных)

# ```
# 
# git-ветка с исключениями
#     исключения на несколько предложений
#      - не правильно, контексты - не синтаксические конструкции
# git-ветка с нейросетью
#     научится...
# git-ветка с другим жестким алгоритмом
#     придумать...
# 
#     работа с деревом вглубь:
#         просмотр вглубь возможен
# 
#         у каждого узла ссылка на правило и его аргументы
#         в узлах дерева поля 
#             context_dep
#                 True - узел зависит от контекста
#                     ссылка на правило, также принимат контекст
#                 False - узел не зависит от контекста
#             context_dep_srcs - массив номеров - 
#                 какие аргументы правила зависят от контекста (или их потомки зависят от контекста)
#                 т.е. какие аргументы правила требую ремейка в случае изменения контекста
# 
#             context(может отсутствовать) - словарь (строка, ссылка на узел), который является контекстом
#                 - устанавливается в правилах
#         функция context_remake(node,context)
# 
# статистика использования паттернов
# статистика повторяющихся структур в тестах (разделить тесты на несвязанные предложения)
# ```

# ## __ по ходу дела по мере необходимости улучшаем гуй, в jupyter notebook-е
# виджетами и прочим  
# а также добавляем возможность переводить html и tex
#     

# ## делаем web-GUI на javascript-е
# 
# выбор паттернов и правил в зависимости от времени 

# watch, двое, трое, пятеро
# 
# scheme('it')
# 
# ...
# для больших текстов p_sentence будет делать срез со своей позции до конца
#     - чтобы обновить кэши ф-ций
# 
# исключения парсить, если регулярным образом распарсилось
#     каждая функция будет с аргументом: парсить или нет исключения
# 
# атрибуты слов: (теги)
# отображение открывающейся кавычки (SAttrs.join)
