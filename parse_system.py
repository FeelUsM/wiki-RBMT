'''функции, связанные с парсингом, обработкой строк и их атрибутами

Вначале текст разбивается на токены - слова в нижнем регистре (кроме 'I' - он остается в верхнем) и знаки пунктуации.
Нестандартные пробелы (отличные от ' ') записываются в атрибут attrs.pre.
Во время преобразования массива элементов, обладающих строковыми атрибутами, 
	они разделяются этими префиксами, если префиксы не пусты, иначе пробелами ' '
Различные виды регистра слова записываются в attrs.changers.
Теги и прочая информация о разметке записывается в attrs.tags. Пока это не реализовано.

SAttrs            - Атрибуты строк - префикс pre, changers и tags
S                 - стд. строка с полем attrs - атрибутами данной строки
ch_title
ch_sentence
ch_anti_sentence
ch_open           - доступные changers

tokenizer - генератор, разбивающий строку на токены
tokenize - вызывает tokenizer и возвращает массив токенов


Есть соглашение: 
	функции, принимающие (s,p) в качестве аргументов, имеют префикс p_
	остальные парсинговые функции возвращают p_-функции.
Поскольку грамматика может быть неоднозначной, результатов может быть больше одного.
Каждая p_-функция возвращает массив пар (p,r), где
	r - результат
	p - позиция, где результат закончил парсится
	
Для LL(*) парсинга есть следующие функции:
seq   - парсит последовательность и применяет правило
alt   - парсит альтернативы
p_alt - парсит альтернативы
ELSE  - используется в alt и p_alt
W     - парсит заданное слово
D     - парсит слово из заданного словаря
#pexcept - 

Следубщие типы используются для исключений:
TestError
ParseError
TextError
'''

from copy import deepcopy, copy
import sys
import re

#------------------------------------------------------------
# # Общее

class TextError(ValueError):
	pass
class ParseError(ValueError):
	pass
class TestError(ValueError):
	pass


def default_warning(s): 
    print(s,file=sys.stderr)
warning_fun = default_warning
def warning(s):
	return warning_fun(s)

DEBUGGING=False
CURRENT_DEBUG_DEPTH=0

DEBUGGING_ID=False
def repr_id(self):
	global DEBUGGING_ID
	return '<'+str(id(self))+'>' if DEBUGGING_ID else ''


PUNCT_CHARS=".,:;?!'\""


# # функции-changer-ы, которые могут быть применены к строке при выводе

def ch_title(s):
	"""делает заглавными первые буквы в словах"""
	return s.title()
def ch_upper(s):
	"""делает все буквы заглавными"""
	return s.upper()
def ch_sentence(s):
	"""делает заглавной только первую букву"""
	if len(s)==0: return ''
	return s[0].upper()+s[1:]
CH_ANTI_SENTENCE=ch_title
def ch_anti_sentence(s):
	"""используется в p_sentence как некоторый хак"""
	return CH_ANTI_SENTENCE(s)
def ch_prefix(s):
	"""используется в p_sentence как некоторый хак"""
	return s
CH_ANTI_PREFIX=ch_title
def ch_anti_prefix(s):
	"""используется в p_sentence как некоторый хак"""
	return s
def ch_none(s):
	return s
def ch_open(s): # для открывающихся кавычек
	return s

# # основные низкоуровневые классы

class SAttrs:
	"""Атрибуты строки: 'pre','changers','tags'
	pre - префикс, который добавится перед строкой при выводе
	changers - функции-changer-ы, которые будут применены к строке при выводе
	tags - not implemented
	"""
	__slots__=['pre','changers','tags']
	#.pre - строка - вместо начальных пробелов
	#.tags - множество пар строк - объединяется
	#.changers - множество функций - объединяется

	def __init__(self,pre='',changers=None,tags=None):
		if changers==None: changers=set()
		if tags==None: tags=set()
		assert type(changers)==set
		assert type(tags)==set
		self.pre=pre
		self.changers=changers
		self.tags=tags
	def __repr__(self):
	#			'<'+str(id(self))+'>'+\
		return 'SAttrs'+repr_id(self)+'('+\
			repr(self.pre)+            ','+(('{'+
				','.join('<'+i.__name__+'>' for i in self.changers)+'}') \
					if len(self.changers)>0 else 'set()')+\
			','+repr(self.tags)+')'
		return 'SAttrs'+repr_id(self)+\
			'(pre='+repr(self.pre)+            ',changers='+(('{'+
				','.join('<'+i.__name__+'>' for i in self.changers)+'}') \
					if len(self.changers)>0 else 'set()')+\
			',tags='+repr(self.tags)+')'

	def get_pre(self):
		if ch_anti_prefix in self.changers and CH_ANTI_PREFIX==ch_none:
			return ''
		else: return self.pre
	def change(self,s):
		"""применяет себя к строке"""
		for changer in self.changers:
			s=changer(s)
		# todo gtags
		return self.get_pre()+s
	#@staticmethod
	def join(self,arr): #todo сделать поддержку ch_open
		"""преобразует элементы массива в строку и объединяет их, где надо добавляя пробелы"""
		def subr(g):
			yield str(next(g))
			for i in g:
				s=str(i)
				if i.attrs.get_pre()!='' or re.fullmatch('['+re.escape(PUNCT_CHARS)+']*',s):
					yield s
				else: yield ' '+s
		global CH_ANTI_SENTENCE
		global CH_ANTI_PREFIX
		if ch_sentence in self.changers:
			stored = CH_ANTI_SENTENCE
			CH_ANTI_SENTENCE = ch_none
		if ch_prefix in self.changers:
			stored_prefix = CH_ANTI_PREFIX
			CH_ANTI_PREFIX = ch_none
		try:
			r = ''.join(subr(iter(arr)))
		finally:
			if ch_sentence in self.changers:
				CH_ANTI_SENTENCE = stored
			if ch_prefix in self.changers:
				CH_ANTI_PREFIX = stored_prefix
		return r

	#@staticmethod
	def from_left(self,l):
		"""копирование атрибутов от левого объекта к правому"""
		if self.pre=='':
			self.pre=l.pre
		self.changers|=l.changers
		self.tags|=l.tags
		return self
	#@staticmethod
	def from_right(self,r):
		"""копирование атрибутов от правого объекта к левому"""
		self.changers|=r.changers
		self.tags|=r.tags
		return self

class ParseInfo:
	"""система отладки для scheme
	инф-а добавляется в результат (в S и в Struct) в функциях D() и debug_pp()
	информация о том, как был получен данный узел

	p_start - начало
	p_end - конец
	rule_group - rule_group
	patterns - массив _имен_ паттернов, которые возвращали этот узел корневым
	"""
	enabled = False
	__slots__=['p_start','p_end','rule_group','patterns']

class S(str):
	"""строка с атрибутом и ParseInfo"""
	__slots__=['attrs','parse_info']
	def __new__(cls,s,attrs=None):
		return str.__new__(cls,s)
	def __init__(self,s,attrs=None):
		self.attrs = attrs if attrs!=None else SAttrs()
		self.parse_info = ParseInfo()
		
	def __repr__(self):
		return 'S'+repr_id(self)+'('+str.__repr__(self)+','+repr(self.attrs)+')'
	def __str__(self):
		return self.attrs.change(str.__str__(self))
	def tostr(self):
		return str(self)

