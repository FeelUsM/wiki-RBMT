'''Паттерны-терминалы, т.е. словарь английских слов. И функции его пополнения.

Чтобы не создавать парсинговые функции, линейно перебирающие английские слова,
эти слова были помещены в соответствующие словари, а в perse_system.py
появилась функция D(), которая проверяет, есть ли текущий токен в словаре
и если есть - возвращает объект-структуру, которым он переводится.

Английское слово может переводится не только одним русским словом а еще и словосочетанием,
т.е. английскому слову в словаре может соответствовать не только объект-структура,
но и древовидная структура, построенная правилом с аргументами из других структур.
По этому некоторые правила объвляются здесь.

r_adj_noun

dict_adj
dict_noun
dict_pronoun_ip
dict_pronoun_dp
dict_numeral
dict_verb
dict_verb_s

функции его пополнения...
'''
from parse_system import S, warning
from classes import I,StNoun
from ru_dictionary import ruwords, CW, add_runoun2, add_skl2, make_skl2, add_runoun1

import ru_dictionary as rd
rd.VERBOSE_ADDS=False
# # Паттерны: EN-Словарь


def add_dict_variant(dic,enw,ruw,reset=False):
	'''добавляет вариант к переводу (как в виде списка так и в виде прямого перевода) и устанавливает указатель на него

	если reset==True - предварительно удалит все предыдущие варианты
	'''
	if enw in dic and not reset:                                         
		if type(dic[enw])==list:
			for w in dic[enw]:
				if w==ruw:
					warning('добавляем уже имеющееся слово')
					return False
			dic[enw].append(ruw)
			dic[enw][0]=len(dic[enw])-1 # 
		else:
			assert dic[enw]!=ruw, 'добавляем уже имеющееся слово'
			tmp=dic[enw]
			dic[enw]=[2,tmp,ruw]
	else:
		dic[enw]=[1,ruw]
	if rd.VERBOSE_ADDS:
		print('в',dic['__name__'],'добавлено',enw)

def add_variant(x,ruw,reset=False):
	'''добавляет вариант к переводу (только в виде списка) и устанавливает указатель на него

	если reset==True - предварительно удалит все предыдущие варианты
	'''
	assert type(x)==list
	if not reset:                                         
		for w in x:
			if w==ruw:
				warning('добавляем уже имеющееся слово')
				return False
		x.append(ruw)
		x[0]=len(x)-1 # 
	else:
		x=[1,ruw]

def remove_variant(x,n):
	'''удаляет вариант (из списка) и по возможности не меняет указатель варианта

	проверяет, чтобы остался хотябы 1 вариант
	'''
	assert type(x)==list and len(x)>2
	del x[n]
	if x[0]>=n: # если указатель варианта указывает на удаляемое слово, будет выбран предыдущий вариант
		x[0]-=1 # иначе указатель продолжиит указывать на прежнее слово

def get_variant(x):
    '''возвращает дефолтный вариант
    
    если вариантов нет - возвращает None
    '''
    if type(x)!=list:
        return 0
    else:
        return x[0]

def select_variant(x,n):
    '''устанавливает дефолтный вариант в группе правил
    
    если это сделать невозможно - ничего не меняет
    '''
    if n==None: 
        warning("can't select variant 'None'")
        return False
    assert type(n)==int and n>=0
    if type(x)!=list and n>1:
        warning("can't select variant from only one ")
        return False
    elif n>=len(x): 
        warning('number out of range')
        return False
    else:
        if n==0: n=1
        x[0]=n
        return True

def variants(x):
    '''печатает список вариантов'''
    if type(x)!=list:
        print('only one variant')
    else:
        print(len(x)-1,'varians, selected number',x[0])
        for i in range(1,len(x)):
            if callable(x[i]):
                if i==x[0]: print(x[i].__name__,'<---')
                else:       print(x[i].__name__)
            else:
                if i==x[0]: print(x[i],'<---')
                else:       print(x[i])
    return x

# ## Noun ----------------------------


