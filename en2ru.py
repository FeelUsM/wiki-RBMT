
# coding: utf-8

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

# In[1]:


'''англо-русский переводчик, основанный на правилах, с простым добавлением паттернов и правил

en2ru
decline
p_noun
p_noun1
r_noun_comma_noun
'''


# In[2]:


from parse_system import S, SAttrs, tokenizer,                         ch_title, ch_sentence, ch_anti_sentence, ch_open,                         rule1, seq, alt, p_alt, ELSE, W, D
from classes import StC, StNum, StNoun, StVerb, I
from ru_dictionary import ruwords, CW
from en_dictionary import dict_adj, dict_noun, dict_pronoun_ip, dict_pronoun_dp,                         dict_numeral, dict_verb, dict_verb_s, r_adj_noun


# In[3]:


def default_warning(s): 
    print(s)
warning = default_warning


# # Паттерны и правила: Составные

# .
# ## паттерны
# 
# ## парвила
# 
# ## классы
# 

# In[4]:


DEBUGGING=False


# In[5]:


def debug_pp(fun):
    s_point=[] # когда изменяется s - означает, что нужно сбросить кэш
    cache={}
    def wrapper(s,p):
        nonlocal s_point,cache
        if not(s is s_point):
            s_point=s
            cache={}
        if DEBUGGING:
            debug_s = '.'*p+'*'+'.'*(len(s)-p-1)+(' ' if p<len(s) else '')+                fun.__name__+'___'+str(p)
        if p in cache:
            if DEBUGGING: print('|'+debug_s)
            if cache[p]==None:
                raise ParseError('зацикливание '+fun.__name__+'(s,'+p+')')
            return cache[p]
        else:
            if DEBUGGING: print('{'+debug_s)
        
        cache[p]=None
        rezs=fun(s,p)
        cache[p]=rezs
        
        if DEBUGGING:
            print('}'+debug_s)
            for p1,r1 in rezs:
                print('-'+'.'*p+'_'*(p1-p)+'.'*(len(s)-p1)+' '+                     str(r1))
            
#            print('_'+'.'*p+str(len(rezs)),'in ',fun.__name__,'}',
#                  [(p,str(r)) for (p,r) in rezs],'\n')
#            for i in rezs:
#                if isinstance(i[1],StDeclinable):
#                    i[1].check_attrs('wrapper:'+fun.__name__)
        
        return rezs
    return wrapper
    return fun


# ## Other

# In[6]:


@debug_pp
def p_numeral(s,p):
    return D(dict_numeral)(s,p)


# In[7]:


#2->
@debug_pp
def p_adj(s,p):
    return D(dict_adj)(s,p)


# ## Noun-like

# In[8]:


def r_A_noun(_a,_n): return StNoun([
    I(maindep=_n,         attrs_from_left=_a)
])


# In[9]:


def r_GOOD_MORNING(_g,_m):  return r_adj_noun(
    CW('добрый',_g),
    CW('утро',_m)
)


# In[10]:


@debug_pp
def p_adj_noun3(s,p): return p_alt(s,p,
    seq([ alt(W('an'),ELSE,W('a')), p_noun3 ],r_A_noun),
    #seq([ alt(W('an'),ELSE,W('a')), p_noun3 ],r_NEKOTORYJ_noun),
    seq([ W('good'), W('morning') ],r_GOOD_MORNING),             ELSE, # исключение
    seq([ p_adj, p_noun3 ],r_adj_noun)
)


# In[11]:


@debug_pp
def p_noun3(s,p): return p_alt(s,p,
    p_adj_noun3, ELSE, # переход к следующему уровню
    p_numeral,
    D(dict_noun),
    D(dict_pronoun_ip)
)


# In[12]:


def r_noun_numeral(n,num): return StNoun([
    I(maindep=n),
    I(nomer=num)
])


# In[13]:


@debug_pp
def p_noun2(s,p): return p_alt(s,p,
    seq([ p_noun3, p_numeral ], r_noun_numeral), ELSE, # переход к следующему уровню
    p_noun3
)


# In[14]:


def r_numeral_noun(num,n):
    if num.chis!=n.chis :
        warning('не совпадают числа числ. и сущ.:'+str(num)+str(n))
    return StNum([
        I(quantity=num,            chis=n.chis, rod=n.rod, odush=n.odush ),
        I(maindep=n)
    ],quantity=num.quantity)


# In[15]:


@debug_pp
def p_noun1(s,p): return p_alt(s,p,
    seq([ p_numeral, p_noun2 ], r_numeral_noun), ELSE, # переход к следующему уровню
    p_noun2
)


# In[16]:


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


# In[17]:


@debug_pp
def p_noun(s,p):
    return p_alt(s,p,
        seq([ p_noun1, W('and'), p_noun ],r_noun_and_noun  ),
        seq([ p_noun1, W(',')  , p_noun ],r_noun_comma_noun),
                 #ELSE, # переход к следующему уровню
                 # идет конфликт с and-ом из глаголов
        p_noun1
    )


# In[18]:


def r_noun_dp(_n): return StNoun([
    I(maindep=_n,         pad='dp')
])


# In[19]:


def r_TO_noun_dp(_t,_n): return StNoun([
    I(maindep=_n,         pad='dp', attrs_from_left=_t)
])


# In[20]:


@debug_pp
def p_noun_dp(s,p): return p_alt(s,p,
    rule1( D(dict_pronoun_dp) ,r_noun_dp), 
    seq([ W('to'), p_noun ],r_TO_noun_dp)
)


# ## Verb-like

# ### verb3:  Сделать кому

# In[21]:


def r_verb_noun_dp_mn(_v_,_n_):    return StVerb([
    I(maindep=_v_,  chis='mn'),
    I(dp=_n_,       pad='dp')
])


# In[22]:


def r_verb_noun_dp_ed(_v_,_n_):     return StVerb([
    I(maindep=_v_,  chis='ed'),
    I(dp=_n_,       pad='dp')
])


# In[23]:


@debug_pp
def p_verb3(s,p): return p_alt(s,p,
    seq([ D(dict_verb),   p_noun_dp ],r_verb_noun_dp_ed),
    seq([ D(dict_verb_s), p_noun_dp ],r_verb_noun_dp_ed),  ELSE, # переход к следующему уровню
#    seq([ D(dict_verb),   p_noun_dp ],r_verb_noun_dp_mn),
#    seq([ D(dict_verb_s), p_noun_dp ],r_verb_noun_dp_mn),  ELSE, # переход к следующему уровню
    D(dict_verb),                                       
    D(dict_verb_s)
)


# ### verb2: сделать что

# In[24]:


def r_SKAZHI_noun(_s,_p): return StVerb([
    I(maindep=CW('сказать',_s)),
    I(vp=_p,   pad='vp')
])
def r_SKAZHI_phrase(_s,_p): return StVerb([
    I(maindep=CW('сказать',_s)),
    I(nodep=_p)
])
def r_SKAZHI_c_phrase(_s,c,_p): return StVerb([
    I(maindep=CW('сказать',_s)),#ruwords['сказать']
    I(punct=c),
    I(nodep=_p)
])
def r_SKAZHI_q_text(_s,q1,_p,q2): return StVerb([
    I(maindep=CW('сказать',_s)),
    I(punct=q1, add_changers={ch_open}),
    I(nodep=_p),
    I(punct=q2),
])
def r_SKAZHI_c_q_text(_s,c,q1,_p,q2): return StVerb([
    I(maindep=CW('сказать',_s)),
    I(punct=c),
    I(punct=q1, add_changers={ch_open}),
    I(nodep=_p),
    I(punct=q2),
])


# In[25]:


def r_verb_noun(v,n): return StVerb([
    I(maindep=v),
    I(vp=n,   pad='vp')
])


