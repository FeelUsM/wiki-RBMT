
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


from classes import *


# In[149]:


def default_warning(s): 
    print(s)
warning = default_warning


# # Правила: RU-Словарь, +отображение

# In[2]:


ruwords={} #какие-то однословные правила складываются сюда, а какие-то остаются в функциях


# ## Noun

# ##### Функции

# In[3]:


def show_noun1(st,word,ip,rp,dp,vp,tp,pp):
    if st.pad=='ip' : return word+ip
    if st.pad=='rp' : return word+rp
    if st.pad=='dp' : return word+dp
    if st.pad=='vp' : return word+vp
    if st.pad=='tp' : return word+tp
    if st.pad=='pp' : return word+pp
    raise RuntimeError()


# In[4]:


#show_noun_map['я']=lambda st: show_noun1(st,"","я","меня","мне","меня","мной","мне")


# In[5]:


def add_runoun(name,och,odush,rod,chis,word,ip,rp,dp,vp,tp,pp):
    ruwords[name]=StNoun(name,och,odush,rod,chis,'ip')
    show_noun_map[name]=lambda st: show_noun1(st,word,ip,rp,dp,vp,tp,pp)

def add_runoun2(name,rod,word,ip,rp,dp,vp,tp,pp,               mname,odush,mword,mip,mrp,mdp,mvp,mtp,mpp):
    add_runoun(name,mname,odush,rod,'ed',word,ip,rp,dp,vp,tp,pp)
    add_runoun(mname,name,odush,rod,'mn',mword,mip,mrp,mdp,mvp,mtp,mpp)


# ##### М.р.

# In[6]:


#                                     ип ,нет ,дать,вижу,творю,думаю
add_runoun2("кот"    ,'m'  ,'кот'    ,'' ,'а' ,'у' ,'а' ,'ом' ,'е' ,
            "коты"   ,True ,'кот'    ,'ы','ов','ам','ов','ами','ах')

add_runoun2("джем"     ,'m'  ,'джем'    ,'' ,'а' ,'у' ,'' ,'ом' ,'е' ,
            "джемы"    ,False,'джем'    ,'ы','ов','ам','ы','ами','ах')
add_runoun2("пистолет" ,'m'  ,'пистолет','' ,'а' ,'у' ,'' ,'ом' ,'е' ,
            "пистолеты",False,'пистолет','ы','ов','ам','ы','ами','ах')

add_runoun2("волк"   ,'m'  ,'волк'   ,'' ,'а' ,'у' ,'а' ,'ом' ,'е' ,
            "волки"  ,True ,'волк'   ,'и','ов','ам','ов','ами','ах')
add_runoun2("мальчик",'m'  ,'мальчик','' ,'а' ,'у' ,'а' ,'ом' ,'е' ,
            "мальчики",True,'мальчик','и','ов','ам','ов','ами','ах')

add_runoun2("ящик"   ,'m'  ,'ящик'   ,'' ,'а' ,'у' ,''  ,'ом' ,'е' ,
            "ящики"  ,False,'ящик'   ,'и','ов','ам','и' ,'ами','ах')
add_runoun2("урок"   ,'m'  ,'урок'   ,'' ,'а' ,'у' ,''  ,'ом' ,'е' ,
            "уроки"  ,False,'урок'   ,'и','ов','ам','и' ,'ами','ах')

add_runoun2("мяч"    ,'m'  ,'мяч'    ,'' ,'а' ,'у' ,''  ,'ом' ,'е' ,
            "мячи"   ,False,'мяч'    ,'и','ей','ам','и' ,'ами','ах')


# In[7]:


add_runoun2("ребёнок",'m'  ,'ребён'  ,'ок','ка','ку','ка','ком','ке',
            "дети"   ,True ,'дет'    ,'и' ,'ей','ям','ей','ьми','ях')

add_runoun2("котёнок",'m'  ,'котён'  ,'ок','ка','ку','ка','ком','ке',
            "котята" ,True ,'котят'  ,'а' ,''  ,'ам',''  ,'ами','ах')


# ##### Ж.р.

# In[8]:


#                                   ип ,нет ,дать ,вижу,творю ,думаю
add_runoun2("белка" ,'g'  ,'белк' ,'а' ,'и' ,'е'  ,'у' ,'ой'  ,'е'  ,
            "белки" ,True ,'бел'  ,'ки','ок','кам','ок','ками','ках')

add_runoun2("кепка"  ,'g'  ,'кепк'  ,'а' ,'и' ,'е'  ,'у' ,'ой'  ,'е'  ,
            "кепки"  ,False,'кеп'   ,'ки','ок','кам','ки','ками','ках')
add_runoun2("шапка"  ,'g'  ,'шапк'  ,'а' ,'и' ,'е'  ,'у' ,'ой'  ,'е'  ,
            "шапки"  ,False,'шап'   ,'ки','ок','кам','ки','ками','ках')
add_runoun2("коробка",'g'  ,'коробк','а' ,'и' ,'е'  ,'у' ,'ой'  ,'е'  ,
            "коробки",False,'короб' ,'ки','ок','кам','ки','ками','ках')
add_runoun2("палка"  ,'g'  ,'палк'  ,'а' ,'и' ,'е'  ,'у' ,'ой'  ,'е'  ,
            "палки"  ,False,'пал'   ,'ки','ок','кам','ки','ками','ках')

add_runoun2("кошка" ,'g'  ,'кошк' ,'а' ,'и' ,'е'  ,'у' ,'ой'  ,'е'  ,
            "кошки" ,True ,'кош'  ,'ки','ек','кам','ек','ками','ках')

add_runoun2("ручка" ,'g'  ,'ручк' ,'а' ,'и' ,'е'  ,'у'  ,'ой' ,'е'  ,
            "ручки" ,False,'руч'  ,'ки','ек','кам','ки','ками','ках')
add_runoun2("чашка" ,'g'  ,'чашк' ,'а' ,'и' ,'е'  ,'у' ,'ой'  ,'е'  ,
            "чашки" ,False,'чаш'  ,'ки','ек','кам','ки','ками','ках')
add_runoun2("ложка" ,'g'  ,'ложк' ,'а' ,'и' ,'е'  ,'у' ,'ой'  ,'е'  ,
            "ложки" ,False,'лож'  ,'ки','ек','кам','ки','ками','ках')


# In[9]:


add_runoun2("собака",'g'  ,'собак','а' ,'и' ,'е'  ,'у'  ,'ой' ,'е' ,
            "собаки",True ,'собак','и' ,''  ,'ам' ,''   ,'ами','ах')

add_runoun2("книга" ,'g'  ,'книг' ,'а' ,'и' ,'е'  ,'у'  ,'ой' ,'е' ,
            "книги" ,False,'книг' ,'и' ,''  ,'ам' ,'и'  ,'ами','ах')

add_runoun2("зебра" ,'g'  ,'зебр' ,'а','ы','е' ,'у' ,'ой' ,'е' ,
            "зебры" ,True ,'зебр' ,'ы','' ,'ам',''  ,'ами','ах')
add_runoun2("крыса" ,'g'  ,'крыс' ,'а','ы','е' ,'у' ,'ой' ,'е' ,
            "крысы" ,True ,'крыс' ,'ы','' ,'ам',''  ,'ами','ах')
add_runoun2("курица",'g'  ,'куриц','а','ы','е' ,'у' ,'ой' ,'е' ,
            "курицы",True ,'куриц','ы','' ,'ам',''  ,'ами','ах')
add_runoun2("лиса"  ,'g'  ,'лис'  ,'а','ы','е' ,'у' ,'ой' ,'е' ,
            "лисы"  ,True ,'лис'  ,'ы','' ,'ам',''  ,'ами','ах')
    
add_runoun2("шляпа" ,'g'  ,'шляп' ,'а','ы','е' ,'у' ,'ой' ,'е' ,
            "шляпы" ,False,'шляп' ,'ы','' ,'ам','ы' ,'ами','ах')
add_runoun2("ваза"  ,'g'  ,'ваз'  ,'а','ы','е' ,'у' ,'ой' ,'е' ,
            "вазы"  ,False,'ваз'  ,'ы','' ,'ам','ы' ,'ами','ах')
add_runoun2("лампа" ,'g'  ,'ламп' ,'а','ы','е' ,'у' ,'ой' ,'е' ,
            "лампы" ,False,'ламп' ,'ы','' ,'ам','ы' ,'ами','ах')
add_runoun2("звезда",'g'  ,'звезд','а','ы','е' ,'у' ,'ой' ,'е' ,
            "звёзды",False,'звёзд','ы','' ,'ам','ы' ,'ами','ах')


# In[139]:


add_runoun2("свинья",'g'  ,'свинь','я' ,'и' ,'е'  ,'ю' ,'ёй'  ,'е'  ,
            "свиньи",True ,'свин' ,'ьи','ей','ьям','ей','ьями','ьях')

add_runoun2("информация",'g'  ,'информаци','я','и','и' ,'ю' ,'ей' ,'и' ,
            "информации",False,'информаци','и','й','ям','еи','ями','ях')


# In[11]:


add_runoun2("мышь"   ,'g'  ,'мыш'   ,'ь','и' ,'и' ,'ь' ,'ью' ,'и' ,
            "мыши"   ,True ,'мыш'   ,'и','ей','ам','ей','ами','ах')

add_runoun2("тетрадь",'g'  ,'тетрад','ь','и' ,'и' ,'ь' ,'ью' ,'и' ,
            "тетради",False,'тетрад','и','ей','ям','и' ,'ями','ях')
add_runoun2("кровать",'g'  ,'кроват','ь','и' ,'и' ,'ь' ,'ью' ,'и' ,
            "кровати",False,'кроват','и','ей','ям','и' ,'ями','ях')


# ##### С.р.

# In[12]:


#                                    ип  ,нет ,дать ,вижу,творю ,думаю о
add_runoun2("утро"  ,'s'  ,'утр'    ,'о' ,'а' ,'у'  ,'о' ,'ом'  ,'е'  ,
            "утра"  ,False,'утр'    ,'а' ,''  ,'ам' ,'а' ,'ами' ,'ах' )
add_runoun2("слово" ,'s'  ,'слов'   ,'о' ,'а' ,'у'  ,'о' ,'ом'  ,'е'  ,
            "слова" ,False,'слов'   ,'а' ,''  ,'ам' ,'а' ,'ами' ,'ах' )

add_runoun2("ружьё"  ,'s'  ,'ружь'  ,'ё' ,'я' ,'ю'  ,'ё' ,'ём'  ,'е'  ,
            "ружья"  ,False,'руж'   ,'ья','ей','ьям','ьи','ьями','ьях')

add_runoun2("вареньё",'s'  ,'варень','е' ,'я' ,'ю'  ,'е' ,'ем' ,'е' ,
            "варенья",False,'варен' ,'ья','ий','ьям','ья','ьями','ьях')


# ##### Мн.ч.

# In[13]:


#                                  ип ,нет ,дать,вижу,творю,думаю
add_runoun('часы (предмет)',None,False,'m','mn','час','ы','ов','ам','ы','ами','ах')


# ## Pronoun

# In[14]:


def show_pronoun1(st,ends,nends):
    if st.npad=='':
        ip,rp,dp,vp,tp,pp = ends
    elif st.npad=='n':
        ip,rp,dp,vp,tp,pp = nends
    else: raise RuntimeError()
    if st.pad=='ip' : return ip
    if st.pad=='rp' : return rp
    if st.pad=='dp' : return dp
    if st.pad=='vp' : return vp
    if st.pad=='tp' : return tp
    if st.pad=='pp' : return pp
    raise RuntimeError()


# In[15]:


ruwords["я (муж)"]=StProNoun("я","мы",1,True,'m','ed','ip')
ruwords["я (жен)"]=StProNoun("я","мы",1,True,'g','ed','ip')
show_noun_map["я"]=lambda st: show_noun1(st,'',"я","меня","мне","меня","мной","мне")

def add_rupronoun(name,sh_name,och,pers,r,c,ends,nends):
    ruwords[name]=StProNoun(sh_name,och,pers,True,r,c,'ip')
    show_noun_map[sh_name]=lambda st: show_pronoun1(st,ends,nends)
add_rupronoun('он','он',"они",3,'m','ed',
              ("он","его" ,"ему" ,"его" ,"им" ,"нём"),
              ("он","него","нему","него","ним","нём"))


# ## Adj

# In[16]:


def show_adj1(st,word,ends):
    if st.chis=='mn' :
        (ip,rp,dp,vp,tp,pp,sh)=ends['mn']
    else:
        (ip,rp,dp,vp,tp,pp,sh)=ends[st.rod]
        
    if   st.pad=='ip' : rez=ip
    elif st.pad=='rp' : rez=rp
    elif st.pad=='dp' : rez=dp
    elif st.pad=='vp' : rez=vp[0] if st.odush else vp[1]
    elif st.pad=='tp' : rez=tp
    elif st.pad=='pp' : rez=pp
    elif st.pad=='sh' : rez=sh
    else: raise RuntimeError()
        
    return word+rez


# In[17]:


def add_ruadj(name,sh_word,ends):
    ruwords[name]=StAdj(name,True,'m','ed','ip')
    show_adj_map[name]=lambda st: show_adj1(st,sh_word,ends)


# In[18]:


adj_std_ends_i={# и
    'm' :('ий','его','ему',('его','ий'),'им' ,'ем','' ),
    's' :('ее','его','ему',('ее', 'ее'),'им' ,'ем','е'),
    'g' :('ая','ей' ,'ей' ,('ую', 'ую'),'ей' ,'ей','а'),
    'mn':('ие','их' ,'им' ,('их', 'ие'),'ими','их','и'),
}
adj_std_ends_y={# ы
    'm' :('ый','ого','ому',('ого','ый'),'ым' ,'ом','' ),
    's' :('ое','ого','ому',('ое', 'ое'),'ым' ,'ом','о'),
    'g' :('ая','ой' ,'ой' ,('ую', 'ую'),'ой' ,'ой','а'),
    'mn':('ые','ых' ,'ым' ,('ых', 'ые'),'ыми','ых','ы'),
}

add_ruadj('летучий','летуч' ,adj_std_ends_i)
add_ruadj('хороший','хорош' ,adj_std_ends_i)

add_ruadj('добрый' ,'добр' ,adj_std_ends_y)

add_ruadj('этот' ,'эт' ,{
    'm' :('от','ого','ому',('ого','от'),'им' ,'ом',None),
    's' :('о' ,'ого','ому',('о' , 'о' ),'им' ,'ом',None),
    'g' :('а' ,'ой' ,'ой' ,('у' , 'у' ),'ой' ,'ой',None),
    'mn':('и' ,'их' ,'им' ,('их', 'и' ),'ими','их',None),
})
add_ruadj('тот' ,'т' ,{
    'm' :('от','ого','ому',('ого','от'),'ем' ,'ом',None),
    's' :('о' ,'ого','ому',('о' , 'о' ),'ем' ,'ом',None),
    'g' :('а' ,'ой' ,'ой' ,('у' , 'у' ),'ой' ,'ой',None),
    'mn':('е' ,'ех' ,'ем' ,('ех', 'е' ),'еми','ех',None),
})


# ## Num

# In[19]:


def show_num1(st,word,ends):
    if st.chis=='mn' :
        (ip,rp,dp,vp,tp,pp)=ends['mn']
    else:
        (ip,rp,dp,vp,tp,pp)=ends[st.rod]
        
    if   st.pad=='ip' : rez=ip
    elif st.pad=='rp' : rez=rp
    elif st.pad=='dp' : rez=dp
    elif st.pad=='vp' : rez=vp[0] if st.odush else vp[1]
    elif st.pad=='tp' : rez=tp
    elif st.pad=='pp' : rez=pp
    else: raise RuntimeError()
        
    return word+rez

def add_runum(name,quantity,chis,start,ends):
    show_num_map[name]=lambda st: show_num1(st,start ,ends)
    ruwords[name]=     StNum(name,quantity  ,False,'m',chis,'ip')


# In[20]:


add_runum('один','1','ed','од' ,
        {
            'm' :('ин','ного','ному',('ного','ин'),'ним' ,'ном'),
            's' :('но','ного','ному',('но'  ,'но'),'ним' ,'ном'),
            'g' :('на','ной' ,'ной' ,('ну'  ,'ну'),'ной' ,'ной'),
            'mn':('ни','них' ,'ним' ,('них', 'ни'),'ними','них'),
        }
    )

show_num_map['два']=    (lambda st:         ("две" if st.rod=='g' else "два")                         if st.pad=='ip' else         "двух"                                                    if st.pad=='rp' else         "двум"                                                    if st.pad=='dp' else         ("двух" if st.odush else "две" if st.rod=='g' else "два") if st.pad=='vp' else         "двумя"                                                   if st.pad=='tp' else         "двух"                                                    if st.pad=='pp' else         throw(RuntimeError('unknown pad: '+st.pad))
    )
ruwords['два']=    StNum('два'   ,'2-4',False,'m','mn','ip')

add_runum('три','2-4','mn','тр' ,
        {   'mn':('и','ёх' ,'ём' ,('ёх', 'и'),'емя','ёх'), }    )
add_runum('четыре','2-4','mn','четыр' ,
        {   'mn':('е','ёх' ,'ём' ,('ёх', 'е'),'ьмя','ёх'), }    )
add_runum('пять','>=5','mn','пят' ,
        {   'mn':('ь','и' ,'и' ,('ь', 'ь'),'ью','и'), }    )
add_runum('шесть','>=5','mn','шест' ,
        {   'mn':('ь','и' ,'и' ,('ь', 'ь'),'ью','и'), }    )
add_runum('семь','>=5','mn','сем' ,
        {   'mn':('ь','и' ,'и' ,('ь', 'ь'),'ью','и'), }    )
add_runum('восемь','>=5','mn','вос' ,
        {   'mn':('емь','ьми' ,'ьми' ,('емь', 'емь'),'емью','ьми'), }    )


# ## Verb

# In[21]:


def show_verb1(st,word,end_map):
    if st.form=='neopr':
        end = end_map[st.form]
    elif  st.form=='povel':
        end = end_map[st.form][0 if st.chis=='ed' else 1]
    else:
        (i,you,he,shi,it,we,yous,they)=end_map[st.form]
        if   (st.pers,st.chis)==(1,'ed'):
            end = i
        elif (st.pers,st.chis)==(2,'ed'):
            end = you
        elif (st.pers,st.chis)==(3,'ed'):
            if   st.rod=='m' : end=he
            elif st.rod=='g' : end=she
            elif st.rod=='s' : end=it
        elif (st.pers,st.chis)==(1,'mn'):
            end = we
        elif (st.pers,st.chis)==(2,'mn'):
            end = yous
        elif (st.pers,st.chis)==(3,'mn'):
            end = they
    return word+end


# In[22]:


show_verb_map['видеть']=    lambda st: show_verb1(st,'ви',
        {    'neopr':"деть",
             'povel':("дь","дьте"),
             'nast': ("жу","дишь","дит","дит","дит","дим","дите","дят")
        }   )
show_verb_map['иметь']=    lambda st: show_verb1(st,'име',
        {    'neopr':"ть",
             'povel':("й","йте"),
             'nast': ("ю","ешь","ет","ет","ет","ем","ете","ют")
        }   )
show_verb_map['показать']=    lambda st: show_verb1(st,'пока',
        {    'neopr':"зать",
             'povel':("жи","жите"),
             'nast': ("жу","жешь","жет","жет","жет","жем","жете","жут")
        }   )
show_verb_map['сказать']=    lambda st: show_verb1(st,'ска',
        {    'neopr':"зать",
             'povel':("жи","жите"),
             'nast': ("жу","жешь","жет","жет","жет","жем","жете","жут")
        }   )
show_verb_map['дать']=    lambda st: show_verb1(st,'да',
        {    'neopr':"ть",
             'povel':("й","йте"),
             'nast': ("м","шь","ст","ст","ст","дим","дите","дут")
        }   )


