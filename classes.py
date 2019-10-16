'''классы древовидных структур из которых конструируются русские предложения

механизм создания древовидной структуры проще показать на примере

StAdj(рыжий) StNoun(кошка)
правило ->
StNoun(StAdj(рыжая) StNoun(кошка))

S(у) StNoun(StAdj(рыжая) StNoun(кошка))
правило ->
StC(S(у) StNoun(StAdj(рыжей) StNoun(кошки)))

Т.е. правило может менять параметры у аргументов
и при изменении параметра объекта могут меняться параметры его дочерних объектов.
 - так было до оптимизации.
После оптимизации правила не могут изменять объекты.
Вмето этого рядом с объектом создается словарь, в котором хранятся свойства и их значения, 
которые переопределяют свойства самого объекта.
Далее будем эти свойства называть внешними свойствами объекта.

После того как текст разобран и древовидная структура создана
можно вызвать метод .pull_deferred(), который применит свойства, 
хранящиеся рядом с объектом к самому объекту, 
и вызовет .pull_deferred() у дочерних объектов.

После этого объект можно преобразовать в строку функцией str().

	Если при изменении свойства объекта должны измениться свойства его дочерних объектов,
		то эти действия записываются в сеттере этого свойства.
		Они будут выполнены в момент вызова pull_deferred().
	Если при изменении свойства объекта должны измениться другие свойства этого же объекта,
		то эти действия записываются в статическом методе ext_props_setter().
		Они будут выполнены сразу при изменении внешнего свойства, и отразятся на внешних свойствах.


Объекты-листья содержат поле word, которое является индексом в show_<type>_map,
в котором хранятся функции, которые получают эту структуру и 
в зависимости от ее параметров выдают слово в соответствующей форме 
(с соответствующим окончанием) в доме который построил Джек.

Внутренние объекты содержат поле talk - массив туплов длины 3:
talk[i][0] - ключевое слово, которое определяет, в каком подчинении находится дочерний объект
	это одно из слов, перечисленных в obediences класса (dependencies наоборот)
talk[i][1] - сам дочерний объект
	его допустимый тип определяется obediences[key_word]
talk[i][2] - словарь (о котором говорилось выше), в котором хранятся внешние свойства и их значения, 
которые переопределяют свойства дочернего объекта.


Помимо всего прочего, каждый объект содержит поле attrs со строковыми атрибутами.
Во время pull_deferred() префикс нулевого объекта talk-а переезжает к объекту родителю.
Это нужно для корретного преобразования в строку.


Имеется следующая иерархия типов:
Struct                            - Абстрактный базовый тип
	StC                             - Структура-контейнер, без параметров и с независимыми дочерними объектами
	StDeclinable                    - Абстрактный базовый тип со склонением
		StNoun (show_noun_map)        - Существительные
			StProNoun (show_noun_map)   - Личные местоимения
		StAdj (show_adj_map)          - Прилагательные
		StNum (show_num_map)          - Числительные
	StVerb (show_verb_map)          - Глаголы
	
Имеются следующие функции для работы с внешнимим свойствами:
I             - функция с красивым синтаксисом, которая создает tupl-ы для talk-ов
get_property  - функция, возвращающая внешнее свойство объекта внутри tupl-а
set_property  - функция, изменяющая внешнее свойство объекта внутри tupl-а
pull_deferred - функция, применяющая внешние свойства к объекту внутри tupl-а

для более детальной отладки имеются глобальные переменные:
DEBUGGING_ID
DEBUGGING_ATTRS
'''
import parse_system
from parse_system import SAttrs, ParseInfo, S, ch_anti_prefix, repr_id, ContextInfo
from copy import copy

def tmp_rez_checker(rez):
	assert isinstance(rez,Struct) or type(rez)==S, (type(rez),rez)
	return rez
parse_system.rez_checker = tmp_rez_checker

# ## Классы отображения

# ### Базовые

# In[27]:

DEBUGGING_ATTRS=False
def repr_attrs(self,_n=False):
	global DEBUGGING_ATTRS
	return '-'+repr(self.attrs) if DEBUGGING_ATTRS else ''
	# +('\n' if _n else '')

def repr_talk(talk):
	s = '[\n'
	for tup in talk:
		assert len(tup)==3
		#s+=repr(tup)+',\n'
		s+= '('+repr(tup[0])+', '+repr(tup[1])+','+('\n' if len(tup[2]) else ' ')+repr(tup[2])+')'+',\n'
	return s+']'

def I(**args):
	i=iter(args.items())
	p=next(i)
	assert isinstance(p[1],Struct) or isinstance(p[1],S), (type(p[1]),p )
	args.pop(p[0])
	if ParseInfo.enabled: # чтобы отделить деревья результатов от того, что кэшируется
		tup = (p[0], copy(p[1]), {})
		tup[1].parse_info = copy(tup[1].parse_info)
	else:
		tup = (p[0], p[1], {})
	for k,v in args.items():
		set_property(tup,**{k:v})
	return tup #p

def get_property(**kwarg): #get_property(prop=tup)
	assert len(kwarg)==1
	prop, tup= next(iter(kwarg.items()))
	assert len(tup)==3, tup
	if prop in tup[2]:
		return tup[2][prop]
	else:
		return getattr(tup[1],prop)
		
def set_property(tup,**kwarg): #set_property(tup,prop=val)
	assert len(kwarg)==1
	prop, val= next(iter(kwarg.items()))
	assert len(tup)==3, tup
	if prop in {'attrs_from_left','attrs_from_right','add_changers','pull_attrs'}:
		tup[2][prop]=val
	else:
		assert hasattr(tup[1],prop),(tup[1],prop)
		if hasattr(tup[1],'ext_props_setter'):
			tup[1].ext_props_setter(tup,**kwarg)
		else: tup[2][prop]=val

'''
спускаясь вглубь дерева 
	применяю внешние свойства (что может вызывать изменение свойств более глубоких объектов)
	и устанавливаю заданные атрибуты

поднимаясь к корню дерева
	подтягиваю префикс


'''


def pull_deferred(tup):
	'''функция pull_deferred(tup)'''
	pull_attrs_no = None
	# применяю внешние свойства
	for prop,val in tup[2].items():
		if prop=='attrs_from_left':
			tup[1].attrs.from_left(val)
			#SAttrs._to_right(val,tup[1])
		elif prop=='attrs_from_right':
			tup[1].attrs.from_right(val)
			#SAttrs._to_left(tup[1],val)
		elif prop=='add_changers':
			tup[1].attrs.changers|=val
		elif prop=='pull_attrs':
			pull_attrs_no = val # val ignored
		else: setattr(tup[1],prop,val)
	tup[2].clear()
	
	# вызываю метод .pull_deferred()
	if isinstance(tup[1],Struct):
		tup[1].pull_deferred()
		
	# если во внешних свойствах было указано 'pull_attrs', подтягиваю attrs
	if pull_attrs_no!=None:
		assert hasattr(tup[1],'talk') and tup[1].attrs.pre=='',\
			(hasattr(tup[1],'talk') , tup[1].attrs.pre=='')
#		tup[1].attrs = tup[1].talk[pull_attrs_no][1].attrs
#		tup[1].talk[pull_attrs_no][1].attrs = SAttrs()
		tup[1].attrs.pre=tup[1].talk[pull_attrs_no][1].attrs.pre
		tup[1].talk[pull_attrs_no][1].attrs.pre=''
		if ch_anti_prefix in tup[1].talk[pull_attrs_no][1].attrs.changers:
			tup[1].attrs.changers |= {ch_anti_prefix}
			tup[1].talk[pull_attrs_no][1].attrs.changers -= {ch_anti_prefix}
#		tup[1].attrs.changers=tup[1].talk[pull_attrs_no][1].attrs.changers
#		tup[1].talk[pull_attrs_no][1].attrs.changers=set()
		tup[1].attrs.tags=tup[1].talk[pull_attrs_no][1].attrs.tags
		tup[1].talk[pull_attrs_no][1].attrs.tags=set()
		

# In[28]:

class Struct:
	'''абстрактный базовый класс всех узлов
	
	talk - массив дочерних узлов, снабженных тегами
	obediences - набор допустимых тегов и проверок типов узлов, снабженных этими тегами
	обычно, если в объекте есть поле word, и оно строка, то это терминальный узел (без потомков)
	
	теги:
		dep, maindep - зависисмый узел - при изменении параметров узла меняются параметры дочернего узла
		nodep, punct, main - независимый узел (пунктуация - тоже независимый)
		main, maindep - при инициализации узла его параметры задаются из заданного дочернего узла
	
	attrs - строковые атрибуты
		перед (между) узлами, у которых attrs.pre=='' при выводе вставляются пробелы
		по этому перед выводом pre из 0го дочернего узла должно быть перемещено в узел выше
	'''
	__slots__=['attrs','talk','parse_info','context_info']
	def __init__(self,attrs=None):
		self.parse_info = ParseInfo()
		self.context_info = ContextInfo()
		if attrs==None:
			self.attrs=SAttrs()
		elif type(attrs)==list:
			raise RuntimeError('pulling attrs does not supported')
	#            self.attrs=SAttrs()
			self.attrs=SAttrs(pre=attrs[0][1].attrs.pre)
			attrs[0][1].attrs.pre=''
			pass # выделеие общих тегов
		else:
			self.attrs=attrs
		#self.talk=talk    #массив структур или туплов (строка-тип, ...)
	def __repr__(self):
		raise NotImplementedError('virtual function')
	def __str__(self):
		raise NotImplementedError('virtual function')
	def check_attrs(self,mes):
		if self.word==None:
			if self.talk[0][1].attrs.pre!='':
				print(repr(self))
			assert self.talk[0][1].attrs.pre=='', mes

	def pull_deferred(self):
		if not hasattr(self,'talk'): return
		# во свех потомках вызываем pull_deferred
		for tup in self.talk:
			pull_deferred(tup)
		# подтягиваем префикс
		if self.attrs.pre=='':
			self.attrs.pre=self.talk[0][1].attrs.pre
			self.talk[0][1].attrs.pre=''
			# подтягиваем запрет на префикс
			if ch_anti_prefix in self.talk[0][1].attrs.changers:
				self.attrs.changers|={ch_anti_prefix}
				self.talk[0][1].attrs.changers-={ch_anti_prefix}
		return self
		
	def tostr(self):
		self.pull_deferred()
		return self.__str__()
		
	def talk_checker(self):
		for k,v,a in self.talk:
			assert k in self.obediences, (k,self.obediences)
			assert self.obediences[k](v), (type(self), k, type(v))
		
#def _assert(x,y=None):
#	assert x, y
def _types_assert(x,*types):
	for i in types:
		if isinstance(x,i):
			return True
	else:
		return False
		
def types_assert(*types):
	return lambda x:_types_assert(x,*types)
def none_fun(x):
	return True
	
# In[29]:


class StC(Struct): # Container
	'''структура контейнер
	
	все дочерние узлы независимые (или пунктуация)
	'''
	obediences = {
		'nodep': none_fun,
		'punct': types_assert(S)
	}
	def __init__(self,talk):
		assert type(talk)==list, talk
		Struct.__init__(self)
		self.talk=talk
		self.talk_checker()
		
	def __repr__(self):
		return 'StContainer'+repr_id(self)+repr_attrs(self,False)+'('+            repr_talk(self.talk) +')'

	def __str__(self):
		return self.attrs.change( self.attrs.join(i[1] for i in self.talk) )


# In[30]:


show_verb_map={}

