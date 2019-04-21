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

# # Основной принцип

# ```
# p_паттерн парсит текст (str, pos), 
#     вызывая другие паттерны, возвращающие древовидные структуры
#     эти древовидные структуры передает одному из правил
#         (остальные вызовы правил закомментированы 
#             - в рамках одного текста каждый паттерн имеет ровно 1 смысл)
#     и возвращает (pos, результат этого правила), помещенный в массив
#     
#     /*пока на ошибках парсинга концентрировать не будем*/
#     если ничего не удалось распарсить, ???возвращаемый массив будет пустым???
#     если удалось распарсить несколько вариантов - в массиве будет насколько вариантов
#         сначала парсятся все исключения
#         потом парсятся все обычные варианты (если нет исключений)
# ```
# 
# ```
# r_правило получает список древовидных структур
#     обрабатывает их по определенному правилу
#     возвращает древовидную структуру
# ```
# 
# ```
# древовидная структура - map, со следующими ключами
#     type: 'noun'/'adj'/'verb'/'num'/... - определяем через isinstance()
#     постоянные параметры (для сущ.: род, число)
#     переменные параметры (для сущ.: падеж)
#     talk: массив древовидных структур
#         или пар (тип, слово), где тип - main/punct/other
# ```
# 
# ```
# str(древовидная структура)
#     превращает древовидную структуру в строку
# ```
# 
# ```
# для каждого типа элемента древовидной структуры будет map
#     где каждой строке (для сущ. - слово в и.п.) будет соответствовать
#         структура данных, которая вместе в переменными параметрами передается в 
#         sh_функция для этого типа элемента древовидной структуры
#             которая будет возвращать слово в соотв. форме (для сущ. в соотв. падеже)
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
# В дальнейшем предполагается, что будет центральная грамматика, 
# а у ее правил пользователи будут создавать исключения и расширения.
# Фишка в том, что приредактировании грамматики этим способом 
#     поведение грамматики для уже имеющихся тестов/текстов не изменится.
# Возможно периодически для оптимизации грамматики будет требоваться полная ее переработка,
# но чисто математическая и довольно вычислительно-сложная задача.
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
# Паттерн C является расширением паттерна B, если
# ...
# 
# В дальнейшем предполагается возможность каждый паттерн связывать с 
# набором правил, а точнее с одним правилом из заданного набора.
# А также возможность эти наборы пополнять.
# Одним из правил перевода исключения будет вариант, когда
# результат исключения отбрасывается а результатом становится 
# результат правила регулярного паттерна.
# Это дает возможность не сломать уже имеющийся перевод из-за добавления исключений к грамматике.
# 
# Вопрос дефолтного связывания паттернов с правилами допускает множество решений
# и остается открытым.
# В любом случае пользователь сможет создавать исключения паттернов и дополнительные правила,
# тем самым пополняя базу данных переводчика,
# а также менять связи паттернов с правилами для своего текста, сохранять эти связи,
# и применять к другим текстам.
# 
# паттерн - набор альтернатив
# альтернатива - последовательность, с которой связан набор правил
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

# In[ ]:


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


# In[ ]:


import parse_system
from parse_system import S, SAttrs, ParseInfo, tokenizer, tokenize,                        ch_title, ch_sentence, ch_anti_sentence, ch_open, ch_prefix, ch_anti_prefix,                        seq, alt, p_alt, ELSE, W, D,                        warning, debug_pp, reset_globals, global_cache
import classes
from classes import StC, StNum, StNoun, StVerb, I
import ru_dictionary
from ru_dictionary import ruwords, CW, add_runoun2, add_skl2, make_skl2
import en_dictionary
from en_dictionary import dict_adj, dict_noun, dict_pronoun_ip, dict_pronoun_dp,                         dict_numeral, dict_verb_simple, dict_verb_komu, r_adj_noun, dict_other,                        add_ennoun2, add_ennoun1, add_dict_variant,                         add_variant, remove_variant, get_variant, select_variant, variants
from importlib import reload


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

# In[ ]:


