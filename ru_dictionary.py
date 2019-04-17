'''Правила без аргументов для паттернов-терминалов, т.е. словарь русских слов. И функции его пополнения.

Изначально правила без аргументов записывались в виде функций со странными названиями (типа r_sobaka()),
возвращающими константу (т.е. всегда один и тот же объект).
Потом эти константы стали помещаться в словарь ruwords, с русскими строковыми индексами, независимо от их части речи.

При использовании этих констант в других правилах-функциях (которые для паттернов-нетерминалов)
их надо скопировать и добавить строковый атрибут из исходного текста (который тоже надо скопировать).
Этим занимется функция CW().

Эти объекты-константы содержат постоянные параметры слова и
дефолтные изменяемые параметры слова, а также
содержат поле word, которое является индексом в show_<type>_map,
в котором хранятся функции, которые получают этот объект и 
в зависимости от его параметров выдают слово в соответствующей форме 
(с соответствующим окончанием) в доме который построил Джек.

Индексы в ruwords и show_<type>_map могут быть любыми, но как правило это 
слово в начальной форме, возможно с уточнением в смысла в скобках.
Несколько объектов из ruwords могут ссылаться (посредством .word) на одну функцию из show_<type>_map.
Но для простоты индексы в ruwords и соответствующем show_<type>_map мы будем делать совпадающими,
а в соответствующие ячейки show_<type>_map будет помещаться одна и та же функция.
Т.е. ruwords[xxx].word==xxx .

Личные местоимения и числительные записываются и редактируются в этом файле.

Для существительных, прилагательных и глаголов есть функции для интерактивного (диалогового)
добавления склонений, пряжений и самих слов.

add_runoun2
add_skl2
make_skl2
'''
from parse_system import SAttrs
from classes import StNoun, StAdj, StProNoun, StNum, StVerb, \
					show_noun_map, show_adj_map, show_num_map, show_verb_map
from copy import deepcopy
					
def CW(ru,en=None):
	r=deepcopy(ruwords[ru])
	r.attrs=SAttrs() if en==None else deepcopy(en.attrs)
	return r

# # Правила: RU-Словарь, +отображение
ruwords={} #однословные правила складываются сюда


VERBOSE_ADDS=False 
# во время загрузки модуля ничего не выводим
# в конце включаем отклик на действия со словарём
def errmes(*args):
	if VERBOSE_ADDS:
		print(*args)
	else:
		raise ValueError(*args)

		
# In[3]:


import re
def end_match(word,end):
	return bool(re.match('.*'+end+'$',word))
def start_match(start,word):
	return bool(re.match(start,word))

def make_skl_pos(*words):
	'''возвращает позицию, начиная с которой слова начинают различаться'''
	for i in range(len(words[0])+1):
		start=words[0][:i]
		for w in words:
			if not start_match(start,w): 
				#print(i,start,w)
				return i-1
	#print(i)
	return i
def make_skl(*words):
	'''возвращает массив различающихся частей слов'''
	i=make_skl_pos(*words)
	return tuple(w[i:] for w in words)
def make_skl_word(*words):
	'''возвращает одинаковую ччасть слов'''
	i=make_skl_pos(*words)
	return word[0][:i]


# ## Noun ----------------------------


skl_noun={
	('m',True):[
		{   'ed':('' ,'а' ,'у' ,'а' ,'ом' ,'е' ),#кот
			'mn':('ы','ов','ам','ов','ами','ах'),
		},
		{   'ed':('а','ы' ,'е' ,'у' ,'ой' ,'е' ),#папа
			'mn':('ы',''  ,'ам',''  ,'ами','ах'),
			# частн. случ. пред.
		},
		{   'ed':('' ,'а' ,'у' ,'а' ,'ом' ,'е' ),#волк, мальчик, кролик
			'mn':('и','ов','ам','ов','ами','ах'),
		},
		{   'ed':('ок','ка','ку','ка','ком','ке'),#ребёнок/дети
			'mn':('и' ,'ей','ям','ей','ьми','ях'),
			# частн. случ. пред.
		},
		{   'ed':('ок','ка','ку','ка','ком','ке'),#котёнок, цыплёнок, утёнок
			'mn':('а' ,''  ,'ам',''  ,'ами','ах')
		},
		{   'ed':("ец","ьца","ьцу","льца","ьцем","ьце"),#владелец
			'mn':("ы" ,"ев" ,"ам" ,"ев"  ,"ами" ,"ах" )
		},
		#{   'ed':(),
		#    'mn':()
		#},
	],
	('m',False):[
		{   'ed':('' ,'а' ,'у' ,'' ,'ом' ,'е' ),#дом
			'mn':('а','ов','ам','а','ами','ах')
		},
		{   'ed':('' ,'а' ,'у' ,'' ,'ом' ,'е' ),
			'mn':('ы','ов','ам','ы','ами','ах')
			 #пистолет, эффект, сайт, проект, интернет, торт
			 #раздел, стол, джем, термин, лимон, фонд, сад, принцип, адрес
		},
		{   'ed':('' ,'а' ,'у' ,''  ,'ом' ,'е' ),#ящик, урок, язык, флаг
			'mn':('и','ов','ам','и' ,'ами','ах'),
			# частн. случ. след.
		},
		{   'ed':('' ,'а' ,'у' ,''  ,'ом' ,'е' ),#мяч, карандаш
			'mn':('и','ей','ам','и' ,'ами','ах'),
			'suffix':['ч','ш']
		},
		{   'ed':('ь','я' ,'ю' ,'ь' ,'ем' ,'е' ),#двигатель, автомобиль
			'mn':('и','ей','ям','и' ,'ями','ях')
			# частн. случ. пред.
		},
	],
	('g',True):[
		{   'ed':('а' ,'и' ,'е'  ,'у' ,'ой'  ,'е'  ),#кошка, девочка, лягушка
			'mn':('ки','ек','кам','ек','ками','ках'),
			'suffix':[('шк','ш'),('чк','ч'),('жк','ж')]
			# частн. случ. след. и след.
		},
		{   'ed':('а' ,'и' ,'е'  ,'у' ,'ой'  ,'е'  ),#белка, утка
			'mn':('ки','ок','кам','ок','ками','ках')
			# частн. случ. след.
		},
		{   'ed':('а' ,'и' ,'е'  ,'у'  ,'ой' ,'е' ),#собака
			'mn':('и' ,''  ,'ам' ,''   ,'ами','ах')
		},
		{   'ed':('а','ы','е' ,'у' ,'ой' ,'е' ),
			'mn':('ы','' ,'ам',''  ,'ами','ах')
			 #зебра, крыса, курица, лиса, рыба, корова, коза, мама
		},
		{   'ed':('я' ,'и' ,'е'  ,'ю' ,'ёй'  ,'е'  ),#свинья
			'mn':('ьи','ей','ьям','ей','ьями','ьях')
			# частн. случ. след.
		},
		{   'ed':('я' ,'и' ,'е'  ,'ю' ,'ёй'  ,'е'  ),#змея
			'mn':('и' ,'й' ,'ям' ,'й' ,'ями' ,'ях' )
		},
		{   'ed':('ь','и' ,'и' ,'ь' ,'ью' ,'и' ),#мышь
			'mn':('и','ей','ам','ей','ами','ах'),
			'suffix':['ш']
			# частн. случ. след.
		},
		{   'ed':('ь','и' ,'и' ,'ь' ,'ью' ,'и' ),#лошадь
			'mn':('и','ей','ям','ей','ями','ах'),
		},
		{   'ed':('ь','и' ,'и' ,'ь' ,'ью' ,'и' ),#лошадь
			'mn':('и','ей','ям','ей','ьми','ах'),
		},
	],
	('g',False):[
		{   'ed':('а' ,'и' ,'е'  ,'у'  ,'ой' ,'е'  ),#ручка, чашка, ложка, рубашка
			'mn':('ки','ек','кам','ки','ками','ках'),
			'suffix':[('шк','ш'),('чк','ч'),('жк','ж')]
			# частн. случ. след. и след.
		},
		{   'ed':('а' ,'и' ,'е'  ,'у' ,'ой'  ,'е'  ),#кепка, шапка, коробка, палка
			'mn':('ки','ок','кам','ки','ками','ках')
			# частн. случ. след.
		},
		{   'ed':('а' ,'и' ,'е'  ,'у'  ,'ой' ,'е' ),#книга, космонавтика
			'mn':('и' ,''  ,'ам' ,'и'  ,'ами','ах')
		},
		{   'ed':('а','ы','е' ,'у' ,'ой' ,'е' ),
			'mn':('ы','' ,'ам','ы' ,'ами','ах')
			 #шляпа, ваза, лампа, звезда, работа, кукла, улица, лента, комната
		},
		{   'ed':('я' ,'и' ,'и'  ,'ю' ,'ей'  ,'и'  ),#информация, википедия, организация
			'mn':('и' ,'й' ,'ям' ,'и' ,'ями' ,'ях' )
		},
		{   'ed':('я' ,'и' ,'е'  ,'ю' ,'ёй'  ,'е'  ),#статья
			'mn':('ьи','ей','ьям','ьи','ьями','ьях')
			# частн. случ. пред.
		},
		{   'ed':('ь','и' ,'и' ,'ь' ,'ью' ,'и' ),#тетрадь, кровать, очередь, скорость
			'mn':('и','ей','ям','и' ,'ями','ях')
		},
	],
	('s',True):[
	],
	('s',False):[
		{   'ed':('о' ,'а' ,'у'  ,'о' ,'ом'  ,'е'  ),
			'mn':('а' ,''  ,'ам' ,'а' ,'ами' ,'ах' )
			 #утро, слово, блюдо, представительство, озеро
		},
		{   'ed':('о' ,'а' ,'у'  ,'о' ,'ом'  ,'е'  ),#бревно
			'mn':('на','ен','нам','на','нами','нах')
			# частн. случ. пред.
		},
		{   'ed':('о' ,'а'  ,'у'  ,'о' ,'ом'  ,'е'  ),#дерево
			'mn':('ья','ьев','ьям','ья','ьями','ьях')
		},
		{   'ed':('ё' ,'я' ,'ю'  ,'ё' ,'ём'  ,'е'  ),#ружьё
			'mn':('ья','ей','ьям','ьи','ьями','ьях')
		},
		{   'ed':('е' ,'я' ,'ю'  ,'е' ,'ем'  ,'е'  ),#варенье, платье
			'mn':('ья','ий','ьям','ья','ьями','ьях')
		},
		{   'ed':('е' ,'я' ,'ю'  ,'е' ,'ем'  ,'и'  ),#название, движение
			'mn':('ия','ий','иям','ия','иями','иях')
		},
	],
}