dict_noun={'__name__':'dict_noun'}
def add_ennoun2(enw,enwmn,ruw,ruwmn,r,o,skl=None,sense=None,reset=False):
	''' add_runoun2 обновляет ruwords[ruw/mn]

	а add_dict_variant просто добавляет еще один вариант
	по этому если старый вариант уже был, его надо сначала удалить из dict_noun
	иначе в dict_noun остануться оба варианта: и старый и новый'''
	if ruw   in ruwords: remove_dict_variant(dict_noun,enw,  ruwords[ruw]  )
	if ruwmn in ruwords: remove_dict_variant(dict_noun,enwmn,ruwords[ruwmn])
	if add_runoun2(ruw,ruwmn,r,o,skl,sense):
		add_dict_variant(dict_noun,enw,  ruwords[ruw]  ,reset)
		add_dict_variant(dict_noun,enwmn,ruwords[ruwmn])
	
def add_ennoun1(enw,ruw,c,r,o,skl=None,sense=None,reset=False):
	''' add_runoun1 обновляет ruwords[ruw]

	а add_dict_variant просто добавляет еще один вариант
	по этому если старый вариант уже был, его надо сначала удалить из dict_noun
	иначе в dict_noun остануться оба варианта: и старый и новый'''
	if ruw   in ruwords: remove_dict_variant(dict_noun,enw,  ruwords[ruw]  )
	if add_runoun1(ruw,c,r,o,skl,sense):
		add_dict_variant(dict_noun,enw,  ruwords[ruw]  ,reset)
	