class RuleVars(list):
	__slots__=['can_be_disabled','link']
	def __init__(self,x,can_be_disabled=False,link=None):
		self.can_be_disabled = can_be_disabled
		self.link = link
		if type(x)==list or isinstance(x,RuleVars):
			assert len(x)>0
			if type(x[0])==int: # инициализируем от списка с числом
				assert len(x)>1
				assert x[0]<len(x)
				for e in x:
					list.append(self,e)
			else: # инициализируем от списка без числа
				list.append(self,1)
				for e in x:
					list.append(self,e)
		else: # инициализируем от единственного объекта
			list.append(self,1)
			list.append(self,x)
	def append(self,ruw,reset=False):
		'''добавляет вариант к переводу (только в виде списка) и устанавливает указатель на него

		если reset==True - предварительно удалит все предыдущие варианты
		'''
		if not reset:
			for w in self:
				if w==ruw:
					warning('добавляем уже имеющееся слово')
					return False
			list.append(self,ruw)
			self[0]=len(self)-1 # 
		else:
			del self[2:]
			self[0]=1
			self[1]=ruw
			#self=[1,ruw]

	def remove(self,n):
		'''удаляет вариант (из списка) и по возможности не меняет указатель варианта

		проверяет, чтобы остался хотябы 1 вариант
		'''
		assert len(self)>=2
		if type(n)!=int: # удаляем конкретный объект
			assert n in self, ("такого объекта нет в списке вариантов", n , self)
			for i in range(1,len(self)):
				if self[i]==n:
					n=i
					break
		assert n>0
		del self[n]
		if n>1 and self[0]>=n: # если указатель варианта указывает на удаляемое слово, будет выбран предыдущий вариант
			self[0]-=1 # иначе указатель продолжиит указывать на прежнее слово
			# но если был выбран 1й или 0й вариант, то он останется прежним
		if self[0]>=len(self):
			self[0]=len(self)-1

	def default(self):
		'''возвращает дефолтный вариант
		
		если вариантов нет - возвращает None
		'''
		return self[0]

	def select(self,n):
		'''устанавливает дефолтный вариант в группе правил
		
		если это сделать невозможно - ничего не меняет
		'''
		if n==None: 
			warning("can't select variant 'None'")
			return False
		assert len(self)>0
		if type(n)!=int:
			assert n in self, ("такого объекта нет в списке вариантов", n , self)
			for i in range(1,len(self)):
				if self[i]==n:
					n=i
					break
		assert type(n)==int and n>=0
		if n>=len(self): 
			warning('number out of range')
			return False
		elif n==0 and not self.can_be_disabled:
			warning('can not be disabled')
			return False
		else:
			self[0]=n
			return True

	def print(self):
		'''печатает список вариантов'''
		print(len(self)-1,'varians, selected number',self[0])
		for i in range(1,len(self)):
			if callable(self[i]):
				if i==self[0]: print(self[i].__name__,'<---')
				else:	   print(self[i].__name__)
			else:
				if i==self[0]: print(self[i],'<---')
				else:	   print(self[i])
		return self


#------------------------------------------------------------
# # Паттерны парсинга


# 'word'
def sp_const_word(str,pos,word):
	return [(pos+len(word),word)] if str[pos:pos+len(word)]==word else []


# [a-zA-Z]+
def sp_word(str,pos):
	"""выставляет слову определенные changer-ы, по особому обрабатывает слово'I' """
	pos1=pos
	while pos1<len(str) and \
			(str[pos1]>='a' and str[pos1]<='z' or str[pos1]>='A' and str[pos1]<='Z' or\
				str[pos1]=='-' and pos1+1<len(str) and pos1-1>=pos and\
					(str[pos1+1]>='a' and str[pos1+1]<='z' or str[pos1+1]>='A' and str[pos1+1]<='Z') and\
					(str[pos1-1]>='a' and str[pos1-1]<='z' or str[pos1-1]>='A' and str[pos1-1]<='Z')) :
		pos1+=1
	if pos1==pos:
		return []

	if str[pos:pos1]=='I':
		return [(pos1,S('I'))]

	s=S(str[pos:pos1].lower())
	if str[pos:pos1].islower():
		pass
	elif str[pos:pos1].istitle():
		s.attrs.changers={ch_title}
	elif str[pos:pos1].isupper():
		s.attrs.changers={ch_upper}
	else:
		warning(s,' - перепутаны заглавные и малые буквы')
	return [(pos1,s)]


# [`PUNCT_CHARS`]
def sp_punct(str,pos):
	pos1=pos
	if pos1<len(str) and str[pos1] in PUNCT_CHARS : # по одному символу, ... - добавим потом
		pos1+=1
	return [] if pos1==pos else [(pos1,S(str[pos:pos1]))]


# In[11]:


def sp_open_tag(s,p):
	return []
def sp_close_tag(s,p):
	return []
def sp_openclose_tag(s,p):
	return sp_const_word(s,p,'<br>')


# In[12]:


# ([ _\r\n\v\t]|sp_openclose_tag)+
def sp_spcs(str,pos):
	pre=''
	pos1=pos
	while pos1<len(str):
		if str[pos1] in ' _\t\n\r\v':
			pre+=str[pos1]
			pos1+=1
			continue
		tmp = sp_openclose_tag(str,pos1)
		if len(tmp)!=0:
			pre+=tmp[0][1]
			pos1=tmp[0][0]
			continue
		break
	return [] if pos1==pos else [(pos1,pre)]    


# In[13]:


def tokenizer(s):
	'''разбивает строку на токены (класса S)'''
	pos=0
	pre=''
	while pos<len(s):
		tmp=sp_spcs(s,pos) 
		if len(tmp)>0:			# если пробелы
			(pos,pre)=tmp[0]    # запоминаем их и всё
			if pre==' ': pre='' # обычные пробелы не учитываются
			continue
		tmp=sp_word(s,pos)
		if len(tmp)>0:
			(pos,foryield) = tmp[0]
			foryield.attrs.pre=pre; pre=''
			yield foryield
			continue
		tmp=sp_punct(s,pos)
		if len(tmp)>0:
			(pos,foryield) = tmp[0]
			foryield.attrs.pre=pre; pre=''
			yield foryield
			continue
		raise TextError("can't tokenize: "+ repr(s[max(0,pos-10):pos])+' - '+repr(s[pos:min(len(s),pos+10)]))


# In[14]:


def tokenize(s) : return [i for i in tokenizer(s)]


#------------------------------------------------------------
# In[15]:


#объекты из словаря и паттернов копируются (полностью), потом из них строится дерево

#в эти копии потом добваляется .attrs
def W(w):
	'''если найдено заданное слово, то возвращает его

	полностью копирует его состроки вместе с атрибутами
	'''
	assert type(w)==str
	return lambda s,p:         [(p+1,deepcopy(s[p]))] if p<len(s) and s[p]==w else []

def D(d):
	'''если найденное слово находится в заданном словаре - возвращает то, что ему сопоставлено

	полностью копирует структуру из словаря 
	и атрибуты полностью копирует из строки
	'''
	assert type(d)==dict , (type(d),d, id(d))
	def p_from_dict(s,p):
		if p<len(s) and s[p] in d:
			if type(d[s[p]])==list or type(d[s[p]])==RuleVars:
				# номер дефолтного варианта находится на 0й позиции.
				# 0 означает что все варианты отключены
				if d[s[p]][0]==0:
					warning(d['__name__']+' '+s[p]+' отключен')
					return [(p+1,[d[s[p]]])]
				else:
					r = d[s[p]][d[s[p]][0]]
			else: r = d[s[p]]
			tmp=deepcopy(r)
			tmp.attrs=deepcopy(s[p].attrs)
			if ParseInfo.enabled:
				tmp.parse_info.patterns = [d['__name__']]
				tmp.parse_info.p_start = p
				tmp.parse_info.p_end = p+1
				tmp.parse_info.rule_group = d[s[p]]
			return [(p+1,tmp)]
		else:
			return []
	return p_from_dict

