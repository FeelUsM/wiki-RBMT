'''функции, связанные с парсингом, обработкой строк и их атрибутами

Вначале текст разбивается на токены - слова в нижнем регистре (кроме 'I') и знаки пунктуации.
Нестандартные пробелы (отличные от ' ') записываются атрибут pre.
Во время преобразования массива элементов, обладающих строковыми атрибутами, 
	они разделяются этими префиксами, если префиксы не пусты, иначе пробелами ' '
Различные виды регистра слова записываются в changers.
Теги и прочая информация о разметке записывается в tags. Пока это не реализовано.
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
rule1 - парсит последовательность длины 1 и применяет правило
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

from copy import deepcopy
import re


# # Общее

# In[2]:


class TextError(ValueError):
	pass
class ParseError(ValueError):
	pass
class TestError(ValueError):
	pass


# # Паттерны парсинга

# In[3]:


# In[4]:


PUNCT_CHARS=".,:;?!'-\""


# In[5]:


class SAttrs:
	__slots__=['pre','changers','tags']
	def __init__(self,pre='',changers=None,tags=None):
		if changers==None: changers=set()
		if tags==None: tags=set()
		self.pre=pre
		self.changers=changers
		self.tags=tags
	def change(self,s):
		for changer in self.changers:
			s=changer(s)
		# todo gtags
		return self.pre+s
	def __repr__(self):
	#			'<'+str(id(self))+'>'+\
		return 'SAttrs'+\
			'(pre='+repr(self.pre)+            ',changers='+(('{'+
				','.join('<'+i.__name__+'>' for i in self.changers)+'}') \
					if len(self.changers)>0 else 'set()')+\
			',tags='+repr(self.tags)+')'

	#@staticmethod
	def join(self,arr): #todo сделать поддержку ch_open
		def subr(g):
			yield str(next(g))
			for i in g:
				s=str(i)
				if i.attrs.pre!='' or re.fullmatch('['+re.escape(PUNCT_CHARS)+']*',s):
					yield s
				else: yield ' '+s
		global CH_ANTI_SENTENCE
		if ch_sentence in self.changers:
			stored = CH_ANTI_SENTENCE
			CH_ANTI_SENTENCE = ch_none
			
		r = ''.join(subr(iter(arr)))
		
		if ch_sentence in self.changers:
			CH_ANTI_SENTENCE = stored
		return r

	@staticmethod
	def _to_right(l,r):
		if r.attrs.pre=='':
			r.attrs.pre=l.attrs.pre
		r.attrs.changers|=l.attrs.changers
		r.attrs.tags|=l.attrs.tags
		return r
	@staticmethod
	def _to_left(l,r):
		l.attrs.change|=r.attrs.change
		l.attrs.tags|=r.attrs.tags
		return l

class ParseInfo:
	enabled = False
	__slots__=['p_start','p_end','rule_group','pattern']

# In[6]:


class S(str): # строка с атрибутом
	__slots__=['attrs','parse_info']
	def __new__(cls,s,attrs=None):
		return str.__new__(cls,s)
	def __init__(self,s,attrs=None):
		self.attrs = attrs if attrs!=None else SAttrs()
		self.parse_info = ParseInfo()
		
	def __repr__(self):
		return 'S('+str.__repr__(self)+','+repr(self.attrs)+')'
	def __str__(self):
		return self.attrs.change(str.__str__(self))
	def tostr(self):
		return str(self)

#.pre - строка - вместо начальных пробелов
#.tags - множество пар строк - объединяется
#.changers - множество функций - объединяется


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


# In[8]:


# 'word'
def sp_const_word(str,pos,word):
	return [(pos+len(word),word)] if str[pos:pos+len(word)]==word else []


# In[9]:


def ch_title(s):
	return s.title()
def ch_upper(s):
	return s.upper()
def ch_sentence(s):
	if len(s)==0: return ''
	return s[0].upper()+s[1:]
CH_ANTI_SENTENCE=ch_title
def ch_anti_sentence(s):
	return CH_ANTI_SENTENCE(s)
def ch_none(s):
	return s
def ch_open(s): # для открывающихся кавычек
	return s

# [a-zA-Z]+
def sp_word(str,pos):
	pos1=pos
	while pos1<len(str) and \
			(str[pos1]>='a' and str[pos1]<='z' or str[pos1]>='A' and str[pos1]<='Z' or\
				str[pos1]=='-' and pos1+1<len(str) and pos1-1>=0 and\
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
		print(s,' - перепутаны заглавные и малые буквы')
	return [(pos1,s)]


# In[10]:


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
	pos=0
	pre=''
	while pos<len(s):
		tmp=sp_spcs(s,pos)
		if len(tmp)>0:
			(pos,pre)=tmp[0]
			if pre==' ': pre=''
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
		raise TextError("can't tokenize: "+                        repr(s[max(0,pos-10):pos])+' - '+repr(s[pos:min(len(s),pos+10)]))


# In[14]:


def tokenize(s) : return [i for i in tokenizer(s)]


# In[15]:


#объекты из словаря и паттернов копируются (полностью), потом из них строится дерево

#в эти копии потом добваляется .attrs
def W(w):
	'''если найдено заданное слово, то возвращает его'''
	assert type(w)==str
	return lambda s,p:         [(p+1,deepcopy(s[p]))] if p<len(s) and s[p]==w else []

def D(d):
	'''если найденное слово находится в заданном словаре - возвращает то, что ему сопоставлено'''
	assert type(d)==dict
	def p_from_dict(s,p):
		if p<len(s) and s[p] in d:
			if type(d[s[p]])==list:
				# номер дефолтного варианта находится на 0й позиции. 0===1
				r = d[s[p]][d[s[p]][0]] if d[s[p]][0]>=1 else d[s[p]][1]
			else: r = d[s[p]]
			tmp=deepcopy(r)
			tmp.attrs=deepcopy(s[p].attrs)
			if ParseInfo.enabled:
				tmp.parse_info.pattern = [d['__name__']]
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
	'''
	for i in range(len(args)):
		if args[i]==ELSE:
			break
	else:
		rezs=[]
		for patt in args:
			rezs+=patt(s,p)
		return rezs
	i+=1
	r_rezs=[]
	while i<len(args):
		assert args[i]!=ELSE
		r_rezs+=args[i](s,p)
		i+=1
	if len(r_rezs)==0: return []
	i=0
	e_rezs=[]
	while args[i]!=ELSE:
		e_rezs+=args[i](s,p)
		i+=1
	if len(e_rezs)==0: return r_rezs
	has0=False
	for p,r in e_rezs:
		if r==0:
			return [(p,r) for p,r in e_rezs if r!=0]+r_rezs
	else:
		return e_rezs
	return
#	
	rezs=[]
	for patt in args:
		if patt==ELSE:
			if len(rezs)>0 : return rezs
		else:
			rezs+=patt(s,p)
	return rezs

def alt(*args):
	return lambda s,p: p_alt(s,p,*args)

def seq(patterns,rule_group):#,numbrs=None
	#numbers = range(len(patterns)) if numbrs==None else numbrs
	def null_handler(*args):
		'''возвращает 0, а alt когда видит на месте результата 0 заменяет его на регулярные результаты
		'''
		return 0
	if type(rule_group)==list:
		rule = null_handler if rule_group[0]==0 else rule_group[rule_group[0]]
	else:
		rule = rule_group
	def rule_froup_adder(r):
		r.parse_info.rule_group = rule_group
		return r
	def p_seq_info(s,p):
		return [(pos,rule_froup_adder(rule(*rez))) for pos,rez in sp_seq(s,p,patterns)]
	def p_seq(s,p):
		return [(pos,                 rule(*rez) ) for pos,rez in sp_seq(s,p,patterns)]
	return p_seq_info if ParseInfo.enabled else p_seq