W('cat')(tokenize('cat'),0)


# ## Other

# In[ ]:


@debug_pp
def p_numeral(s,p):
    return D(dict_numeral)(s,p)


# In[ ]:


#2->
@debug_pp
def p_adj(s,p):
    return D(dict_adj)(s,p)


# ## Noun-like

# In[ ]:


@debug_pp
def p_adj_noun3(s,p): return p_alt(s,p,
    seq([ alt(W('an'),W('a')), p_noun3 ],r_A_noun),
    seq([ W('the')           , p_noun3 ],r_THE_noun),
    seq([ W('good'), W('morning') ],r_GOOD_MORNING),             
ELSE,
    seq([ p_adj, p_noun3 ],r_adj_noun)
)
# r_adj_noun определен в en_dictionary.py


# In[ ]:


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


# In[ ]:


@debug_pp
def p_noun3(s,p): return p_alt(s,p,
    p_adj_noun3, #ELSE, # переход к следующему уровню
    p_adj, #ELSE, # переход к следующему уровню
    p_numeral,
    D(dict_noun)
)


# In[ ]:


@debug_pp
def p_noun2_1(s,p): return p_alt(s,p,
    seq([ p_noun3, p_dops ], r_noun_dops), #ELSE, # переход к следующему уровню
    p_noun3
)
def r_noun_dops(n,d): return StNoun([
    I(maindep=n),
    I(nodep=d)
])


# In[ ]:


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


# In[ ]:


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
    if num.chis!=n.chis :
        warning('не совпадают числа числ. и сущ.:'+str(num)+str(n))
    return StNum([
        I(quantity=num,            chis=n.chis, rod=n.rod, odush=n.odush ),
        I(maindep=n)
    ],quantity=num.quantity)


# In[ ]:


@debug_pp
def p_noun(s,p):
    return p_alt(s,p,
        seq([ p_noun1, W('and'), p_noun ],r_noun_and_noun  ),
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
def r_noun_comma_noun(sn,c,n):    return StNoun([
    I(dep=sn),
    I(punct=S(',',c.attrs)),
    I(dep=n)
],c='mn', p='ip',o=False,r='m')


# ## Существительные в разных формах

# In[ ]:


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


# In[ ]:


# на (определенной) улице
@debug_pp
def pe_IN_THE_STREET(s,p): return p_alt(s,p,
    seq([W('in'), W('the'), W('street') ],r_NA_X_ULITSE),
)
def r_NA_X_ULITSE(v,_a,_U): return StC([
    I(nodep=S('на',v.attrs)),
    I(nodep=CW('улица',_U),pad='pp')
])


# In[ ]:


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


# In[ ]:


# где
@debug_pp
def p_where(s,p): return p_alt(s,p,
    pe_IN_adj_STREET,
    ELSE,
    seq([W('in'), p_dop_noun ],r_V_noun_pp),
    seq([W('on'), p_dop_noun ],r_NA_noun_pp),
)
def r_V_noun_pp(v,_n): return StC([
    I(nodep=S('в',v.attrs)),
    I(nodep=_n,  pad='pp'),
])
def r_NA_noun_pp(v,_n): return StC([
    I(nodep=S('на',v.attrs)),
    I(nodep=_n,  pad='pp'),
])


# In[ ]:


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


# In[ ]:


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

# In[ ]:


px_HAVE_HAS = alt( W('have'), W('has') )


# In[ ]:


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
rv_HOW_MANY_noun_HAVE_noun = [2,r_SKOLKO_noun_U_noun,r_SKOLKO_U_noun_noun]


# In[ ]:


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
rv_noun_HAVE_noun = [2,r_U_noun_noun, r_U_noun_EST_noun]

def r_U_noun_NET_noun(_n1_,_h_,_no_,_n2_):    return StC([
    I(nodep=StC([
        I(nodep=S('у')),
        I(nodep=_n1_,   pad='rp', npad='n' )# у Него
    ]), pull_attrs=1 ),
    I(nodep=S('нет',_h_.attrs)),
    I(nodep=_n2_,        pad='rp')
])


# In[ ]:


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


# In[ ]:


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

# In[ ]:


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


# In[ ]:


@debug_pp
def pe_noun_TOBE_noun(s,p): return p_alt(s,p,
    seq([W('this'),p_TOBE,p_noun],re_ETO_X_noun),
    seq([W('that'),p_TOBE,p_noun],re_TO_X_noun),
    ELSE,
    seq([p_noun_ip,p_TOBE,p_noun],r_noun_X_noun)
)

def r_noun_X_noun(_n1,_tobe,_n2): return StC([
    I(nodep=_n1),
    I(nodep=S('--',_tobe.attrs)),
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


# In[ ]:


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


# In[ ]:


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
rv_TOBE_noun = [1, r_EST_noun_ip, r_JAVLYATSA_noun_tp]


# ## Глагол с дополнениями

# In[ ]:


# разделяемые правила
def r_verb_noun_vp(_v,_p): return StVerb([
    I(maindep= _v),
    I(vp=_p,   pad='vp')
])
def r_verb_noun_dp(_v,_p): return StVerb([
    I(maindep= _v),
    I(dp=_p,   pad='dp')
])


# In[ ]:


# сделать кому-то
@debug_pp
def p_verb3_komu(s,p): return p_alt(s,p,
    seq([D(dict_verb_komu), p_noun_dp], r_verb_noun_dp),
    D(dict_verb_komu)
)
# r_verb_noun_dp - разделяемое


# In[ ]:


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


# In[ ]:


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


# In[ ]:


# сделать что-то
@debug_pp
def p_verb3_simple(s,p): return p_alt(s,p,
    seq([p_verb2, p_noun], r_verb_noun_vp),
    p_verb2
)
# r_verb_noun_vp - разделяемое


# In[ ]:


# сделать (кому-то что-то)
@debug_pp
def p_verb3_1(s,p): return p_alt(s,p,
    p_verb3_simple,
    p_verb3_komu_chto,
    p_HAVE_noun,
    p_TOBE_noun,
)


# In[ ]:


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

# In[ ]:


# некто делает
@debug_pp
def p_noun_verb1(s,p): return p_alt(s,p,
    pe_noun_HAVE_noun,
    pe_noun_HAVE,
    pe_noun_TOBE_noun,
ELSE,
    pe_noun_TOBE_where,
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


# In[ ]:


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
rv_rule_povel_verb = [1,r_povel_verb_ed,r_povel_verb_mn]


# In[ ]:


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

# In[ ]:


@debug_pp
def p_phrase(s,p): 
    return p_alt(s,p,
        p_verb,    #ELSE,
        p_noun_ip,    #ELSE,
        p_noun_dp, #ELSE,
        p_dop,
        D(dict_other),
        seq([W('yes'),W(','),p_verb],r_DA_COMMA_verb),
        seq([W('no') ,W(','),p_verb],r_NET_COMMA_verb),
        seq([p_noun  ,W(','),p_verb],r_noun_COMMA_verb),
    )

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


# In[ ]:


@debug_pp
def p_question_phrase(s,p): 
    return p_have_question(s,p)


# In[ ]:


dict_proper={}# имена собственные


# In[ ]:


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


# In[ ]:


@debug_pp
def p_text(s,p):
    '''или последовательность предложений или 1 фраза
    p_text::= p_sentence* | p_phrase
    '''
    rez=[]
    while p<len(s):
        rezs=maxlen_filter(p_sentence,s,p)
        if len(rezs)==0: break
        p1,r1=rezs[0] # отбрасываем остальные результаты
        p=p1
        rez.append(I(nodep=r1))
    if len(rez)>0:
        return [(p,StC(rez))]
    else:
        return maxlen_filter(alt(p_phrase,p_question_phrase),s,p)

def maxlen_filter(patt,s,p):
    '''находит самые длинные результаты, а остальные отбрасывает
    
    если самых длинных несколько - warning
    '''
    rezs=patt(s,p)
    m=0
    im=set()
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
            SAttrs().join(s[p:m])+'\n'+
            '\n'.join(r.tostr() for void,r in long_rezs)
        )
            
    return [] if len(long_rezs)==0 else long_rezs


# ## Запуск и отладка

# In[ ]:


def _en2ru(s): # main
    ''' (text|.)* + warning-и
    '''
    s=[ i for i in tokenizer(s)]
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
            p1,r1 = rezs[0] # отбрасываем остальные результаты
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
    
    дополнительно пишет отладочный вывод'''
    l_d = parse_system.DEBUGGING
    parse_system.DEBUGGING=True
    try:
        r=_en2ru(s)
    finally:
        parse_system.DEBUGGING=l_d
    return r

def pr_l_repr(s):
    """печатает строку в тройных кавычках"""
    print("'''"+s+"'''")
    


# In[ ]:


def en2ru_with_variants(variants,s):
    saves = {}
    for k,v in variants:
        saves[id(k)]=get_variant(k)
        select_variant(k,v)
    s = en2ru(s)
    for k,v in variants:
        select_variant(k,saves[id(k)])
    return s


# In[ ]:


def decline(s,pads=['ip','rp','dp','vp','tp','pp']):
    s=[ i for i in tokenizer(s)]
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


# In[ ]:


def _parse_pat(patt,s):
    s=[ i for i in tokenizer(s)]
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
        r=parsepat(s,patt)
    finally:
        parse_system.DEBUGGING=l_d
    return r


# In[ ]:


def scheme(s,detailed=1):
    '''печатает схему разбора
    
    есть дополнительный аргумент datailed
        0 - не печатает сквозные паттерны (которые без правил)
        1 - дефолтный вывод
        2 - дополнительно печатает нестрингифицированные объекты
    '''
    # токенизируем строку
    s=[ i for i in tokenizer(s)]
    
    # парсим строку
    ParseInfo.enabled = True
    try:
        rezs=maxlen_filter(alt(p_sentence,p_phrase,p_question_phrase),s,0)
    finally:
        ParseInfo.enabled = False
        
    print(len(rezs),'результатов')
    # анализируем каждый результат
    for end,rez in rezs:
        print()
        # простой построчный вывод узлов результата
        if detailed==2:
            def print_rez0(rez,depth):
                info = rez.parse_info
                if hasattr(info,'p_start'):
                    print('  '*depth+' '+SAttrs().join( s[info.p_start : info.p_end] ))
                if hasattr(info,'patterns') or hasattr(info,'rule_group'):
                    if hasattr(info,'patterns'):
                        #'<'+str(id(info.patterns))+'>'+
                        patterns = ' '.join(info.patterns) if detailed>=1 else info.patterns[0]
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
                        print_rez0(x[1],depth+1)
        
            rez.pull_deferred()
            print_rez0(rez,0)
        
        # создание узлов
        class Node:
            __slots__ = ['childs','p_start','p_end','patterns','rule','rez']
        def make_tree(struct):
            if hasattr(struct,'talk'):
                if hasattr(struct.parse_info,'p_start'):
                    info = struct.parse_info
                    node = Node()
                    node.p_start = info.p_start
                    node.p_end = info.p_end
                    node.patterns = info.patterns
                    if hasattr(info,'rule_group'):
                        if type(info.rule_group)==list:
                            assert info.rule_group[0]!=0, info.rule_group
                            rule = info.rule_group[info.rule_group[0]]
                            rules = str(info.rule_group[0])+'/'+str(len(info.rule_group)-1)+' '
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
                        d,m = make_tree(tup[1])
                        if d>depth: depth = d
                        node.childs+=m
                    node.childs.sort(key=lambda node:node.p_start)
                    return (depth+1,[node])
                else:
                    mm = []
                    depth = 0
                    for tup in struct.talk:
                        d,m = make_tree(tup[1])
                        if d>depth: depth = d
                        mm+=m
                    return (depth,mm)
            elif hasattr(struct.parse_info,'p_start'):
                info = struct.parse_info
                node = Node()
                node.p_start = info.p_start
                node.p_end = info.p_end
                node.patterns = info.patterns
                if hasattr(info,'rule_group'):
                    if type(info.rule_group)==list:
                        no = info.rule_group[0] if info.rule_group[0]!=0 else 1
                        rule = info.rule_group[no]
                        rules = str(info.rule_group[0])+'/'+str(len(info.rule_group)-1)+' '
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
        
        # простой вывод узлов
        if 0:
            def print_rez1(info,depth):
                if hasattr(info,'p_start'):
                    print('  '*depth+' '+SAttrs().join( s[info.p_start : info.p_end] ))
                patterns = ' '.join(info.patterns) if full else info.patterns[0]
                print('  '*depth +' '+ patterns+' -> '+info.rule)
                print('  '*depth+'*'+str(info.rez))

                if hasattr(info,'childs'):
                    for x in info.childs:
                        print_rez1(x,depth+1)
                    
            rez.pull_deferred()
            
        # создание дерева
        depth,mm = make_tree(rez)
        assert len(mm)==1
        tree=mm[0]
        
        # простой вывод узлов
        if 0:
            print('depth=',depth)
            print_rez1(tree,0)
        
        DISTANCE = 2
        cols = []
        pos=0
        for word in s:
            cols.append(pos)
            pos+=len(word)+DISTANCE
        cols.append(pos)
        
        class Line:
            __slots__=['h','line']
            def __init__(self,h,l):
                self.h = h
                self.line = l
                
        lines = [Line(0,[None for i in range(len(s))]) for j in range(depth)]
        def make_lines(node):
            dd=0
            for c in node.childs:
                d = make_lines(c)
                if d>dd: dd = d
                    
            node.rez = repr(node.rez.tostr())[1:-1]
            for i in range(1,len(node.patterns)):
                node.patterns[i] = '('+node.patterns[i]+')'
            
            if len(node.patterns)>lines[dd].h: lines[dd].h = len(node.patterns)
                
            maxlen = max(len(node.rule),len(node.rez),max([len(i) for i in node.patterns]))
            dlen = (maxlen+DISTANCE) - (cols[node.p_end]-cols[node.p_start])
            #print(node.rez,maxlen,dlen)
            if dlen>0:
                for i in range(node.p_end,len(cols)):
                    cols[i]+=dlen
            
            lines[dd].line[node.p_start] = node
            return dd+1
        dd = make_lines(tree)
        assert dd==depth
        
        def inde(s,p_start,p_end):
            return s+' '*(cols[p_end]-cols[p_start]-len(s))
        
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
                    l+=inde(line[i].rez,line[i].p_start,line[i].p_end)
                    i=line[i].p_end
            print(l)
            
            if detailed>=1:
                for j in range(1,line_.h):
                    # patterns[j]
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
           


# # todo

# ## составляем основную грамматику

# ```
# выбираем варианты вручную
# пока в одном тексте не начнут требоваться разные варианты одного правила
# 
# КОДИТЬ И ДЕБАЖИТЬ ТЕКУЩЕЕ
# 12) прилагательные, расположение
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
# ```

# ## придумываем способ выборов вариантов (контекстных)

# ```
# 
# git-ветка с исключениями
#     исключения на несколько предложений
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
#             contect_dep_srcs - массив номеров - 
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

# # Тесты

# In[ ]:


get_ipython().system('jupyter nbconvert --to script en2ru.ipynb')


# In[ ]:


en2ru('I see jam and one cup.')


# In[ ]:


#decline('two watches')


# In[ ]:


get_ipython().getoutput('!')
pr_l_repr(en2ru_with_variants([
    (dict_pronoun_ip['it'],3),
],'''She has a hat; it is white too.
She has a ribbon; it is red.
'''))


# In[ ]:


import tests
tests = reload(tests)
tests.init(parse_system,en_dictionary,
           en2ru,en2ru_with_variants,decline,scheme,d_en2ru,pr_l_repr,
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
tests.finalize()
tests.TEST_ERRORS


# In[ ]:




