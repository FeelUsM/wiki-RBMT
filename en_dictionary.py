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
from parse_system import S
from classes import I,StNoun
from ru_dictionary import ruwords, CW

# # Правила: Составные - общие

# In[25]:


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

# In[26]:


dict_adj={}
def ____Adj():

	# In[27]:


	dict_adj['a'] = S('')
	#dict_adj['a'] : r_nekotoryj(),
	dict_adj['an']= S('')
	#dict_adj['an'] : r_nekotoryj(),

	dict_adj['good']=ruwords["хороший"]

	dict_adj['this']=ruwords["этот"]
	dict_adj['that']=ruwords["тот"]

____Adj()

# ## Noun

# In[28]:


dict_noun={}
def ____Noun():


	# In[29]:


	#dict_noun['cat']=   ruwords["кошка"]
	dict_noun['cat']=   ruwords["кот"]
	#dict_noun['cats']=   ruwords["кошки"]
	dict_noun['cats']=   ruwords["коты"]
		
	#dict_noun['rat']=   ruwords["мышь"]
	dict_noun['rat']=   ruwords['крыса']
	#dict_noun['rats']=   ruwords["мыши"]
	dict_noun['rats']=   ruwords['крысы']
		
	dict_noun['bat']=   r_adj_noun(CW('летучий'),CW("мышь"))
	dict_noun['bats']=   r_adj_noun(CW('летучий'),CW("мыши"))
		
	dict_noun['lesson']=ruwords["урок"]
	dict_noun['lessons']=ruwords["уроки"]
		


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


	# In[36]:


	dict_noun['girl']= ruwords['девочка']
	dict_noun['girls']= ruwords['девочки']
	dict_noun['dish']= ruwords['блюдо']
	dict_noun['dishes']= ruwords['блюда']
	dict_noun['fish']= ruwords['рыба']
	dict_noun['fishes']= ruwords['рыбы']

#	dict_noun['']= ruwords['']


	# In[37]:


	dict_noun['child']= ruwords['ребёнок']
	dict_noun['children']= ruwords['дети']

	dict_noun['information']= ruwords['информация']
	dict_noun['informations']=ruwords['информации']

#	dict_noun['watch']= ruwords['часы (предмет)']
#	dict_noun['watches']= ruwords['часы (предмет)']

____Noun()

# ## Pronoun

# In[38]:


dict_pronoun_ip={}
dict_pronoun_dp={}
def ____Pronoun():

	# In[39]:


	dict_pronoun_ip['I']= ruwords["я (муж)"]
	#dict_pronoun_ip['I']= ruwords["я (жен)"]
	dict_pronoun_dp['me']= ruwords["я (муж)"]
	#dict_pronoun_dp['I']= ruwords["я (жен)"]

	dict_pronoun_ip['he']= ruwords["он"]
	dict_pronoun_dp['him']= ruwords["он"]

____Pronoun()

# ## Numeral

# In[40]:


dict_numeral={}
def ____Numeral():


	# In[41]:


	dict_numeral['one']=   ruwords['один']
	dict_numeral['two']=   ruwords['два']
	dict_numeral['three']= ruwords['три']
	dict_numeral['four']=  ruwords['четыре']
	dict_numeral['five']=  ruwords['пять']
	dict_numeral['six']=   ruwords['шесть']
	dict_numeral['seven']= ruwords['семь']
	dict_numeral['eight']= ruwords['восемь']

____Numeral()

# ## Verb

# In[42]:


dict_verb={}
dict_verb_s={}
def ____Verb():

	# In[43]:


	dict_verb  ['see']= ruwords['видеть']
	dict_verb_s['sees']= ruwords['видеть']
	dict_verb  ['have']= ruwords['иметь']
	dict_verb_s['has']= ruwords['иметь']

	dict_verb  ['give']= ruwords['дать']
	dict_verb_s['gives']= ruwords['дать']
	dict_verb  ['show']= ruwords['показать']
	dict_verb_s['shows']= ruwords['показать']
	dict_verb  ['say']= ruwords['сказать']
	dict_verb_s['says']= ruwords['сказать']
____Verb()