def make_skl2(ip1,ip2, rp1,rp2, dp1,dp2, vp1,vp2, tp1,tp2, pp1,pp2):
	return (make_skl(ip1,rp1,dp1,vp1,tp1,pp1), make_skl(ip2,rp2,dp2,vp2,tp2,pp2)) 

def decline_show_noun2(word, wordmn, r,o,skl):
	'''склоняет слова в ед. и мн. ч. по заданному склонению и печает это

	аргументы: слово, слово во мн.ч., род, одушевленность, склонение'''
	skl_ed=skl_noun[(r,o)][skl]['ed']
	skl_mn=skl_noun[(r,o)][skl]['mn']
	assert end_match(word,skl_ed[0]), (word,skl_ed[0])
	assert end_match(wordmn,skl_mn[0]), (wordmn,skl_mn[0])
	w_ed=word  [:-len(skl_ed[0])] if len(skl_ed[0])>0 else word
	w_mn=wordmn[:-len(skl_mn[0])] if len(skl_mn[0])>0 else wordmn
	dl = max(len(i) for i in skl_ed)+2
	intro=('        ','нет     ','дать    ','вижу    ','творю   ','думаю о ')
	errmes('склонение',skl)
	for i in range(len(intro)):
		errmes(intro[i]+repr(w_ed+skl_ed[i])+' '*(dl-len(skl_ed[i]))+','+repr(w_mn+skl_mn[i])+',')
	errmes('')

def decline_show_noun1(word, c, r,o,skl_n):
	'''склоняет слова в заданном числе по заданному склонению и печает это

	аргументы: слово, число, род, одушевленность, склонение'''
	skl=skl_noun[(r,o)][skl_n][c]
	assert end_match(word,skl[0]), (word,skl[0])
	w = word  [:-len(skl[0])] if len(skl[0])>0 else word
	intro=('        ','нет     ','дать    ','вижу    ','творю   ','думаю о ')
	errmes('склонение',skl_n)
	for i in range(len(intro)):
		errmes(intro[i]+repr(w+skl[i])+',')
	errmes('')

def auto2_skl_noun2(r,o,set1):
	'''находит и возвращает более частное склонение (склонения)
	
	по хорошему надо делать матрицу, кто в ком содержится
	обязательно должен быть флаг склонений (a subset b, b subset c, c subset d...)
	но мы просто найдем склонения, которые содержатся в минимальном количестве склонений
	или склонения, в которых содержится максимальное количество склонений
	кароче что-то одно из этого
	'''
	if len(set1)==0: 
		return set1
	
	skl=skl_noun[(r,o)]
	def subset(i,j):
		return end_match(skl[i]['ed'][0],skl[j]['ed'][0]) and             end_match(skl[i]['mn'][0],skl[j]['mn'][0])
	m = {i:0 for i in set1}
	for i in set1:
		for j in set1:
			if subset(i,j):
				m[i]+=1
	#print(repr(m))
	ma=max(v for k,v in m.items())
	return {k for k,v in m.items() if v==ma}