class StVerb(Struct):
	'''глагол (в зачаточном состоянии (только настоящее время пока))
	
	параметры:
		asp	# 'sov'/'nesov' - аспект - совершенный/несовершенный (сделать/делать)
		oasp # None или слово - other asp - с противоположной совершенностью
		form # 'neopr'/'povel'/'nast' - форма-наклонение-время
		chis # 'ed'/'mn' - число
		rod # 'm'/'g'/'s' - род - имеет смысл только в настоящем времени
		pers # 1/2/3 - лицо - имеет смысл только в настоящем времени
		
	теги ip, rp, dp, vp, tp, pp - пока все независимые, для существительных в соотв. падеже
	у зависимых узлов меняются form, rod, chis, pers
	'''
	obediences = {
		'main': lambda x:_types_assert(x,StVerb),
		'maindep': lambda x:_types_assert(x,StVerb),
		'nodep': none_fun,
		'punct': types_assert(S),
		'ip': lambda x:_types_assert(x,StDeclinable),
		'rp': lambda x:_types_assert(x,StDeclinable),
		'dp': lambda x:_types_assert(x,StDeclinable),
		'vp': lambda x:_types_assert(x,StDeclinable),
		'tp': lambda x:_types_assert(x,StDeclinable),
		'pp': lambda x:_types_assert(x,StDeclinable),
		#'gde',
		#'kogda',
		#'skolko'
	}
	__slots__=[
		'word', # None или слово - индекс для отображения
		'oasp', # None или слово - с противоположной совершенностью
		
		'_asp',	# 'sov'/'nesov' - аспект
		'_form',# 'neopr'/'povel'/'nast' - форма-наклонение-время
		'_rod', # 'm'/'g'/'s'
		'_chis',# 'ed'/'mn'
		'_pers' # 1/2/3 - лицо
	]
		
	@staticmethod
	def asp_checker(asp):
		assert asp in {'sov','nesov'} ,                                'wrong asp: '+repr(asp)
		return asp

	@staticmethod
	def form_checker(form):
		assert form in {'neopr','povel','nast'} ,                      'wrong form: '+repr(form)
		return form

	@staticmethod
	def chis_checker(form,chis):
		assert form=='neopr' and chis==None or \
			   form!='neopr' and chis in{'ed','mn'},                   'wrong chis: '+repr(chis)+' /'+repr(form)
		return chis

	@staticmethod
	def rod_checker(form,rod):
		assert form in {'neopr','povel'}     and rod==None or \
			   form not in {'neopr','povel'} and rod in {'m','g','s'}, 'wrong rod: '+repr(rod)+' /'+repr(form)
		return rod

	@staticmethod
	def pers_checker(form,pers):
		assert form in {'neopr','povel'}     and pers==None or \
			   form not in {'neopr','povel'} and pers in {1,2,3},      'wrong pers: '+repr(pers)+' /'+repr(form)
		return pers

	def __init__(self,word,oasp=0,asp=None,form=None,chis=0,rod=0,pers=0):
		if type(word)==str:
			Struct.__init__(self)
			self.word=word
			assert oasp==None or type(oasp)==str , oasp
			self.oasp=oasp
		else:
			Struct.__init__(self)
			self.word=None
			self.talk=word
			self.talk_checker()

			found=None
			for i in word:
				if i[0]=='main' or i[0]=='maindep':
					assert found==None , 'we must have only one main or maindep'
					found =i#[1]
					assert asp==None and form==None and chis==0 and pers==0 ,\
						'main or maindep may conflits with asp/form/chis/pers'
					asp=get_property(asp=found)
					form=get_property(form=found)
					rod=get_property(rod=found)
					chis=get_property(chis=found)
					pers=get_property(pers=found)
		self.asp  =self.asp_checker(asp)
		self.form =self.form_checker(form)
		self.rod  =self.rod_checker(form,rod)
		self.chis =self.chis_checker(form,chis)
		self.pers =self.pers_checker(form,pers)

	@staticmethod
	def ext_props_setter(tup,**kwarg): #ext_prop_setter(tup,prop=val)
		prop, val= next(iter(kwarg.items()))
		tup[2][prop]=val
		if prop=='form':
			StVerb.form_checker(val)
			if val=='neopr':
				set_property(tup,chis=None)
			elif val in {'neopr','povel'}:
				set_property(tup,rod=None)
				set_property(tup,pers=None)
		elif prop=='rod':  StVerb.rod_checker(get_property(form=tup),val)
		elif prop=='chis': StVerb.chis_checker(get_property(form=tup),val)
		elif prop=='pers': StVerb.pers_checker(get_property(form=tup),val)
		elif prop=='asp':  StVerb.asp_checker(val)
		
	form=property()
	@form.getter
	def form(self):
		return self._form
	@form.setter
	def form(self,val):
		self._form=val
		if self.word==None:
			for i in self.talk:
				if i[0]=='dep' or i[0]=='maindep' :
					set_property(i,form=val)
				
	rod=property()
	@rod.getter
	def rod(self):
		return self._rod
	@rod.setter
	def rod(self,val):
		self._rod=val
		if self.word==None:
			for i in self.talk:
				if i[0]=='dep' or i[0]=='maindep' :
					set_property(i,rod=val)
				
	chis=property()
	@chis.getter
	def chis(self):
		return self._chis
	@chis.setter
	def chis(self,val):
		self._chis=val
		if self.word==None:
			for i in self.talk:
				if i[0]=='dep' or i[0]=='maindep' :
					set_property(i,chis=val)
				
	pers=property()
	@pers.getter
	def pers(self):
		return self._pers
	@pers.setter
	def pers(self,val):
		self._pers=val
		if self.word==None:
			for i in self.talk:
				if i[0]=='dep' or i[0]=='maindep' :
					set_property(i,pers=val)
				
	asp=property()
	@asp.getter
	def asp(self):
		return self._asp
	@asp.setter
	def asp(self,val):
		#print('set asp')#,repr(self))
		if not hasattr(self,'_asp'): # for constructor
			self._asp=val
		elif self._asp!=val:
			#print('change asp')
			self._asp=val
			if self.word!=None:
				if self.oasp==None :
					pass
				elif type(self.oasp)==str:
					tmp=self.oasp
					self.oasp=self.word
					self.word=tmp
				else:
					raise RuntimeError('internal error: StNoun.oasp = '+self.oasp)
			else:
				for i in self.talk:
					if i[0]=='dep' or i[0]=='maindep' :
						set_property(i,asp=val)

	def __repr__(self):
		return 'StVerb'+repr_id(self)+repr_attrs(self,self.word!=None)+'('+\
			(repr_talk(self.talk) if self.word==None else repr(self.word)+','\
			+repr(self.oasp))+','+ 'asp='+repr(self.asp)+','+ 'form='+repr(self.form)+','+ 'chis='+repr(self.chis)+','+            'pers='+repr(self.pers)+')'

	def __str__(self):
		return self.attrs.change(
			self.attrs.join(i[1] for i in self.talk)
				if self.word==None else show_verb_map[self.word](self)
			)


# ### Склоняемые

# In[31]:


class StDeclinable(Struct):
	'''абстрактный базовый класс для всех склоняемых типов (существительное, личное местоимение, прилагательное, числительное)
	
	параметры
		odush # True/False - одушевленный/неодушевленный
		rod - род
		chis - число
		pad - падеж
		
	у зависимых узлов меняется pad
	'''
	#__slots__=['word','odush','rod','chis','_pad']#  

	@staticmethod
	def odush_checker(odush):
		assert type(odush)==bool , 'odush must be bool, not '+repr(odush)
		return odush
		
	@staticmethod
	def rod_checker(rod):
		assert rod in {'m','g','s'}, 'rod must be m or g or s, not '+repr(rod)
		return rod

	@staticmethod
	def chis_checker(chis):
		assert chis in {'ed','mn'} , 'chis must be ed or mn, not '+repr(chis)
		return chis

	@staticmethod
	def pad_checker(pad):
		assert pad in {'ip','rp','dp','vp','tp','pp'},\
			'pad must be ip, rp, dp, vp, tp or pp, not '+repr(pad)
		return pad

	def __init__(self,word,o=None,r=None,c=None,p=None):
		if type(word)==str:
			#Struct.__init__(self,word.attrs)
			# в словаре атрибуты отсутствуют
			# при парсинге узел копируется со словаря и туда добавляются атрибуты
			Struct.__init__(self)
			# но тем не менее все должны иметь атрибуты 
			# например для словосочетаний в словаре паттернов
			self.word=word
		elif type(word)==list:
			Struct.__init__(self)
			self.word=None
			self.talk=word
			self.talk_checker()
			
			found=None
			for i in word:
				if i[0]=='maindep':
					assert found==None, 'we must have only one maindep'
					found =i#[1]
					assert o==None and r==None and c==None, 'maindep may conflits with o/r/c'
					o=get_property(odush=found)
					r=get_property(rod=found)
					c=get_property(chis=found)
					if p==None: 
						p=get_property(pad=found)
		self.odush=self.odush_checker(o)
		self.rod  =self.  rod_checker(r)
		self.chis =self. chis_checker(c)
		self.pad =self.  pad_checker(p)
		
	pers=3 #for pronoun
	pad=property()
	@pad.getter
	def pad(self):
		return self._pad
	@pad.setter
	def pad(self,val):
		self._pad=val
		if self.word==None:
			for i in self.talk:
				if i[0]=='dep' or i[0]=='maindep' :
					set_property(i,pad=val)
				
	npad=property()
	@npad.getter
	def npad(self):
		return ''
	@npad.setter
	def npad(self,val):
		pass
		
	def post_repr(self):
		return 'o='+repr(self.odush)+',r='+repr(self.rod)+ ',c='+repr(self.chis)+',p='+repr(self.pad)+')'
	def __repr__(self):
		raise NotImplementedError('virtual function')

	show_map=None
	def __str__(self):
		return self.attrs.change(
			self.attrs.join(i[1] for i in self.talk)
				if self.word==None else self.show_map[self.word](self)
			)


