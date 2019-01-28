
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
# а парсится как есть, с возвратами (LL(*)), по этому результаты нетерминалов кэшируются.
# Также стоит защита от зацикливания.
# Никто не обещал, что грамматика будет однозначной, 
# поэтому каждый нетерминал возвращает массив результатов.
# Но в конечном итоге таких результатов должно быть немного.
# Ситуация, когда получаются одинаковые результаты явлется нежелательной.
# 
# В дальнейшем предполагается, что будет центральная грамматика, 
# а у ее правил пользователи будут создавать исключения.
# Паттерн A является исключением паттерна B, если 
# всё что может разобрать паттерн A может разобрать паттерн B,
# т.е. A задает подъязык языка B, 
# т.е. A является частным случаем B (но связано с другим правилом).
# Сначала парсится B, и если это оказалось удачным, парсится A.
# Если А распарсилось неудачно, то результатом станосится результат B,
# а если удачно - то результат B отбрасывается и результатом станосится результат A.
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

# In[1]:


'''англо-русский переводчик, основанный на правилах, с простым добавлением паттернов и правил

en2ru
decline
p_noun
p_noun1
r_noun_comma_noun
''';


# # Паттерны и правила: Составные

# -Когда в правилах использовать S а когда один из классов Struct ?
# 
# -S используется для неизменяемых узлов-листьев. Во всех остальных случаях используется один из классов Struct
# 
# pull_attrs - если имеющуюся структуру надо расширить константами и распространить attrs структуры на расширенную структуру - смотри пример в как в r_U_noun_EST_noun
# значение pull_attrs задается равным исходной структуры в расширенной
# 
# attrs_from_left/attrs_from_right - если в правиле один из аргументов пропадает, то его атрибуты желательно добавить к другому аргументу. 
# Синтаксис `I(tag=remain_arg, ... , attrs_from_left=lost_arg)`

# In[2]:


from parse_system import S, SAttrs, ParseInfo, tokenizer, tokenize,                        ch_title, ch_sentence, ch_anti_sentence, ch_open,                         seq, alt, p_alt, ELSE, W, D,                        warning, debug_pp, reset_globals
import parse_system
from classes import StC, StNum, StNoun, StVerb, I
from ru_dictionary import ruwords, CW, add_runoun2, add_skl2, make_skl2
from en_dictionary import dict_adj, dict_noun, dict_pronoun_ip, dict_pronoun_dp,                         dict_numeral, dict_verb_simple, dict_verb_komu, r_adj_noun, dict_other,                        add_ennoun2


# ## Исключения

# In[3]:


def r_A_noun(_a,_n): return StNoun([
    I(maindep=_n,         attrs_from_left=_a)
])
def r_THE_noun(_a,_n): return StNoun([
    I(maindep=_n,         attrs_from_left=_a)
])


# In[4]:


def r_GOOD_MORNING(_g,_m):  return r_adj_noun(
    CW('добрый',_g),
    CW('утро',_m)
)


# In[5]:


def r_U_noun_EST_noun(_n1_,_h_,_n2_):    return StC([
    I(nodep=StC([
        I(nodep=S('у')),
        I(nodep=_n1_,   pad='rp', npad='n' )# у Него
    ]), pull_attrs=1 ),
    I(nodep=S('есть',_h_.attrs)),
    I(nodep=_n2_)
])

def r_U_noun_NET_noun(_n1_,_h_,_no_,_n2_):    return StC([
    I(nodep=StC([
        I(nodep=S('у')),
        I(nodep=_n1_,   pad='rp', npad='n' )# у Него
    ]), pull_attrs=1 ),
    I(nodep=S('нет',_h_.attrs)),
    I(nodep=_n2_,        pad='rp')
])


# In[6]:


@debug_pp
def pe_noun_HAVE_noun(s,p):
    p_HAVE_HAS = alt( W('have'), W('has') )
    p_pronoun_dp = alt( D(dict_pronoun_dp), p_noun )
    return p_alt(s,p,
        seq([ p_noun, p_HAVE_HAS,          p_pronoun_dp ],r_U_noun_EST_noun),
        seq([ p_noun, p_HAVE_HAS, W('no'), p_pronoun_dp ],r_U_noun_NET_noun)
#        seq([ p_noun, p_HAVE_HAS,          p_pronoun_dp ],r_noun_EST_U_noun),
#        seq([ p_noun, p_HAVE_HAS, W('no'), p_pronoun_dp ],r_noun_NET_U_noun)
    )