def auto1_skl_noun2(word,wordmn,r,o):
	'''по окончаниям ип (и если есть по suffix) ищет подходящие варианты
		
	сначала ищет просто по окончаниям, потом сужает поиск по suffix (если есть)
	если есть и с suffix и без suffix, оставляет только с suffix (там остается 1 вариант)
	иначе возвращает auto2_skl_noun2(от найденного множества)
	'''
	set1=set()
	skl=skl_noun[(r,o)]
	for i in range(len(skl)):
		#print(i,word,skl[i]['ed'][0],wordmn,skl[i]['mn'][0],\
		#	end_match(word,skl[i]['ed'][0]),end_match(wordmn,skl[i]['mn'][0]))
		if end_match(word,skl[i]['ed'][0]) and end_match(wordmn,skl[i]['mn'][0]):
			set1|={i}
	#print(repr(set1))
	set2 = set()# подходят для suffix
	set11=set()# не подходят для suffix
	for i in set1:
		if 'suffix' in skl[i]:
			for e in skl[i]['suffix']:
				eed=e if type(e)==str else e[0]
				emn=e if type(e)==str else e[1]
				if end_match(word,eed+skl[i]['ed'][0]) and end_match(wordmn,emn+skl[i]['mn'][0]):
					set2|={i}
					break
			else:
				set11|={i}
	if len(set2)>0:
		return set2
	else:
		if len(set11)>0 and VERBOSE_ADDS:
			print('из-за уточняющих suffix отбрасываются следующие склонения',set11)
			for i in set11:
				print(skl[i]['suffix'])
				decline_show_noun2(word, wordmn, r,o,i)
		return auto2_skl_noun2(r,o,set1-set11)

def auto2_skl_noun1(c,r,o,set1):
	'''находит и возвращает более частное склонение (склонения)
	
	по хорошему надо делать матрицу, кто в ком содержится
	обязательно должен быть флаг склонений (a subset b, b subset c, c subset d...)
	но мы просто найдем склонения, которые содержатся в минимальном количестве склонений
	или склонения, в которых содержится максимальное количество склонений
	кароче что-то одно из этого
	'''
	if len(set1)==0: 
		return set1
	
	skl=skl_noun[(r,o)]
	def subset(i,j):
		return end_match(skl[i][c][0],skl[j][c][0])
	m = {i:0 for i in set1} # создаем map из set-а
	for i in set1:
		for j in set1:
			if subset(i,j):
				m[i]+=1
	#print(repr(m))
	ma=max(v for k,v in m.items())
	return {k for k,v in m.items() if v==ma}

def same_skl_filter(c,r,o,set1):
	tmp=set()
	for sn in set1:
		for ysn in tmp:
			if skl_noun[(r,o)][sn][c] == skl_noun[(r,o)][ysn][c]:
				break
		else:
			tmp|={sn}
	return tmp

def auto1_skl_noun1(word,c,r,o):
	'''по окончаниям ип (и если есть по suffix) ищет подходящие варианты
		
	сначала ищет просто по окончаниям, потом сужает поиск по suffix (если есть)
	если есть и с suffix и без suffix, оставляет только с suffix (там остается 1 вариант)
	иначе возвращает auto2_skl_noun2(от найденного множества)
	'''
	set1=set()
	skl=skl_noun[(r,o)]
	for i in range(len(skl)):
		#print(i,word,skl[i]['ed'][0],wordmn,skl[i]['mn'][0],\
		#	end_match(word,skl[i]['ed'][0]),end_match(wordmn,skl[i]['mn'][0]))
		if end_match(word,skl[i][c][0]):
			set1|={i}
	#print(repr(set1))
	set2 = set()# подходят для suffix
	set11=set()# не подходят для suffix
	for i in set1:
		if 'suffix' in skl[i]:
			for e in skl[i]['suffix']:
				eed=e if type(e)==str else e[0]
				emn=e if type(e)==str else e[1]
				if end_match(word,eed+skl[i]['ed'][0]) and end_match(wordmn,emn+skl[i]['mn'][0]):
					set2|={i}
					break
			else:
				set11|={i}
	if len(set2)>0:
		return same_skl_filter(c,r,o,set2)
	else:
		if len(set11)>0 and VERBOSE_ADDS:
			print('из-за уточняющих suffix отбрасываются следующие склонения',same_skl_filter(c,r,o,set11))
			for i in same_skl_filter(c,r,o,set11):
				print(skl[i]['suffix'])
				decline_show_noun1(word, c, r,o,i)
		return auto2_skl_noun1(c,r,o,same_skl_filter(c,r,o,set1-set11))

# In[5]:


def show_noun_fun(st,word,ends):
	'''берет слово и добавляет к нему окончание в падеже, указанном в структуре'''
	ip,rp,dp,vp,tp,pp = ends
	if st.pad=='ip' : return word+ip
	if st.pad=='rp' : return word+rp
	if st.pad=='dp' : return word+dp
	if st.pad=='vp' : return word+vp
	if st.pad=='tp' : return word+tp
	if st.pad=='pp' : return word+pp
	raise RuntimeError()
	