# In[26]:


@debug_pp
def p_verb2(s,p): return p_alt(s,p,
    seq([ alt(W('say'),W('says')),                 p_phrase      ], r_SKAZHI_noun), 
       ELSE, # исключение исключения
    seq([ alt(W('say'),W('says')),                 p_phrase      ], r_SKAZHI_phrase),
    seq([ alt(W('say'),W('says')), W(':'),         p_phrase      ], r_SKAZHI_c_phrase),
    seq([ alt(W('say'),W('says')),         W('"'), p_text, W('"')], r_SKAZHI_q_text),
    seq([ alt(W('say'),W('says')), W(':'), W('"'), p_text, W('"')], r_SKAZHI_c_q_text), 
       ELSE, # исключение
    seq([ p_verb3, p_noun ],r_verb_noun),    ELSE, # переход к следующему уровню
    p_verb3
)


# ### verb1: кто (тоже) делает

# In[27]:


def r_U_noun_EST_noun(_n1_,_h_,_n2_):    return StC([
    I(nodep=StC([
        I(nodep=S('у')),
        I(nodep=_n1_,   pad='rp', npad='n' )# у Него
    ])),
    I(nodep=S('есть',_h_.attrs)),
    I(nodep=_n2_)
])

def r_U_noun_NET_noun(_n1_,_h_,_no_,_n2_):    return StC([
    I(nodep=StC([
        I(nodep=S('у')),
        I(nodep=_n1_,   pad='rp', npad='n' )# у Него
    ])),
    I(nodep=S('нет',_h_.attrs)),
    I(nodep=_n2_,        pad='rp')
])


# In[28]:


@debug_pp
def pe_HAVE_noun(s,p):
    p_HAVE_HAS = alt( W('have'), W('has') )
    p_pronoun_dp = alt( D(dict_pronoun_dp), ELSE, p_noun )
    return p_alt(s,p,
        seq([ p_noun, p_HAVE_HAS,          p_pronoun_dp ],r_U_noun_EST_noun),
        seq([ p_noun, p_HAVE_HAS, W('no'), p_pronoun_dp ],r_U_noun_NET_noun)
#        seq([ p_noun, p_HAVE_HAS,          p_pronoun_dp ],r_noun_EST_U_noun),
#        seq([ p_noun, p_HAVE_HAS, W('no'), p_pronoun_dp ],r_noun_NET_U_noun)
    )


# In[29]:


def r_to_verb(_t,_v): return StVerb([
    I(maindep=_v,         form='neopr', attrs_from_left=_t)
])


# In[30]:


def r_noun_verb(n,v): return StVerb([
    I(ip=n),
    I(main=v,   form='nast', pers=n.pers, chis=n.chis, rod=n.rod)
])


# In[31]:


@debug_pp
def p_verb1_1(s,p): return p_alt(s,p,
    pe_HAVE_noun,                           ELSE, # исключение
    seq([ p_noun, p_verb2 ],r_noun_verb),
    seq([ W('to'), p_verb2 ],r_to_verb),   ELSE, # переход к следующему уровню
    p_verb2
)


# In[32]:


def r_noun_TOZHE_verb(_n, _v, _t): return StVerb([
    I(ip=_n),
    I(nodep=S('тоже',_t.attrs)),
    I(main=_v,   form='nast', pers=_n.pers, chis=_n.chis, rod=_n.rod)
])


# In[33]:


@debug_pp
def p_verb1(s,p): return p_alt(s,p,
    seq([ p_noun, p_verb1_1, W('too') ],r_noun_TOZHE_verb), ELSE, # переход к следующему уровню
    p_verb1_1
)


# ### verb: сделать одно и/но сделать сдругое

# In[34]:


def r_verb_NO_verb(_v1_,_c_,_but_,_v2_):    return StC([
    I(nodep=_v1_),
    I(nodep=_c_),
    I(nodep=S('но',_c_.attrs)),
    I(nodep=_v2_)
])