# In[7]:


def r_noun_X_where(_n,x,_w): return StC([
    I(nodep=_n),
    I(nodep=_w, attrs_from_left=x)
])


# In[8]:


@debug_pp
def pe_noun_TOBE_where(s,p): return p_alt(s,p,
    seq([p_noun,p_TOBE,p_where],r_noun_X_where)
)


# In[9]:


def re_povel_verb2_sov_ed(_v): return StVerb([
    I(maindep = _v, asp='sov',form='povel',chis='ed')
])
def re_povel_verb2_sov_mn(_v): return StVerb([
    I(maindep = _v, asp='sov',form='povel',chis='mn')
])


# In[10]:


# глагол с дополнением
@debug_pp
def pe_verb2_sov(s,p): return p_alt(s,p,
    seq([p_verb3_komu_chto, p_dops],r_verb_dops),
    p_verb3_komu_chto
)


# ## Other

# In[11]:


@debug_pp
def p_numeral(s,p):
    return D(dict_numeral)(s,p)


# In[12]:


#2->
@debug_pp
def p_adj(s,p):
    return D(dict_adj)(s,p)


# ## Noun-like

# In[13]:


def r_noun_numeral(n,num): return StNoun([
    I(maindep=n),
    I(nomer=num)
])


# In[14]:


def r_numeral_noun(num,n):
    if num.chis!=n.chis :
        warning('не совпадают числа числ. и сущ.:'+str(num)+str(n))
    return StNum([
        I(quantity=num,            chis=n.chis, rod=n.rod, odush=n.odush ),
        I(maindep=n)
    ],quantity=num.quantity)


# In[15]:


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


# In[16]:


@debug_pp
def p_adj_noun3(s,p): return p_alt(s,p,
    seq([ alt(W('an'),W('a')), p_noun3 ],r_A_noun),
    seq([ W('the')           , p_noun3 ],r_THE_noun),
    seq([ W('good'), W('morning') ],r_GOOD_MORNING),             
ELSE,
    seq([ p_adj, p_noun3 ],r_adj_noun)
)


# In[17]:


@debug_pp
def p_noun3(s,p): return p_alt(s,p,
    p_adj_noun3, #ELSE, # переход к следующему уровню
    p_numeral,
    D(dict_noun),
    D(dict_pronoun_ip)
)


# In[18]:


@debug_pp
def p_noun2(s,p): return p_alt(s,p,
    seq([ p_noun3, p_numeral ], r_noun_numeral), #ELSE, # переход к следующему уровню
    p_noun3
)


# In[19]:


@debug_pp
def p_noun1(s,p): return p_alt(s,p,
    seq([ p_numeral, p_noun2 ], r_numeral_noun), #ELSE, # переход к следующему уровню
    p_noun2
)


# In[20]:


@debug_pp
def p_noun(s,p):
    return p_alt(s,p,
        seq([ p_noun1, W('and'), p_noun ],r_noun_and_noun  ),
        seq([ p_noun1, W(',')  , p_noun ],r_noun_comma_noun),
                 #ELSE, # переход к следующему уровню
                 # идет конфликт с and-ом из глаголов
        p_noun1
    )


# ## Существительные в разных формах

# In[21]:


def r_noun_dp(_n): return StNoun([
    I(maindep=_n,         pad='dp')
])


# In[22]:


def r_TO_noun_dp(_t,_n): return StNoun([
    I(maindep=_n,         pad='dp', attrs_from_left=_t)
])


# In[23]:


@debug_pp
def p_noun_dp(s,p): return p_alt(s,p,
    seq([D(dict_pronoun_dp)],r_noun_dp), 
    seq([ W('to'), p_noun ],r_TO_noun_dp)
)


# ## Глагол с дополнениями

# In[24]:


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

def r_EST(_v): return StVerb([
    I(maindep=CW('есть (быть)',_v)),
])
def r_EST_noun_ip(_v,_n): return StVerb([
    I(maindep=CW('есть (быть)',_v)),
    I(ip=_n,   pad='ip')
])
def r_JAVLYATSA_noun_tp(_v,_n): return StVerb([
    I(maindep=CW('являться',_v)),
    I(tp=_n,   pad='tp')
])


# In[25]:


@debug_pp
def p_HAVE(s,p): 
    p_have = alt(W('have'),W('has'))
    return p_alt(s,p,
        seq([p_have,          alt(p_noun,D(dict_pronoun_dp))], r_IMET_noun_vp),
        seq([p_have, W('no'), alt(p_noun,D(dict_pronoun_dp))], r_NE_IMET_noun_vp),
        seq([p_have],r_IMET)
    )
@debug_pp
def p_TOBE_(s,p): return p_alt(s,p,
    seq([W('be')],r_EST),
    seq([W('am')],r_EST),
    seq([W('is')],r_EST),
    seq([W('are')],r_EST)
)
@debug_pp
def p_TOBE(s,p): return p_alt(s,p,
    seq([p_TOBE_, alt(p_noun,D(dict_pronoun_dp))], 
          [1, r_EST_noun_ip, r_JAVLYATSA_noun_tp]),
#    seq([p_tobe, W('no'), alt(p_noun,D(dict_pronoun_dp))], r_NE_IMET_noun_vp),
    p_TOBE_
)


# In[26]:


def r_verb_noun_vp(_v,_p): return StVerb([
    I(maindep= _v),
    I(vp=_p,   pad='vp')
])
def r_verb_noun_dp(_v,_p): return StVerb([
    I(maindep= _v),
    I(dp=_p,   pad='dp')
])
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


# In[27]:


@debug_pp
def p_verb3_komu(s,p): return p_alt(s,p,
    seq([D(dict_verb_komu), D(dict_pronoun_dp)], r_verb_noun_dp),
    D(dict_verb_komu)
)

@debug_pp
def p_verb3_komu_chto(s,p): return p_alt(s,p,
    seq([ p_verb3_komu,                 p_noun        ], r_verb_noun_vp),
    seq([ p_verb3_komu, W(':'),         p_phrase      ], r_verb_c_phrase),
    seq([ p_verb3_komu,         W('"'), p_text, W('"')], r_verb_q_text),
    seq([ p_verb3_komu, W(':'), W('"'), p_text, W('"')], r_verb_c_q_text), 
    p_verb3_komu
)

@debug_pp
def p_verb3_simple(s,p): return p_alt(s,p,
    seq([D(dict_verb_simple), alt(p_noun,D(dict_pronoun_dp))], r_verb_noun_vp),
    D(dict_verb_simple)
)

@debug_pp
def p_verb3(s,p): return p_alt(s,p,
    p_verb3_simple,
    p_verb3_komu_chto,
    p_HAVE,
    p_TOBE,
)


# In[28]:


def r_X_noun_dp(x,n): return StNoun([
    I(maindep=n,  pad='dp',         attrs_from_left=x)
])

def r_V_noun_pp(v,_n): return StC([
    I(nodep=S('в',v.attrs)),
    I(nodep=_n,  pad='pp'),
])
def r_NA_noun_pp(v,_n): return StC([
    I(nodep=S('на',v.attrs)),
    I(nodep=_n,  pad='pp'),
])

def r_seq_dops(d1,d2): return StC([
    I(nodep=d1),
    I(nodep=d2)
])
def r_verb_dops(_v,_d): return StVerb([
    I(maindep=_v),
    I(nodep=_d)
])


# In[29]:


# одно дополнение

@debug_pp
def p_where(s,p): return p_alt(s,p,
    seq([W('in'), p_noun ],r_V_noun_pp),
    seq([W('on'), p_noun ],r_NA_noun_pp),
)
@debug_pp
def p_dop(s,p): return p_alt(s,p,
    seq([W('to'), p_noun ],r_X_noun_dp),
    p_where
)

# последовательность дополнений
@debug_pp
def p_dops(s,p): return p_alt(s,p,
    p_dop,
    seq([p_dop, p_dops], r_seq_dops)
)

# глагол с дополнением
@debug_pp
def p_verb2(s,p): return p_alt(s,p,
    seq([p_verb3, p_dops],r_verb_dops),
    p_verb3
)


# ## Глагол(ы) с подлежащим

# In[30]:


#verb1: кто делает
def r_to_verb(_t,_v): return StVerb([
    I(maindep=_v,         form='neopr', attrs_from_left=_t)
])

def r_noun_verb(n,v): return StVerb([
    I(ip=n),
    I(main=v,   form='nast', pers=n.pers, chis=n.chis, rod=n.rod)
])