def add_skl2(r,o,ends):
	'''добавляет склонение для ед. и мн. ч.

	при этом проверяет, чтобы оно не дублировалось'''
	ed_ends, mn_ends = ends
	skl_ro = skl_noun[(r,o)]
	for i in range(len(skl_ro)):
		#print(skl_ro[i]['ed'],ed_ends,skl_ro[i]['mn'],mn_ends)
		if skl_ro[i]['ed']==ed_ends and skl_ro[i]['mn']==mn_ends:
			errmes('Это склонение уже существует:',i,repr(skl_ro[i]))
			return
	skl_ro.append(dict(ed=ed_ends, mn=mn_ends))
	if VERBOSE_ADDS: print('Добавлено новое склонение',len(skl_ro)-1,r,o,skl_ro[len(skl_ro)-1])
def add_skl1(c,r,o,ends):
	skl_ro = skl_noun[(r,o)]
	for i in range(len(skl_ro)):
		if skl_ro[i][с]==ends:
			errmes('Это склонение уже существует:',i)
			return
	skl_ro.append({c:ends})
	if VERBOSE_ADDS: 
		print('Добавлено новое склонение',len(skl_ro)-1)
		

def add_runoun2(word,wordmn,r,o,skl=None,sense=None):
	'''определяет склонение (если не указано) и добавляет слово в словарь'''
	if skl==None:
		skl = auto1_skl_noun2(word,wordmn,r,o)
		if len(skl)==0:
			errmes('Не найдено ни одного подходящего склонения:', word,wordmn)
			return False
		elif len(skl)>1:
			errmes('найдено больше одного склонения, уточните:', word,wordmn,skl)
			for i in skl:
				decline_show_noun2(word, wordmn, r,o,i)
			return False
		else:
			skl=next(iter(skl))
	name = word+((' ('+sense+')') if sense !=None else '')
	namemn = wordmn+((' ('+sense+')') if sense !=None else '')
	skl_ed = skl_noun[(r,o)][skl]['ed']
	skl_mn = skl_noun[(r,o)][skl]['mn']
	shword = word  [:-len(skl_ed[0])] if len(skl_ed[0])>0 else word
	shwordmn = wordmn  [:-len(skl_mn[0])] if len(skl_mn[0])>0 else wordmn
	ruwords[name]=StNoun(name,namemn,o,r,'ed','ip')#StNoun
	ruwords[namemn]=StNoun(namemn,name,o,r,'mn','ip')
	show_noun_map[name]=lambda st: show_noun_fun(st,shword,skl_ed)
	show_noun_map[namemn]=lambda st: show_noun_fun(st,shwordmn,skl_mn)
	if VERBOSE_ADDS:
		print('добавлены',word,wordmn)
		decline_show_noun2(word, wordmn, r,o,skl)
	return True

def add_runoun1(word,c,r,o,skl_n=None,sense=None):
	'''определяет склонение (если не указано) и добавляет слово в словарь'''
	if skl_n==None:
		skl_n = auto1_skl_noun1(word,c,r,o)
		if len(skl_n)==0:
			errmes('Не найдено ни одного подходящего склонения:', word)
			return False
		elif len(skl_n)>1:
			errmes('найдено больше одного склонения, уточните:', word,c,skl_n)
			for i in skl_n:
				decline_show_noun1(word, c, r,o,i)
			return False
		else:
			skl_n=next(iter(skl_n))
	name = word+((' ('+sense+')') if sense !=None else '')
	skl = skl_noun[(r,o)][skl_n][c]
	shword = word  [:-len(skl[0])] if len(skl[0])>0 else word
	ruwords[name]=StNoun(name,None,o,r,c,'ip')#StNoun
	show_noun_map[name]=lambda st: show_noun_fun(st,shword,skl)
	if VERBOSE_ADDS:
		print('добавлено',word)
		decline_show_noun1(word, c, r,o,skl_n)
	return True


# ## Pronoun ----------------------------


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