# In[35]:


def r_verb_c_verb(_v1_,_c_,_v2_):    return StC([
    I(nodep=_v1_),
    I(nodep=_c_),
    I(nodep=_v2_)
])


# In[36]:


def r_verb_I_verb(_v1_,_i_,_v2_):    return StC([
    I(nodep=_v1_),
    I(nodep=S('и',_i_.attrs)),
    I(nodep=_v2_)
])


# In[37]:


@debug_pp
def p_verb(s,p): return p_alt(s,p,
    seq([ p_verb1, W(','), p_verb1 ],r_verb_c_verb),   
    seq([ p_verb1, W(','), W('but'), p_verb1 ],r_verb_NO_verb),   
    seq([ p_verb1, W('and'), p_verb1 ],r_verb_I_verb),    ELSE, # переход к следующему уровню
    p_verb1
)


# ## Фразы, предложения, текст

# In[38]:


@debug_pp
def p_phrase(s,p): return p_alt(s,p,
    p_verb,    ELSE,
    p_noun,    ELSE,
    p_noun_dp, ELSE,
    p_adj
)


# In[39]:


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
    
    rezs=seq([p_phrase,alt(W('.'),W('!'))],r_sentence)(s,p)
    
    if restore_title:
        s[p].attrs.changers|={ch_title}
        s[p].attrs.changers-={ch_anti_sentence}
    return rezs


# In[40]:


def maxlen_filter(patt,s,p): #
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
        warning('multiple results:')
        warning(SAttrs.join(s[p:m]))
        for void,r in long_rezs:
            warning(str(r))
    return [] if len(long_rezs)==0 else [long_rezs[0]]

@debug_pp
def p_text(s,p):
    rez=[]
    while p<len(s):
        rezs=maxlen_filter(p_sentence,s,p)
        if len(rezs)==0: break
        p1,r1=rezs[0]
        p=p1
        rez.append(I(nodep=r1))
    if len(rez)>0:
        return [(p,StC(rez))]
    else:
        return maxlen_filter(p_phrase,s,p)
        


# In[41]:


def _en2ru(s): # main
    s=[ i for i in tokenizer(s)]
    if len(s)==0:
        warning('no tokens')
        return ''
    rezs= p_text(s,0)
    if len(rezs)==0:
        warning('NO RESULTS AT ALL')
        return ''
    p,r1 = rezs[0]
    if p!=len(s):
        warning('NOT PARSED:')
        warning(SAttrs().join(s[p:]))
    return r1.tostr()

def en2ru(s):
    global DEBUGGING
    DEBUGGING=False
    return _en2ru(s)

def d_en2ru(s):
    global DEBUGGING
    l_d = DEBUGGING
    DEBUGGING=True
    r=_en2ru(s)
    DEBUGGING=l_d
    return r

def pr_en2ru(s):
    print("'''"+en2ru(s)+"'''")


# In[42]:


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


# # Тесты

# ```
#     9)  (находится) на/в
#     10) вопросы-ответы
#         считать от до
#         ловить
#     11) сколько
#     13) где
#     14) какого цвета
#         КОНТЕКСТ
#     15) посмотри
# 
# 
# 
# контекст пока игнорим
# 
# watch, двое, трое, пятеро
# ...
# открывающиеся кавычки
# 
# для больших текстов p_sentence будет делать срез со своей позции до конца
#     - чтобы обновить кэши ф-ций
# 
# исключения парсить, если регулярным образом распарсилось
#     каждая функция будет с аргументом парсить или нет исключения
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


# ## Lesson 9

# In[46]:


pr_en2ru('''This girl has a fish.
This fish is on the dish.''')


# In[47]:


dict_noun['dolls']=ruwords['мячи']


# In[48]:


pr_en2ru('''This girl has three dolls.
This boy has two balls.
That girl has five books.
That boy has four pens.''')


# In[49]:


#dict_adj['the']=S('')