def ____Noun():
	
	add_ennoun2('cat'     ,'cats'      ,"кошка"   ,"кошки"     ,'g',True)
	add_ennoun2('cat'     ,'cats'      ,"кот"     ,"коты"      ,'m',True)
	#bat - составное - в конце
	add_ennoun2('rat'     ,'rats'      ,"мышь"    ,"мыши"      ,'g',True)
	add_ennoun2('rat'     ,'rats'      ,"крыса"   ,"крысы"     ,'g',True)
	add_ennoun2('lesson'  ,'lessons'   ,"урок"    ,"уроки"     ,'m',False)
	
	add_ennoun2('cap'     ,'caps'      ,"шапка"   ,"шапки"     ,'g',False)
	add_ennoun2('cap'     ,'caps'      ,"кепка"   ,"кепки"     ,'g',False)
	add_ennoun2('pen'     ,'pens'      ,"ручка"   ,"ручки"     ,'g',False)
	add_ennoun2('hat'     ,'hats'      ,"шляпа"   ,"шляпы"     ,'g',False)
	add_ennoun2('hen'     ,'hens'      ,"курица"  ,"курицы"    ,'g',True)

	add_ennoun2('dog'     ,'dogs'      ,"собака"  ,"собаки"    ,'g',True)
	add_ennoun2('pig'     ,'pigs'      ,"свинья"  ,"свиньи"    ,'g',True)
	add_ennoun2('gun'     ,'guns'      ,"ружьё"   ,"ружья"     ,'s',False)
	add_ennoun2('cup'     ,'cups'      ,"чашка"   ,"чашки"     ,'g',False)
	
	add_ennoun2('box'     ,'boxes'     ,"коробка" ,"коробки"   ,'g',False)
	add_ennoun2('box'     ,'boxes'     ,"ящик"    ,"ящики"     ,'m',False)
	add_ennoun2('jam'     ,'jams'      ,"варенье" ,"варенья"   ,'s',False)
	add_ennoun2('jam'     ,'jams'      ,"джем"    ,"джемы"     ,'m',False)
	add_ennoun2('bed'     ,'beds'      ,"кровать" ,"кровати"   ,'g',False)
	add_ennoun2('fox'     ,'foxes'     ,"лиса"    ,"лисы"      ,'g',True)
	
	add_ennoun2('kitten'  ,'kittens'   ,"котёнок" ,"котята"    ,'m',True)
	add_ennoun2('vase'    ,'vases'     ,"ваза"    ,"вазы"      ,'g',False)
	add_ennoun2('star'    ,'stars'     ,"звезда"  ,"звёзды"    ,'g',False)
	add_ennoun2('lamp'    ,'lamps'     ,"лампа"   ,"лампы"     ,'g',False)

	add_ennoun2('squirrel','squirrels' ,"белка"   ,"белки"     ,'g',True)
	add_ennoun2('wolf'    ,'wolfs'     ,"волк"    ,"волки"     ,'m',True)
	add_ennoun2('zebra'   ,'zebras'    ,"зебра"   ,"зебры"     ,'g',True)
	add_skl2('m',True,make_skl2(
		'парень'  ,'парни',
		'парня'   ,'парней',
		'парню'   ,'парням',
		'парня'   ,'парней',
		'парнем'  ,'парнями',
		'парне'   ,'парнях'))
	add_ennoun2('boy'     ,'boys'      ,"парень"  ,"парни"     ,'m',True)
	add_ennoun2('boy'     ,'boys'      ,"мальчик" ,"мальчики"  ,'m',True)

	add_ennoun2('copy-book','copy-books',"тетрадь","тетради"   ,'g',False)
	add_ennoun2('book'    ,'books'     ,"книга"   ,"книги"     ,'g',False)
	add_ennoun2('spoon'   ,'spoons'    ,"ложка"   ,"ложки"     ,'g',False)
	add_ennoun2('morning' ,'mornings'  ,"утро"    ,"утра"      ,'s',False)
                                       
	add_ennoun2('pistol'  ,'pistols'   ,"пистолет","пистолеты" ,'m',False)
	add_ennoun2('ball'    ,'balls'     ,"мяч"     ,"мячи"      ,'m',False)
	add_ennoun2('stick'   ,'sticks'    ,"палка"   ,"палки"     ,'g',False)
	add_ennoun2('word'    ,'words'     ,"слово"   ,"слова"     ,'s',False)
                                       
	add_ennoun2('girl'    ,'girls'     ,"девочка" ,"девочки"   ,'g',True)
	add_ennoun2('dish'    ,'dishes'    ,"блюдо"   ,"блюда"     ,'s',False)
	add_ennoun2('fish'    ,'fishes'    ,"рыба"    ,"рыбы"      ,'g',True)
                                       
	add_ennoun2('child'   ,'children'  ,"ребёнок" ,"дети"      ,'m',True)
	add_ennoun2('information','informations',"информация","информации",'g',False)

	add_ennoun2('doll'    ,'dolls'     ,"кукла"   ,"куклы"     ,'g',False)
	add_ennoun2('frog'    ,'frogs'     ,"ягушка"  ,"лягушки"   ,'g',True)
	add_ennoun2('log'     ,'logs'      ,"бревно"  ,"брёвна"    ,'s',False)
	add_ennoun2('lake'    ,'lakes'     ,"озеро"   ,"озёра"     ,'s',False)
	add_ennoun2('snake'   ,'snakes'    ,"змея"    ,"змеи"      ,'g',True)
	add_ennoun2('cake'    ,'cakes'     ,"торт"    ,"торты"     ,'m',False)
	#add_skl2('s',False,make_skl2(
	#'пирожное'   ,'пирожные',
	#'пирожного'  ,'пирожных',
	#'пирожному'  ,'пирожным',
	#'пирожное'   ,'пирожные',
	#'пирожным'   ,'пирожными',
	#'пирожном'   ,'пирожных'
	#))                     #cakes
	#add_ennoun2('cake'    ,'cakes'     ,"пирожное","пирожные"  ,'s',False)

	add_ennoun2('chicken'  ,'chickens'  ,"цыплёнок","цыплята"   ,'m',True)
	add_skl2('m',True,make_skl2(
		'заяц'    ,'зайцы',
		'зайца'   ,'зайцев',
		'зайцу'   ,'зайцам',
		'зайца'   ,'зайцев',
		'зайцем'  ,'зайцами',
		'зайце'   ,'зайцах'))
	add_ennoun2('rabbit'   ,'rabbits'   ,"заяц"    ,"зайцы"     ,'m',True)
	add_ennoun2('rabbit'   ,'rabbits'   ,"кролик"  ,"кролики"   ,'m',True)

	add_ennoun2('duck'     ,'ducks'     ,"утка"    ,"утки"      ,'g',True)
	add_ennoun2('duckling' ,'ducklings' ,"утёнок"  ,"утята"     ,'m',True)
	add_ennoun2('cow'      ,'cows'      ,"корова"  ,"коровы"    ,'g',True)
	add_ennoun2('leg'      ,'legs'      ,"нога"    ,"ноги"      ,'g',False)
	add_ennoun2('tail'     ,'tails'     ,"хвост"   ,"хвосты"    ,'m',False)
	add_ennoun1('milk'                  ,"молоко"  ,'ed'        ,'s',False)

	add_skl2('m',True,make_skl2(
		'конь'   ,'кони',
		'коня'   ,'коней',
		'коню'   ,'коням',
		'коня'   ,'коней',
		'конём'  ,'конями',
		'коне'   ,'конях'))
	add_ennoun2('horse'    ,'horses'    ,"конь"    ,"кони"      ,'m',True)
	add_ennoun2('horse'    ,'horses'    ,"лошадь"  ,"лошади"    ,'g',True,skl=8)
	add_skl2('m',True,make_skl2(
		'козёл'   ,'козлы',
		'козла'   ,'козлов',
		'козлу'   ,'козлам',
		'козла'   ,'козлов',
		'козлом'  ,'козлами',
		'козле'   ,'козлах',))
	add_ennoun2('goat'     ,'goats'     ,"козёл"   ,"козлы"     ,'m',True)
	add_ennoun2('goat'     ,'goats'     ,"коза"    ,"козы"      ,'g',True)
	add_ennoun2('car'      ,'cars'      ,"машина"  ,"машины"    ,'g',False)
	add_ennoun2('car'      ,'cars'      ,"автомобиль","автомобили",'m',False)
	add_ennoun2('street'   ,'streets'   ,"улица"   ,"улицы"     ,'g',False)
	add_ennoun2('ribbon'   ,'ribbons'   ,"лента"   ,"ленты"     ,'g',False)
	add_ennoun2('lemon'    ,'lemons'    ,"лимон"   ,"лимоны"    ,'m',False)

	#add_runoun('часы (предмет)',None,False,'m','mn','час','ы','ов','ам','ы','ами','ах')
	#dict_noun['watch']= ruwords['часы (предмет)']
	#dict_noun['watches']= ruwords['часы (предмет)']



	#add_skl2('m',False,make_skl2(
	#'цветок'   ,'цветки',
	#'цветка'   ,'цветков',
	#'цветку'   ,'цветкам',
	#'цветок'   ,'цветки',
	#'цветком'  ,'цветками',
	#'цветке'   ,'цветках'))
	#add_runoun2("цветок" ,"цветки"   ,'m',False)

	#add_skl2('m',False,make_skl2(
	#'путь'   ,'пути',
	#'пути'   ,'путей',
	#'путю'   ,'путям',
	#'путь'   ,'пути',
	#'путём'  ,'путями',
	#'путе'   ,'путях'
	#))
	#add_runoun2("путь" ,"пути"   ,'m',False)
	
	#add_runoun2("лошадь" ,"лошади"   ,'g',True)