ELSE=42 # some unusial constant
def p_alt(s,p,*args):
	'''альтернативы и исключения
	
		идем по аргументам до 1го ELSE
		если ELSE нет - парсим все аргументы и всё
		парсим все аргументы после ELSE
			assert ELSE больше не встречается
		если результатов нет (регулярных), то всё
		парсим все аргументы с начала до ELSE
		если результатов (исключений) нет, возвращаем регулярные, всё
		если есть хоть один результат со значением 0
			удаляем все результаты со значением 0
			добавляем регулярные результаты
		всё
		
		+защита от коротких/длинных исключений:
		исключение длины r замещает регулярный текст длины r
	'''
	for i in range(len(args)): #идем по аргументам до 1го ELSE
		if args[i]==ELSE:
			break
	else:                      #если ELSE нет - парсим все аргументы и всё
		rezs=[]
		for patt in args:
			rezs+=patt(s,p)
		return rezs
	i+=1
	r_rezs=[]                  #парсим все аргументы после ELSE
	while i<len(args):
		assert args[i]!=ELSE   #    assert ELSE больше не встречается
		r_rezs+=args[i](s,p)
		i+=1
	if len(r_rezs)==0: return []#если результатов нет (регулярных), то всё
	r_ends = {p1 for p1,r1 in r_rezs}### длины регулярных результатов
	i=0
	e_rezs=[]                  #парсим все аргументы с начала до ELSE
	while args[i]!=ELSE:
		e_rezs+=args[i](s,p)
		i+=1
	if len(e_rezs)==0: 
		return r_rezs          #если результатов (исключений) нет, возвращаем регулярные, всё
							# выключенные исключения
	disabled_e_rezs = [(p1,r1) for p1,r1 in e_rezs if r1==0 or isinstance(r1,RuleVars)]
	disabled_e_ends = {p1 for p1,r1 in disabled_e_rezs}### длины результатов выключенных исключений
	e_rezs = [(p1,r1) for p1,r1 in e_rezs if not (r1==0 or isinstance(r1,RuleVars)) ]
	e_ends = {p1 for p1,r1 in e_rezs}### длины результатов исключений
		
	wrong_ends = e_ends - r_ends#защита от коротких/длинных исключений
	if len(wrong_ends)>0:
		for p1,r1 in e_rezs:
			if p1 in wrong_ends:
				warning('WRONG_EXCEPTION ('+str(p)+':'+str(p1)+'): '+str(r1))
		e_rezs = [(p1,r1) for p1,r1 in e_rezs if p1 not in wrong_ends]	
	remain_ends = r_ends - e_ends#регулярные результаты, для которых нет исключений

	def else_adder(r):
		'''в исключения добавляем __ELSE__'''
		if not hasattr(r.parse_info,'patterns'):
			r.parse_info.patterns = []
		r.parse_info.patterns.append('__ELSE__')
		return r
	def zero_adder(p,r):
		'''в регулярные результаты для которых есть отключенные исключения добавляем эти исключения'''
		if p in disabled_e_ends:
			if not hasattr(r.parse_info,'patterns'):
				r.parse_info.patterns = []
			for p2,r2 in disabled_e_rezs:
				r.parse_info.patterns.append(r2)
		return r
	if ParseInfo.enabled:
		return [(p1,else_adder(r1)) for p1,r1 in e_rezs]+\
			[(p1,zero_adder(p1,r1)) for p1,r1 in r_rezs if p1 in remain_ends]#добавляем регулярные результаты
	else:
		return [(p1,r1) for p1,r1 in e_rezs]+\
			[(p1,r1) for p1,r1 in r_rezs if p1 in remain_ends]#добавляем регулярные результаты
	return
#	old p_alt:
	rezs=[]
	for patt in args:
		if patt==ELSE:
			if len(rezs)>0 : return rezs
		else:
			rezs+=patt(s,p)
	return rezs

def alt(*args):
	return lambda s,p: p_alt(s,p,*args)

# In[7]:


def sp_seq(str,pos,patterns):
	if len(patterns)==1:
		return [(p,[r]) for (p,r) in patterns[0](str,pos)]
	first=patterns[0](str,pos)
	first.sort(key=lambda i:i[0]) # в дальнейшем отключить повторное вычисление 
	# продолжения для одинаковых позиций
	rezs=[]
	for r in first:
		tmp=sp_seq(str,r[0],patterns[1:])
		for rr in tmp:
			rr[1].insert(0,r[1])
		rezs+=tmp
	return rezs


def seq(patterns,rule_group):#,numbrs=None
	#numbers = range(len(patterns)) if numbrs==None else numbrs
	def null_handler(*args):
		'''возвращает rule_group, а alt когда видит на месте результата rule_group, 
		заменяет его на регулярные результаты
		'''
		return rule_group # 0
	if type(rule_group)==list or type(rule_group)==RuleVars:
		rule = null_handler if rule_group[0]==0 else rule_group[rule_group[0]]
	else:
		rule = rule_group
	def rule_group_adder(r):
		r.parse_info.rule_group = rule_group
		return r
	def p_seq_info(s,p):
		return [(pos,rule_group_adder(rule(*rez))) for pos,rez in sp_seq(s,p,patterns)]
	def p_seq(s,p):
		return [(pos,                 rule(*rez) ) for pos,rez in sp_seq(s,p,patterns)]
	return p_seq_info if ParseInfo.enabled else p_seq