# In[23]:


#(self,word,oasp=0,asp=None,form=None,chis=0,rod=0,pers=0)
def r_videt():   return StVerb('видеть'  ,"увидеть"   ,'nesov','povel','mn',None,None)
def r_imet():    return StVerb('иметь'   ,"заиметь"   ,'nesov','povel','mn',None,None)
def r_dat():     return StVerb('дать'    ,'давать'    ,'sov'  ,'povel','mn',None,None)
def r_pokazat(): return StVerb('показать','показывать','sov'  ,'povel','mn',None,None)
def r_skazat():  return StVerb('сказать' ,'говорить'  ,'sov'  ,'povel','mn',None,None)


# # Правила: Составные - общие

# In[24]:


def r_adj_noun(_a_,_n_): 
    return StNoun([
        I(dep=_a_,
            rod=_n_.rod,
            chis=_n_.chis,
            pad=_n_.pad),
        I(maindep=_n_)
    ])


# # Паттерны: EN-Словарь

# ## Adj

# In[25]:


dict_adj={}


# In[26]:


dict_adj['a'] = S('')
#dict_adj['a'] : r_nekotoryj(),
dict_adj['an']= S('')
#dict_adj['an'] : r_nekotoryj(),

dict_adj['good']=ruwords["хороший"]

dict_adj['this']=ruwords["этот"]
dict_adj['that']=ruwords["тот"]


# ## Noun

# In[27]:


dict_noun={}


# In[28]:


#dict_noun['cat']=   ruwords["кошка"]
dict_noun['cat']=   ruwords["кот"]
#dict_noun['cats']=   ruwords["кошки"]
dict_noun['cats']=   ruwords["коты"]
    
#dict_noun['rat']=   ruwords["мышь"]
dict_noun['rat']=   ruwords['крыса']
#dict_noun['rats']=   ruwords["мыши"]
dict_noun['rats']=   ruwords['крысы']
    
dict_noun['bat']=   r_adj_noun(deepcopy(ruwords['летучий']),deepcopy(ruwords["мышь"]))
dict_noun['bats']=   r_adj_noun(deepcopy(ruwords['летучий']),deepcopy(ruwords["мыши"]))
    
dict_noun['lesson']=ruwords["урок"]
dict_noun['lessons']=ruwords["уроки"]
    


# In[29]:


ruwords["мыши"]


# In[30]:


dict_noun['cap']=   ruwords["кепка"]
#dict_noun['cap']=  ruwords["шапка"]
dict_noun['caps']=   ruwords["кепки"]
#dict_noun['caps']=  ruwords["шапки"]
    
dict_noun['pen']=   ruwords["ручка"]
dict_noun['pens']=   ruwords["ручки"]
    
dict_noun['hat']=   ruwords["шляпа"]
dict_noun['hats']=   ruwords["шляпы"]
    
dict_noun['hen']=   ruwords["курица"]
dict_noun['hens']=   ruwords["курицы"]
    


# In[31]:


dict_noun['dog']=   ruwords['собака']
dict_noun['dogs']=   ruwords['собаки']
dict_noun['pig']=   ruwords['свинья']
dict_noun['pigs']=   ruwords['свиньи']
dict_noun['gun']=   ruwords['ружьё']
dict_noun['guns']=   ruwords['ружья']
dict_noun['cup']=   ruwords['чашка']
dict_noun['cups']=   ruwords['чашки']
    


# In[32]:


#dict_noun['box']=   ruwords['коробка']
#dict_noun['boxes']=   ruwords['коробки']
dict_noun['box']=   ruwords['ящик']
dict_noun['boxes']=   ruwords['ящики']

dict_noun['jam']=   ruwords['джем']
#dict_noun['jam']=   ruwords['варенье']

dict_noun['bed']=   ruwords['кровать']
dict_noun['beds']=   ruwords['кровати']

dict_noun['fox']=   ruwords['лиса']
dict_noun['foxes']=   ruwords['лисы']
    


# In[33]:


dict_noun['kitten']= ruwords['котёнок']
dict_noun['kittens']= ruwords['котята']
dict_noun['vase']= ruwords['ваза']
dict_noun['vases']= ruwords['вазы']
dict_noun['star']= ruwords['звезда']
dict_noun['stars']= ruwords['звёзды']
dict_noun['lamp']= ruwords['лампа']
dict_noun['lamps']= ruwords['лампы']
    


# In[34]:


dict_noun['squirrel']= ruwords['белка']
dict_noun['squirrels']= ruwords['белки']
dict_noun['wolf']= ruwords['волк']
dict_noun['wolfs']= ruwords['волки']
dict_noun['zebra']= ruwords['зебра']
dict_noun['zebras']= ruwords['зебры']
dict_noun['boy']= ruwords['мальчик']
dict_noun['boys']= ruwords['мальчики']
#dict_noun['boy']= ruwords['парень']
#dict_noun['boy']= ruwords['парни']


# In[35]:


dict_noun['copy-book']= ruwords['тетрадь']
dict_noun['copy-books']= ruwords['тетради']
dict_noun['book']= ruwords['книга']
dict_noun['books']= ruwords['книги']
dict_noun['spoon']= ruwords['ложка']
dict_noun['spoons']= ruwords['ложки']
dict_noun['morning']= ruwords['утро']
dict_noun['mornings']= ruwords['утра']


# In[36]:


dict_noun['pistol']= ruwords['пистолет']
dict_noun['pistols']= ruwords['пистолеты']
dict_noun['ball']= ruwords['мяч']
dict_noun['balls']= ruwords['мячи']
dict_noun['stick']= ruwords['палка']
dict_noun['sticks']= ruwords['палки']
dict_noun['word']= ruwords['слово']
dict_noun['words']= ruwords['слова']


# In[140]:


dict_noun['child']= ruwords['ребёнок']
dict_noun['children']= ruwords['дети']

dict_noun['information']= ruwords['информация']
dict_noun['informations']=ruwords['информации']

dict_noun['watch']= ruwords['часы (предмет)']
dict_noun['watches']= ruwords['часы (предмет)']


# ## Pronoun

# In[38]:


dict_pronoun_ip={}
dict_pronoun_dp={}


# In[39]:


dict_pronoun_ip['I']= ruwords["я (муж)"]
#dict_pronoun_ip['I']= ruwords["я (жен)"]
dict_pronoun_dp['me']= ruwords["я (муж)"]
#dict_pronoun_dp['I']= ruwords["я (жен)"]

dict_pronoun_ip['he']= ruwords["он"]
dict_pronoun_dp['him']= ruwords["он"]


# ## Numeral

# In[40]:


dict_numeral={}


# In[41]:


dict_numeral['one']=   ruwords['один']
dict_numeral['two']=   ruwords['два']
dict_numeral['three']= ruwords['три']
dict_numeral['four']=  ruwords['четыре']
dict_numeral['five']=  ruwords['пять']
dict_numeral['six']=   ruwords['шесть']
dict_numeral['seven']= ruwords['семь']
dict_numeral['eight']= ruwords['восемь']


# ## Verb

# In[42]:


dict_verb={}
dict_verb_s={}


# In[43]:


dict_verb  ['see']= r_videt()
dict_verb_s['sees']= r_videt()
dict_verb  ['have']= r_imet()
dict_verb_s['has']= r_imet()

dict_verb  ['give']= r_dat()
dict_verb_s['gives']= r_dat()
dict_verb  ['show']= r_pokazat()
dict_verb_s['shows']= r_pokazat()
dict_verb  ['say']= r_skazat()
dict_verb_s['says']= r_skazat()


# # Паттерны и правила: Составные

# In[94]:


DEBUGGING=False


# In[96]:


def debug_pp(fun):
    def wrapper(s,p):
        if DEBUGGING:
            print('{'+'.'*p+fun.__name__)
            
        rezs=fun(s,p)
        
        if DEBUGGING:
            print('_'+'.'*p+str(len(rezs)),'in ',fun.__name__,'}',
                  [(p,str(r)) for (p,r) in rezs],'\n')
            for i in rezs:
                if isinstance(i[1],StDeclinable):
                    i[1].check_attrs('wrapper:'+fun.__name__)
        return rezs
    return wrapper
    return fun


# ## Other

# In[97]:


@debug_pp
def p_numeral(s,p):
    return D(dict_numeral)(s,p)


# In[98]:


#2->
@debug_pp
def p_adj(s,p):
    return D(dict_adj)(s,p)


# ## Noun-like

# In[99]:


def r_A_noun(a,n): 
    return SAttrs.to_right(a,n)


# In[100]:


def r_GOOD_MORNING(_g,_m):
    return r_adj_noun(
        CW(ruwords['добрый'],_g),
        CW(ruwords['утро'],_m)
    )


# In[101]:


@debug_pp
def p_adj_noun3(s,p): return p_alt(s,p,
    seq([ alt(W('an'),ELSE,W('a')), p_noun3 ],r_A_noun),
    #seq([ alt(W('an'),ELSE,W('a')), p_noun3 ],r_NEKOTORYJ_noun),
    seq([ W('good'), W('morning') ],r_GOOD_MORNING),             ELSE, # исключение
    seq([ p_adj, p_noun3 ],r_adj_noun)
)


# In[102]:


@debug_pp
def p_noun3(s,p): return p_alt(s,p,
    p_adj_noun3, ELSE, # переход к следующему уровню
    p_numeral,
    D(dict_noun),
    D(dict_pronoun_ip)
)


# In[103]:


def r_noun_numeral(n,num): return StNoun([
    I(maindep=n),
    I(nomer=num)
])


# In[104]:


@debug_pp
def p_noun2(s,p): return p_alt(s,p,
    seq([ p_noun3, p_numeral ], r_noun_numeral), ELSE, # переход к следующему уровню
    p_noun3
)


# In[150]:


def r_numeral_noun(num,n):
    if num.chis!=n.chis :
        warning('не совпадают числа числ. и сущ.:'+str(num)+str(n))
    return StNum([
        I(quantity=num,
            chis=n.chis,
            rod=n.rod,
            odush=n.odush),
        I(maindep=n)
    ],quantity=num.quantity)