# In[32]:


show_noun_map={}

# Существительное
class StNoun(StDeclinable):
	'''существительное
	
	параметры
		och - other chis - слово с противоположным числом
	у зависимых слов также меняется число
	
	теги
		nomer - типа "урок пять" - независимый
	'''
	obediences = {
		'dep'    : lambda x:_types_assert(x,StDeclinable),
		'maindep': lambda x:_types_assert(x,StDeclinable),
		'nodep'  : none_fun,
		'nomer'  : lambda x:_types_assert(x,StNum),
		'punct'  :           types_assert(S)
	}
	__slots__=['_chis','_rod','och']
	def __init__(self,word=None,och=0,o=None,r=None,c=None,p=None):
		if type(word)==list:
			assert och==0 , 'Noun-och must be in leaf, och='+repr(och)
		else:
			assert type(och)==str or och==None , och
			self.och=och
		StDeclinable.__init__(self,word,o,r,c,p)

	#	@staticmethod
	#	def ext_props_setter(tup,**kwarg): #ext_prop_setter(tup,prop=val)
	#	word и och являются постоянными параметрами и снаружи их менять нельзя
	#todo сделать для этого checker
	#   по этому ext_props_setter для chis не нужен
		
	chis=property()
	@chis.getter
	def chis(self):
		return self._chis
	@chis.setter
	def chis(self,val):
		#print('set chis')#,repr(self))
		if not hasattr(self,'_chis'): # for constructor
			self._chis=val
		elif self._chis!=val:
			#print('change chis')
			self._chis=val
			if self.word!=None:
				if self.och==None :
					pass
				elif type(self.och)==str:
					tmp=self.och
					self.och=self.word
					self.word=tmp
				else:
					raise RuntimeError('internal error: StNoun.och = '+self.och)
			else:
				for i in self.talk:
					if i[0]=='dep' or i[0]=='maindep' :
						set_property(i,chis=val)

	rod=property()
	@rod.getter
	def rod(self):
		return self._rod
	@rod.setter
	def rod(self,val):
		if not hasattr(self,'_rod'): # for constructor
			self._rod=val
		
	def __repr__(self):
		return 'StNoun'+repr_id(self)+repr_attrs(self,self.word!=None)+'('+\
		   (repr_talk(self.talk) if self.word==None   else repr(self.word)+','+repr(self.och))+','+            self.post_repr()

	show_map=show_noun_map


# In[33]:


# Местоимение личное
class StProNoun(StNoun):
	'''личное местоимение
	
	дочерних узлов не бывает
	
	параметры
		pers - лицо - 1,2,3
		npad - {'', 'n'} - особый параметр падежности
			нет его, у него
	'''
	__slots__=['pers','npad']
	def __init__(self,word=None,och=0,pers=None,o=None,r=None,c=None,p=None,npad=''):
		assert type(word)==str, word
		StNoun.__init__(self,word,och,o,r,c,p)
		assert pers in {1,2,3}, pers
		self.pers=pers
		assert npad in {'', 'n'} , npad # его/него
		self.npad=npad


# In[34]:


show_num_map={}

# Числительное
class StNum(StDeclinable):
	'''числительное (в зачаточном состоянии)
	
	'рыжий кот' - существительное,  'пять котов' - числительное
	параметры 
		quantity - {'1', '2-4', '>=5'} - 1 кот, 2-4 кота, >=5 котов
		
	теги
		quantity - зависимое числительное
	'''
	obediences = {
		'maindep': types_assert(StDeclinable),
		'quantity': lambda x:_types_assert(x,StNum)
	}
	__slots__=['quantity']
	def __init__(self,word=None,quantity=None,o=None,r=None,c=None,p=None):
		assert quantity in {'1', '2-4', '>=5'}, 'quantity must be "1", "2-4" or ">=5"'
		self.quantity=quantity
		StDeclinable.__init__(self,word,o,r,c,p)

	pad=property()
	@pad.getter
	def pad(self):
		return self._pad
	@pad.setter
	def pad(self,val): #...
		#print('num.pad',val)
		self._pad=val
		if self.word==None:
			for i in self.talk:
				if i[0]=='quantity':
					set_property(i,pad=val)
				if i[0]=='dep' or i[0]=='maindep' :
					if self.quantity=='1':
						set_property(i,pad=val)
					elif self.quantity=='2-4':
						set_property(i,chis='mn')
						if val=='ip':
							set_property(i,chis='ed')
							set_property(i,pad='rp')
						elif val=='vp':
							if i[1].odush :
								set_property(i,pad='rp')
							else:
								set_property(i,chis='ed')
								set_property(i,pad='rp')
						else:
							set_property(i,pad=val)
					elif self.quantity=='>=5':
						if val=='ip' or val=='vp':
							set_property(i,pad='rp')
						else:
							set_property(i,pad=val)
					else:
						raise RuntimeError()

	def __repr__(self):
		return 'StNum'+repr_id(self)+repr_attrs(self,self.word!=None)+'('+\
			(repr_talk(self.talk) if self.word==None else repr(self.word))+','+ repr(self.quantity)+','+  self.post_repr()

	show_map=show_num_map


# In[35]:


show_adj_map={}

# Прилагательное
class StAdj(StDeclinable):
	'''прилагательное
	
	дочерних узлов пока нет
	
	pad дополнительно имеет еще 1 вариант 'sh' - прилагательное в укороченной форме
	'''
	__slots__=['_chis','_rod']
	obediences = {
		'maindep': lambda x:_types_assert(x,StDeclinable),
		'dep': lambda x:_types_assert(x,StDeclinable),
		'nodep'  : none_fun,
	}
	@staticmethod
	def pad_checker(pad):
		assert pad in {'ip','rp','dp','vp','tp','pp','sh'} , pad
		return pad# пока особого смысла в этом нет
	
	def __init__(self,word=None,o=None,r=None,c=None,p=None):
		StDeclinable.__init__(self,word,o,r,c,p)

	rod=property()
	@rod.getter
	def rod(self):
		return self._rod
	@rod.setter
	def rod(self,val):
		self._rod=val
		if self.word==None:
			for i in self.talk:
				if i[0]=='dep' or i[0]=='maindep' :
					set_property(i,rod=val)
				
	chis=property()
	@chis.getter
	def chis(self):
		return self._chis
	@chis.setter
	def chis(self,val):
		self._chis=val
		if self.word==None:
			for i in self.talk:
				if i[0]=='dep' or i[0]=='maindep' :
					set_property(i,chis=val)
				
	def __repr__(self):
		return 'StAdj'+repr_id(self)+repr_attrs(self,self.word!=None)+'('+\
			(repr_talk(self.talk) if self.word==None else repr(self.word))+','+ self.post_repr()
	
	show_map=show_adj_map
	