# In[50]:


DEBUGGING=False


# In[51]:


en2ru('''The girl has one dish.
She has two spoons.-
The boy has three sticks.
He has five stars.''')


# In[52]:


en2ru('''This frog is on the log.
That frog is in the lake.
The snake is in the box.''')


# In[53]:


en2ru('''The spoon is in the
cup.
The squirrel is on the
log.
The doll is on the
bed.''')


# In[54]:


en2ru('''I like cakes.
I have two cakes.
He has two stars.
She has three dolls.''')


# In[55]:


en2ru('''The doll is on the bed.
The snake is in the lake.
The hen is on the log.
The bat is in the hat.''')


# In[56]:


en2ru('''This girl has five
kittens and two cats.''')


# In[57]:


en2ru('''She has three hens.
I have four books and
nine copy-books.
This boy has eight
stars.
He has six sticks, but
he has no gun.
I like fish.
One snake is in the
lake.
One frog is on the
log.
Jam is in the vase.''')


# ## Lesson 10

# In[58]:


en2ru('''Has she a doll?
Yes, she has.
Have you a rabbit?
No, I have not.''')


# In[59]:


en2ru('''Count from one to ten! One, two, three,
four, five, six, seven, eight, nine, ten.''')


# In[60]:


en2ru('''Count the rabbits!
One, two.
Count the chickens!
One, two, three.
This girl has three
rabbits.
She has five chickens.''')


# In[61]:


en2ru('''Has this girl a kitten? Yes, she has.
Has this girl a vase? Yes, she has.
Has she	a	dog?	Yes,	she	has.
Has she	a	hat?	Yes,	she	has.
Has she	a	snake?	No,	she	has	not.
Has she	a	frog?	No,	she	has	not.
Has she	a	bat?	No,	she	has	not.''')


# In[62]:


en2ru('''That boy has two squirrels.
He has one fox too.
He has nine rabbits.
He has four bats.''')


# In[63]:


en2ru('''Has that boy a wolf?
Has he a gun?
Has he a pistol?
Has he a stick?
Has he a ball?
No, he has not.
No, he has not.
No, he has not.
Yes, he has.
Yes, he has.''')


# In[64]:


en2ru('''You have one hen and eight chickens.
You have nine rabbits too.''')


# In[65]:


en2ru('''Have you a hat? Yes, I have.
Have you a stick? No, I have not.
Catch that rabbit!''')


# In[66]:


en2ru('''Have you a ball?
Yes, I have.
Show me the ball!
Cat, cat, catch a bat!
Count the chickens!
Catch that boy!
Show me this rabbit!
Count from ten to one!
Have you a doll?
No, I have not.
Say ten words!''')


# ## Lesson 11

# In[67]:


en2ru('''How many balls have you?''')


# In[68]:


en2ru('''Have you a cat? Yes,
we have.
How many kittens has
the cat?
It has one kitten.
How many ducks have
you?
We have two ducks and
ten ducklings.''')


# In[69]:


en2ru('''How many hens have you? I have eight
hens.
How many cows have you?
We have one cow.''')


# In[70]:


en2ru('''How many dogs
have you?
I have two dogs.
How many books
has this boy?
He has eleven.''')


# In[71]:


en2ru('''How many copy-books has that girl?
She has four.
How many pens has she?
She has ten pens.
How many kittens have you?
I have three kittens.''')


# In[72]:


en2ru('''How many chickens has the hen?
It has eleven.
How many ducklings has the duck?
It has eight.
How many kittens has the cat?
It has three.
How many dolls has the girl?
She has two.
How many sticks has the boy?
He has five.
How many hats have I?
You have one.''')


# In[73]:


en2ru('''It has four legs, a long tail and it can give milk.''')


# In[74]:


en2ru('''''')


# In[75]:


en2ru('''''')


# In[76]:


en2ru('''''')


# In[77]:


en2ru('''''')


# In[78]:


en2ru('''''')