____Noun()


# ## Pronoun ----------------------------


dict_pronoun_ip={'__name__':'dict_pronoun_ip'}
dict_pronoun_dp={'__name__':'dict_pronoun_dp'}
def ____Pronoun():

	dict_pronoun_ip['I']=   [0, ruwords["я (муж)"],  ruwords["я (жен)"] ]
	dict_pronoun_dp['me']=  [0, ruwords["я (муж)"],  ruwords["я (жен)"] ]
	dict_pronoun_ip['you']= [0, ruwords["ты (муж)"], ruwords["ты (жен)"],  ruwords["вы"] ]
	dict_pronoun_dp['you']= [0, ruwords["ты (муж)"], ruwords["ты (жен)"],  ruwords["вы"] ]

	dict_pronoun_ip['we']=  ruwords["мы"]
	dict_pronoun_dp['us']=  ruwords["мы"]

	dict_pronoun_ip['it']=  ruwords["оно"]
	dict_pronoun_dp['it']=  ruwords["оно"]
	dict_pronoun_ip['he']=  ruwords["он"]
	dict_pronoun_dp['him']= ruwords["он"]
	dict_pronoun_ip['she']= ruwords["она"]
	dict_pronoun_dp['her']= ruwords["она"]
	dict_pronoun_ip['they']= ruwords["они"]
	dict_pronoun_dp['them']= ruwords["они"]

	it = dict_pronoun_ip['it']
	tmp = get_variant(it)
	add_dict_variant(dict_pronoun_ip,'it',dict_pronoun_ip['he'])
	it = dict_pronoun_ip['it']
	add_variant(it,dict_pronoun_ip['she'])
	select_variant(it,tmp)

____Pronoun()


# ## Adj

# In[26]:


dict_adj={'__name__':'dict_adj'}
def ____Adj():

	# In[27]:


	dict_adj['a'] = ruwords["некоторый"]
	dict_adj['an']= ruwords["некоторый"]
	dict_adj['the']= ruwords["определённый"]

	dict_adj['long']= ruwords["длинный"]
	dict_adj['good']=ruwords["хороший"]

	dict_adj['black']=ruwords["чёрный"]
	dict_adj['big']=ruwords["большой"]
	dict_adj['white']=ruwords["белый"]
	dict_adj['red']=ruwords["красный"]
	dict_adj['short']=ruwords["короткий"]

	dict_adj['this']=ruwords["этот"]
	dict_adj['that']=ruwords["тот"]