def r_povel_verb_ed(_v): return StVerb([
    I(maindep=_v, form='povel',chis='ed')
])
def r_povel_verb_mn(_v): return StVerb([
    I(maindep=_v, form='povel',chis='mn')
])


# In[31]:


#verb1: кто (тоже) делает
def r_noun_TOZHE_verb(_n, _v, _t): return StVerb([
    I(ip=_n),
    I(nodep=S('тоже',_t.attrs)),
    I(main=_v,   form='nast', pers=_n.pers, chis=_n.chis, rod=_n.rod)
])


# In[32]:


#verb: сделать одно и/но сделать сдругое
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


# In[33]:


#verb1: кто делает/ делать/ делай

@debug_pp
def p_noun_verb1(s,p): return p_alt(s,p,
    pe_noun_HAVE_noun,
    pe_noun_TOBE_where,
ELSE,
    seq([ p_noun , p_verb2 ],r_noun_verb)
)

@debug_pp
def p_verb1_2(s,p): return p_alt(s,p,
    seq([pe_verb2_sov],[1,re_povel_verb2_sov_ed,re_povel_verb2_sov_mn]),
ELSE,
    seq([    p_verb2 ],[1,r_povel_verb_ed,r_povel_verb_mn])
)

@debug_pp
def p_verb1_1(s,p): return p_alt(s,p,
    p_noun_verb1,
    seq([ W('to'), p_verb2 ],r_to_verb),   #ELSE, # переход к следующему уровню
    p_verb1_2
)


# In[34]:


#verb1: кто (тоже) делает
@debug_pp
def p_verb1(s,p): return p_alt(s,p,
    seq([ p_noun, p_verb1_1, W('too') ],r_noun_TOZHE_verb), #ELSE, # переход к следующему уровню
    p_verb1_1
)


# In[35]:


#verb: сделать одно и/но сделать сдругое
@debug_pp
def p_verb(s,p): return p_alt(s,p,
    seq([ p_verb1, W(','), p_verb1 ]          ,r_verb_c_verb),   
    seq([ p_verb1, W(','), W('but'), p_verb1 ],r_verb_NO_verb),   
    seq([ p_verb1, W('and'), p_verb1 ]        ,r_verb_I_verb),
    #ELSE, # переход к следующему уровню
    p_verb1
)


# ## Фразы, предложения, текст

# In[36]:


@debug_pp
def p_phrase(s,p): 
#    rezs=[]
#    rezs+=p_verb(s,p)
#    if len(rezs)>0: return rezs
#    rezs+=p_noun(s,p)
#    if len(rezs)>0: return rezs
#    rezs+=p_noun_dp(s,p)
#    if len(rezs)>0: return rezs
#    rezs+=p_adj(s,p)
#    return rezs
    return p_alt(s,p,
        p_verb,    #ELSE,
        p_noun,    #ELSE,
        p_noun_dp, #ELSE,
        p_adj,
        D(dict_other)
    )


# In[37]:


dict_proper={}# имена собственные
@debug_pp
def p_sentence(s,p):
    first_capital = s[p]=='I' or ch_title in s[p].attrs.changers
    def r_sentence(ph,d):
        rez=StC([I(nodep=ph),I(punct=d)])
        if first_capital: rez.attrs.changers|={ch_sentence}
        return rez
    restore_title=False
    if ch_title in s[p].attrs.changers and s[p] not in dict_proper:
        s[p].attrs.changers-={ch_title}
        s[p].attrs.changers|={ch_anti_sentence}
        restore_title=True
    try:
        rezs=seq([p_phrase,alt(W('.'),W('!'))],r_sentence)(s,p)
    finally:
        if restore_title:
            s[p].attrs.changers|={ch_title}
            s[p].attrs.changers-={ch_anti_sentence}
    return rezs


# In[38]:


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

