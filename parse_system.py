# # Общее

# In[1]:


def throw(ex):
    raise ex


# In[2]:


class TextError(ValueError):
    pass
class ParseError(ValueError):
    pass
class TestError(ValueError):
    pass


# # Паттерны парсинга

# In[3]:


from copy import deepcopy,copy
import re


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


# In[6]:


class S(str): # строка с атрибутом
	__slots__='attrs'
	def __new__(cls,s,attrs=None):
		return str.__new__(cls,s)
	def __init__(self,s,attrs=None):
		self.attrs = attrs if attrs!=None else SAttrs()
		
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
#    for patt in patterns:
#        tmp=patt(str,pos)
#        if len(tmp)>1 : raise NotImplementedError()
#        if len(tmp)==0 : return []
#        (pos,tmp)=tmp[0]
#        rezs.append(tmp)
#    return [(pos,rezs)]
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
    assert type(w)==str
    return lambda s,p:         [(p+1,deepcopy(s[p]))] if p<len(s) and s[p]==w else []

def D(d):
    assert type(d)==dict
    def p_from_dict(s,p):
        if p<len(s) and s[p] in d:
            tmp=deepcopy(d[s[p]])
            tmp.attrs=deepcopy(s[p].attrs)
            return [(p+1,tmp)]
        else:
            return []
    return p_from_dict

def seq(patterns,handler):#,numbrs=None
	#numbers = range(len(patterns)) if numbrs==None else numbrs
	def p_seq(s,p):
		return [(pos,handler(*rez)) for pos,rez in sp_seq(s,p,patterns)]
		
		assert False, 'unused'
		# p_seq(s,p,[p0,p1,p2,p3],handle,[0,2,3]) ->
		# for k:
		#   (pos1,rez1) = sp_seq(s,p,[p0,p1,p2,p3]) [k]
		#   rezs.append((pos1,handle(rezs[0],rezs[2],rezs[3],)))
		rezs=[]
		for (pos1,rez1) in sp_seq(s,p,patterns):
			m=[False for i in range(len(patterns))]
			for i in numbers: m[i]=True
			for i in range(max(numbers)):
				if not m[i]: SAttrs.to_right(rez1[i],rez1[i+1])
			for i in range(len(patterns)-1,max(numbers),-1):
				if not m[i]: SAttrs.to_left(rez1[i-1],rez1[i])
			rez2=handler(*[rez1[i] for i in numbers])
			#        for i in rez1:
			#            if isinstance(i,StDeclinable):
			#                i.check_attrs('p_seq')
			#        if isinstance(rez2,StDeclinable):
			#                rez2.check_attrs('p_seq:'+handler.__name__)
			rezs.append((pos1,rez2))
		return rezs
	return p_seq

ELSE=42 # some unusial constant
def alt(*args):
    def p_alt(s,p):
        rezs=[]
        for patt in args:
            if patt==ELSE:
                if len(rezs)>0 : return rezs
            else:
                rezs+=patt(s,p)
        return rezs
    return p_alt

def p_alt(s,p,*args):
	rezs=[]
	for patt in args:
		if patt==ELSE:
			if len(rezs)>0 : return rezs
		else:
			rezs+=patt(s,p)
	return rezs

def rule1(patt,rule):
	def p_rule1(s,p):
		rezs_in=patt(s,p)
		rezs=[]
		for p1,r in rezs_in:
			rezs.append((p1,rule(r)))
		return rezs
	return p_rule1

def CW(ru,en=None,):
    r=deepcopy(ru)
    r.attrs=SAttrs() if en==None else en.attrs
    return r
	
def add_changer(x,changer):
	x.attrs.changers |= {changer}
	return x