def ____Pronoun():
	ruwords["я (муж)"]=StProNoun("я","мы",1,True,'m','ed','ip')
	ruwords["я (жен)"]=StProNoun("я","мы",1,True,'g','ed','ip')
	show_noun_map["я"]=lambda st: show_noun_fun(st,'',("я","меня","мне","меня","мной","мне"))
	ruwords["ты (муж)"]=StProNoun("ты","вы",2,True,'m','ed','ip')
	ruwords["ты (жен)"]=StProNoun("ты","вы",2,True,'g','ed','ip')
	show_noun_map["ты"]=lambda st: show_noun_fun(st,'',("ты","тебя","тебе","тебя","тобой","тебе"))

	ruwords["мы"]=StProNoun("мы","я (муж)",1,True,'m','mn','ip')
	show_noun_map["мы"]=lambda st: show_noun_fun(st,'',("мы","нас","нам","нас","нами","нас"))
	ruwords["вы"]=StProNoun("вы","ты (муж)",2,True,'m','mn','ip')
	show_noun_map["вы"]=lambda st: show_noun_fun(st,'',("вы","вас","вам","вас","вами","вас"))

	def add_rupronoun(name,sh_name,och,pers,r,c,ends,nends):
		ruwords[name]=StProNoun(sh_name,och,pers,True,r,c,'ip')
		show_noun_map[sh_name]=lambda st: show_pronoun1(st,ends,nends)
	add_rupronoun('он','он',"они",3,'m','ed',
						  ("он", "его" ,"ему" ,"его" ,"им"  ,"нём"),
						  ("он", "него","нему","него","ним" ,"нём"))
	add_rupronoun('оно','оно',"они",3,'s','ed',
						  ("оно","его" ,"ему" ,"его" ,"им"  ,"нём"),
						  ("оно","него","нему","него","ним" ,"нём"))
	add_rupronoun('она','она',"они",3,'g','ed',
						  ("она","её"  ,"ей"  ,"её"  ,"ей"  ,"ней"),
						  ("она","неё" ,"ней" ,"неё" ,"ней" ,"ней"))
	add_rupronoun('они','они',"он",3,'m','mn',
						  ("они","их"  ,"им"  ,"их"  ,"ими" ,"них"),
						  ("они","них" ,"ним" ,"них" ,"ними","них"))
	# он                   оно                  она                 они         
	# нет его      у него  нет его      у него  нет её      у неё   нет их      у них
	# дать ему     к нему  дать ему     к нему  дат ей      к ней   дать им     к ним
	# вижу его     в него  вижу его     в него  вижу её     в неё   вижу их     в них
	# творю им     под ним творю им     под ним творю ей    под ней творю ими   под ними
	# думаю о нём          думаю о нём          думаю о ней         думаю о них 
____Pronoun()


# ## Adj ----------------------------


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

def ____Adj():
	# In[18]:


	def add_ruadj(name,sh_word,ends):
		ruwords[name]=StAdj(name,True,'m','ed','ip')
		show_adj_map[name]=lambda st: show_adj1(st,sh_word,ends)


	# In[19]:


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
	adj_std_ends_ny={# ы
		'm' :('ный','ного','ному',('ного','ный'),'ным' ,'ном','' ),
		's' :('ное','ного','ному',('ное', 'ное'),'ным' ,'ном','о'),
		'g' :('ная','ной' ,'ной' ,('ную', 'ную'),'ной' ,'ной','а'),
		'mn':('ные','ных' ,'ным' ,('ных', 'ные'),'ными','ных','ы'),
	}
	adj_std_ends_ny2={# ы
		'm' :('ный','ного','ному',('ного','ный'),'ным' ,'ном','ен' ),
		's' :('ное','ного','ному',('ное', 'ное'),'ным' ,'ном','но'),
		'g' :('ная','ной' ,'ной' ,('ную', 'ную'),'ной' ,'ной','на'),
		'mn':('ные','ных' ,'ным' ,('ных', 'ные'),'ными','ных','ны'),
	}
	adj_std_ends_y_sh={# ы
		'm' :('ый','ого','ому',('ого','ый'),'ым' ,'ом',None),
		's' :('ое','ого','ому',('ое', 'ое'),'ым' ,'ом',None),
		'g' :('ая','ой' ,'ой' ,('ую', 'ую'),'ой' ,'ой',None),
		'mn':('ые','ых' ,'ым' ,('ых', 'ые'),'ыми','ых',None),
	}

	add_ruadj('летучий','летуч' ,adj_std_ends_i)
	add_ruadj('хороший','хорош' ,adj_std_ends_i)

	add_ruadj('добрый' ,'добр' ,adj_std_ends_y)
	add_ruadj('некоторый' ,'некотор' ,adj_std_ends_y_sh)
	add_ruadj('определённый' ,'определён' ,adj_std_ends_ny)
	add_ruadj('длинный' ,'длин' ,adj_std_ends_ny2)

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
____Adj()


# ## Num ----------------------------