@debug_pp
def p_text(s,p):
    '''или последовательность предложений или 1 фраза
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
        return maxlen_filter(p_phrase,s,p)
        


# ## Запуск и отладка

# In[39]:


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
    parse_system.DEBUGGING=False
    return _en2ru(s)

def d_en2ru(s):
    l_d = parse_system.DEBUGGING
    parse_system.DEBUGGING=True
    try:
        r=_en2ru(s)
    finally:
        parse_system.DEBUGGING=l_d
    return r

def pr_en2ru(s):
    print("'''"+en2ru(s)+"'''")
    


# In[40]:


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


# In[41]:


def _parse_pat(patt,s):
    s=[ i for i in tokenizer(s)]
    return patt(s,0)

def parse_pat(patt,s):
    parse_system.DEBUGGING=False
    return _parse_pat(patt,s)

def d_parse_pat(patt,s):
    l_d = parse_system.DEBUGGING
    parse_system.DEBUGGING=True
    try:
        r=parsepat(s,patt)
    finally:
        parse_system.DEBUGGING=l_d
    return r


# In[42]:


def scheme(s,full=True):
    s=[ i for i in tokenizer(s)]
    ParseInfo.enabled = True
    rezs=maxlen_filter(p_text,s,0)
    ParseInfo.enabled = False
    for end,rez in rezs:
        if 0:
            def print_rez0(rez,depth):
                info = rez.parse_info
                if hasattr(info,'p_start'):
                    print('  '*depth+' '+SAttrs().join( s[info.p_start : info.p_end] ))
                if hasattr(info,'patterns') or hasattr(info,'rule_group'):
                    if hasattr(info,'patterns'):
                        #'<'+str(id(info.patterns))+'>'+
                        patterns = ' '.join(info.patterns) if full else info.patterns[0]
                    else:
                        patterns = ''
                    if hasattr(info,'rule_group'):
                        if type(info.rule_group)==list:
                            assert info.rule_group[0]!=0
                            rule = info.rule_group[info.rule_group[0]]
                            rules = str(info.rule_group[0])+'/'+str(len(info.rule_group)-1)+' '
                        else:
                            rule = info.rule_group
                            rules = ''
                        rules += (rule.__name__ if callable(rule) else str(rule))
                    else:
                        rules = ''
                    print('  '*depth +' '+ patterns+' -> '+rules)
                print('  '*depth+'*'+str(rez))

                if hasattr(rez,'talk'):
                    for x in rez.talk:
                        print_rez0(x[1],depth+1)
        
            rez.pull_deferred()
            print_rez0(rez,0)
        
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
            
        depth,mm = make_tree(rez)
        assert len(mm)==1
        tree=mm[0]
        
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
            
            if full:
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
           


# # Тесты

# ```
# 
#     КОДИТЬ И ДЕБАЖИТЬ ТЕКУЩЕЕ
#     10) вопросы-ответы
#         считать от до
#         ловить
#     11) сколько
#     13) где
#     14) какого цвета
#         КОНТЕКСТ
#     15) посмотри
# 
# автовыбор склонений/спряжений для существительных с одним числом, прилагательных и глаголов
# регламентировать использование attrs-ов в правилах и только потом приступать к контекстам
# сделать устранение конфликтов исключений
# 
# на потом: 
# 	задание глобального контекста (задание дефолтных правил)
# 	выбор паттернов и правил в зависимости от времени 
# 
# работа с деревом вглубь:
# 	просмотр вглубь возможен
# 	
# 	у каждого узла ссылка на правило и его аргументы
# 	в узлах дерева поля 
# 		context_dep
# 			True - узел зависит от контекста
# 				ссылка на правило, также принимат контекст
# 			False - узел не зависит от контекста
# 		contect_dep_srcs - массив номеров - 
# 			какие аргументы правила зависят от контекста (или их потомки зависят от контекста)
# 			т.е. какие аргументы правила требую ремейка в случае изменения контекста
# 			
# 		context(может отсутствовать) - словарь (строка, ссылка на узел), который является контекстом
# 			- устанавливается в правилах
# 	функция context_remake(node,context)
# 
# два рыжих кота
# вижу двух рыжих котов
# вижу два горячих утюга
# два пирожных
# 
# watch, двое, трое, пятеро
# 
# написать везде строки документации
# написать инструкцию как пользоваться
# 
# ...
# открывающиеся кавычки
# 
# для больших текстов p_sentence будет делать срез со своей позции до конца
#     - чтобы обновить кэши ф-ций
# 
# исключения парсить, если регулярным образом распарсилось
#     каждая функция будет с аргументом: парсить или нет исключения
# 
# атрибуты слов: (теги)
# отображение открывающейся кавычки (SAttrs.join)
# ```

# In[43]:


#decline('two watches')


# In[44]:


en2ru('')


# In[45]:


en2ru('I see jam and one cup.')