global_cache=dict()
def debug_pp(fun):
	s_point=[] # когда изменяется s - означает, что нужно сбросить кэш
	cache={}
	global gloabal_cache
	global_cache[fun.__name__] = cache
	#эта вся функция относится к какому-то паттерну (который обернут этой функцией)
	#cache индексируется позицией в строке
	# и содержит полный_результат - массив пар (позиция,разултат)
	def wrapper(s,p):
		global CURRENT_DEBUG_DEPTH
		nonlocal s_point,cache
		if not(s is s_point):
			s_point=s
			cache={}
			global gloabal_cache
			global_cache[fun.__name__] = cache
		if DEBUGGING:
			indent = '    '*CURRENT_DEBUG_DEPTH
			debug_s = '.'*p+'*'+'.'*(len(s)-p-1)+(' ' if p<len(s) else '')+\
				fun.__name__+'___'+str(p)
		if p in cache:
			if cache[p]==None:
				raise ParseError('зацикливание '+fun.__name__+'(s,'+str(p)+')')
			if DEBUGGING: 
				print(indent+'|'+debug_s)
				if ParseInfo.enabled:
					for p1,r1,patts in cache[p]:
						print(indent+'-'+'.'*p+'_'*(p1-p)+'.'*(len(s)-p1)+' '+\
							 str(r1)+' <'+str(id(patts))+'>'+repr(patts))
				else:
					for p1,r1 in cache[p]:
						print(indent+'-'+'.'*p+'_'*(p1-p)+'.'*(len(s)-p1)+' '+\
							 str(r1))
			if ParseInfo.enabled:
				def cache_info_adder(r1,patterns):
					r1.parse_info.patterns = patterns
					return r1
				return [(p1,cache_info_adder(r1,patterns)) \
						for p1,r1,patterns in cache[p]]
			else:
				return cache[p]
		else:
			if DEBUGGING: print(indent+'{'+debug_s)
		
		cache[p]=None
		rezs=fun(s,p)   # CALL FUN
		assert type(rezs)==list , 'паттерн '+fun.__name__+' вернул неправильный тип'
		if not ParseInfo.enabled:
			cache[p]=rezs
		else:
			def info_adder(p1,r1):
				r1.parse_info.p_start = p
				r1.parse_info.p_end = p1
				if not hasattr(r1.parse_info,'patterns'):
					r1.parse_info.patterns = []
				patt = copy(r1.parse_info.patterns)
				patt.append(fun.__name__)
				r1.parse_info.patterns = patt
				return r1
			rezs = [(p1,info_adder(p1,r1)) for p1,r1 in rezs]
			cache[p]=[ ( p1,r1,r1.parse_info.patterns ) for p1,r1 in rezs]
		
		#for p1,r1 in rezs:
		#    assert p1>p, r1
		
		if DEBUGGING:
			print(indent+'}'+debug_s)
			if ParseInfo.enabled:
				for p1,r1 in rezs:
					print(indent+'-'+'.'*p+'_'*(p1-p)+'.'*(len(s)-p1)+' '+\
						 str(r1)+' <'+str(id(r1.parse_info.patterns))+'>'+\
						  repr(r1.parse_info.patterns))
			else:
				for p1,r1 in rezs:
					print(indent+'-'+'.'*p+'_'*(p1-p)+'.'*(len(s)-p1)+' '+\
						 str(r1))
			
			#print('_'+'.'*p+str(len(rezs)),'in ',fun.__name__,'}',
			#      [(p,str(r)) for (p,r) in rezs],'\n')
			#for i in rezs:
			#    if isinstance(i[1],StDeclinable):
			#        i[1].check_attrs('wrapper:'+fun.__name__)
		
		return rezs
	
	def wrapper2(s,p):
		global CURRENT_DEBUG_DEPTH
		CURRENT_DEBUG_DEPTH+=1
		try:
			r = wrapper(s,p)
		finally:
			CURRENT_DEBUG_DEPTH-=1
		return r
	
	return wrapper2

def reset_globals():
	global DEBUGGING
	DEBUGGING=False
	global CURRENT_DEBUG_DEPTH
	CURRENT_DEBUG_DEPTH=0
	global warning
	warning = default_warning
	global CH_ANTI_SENTENCE
	CH_ANTI_SENTENCE=ch_title
	ParseInfo.enabled = False
	