# In[106]:


@debug_pp
def p_noun1(s,p): return p_alt(s,p,
    seq([ p_numeral, p_noun2 ], r_numeral_noun), ELSE, # переход к следующему уровню
    p_noun2
)


# In[107]:


def r_noun_and_noun(sn,a,n):
    return StNoun([
        I(dep=sn),
        I(nodep=S('и',a.attrs)),
        I(dep=n)
    ],c='mn', p='ip',o=False,r='m')
def r_noun_comma_noun(sn,c,n):
    return StNoun([
        I(dep=sn),
        I(punct=S(',',c.attrs)),
        I(dep=n)
    ],c='mn', p='ip',o=False,r='m')


# In[108]:


@debug_pp
def p_noun(s,p):
    @debug_pp
    def p_noun1_and_noun(s,p):
        rezs=  seq([ p_noun1, W('and'), p_noun ],r_noun_and_noun  )(s,p)
        rezs+= seq([ p_noun1, W(',')  , p_noun ],r_noun_comma_noun)(s,p)
        return rezs
    return p_alt(s,p,
        p_noun1_and_noun, #ELSE, # переход к следующему уровню
                 # идет конфликт с and-ом из глаголов
        p_noun1
    )


# In[109]:


def r_noun_dp(_n_):
    _n_.pad='dp'
    return _n_


# In[110]:


@debug_pp
def p_noun_dp(s,p): return p_alt(s,p,
    rule1( D(dict_pronoun_dp) ,r_noun_dp), 
    seq([ W('to'), p_noun ],r_noun_dp,[1])
)


# ## Verb-like

# ### verb3:  Сделать кому

# In[111]:


def r_verb_noun_dp_mn(_v_,_n_): 
    return StVerb([
        I(maindep=_v_,
            chis='mn'),
        I(dp=_n_,
            pad='dp')
    ])


# In[112]:


def r_verb_noun_dp_ed(_v_,_n_): 
    return StVerb([
        I(maindep=_v_,
            chis='ed'),
        I(dp=_n_,
            pad='dp')
    ])


# In[113]:


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

# In[145]:


def r_SKAZHI_noun(_s,_p): return StVerb([
    I(maindep=CW(r_skazat(),_s)),
    I(vp=_p,
         pad='vp')
])
def r_SKAZHI_phrase(_s,_p): return StVerb([
    I(maindep=CW(r_skazat(),_s)),
    I(nodep=_p)
])
def r_SKAZHI_c_phrase(_s,c,_p): return StVerb([
    I(maindep=CW(r_skazat(),_s)),#ruwords['сказать']
    I(punct=c),
    I(nodep=_p)
])
def r_SKAZHI_q_text(_s,q1,_p,q2): return StVerb([
    I(maindep=CW(r_skazat(),_s)),
    I(punct=add_changer(q1,ch_open)),
    I(nodep=_p),
    I(punct=q2),
])
def r_SKAZHI_c_q_text(_s,c,q1,_p,q2): return StVerb([
    I(maindep=CW(r_skazat(),_s)),
    I(punct=c),
    I(punct=add_changer(q1,ch_open)),
    I(nodep=_p),
    I(punct=q2),
])


# In[115]:


def r_verb_noun(v,n): return StVerb([
    I(maindep=v),
    I(vp=n,
        pad='vp')
])


# In[147]:


@debug_pp
def p_verb2(s,p): return p_alt(s,p,
    seq([ alt(W('say'),W('says')),                 p_phrase      ], r_SKAZHI_noun), ELSE, # исключение исключения
    seq([ alt(W('say'),W('says')),                 p_phrase      ], r_SKAZHI_phrase),
    seq([ alt(W('say'),W('says')), W(':'),         p_phrase      ], r_SKAZHI_c_phrase),
    seq([ alt(W('say'),W('says')),         W('"'), p_text, W('"')], r_SKAZHI_q_text),
    seq([ alt(W('say'),W('says')), W(':'), W('"'), p_text, W('"')], r_SKAZHI_c_q_text), 
        ELSE, # исключение
    seq([ p_verb3, p_noun ],r_verb_noun),    ELSE, # переход к следующему уровню
    p_verb3
)


# ### verb1: кто (тоже) делает

# In[117]:


def r_U_noun_EST_noun(_n1_,_h_,_n2_):
    return StC([
        I(nodep=StC([
            I(nodep=S('у')),
            I(nodep=_n1_,
                pad='rp',
                npad='n' )# у Него
        ])),
        I(nodep=S('есть',_h_.attrs)),
        I(nodep=_n2_)
    ])

def r_U_noun_NET_noun(_n1_,_h_,_no_,_n2_):
    return StC([
        I(nodep=StC([
            I(nodep=S('у')),
            I(nodep=_n1_,
                pad='rp',
                npad='n' )# у Него
        ])),
        I(nodep=S('нет',_h_.attrs)),
        I(nodep=_n2_,
            pad='rp')
    ])


# In[165]:


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


# In[119]:


def r_to_verb(t,v): 
    v.form='neopr'
    return SAttrs.to_right(t,v)


# In[120]:


def r_noun_verb(n,v): return StVerb([
    I(ip=n),
    I(main=v,
        form='nast',
        pers=n.pers,
        chis=n.chis,
        rod=n.rod)
])


# In[164]:


@debug_pp
def p_verb1_1(s,p): return p_alt(s,p,
    pe_HAVE_noun,                           ELSE, # исключение
    seq([ p_noun, p_verb2 ],r_noun_verb),
    seq([ W('to'), p_verb2 ],r_to_verb),   ELSE, # переход к следующему уровню
    p_verb2
)


# In[122]:


def r_noun_TOZHE_verb(_n, _v, _t): return StVerb([
    I(ip=_n),
    I(nodep=S('тоже',_t.attrs)),
    I(main=_v,
        form='nast',
        pers=_n.pers,
        chis=_n.chis,
        rod=_n.rod)
])


# In[123]:


@debug_pp
def p_verb1(s,p): return p_alt(s,p,
    seq([ p_noun, p_verb1_1, W('too') ],r_noun_TOZHE_verb), ELSE, # переход к следующему уровню
    p_verb1_1
)


# ### verb: сделать одно и/но сделать сдругое

# In[137]:


def r_verb_NO_verb(_v1_,_c_,_but_,_v2_):
    return StC([
        I(nodep=_v1_),
        I(nodep=_c_),
        I(nodep=S('но',_c_.attrs)),
        I(nodep=_v2_)
    ])


# In[138]:


def r_verb_c_verb(_v1_,_c_,_v2_):
    return StC([
        I(nodep=_v1_),
        I(nodep=_c_),
        I(nodep=_v2_)
    ])


# In[125]:


def r_verb_I_verb(_v1_,_i_,_v2_):
    return StC([
        I(nodep=_v1_),
        I(nodep=S('и',_i_.attrs)),
        I(nodep=_v2_)
    ])


# In[136]:


@debug_pp
def p_verb(s,p): return p_alt(s,p,
    seq([ p_verb1, W(','), p_verb1 ],r_verb_c_verb),   
    seq([ p_verb1, W(','), W('but'), p_verb1 ],r_verb_NO_verb),   
    seq([ p_verb1, W('and'), p_verb1 ],r_verb_I_verb),    ELSE, # переход к следующему уровню
    p_verb1
)


# ## Фразы, предложения, текст

# In[127]:


@debug_pp
def p_phrase(s,p): return p_alt(s,p,
    p_verb,    ELSE,
    p_noun,    ELSE,
    p_noun_dp, ELSE,
    p_adj
)


# In[128]:


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
        restore_title=True
    
    def p_DOT_EXCL(s,p):
        rezs=W('.')(s,p)
        rezs+=W('!')(s,p)
        return rezs
    rezs=seq([p_phrase,p_DOT_EXCL],r_sentence)(s,p)
    
    if restore_title:
        s[p].attrs.changers|={ch_title}
    return rezs


# In[129]:


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
        


# In[151]:


def en2ru(s): # main
    s=[ i for i in tokenizer(s)]
    if len(s)==0:
        warning('no tokens')
        return ''
    rezs= p_text(s,0)
    if len(rezs)==0:
        raise ParseError('no results')
    p,r1 = rezs[0]
    if p!=len(s):
        warning('NOT PARSED:')
        warning(SAttrs.join(s[p:]))
    return str(r1)

def d_en2ru(s):
    global DEBUGGING
    l_d = DEBUGGING
    DEBUGGING=True
    r=en2ru(s)
    DEBUGGING=l_d
    return r


# In[131]:


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
        m.append(prompt+str(tmp))#        print(prompt+str(tmp))
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
# watch, двое, трое, пятеро
# ...
# I() - чтобы чтобы модификации свойств записывала в 3й элемент тупла
# get_property(tuple)
#     если 2 элемента - берет настоящее сойство
#     если 3 элемента - берет свойство из 3го элемента
# использовать её в init-ах для main и maindep
# .pull_deferred():
#     с каждым tupl-ом из talk
#         если он Struct
#             вызываем его.pull_deferred()
#         применяем свойства из 3го элемента tupl-а
#     подтягиваем .pre из talk[0]
# .tistr()
#     .pull_deferred
#     .__str__
# 
# сделать кэширование результатов
#     статистика использования паттернов/словарей/правил
# 
# атрибуты слов: (теги)
# отображение открывающейся кавычки (SAttrs.join)
# ...
# нужен LR-парсер, причем недетерминированный - посмотреть, какие есть библиотеки
#     возможно стоит придумать уровни для паттернов...
# ```

# In[80]:


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
        m.append(prompt+str(tmp))#        print(prompt+str(tmp))
    return m


# In[163]:


#decline('two watches')


# In[155]:


def timing(f,*args):
    import time
    start_time = time.time()
    r=f(*args)
    print("--- %.3f seconds ---" % (time.time() - start_time))
    return r


# In[161]:


#timing(en2ru,'Say: "Seven, six, four, two, five, three, one."')


# In[162]:


#timing(en2ru,'say: say seven')


# In[82]:


en2ru('')


# In[83]:


en2ru('I see jam and one cup')