def ____Num():

	# In[20]:


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


	# In[21]:


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

	add_runum('три'          ,'2-4','mn','тр'           ,{   'mn':('и','ёх','ём',('ёх','и'),'емя','ёх'), }    )
	add_runum('четыре'       ,'2-4','mn','четыр'        ,{   'mn':('е','ёх','ём',('ёх','е'),'ьмя','ёх'), }    )
	add_runum('много'        ,'>=5','mn','мног'         ,{   'mn':('о','о' ,'им',('о', 'о'),'ими','их'), }    )
	add_runum('пять'         ,'>=5','mn','пят'          ,{   'mn':('ь','и' ,'и' ,('ь', 'ь'),'ью' ,'и' ), }    )
	add_runum('шесть'        ,'>=5','mn','шест'         ,{   'mn':('ь','и' ,'и' ,('ь', 'ь'),'ью' ,'и' ), }    )
	add_runum('семь'         ,'>=5','mn','сем'          ,{   'mn':('ь','и' ,'и' ,('ь', 'ь'),'ью' ,'и' ), }    )
	add_runum('восемь'       ,'>=5','mn','вос'          ,{   'mn':('емь','ьми','ьми',('емь','емь'),'емью','ьми'),})
	add_runum('девять'       ,'>=5','mn','девят'        ,{   'mn':('ь','и' ,'и' ,('ь', 'ь'),'ью' ,'и' ), }    )
	add_runum('десять'       ,'>=5','mn','десят'        ,{   'mn':('ь','и' ,'и' ,('ь', 'ь'),'ью' ,'и' ), }    )
	add_runum('одинадцать'   ,'>=5','mn','одинадцат'    ,{   'mn':('ь','и' ,'и' ,('ь', 'ь'),'ью' ,'и' ), }    )
	add_runum('двенадцать'   ,'>=5','mn','двенадцат'    ,{   'mn':('ь','и' ,'и' ,('ь', 'ь'),'ью' ,'и' ), }    )
	add_runum('тринадцать'   ,'>=5','mn','тринадцат'    ,{   'mn':('ь','и' ,'и' ,('ь', 'ь'),'ью' ,'и' ), }    )
	add_runum('четырнадцать' ,'>=5','mn','четырнадцат'  ,{   'mn':('ь','и' ,'и' ,('ь', 'ь'),'ью' ,'и' ), }    )
	add_runum('пятнадцать'   ,'>=5','mn','пятннадцат'   ,{   'mn':('ь','и' ,'и' ,('ь', 'ь'),'ью' ,'и' ), }    )
	add_runum('шестнадцать'  ,'>=5','mn','шестнадцат'   ,{   'mn':('ь','и' ,'и' ,('ь', 'ь'),'ью' ,'и' ), }    )
	add_runum('семнадцать'   ,'>=5','mn','семнадцат'    ,{   'mn':('ь','и' ,'и' ,('ь', 'ь'),'ью' ,'и' ), }    )
	add_runum('восемнадцать' ,'>=5','mn','восемнадцат'  ,{   'mn':('ь','и' ,'и' ,('ь', 'ь'),'ью' ,'и' ), }    )
	add_runum('девятнадцать' ,'>=5','mn','девятнадцат'  ,{   'mn':('ь','и' ,'и' ,('ь', 'ь'),'ью' ,'и' ), }    )
	add_runum('двадцать'      ,'>=5','mn','двадцат'      ,{   'mn':('ь','и' ,'и' ,('ь', 'ь'),'ью' ,'и' ), }    )
#	add_runum('надцать','>=5','mn','ннадцат' ,			{   'mn':('ь','и' ,'и' ,('ь', 'ь'),'ью','и'), }    )
____Num()


# ## Verb ----------------------------