____Adj()


# ## Numeral

# In[40]:


dict_numeral={'__name__':'dict_numeral'}
def ____Numeral():

	dict_numeral['one']=       [1,ruwords['один'],ruwords['одна'],ruwords['одно']]
	dict_numeral['two']=       [1,ruwords['два'],ruwords['две']]
	dict_numeral['three']=     ruwords['три']
	dict_numeral['four']=      ruwords['четыре']
	dict_numeral['many']=      ruwords['много']
	dict_numeral['five']=      ruwords['пять']
	dict_numeral['six']=       ruwords['шесть']
	dict_numeral['seven']=     ruwords['семь']
	dict_numeral['eight']=     ruwords['восемь']
	dict_numeral['nine']=      ruwords['девять']
	dict_numeral['ten']=       ruwords['десять']
	dict_numeral['eleven']=   ruwords['одинадцать']
	dict_numeral['twelve']=    ruwords['двенадцать']
	dict_numeral['thirteen']=  ruwords['тринадцать']
	dict_numeral['fourteen']=  ruwords['четырнадцать']
	dict_numeral['fifteen']=   ruwords['пятнадцать']
	dict_numeral['sixteen']=   ruwords['шестнадцать']
	dict_numeral['seventeen']= ruwords['семнадцать']
	dict_numeral['eighteen']=  ruwords['восемнадцать']
	dict_numeral['nineteen']=  ruwords['девятнадцать']
	dict_numeral['twenty']=    ruwords['двадцать']

____Numeral()


# ## Verb

# In[42]:


dict_verb_simple={'__name__':'dict_verb_simple'}
dict_verb_komu={'__name__':'dict_verb_komu'}
def ____Verb():

	#dict_verb['be']= [0, ruwords['являться'], ruwords['находиться'] ]
	#dict_verb['am']= [0, ruwords['являться'], ruwords['находиться'] ]
	#dict_verb['are']=[0, ruwords['являться'], ruwords['находиться'] ]
	#dict_verb['is']= [0, ruwords['являться'], ruwords['находиться'] ]
	#dict_verb['have']=  ruwords['иметь']
	#dict_verb['has']=   ruwords['иметь']
	
	dict_verb_komu['give']=  ruwords['давать']
	dict_verb_komu['gives']= ruwords['давать']
	dict_verb_komu['show']=  [ 2, ruwords['показать'], ruwords['показывать'] ]
	dict_verb_komu['shows']= [ 2, ruwords['показать'], ruwords['показывать'] ]
	dict_verb_komu['say']=   ruwords['говорить']
	dict_verb_komu['says']=  ruwords['говорить']

	dict_verb_simple['can']=   ruwords['мочь']

	dict_verb_simple['see']=   ruwords['видеть']
	dict_verb_simple['sees']=  ruwords['видеть']
	dict_verb_simple['like']=  ruwords['любить']
	dict_verb_simple['likes']= ruwords['любить']
	dict_verb_simple['catch']= ruwords['ловить']
	dict_verb_simple['catches']=ruwords['ловить']
	dict_verb_simple['count']=  ruwords['считать']
	dict_verb_simple['counts']= ruwords['считать']
____Verb()


# ## Other

# In[42]:


dict_other={'__name__':'dict_other'}
def ____Other():
	dict_other['on']=S('на')
	dict_other['in']=S('в')
	dict_other['yes']=S('да')
	dict_other['no']=S('нет')
	dict_other['not']=S('не')
	dict_other['and']=S('и')
	dict_other['but']=S('но')
	dict_other['to']=S('к')
	dict_other['too']=S('тоже')
	dict_other['.']=S('.')
	dict_other[',']=S(',')
	dict_other['!']=S('!')
	dict_other[':']=S(':')
	dict_other['"']=S('"')
	dict_other["'"]=S("'")
____Other()


# # Правила: Составные - общие


def r_adj_noun(_a_,_n_): 
    return StNoun([
        I(dep=_a_,
            rod=_n_.rod,
            chis=_n_.chis,
            pad=_n_.pad),
        I(maindep=_n_)
    ])



dict_noun['bat']=   r_adj_noun(CW('летучий'),CW("мышь"))
dict_noun['bats']=   r_adj_noun(CW('летучий'),CW("мыши"))
rd.VERBOSE_ADDS=True