def ____Verb():

	# In[22]:


	def show_verb1(st,word,end_map):
		if st.form=='neopr':
			end = end_map[st.form]
		elif  st.form=='povel':
			end = end_map[st.form][0 if st.chis=='ed' else 1]
		else:
			(i,you,he,she,it,we,yous,they)=end_map[st.form]
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
	def add_ruverb(word,oasp,asp,wo,ends):
		ruwords[word]= StVerb(word,oasp,asp,'neopr',None,None,None)
		show_verb_map[word]=    lambda st: show_verb1(st,wo,ends)

	# In[23]:


	add_ruverb('видеть',"увидеть"   ,'nesov','ви',
			{    'neopr':"деть",
				 'povel':("дь","дьте"),
				 'nast': ("жу","дишь","дит","дит","дит","дим","дите","дят")
			}   )
	add_ruverb('увидеть',"видеть"   ,'sov','уви',
			{    'neopr':"деть",
				 'povel':("дь","дьте"),
				 'nast': ("жу","дишь","дит","дит","дит","дим","дите","дят")
			}   )

	add_ruverb('показать','показывать','sov','пока',
			{    'neopr':"зать",
				 'povel':("жи","жите"),
				 'nast': ("жу","жешь","жет","жет","жет","жем","жете","жут")
			}   )
	add_ruverb('показывать','показать','nesov','пока',
			{    'neopr':"зывать",
				 'povel':("жи","жите"),
				 'nast': ("зываю","зываешь","зывает","зывает","зывает","зываем","зываете","зывают")
			}   )

	add_ruverb('сказать','говорить'  ,'sov','ска',
			{    'neopr':"зать",
				 'povel':("жи","жите"),
				 'nast': ("жу","жешь","жет","жет","жет","жем","жете","жут")
			}   )
	add_ruverb('говорить','сказать','nesov','говор',
			{    'neopr':"ить",
				 'povel':("и","ите"),
				 'nast': ("ю","ишь","ит","ит","ит","им","ите","ят")
			}   )

	add_ruverb('дать','давать'    ,'sov','да',
			{    'neopr':"ть",
				 'povel':("й","йте"),
				 'nast': ("м","шь","ст","ст","ст","дим","дите","дут")
			}   )
	add_ruverb('давать','дать'    ,'nesov','да',
			{    'neopr':"вать",
				 'povel':("вай","вайте"),
				 'nast': ("ю","ёшь","ёт","ёт","ёт","ём","ёте","ют")
			}   )

	add_ruverb('иметь',"заиметь"   ,'nesov','име',
			{    'neopr':"ть",
				 'povel':("й","йте"),
				 'nast': ("ю","ешь","ет","ет","ет","ем","ете","ют")
			}   )
	add_ruverb('заиметь',"иметь"   ,'sov','заиме',
			{    'neopr':"ть",
				 'povel':("й","йте"),
				 'nast': ("ю","ешь","ет","ет","ет","ем","ете","ют")
			}   )

	add_ruverb('мочь',"смочь"   ,'nesov','мо',
			{    'neopr':"чь",
				 'povel':("ги","гите"),
				 'nast': ("гу","жешь","жет","жет","жет","жем","жете","гут")
			}   )
	add_ruverb('смочь',"мочь"   ,'sov','смо',
			{    'neopr':"чь",
				 'povel':("ги","гите"),
				 'nast': ("гу","жешь","жет","жет","жет","жем","жете","гут")
			}   )

	add_ruverb('есть (быть)','стать'   ,'nesov','',
			{    'neopr':"есть",
				 'povel':("стань","станьте"),
				 'nast': ("есть","есть","есть","есть","есть","есть","есть","есть")
			}   )
	add_ruverb('являться',None   ,'nesov','явля',
			{    'neopr':"яться",
				 'povel':("йся","йтесь"),
				 'nast': ("юсь","ешься","ется","ется","ется","емся","етесь","ются")
			}   )
	add_ruverb('находиться',None   ,'nesov','нахо',
			{    'neopr':"диться",
				 'povel':("дись","дитесь"),
				 'nast': ("жусь","дишься","дится","дится","дится","димся","дитесь","дятся")
			}   )

	add_ruverb('любить','полюбить','nesov','люб',
			{    'neopr':"ить",
				 'povel':("и","ите"),
				 'nast': ("лю","ишь","ит","ит","ит","им","ите","ят")
			}   )
	add_ruverb('полюбить','любить','sov','полюб',
			{    'neopr':"ить",
				 'povel':("и","ите"),
				 'nast': ("лю","ишь","ит","ит","ит","им","ите","ят")
			}   )

	add_ruverb('нравиться','понравиться','nesov','нрав',
			{    'neopr':"иться",
				 'povel':("ься","ьтесь"),
				 'nast': ("люсь","ишься","ится","ится","ится","имся","итесь","ятся")
			}   )
	add_ruverb('понравиться','нравиться','sov','понрав',
			{    'neopr':"иться",
				 'povel':("ься","ьтесь"),
				 'nast': ("люсь","ишься","ится","ится","ится","имся","итесь","ятся")
			}   )

	add_ruverb('ловить','поймать','nesov','лов',
			{    'neopr':"ить",
				 'povel':("и","ите"),
				 'nast': ("лю","ишь","ит","ит","ит","им","ите","ят")
			}   )
	add_ruverb('поймать','ловить','sov','пойма',
			{    'neopr':"ть",
				 'povel':("й","йте"),
				 'nast': ("ю","ешь","ет","ет","ет","ем","ете","ют")
			}   )

	add_ruverb('считать','посчитать','nesov','счита',
			{    'neopr':"ть",
				 'povel':("й","йте"),
				 'nast': ("ю","ешь","ет","ет","ет","ем","ете","ют")
			}   )
	add_ruverb('сосчитать','считать','sov','счита',
			{    'neopr':"ть",
				 'povel':("й","йте"),
				 'nast': ("ю","ешь","ет","ет","ет","ем","ете","ют")
			}   )
	add_ruverb('посчитать','считать','sov','счита',
			{    'neopr':"ть",
				 'povel':("й","йте"),
				 'nast': ("ю","ешь","ет","ет","ет","ем","ете","ют")
			}   )

____Verb()
	
VERBOSE_ADDS=True
