from parse_system import *

# ## Классы отображения

# ### Базовые

# In[27]:

DEBUGGING_ID=True
def repr_id(self):
	global DEBUGGING_ID
	return '<'+str(id(self))+'>' if DEBUGGING_ID else ''
	
DEBUGGING_ATTRS=True
def repr_attrs(self):
	global DEBUGGING_ATTRS
	return '_'+repr(self.attrs) if DEBUGGING_ATTRS else ''


def I(**args):
#	if len(args)!=1:
#		raise ValueError()
	i=iter(args.items())
	p=next(i)
	assert p[0] in {'maindep','dep','nodep','punct','nomer','quantity',
				   'main','ip','dp','vp'} 
	assert isinstance(p[1],Struct) or isinstance(p[1],S)
#	for k,v in i:
#		setattr(p[1],k,v)
	args.pop(p[0])
	return (p[0], p[1], args)#p
	
def get_property(**kwarg):
	assert len(kwarg)==1
	prop, tup= next(iter(kwarg.items()))
	if len(tup)==2:
		return getattr(tup[1],prop)
	elif len(tup)==3:
		if prop in tup[2]:
			return tup[2][prop]
		else:
			return getattr(tup[1],prop)
	else:
		raise RuntimeError('bad tuple')
def set_property(tup,**kwarg):
	assert len(kwarg)==1
	prop, val= next(iter(kwarg.items()))
	if len(tup)==2:
		setattr(tup[1],prop,val)
	elif len(tup)==3:
		tup[2][prop]=val
	else:
		raise RuntimeError('bad tuple')

# In[28]:


class Struct:
	__slots__=['attrs','talk']
	def __init__(self,attrs=None):
		if attrs==None:
			self.attrs=SAttrs()
		elif type(attrs)==list:
			raise RuntimrError('pulling attrs does not supported')
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
		for tup in self.talk:
			for prop,val in tup[2].items():
				if prop=='attrs_from_left':
					SAttrs._to_right(val,tup[1])
				elif prop=='attrs_from_right':
					SAttrs._to_left(tup[1],val)
				else: setattr(tup[1],prop,val)
			tup[2].clear()
			if isinstance(tup[1],Struct):
				tup[1].pull_deferred()
		if self.attrs.pre=='':
			self.attrs.pre=self.talk[0][1].attrs.pre
			self.talk[0][1].attrs.pre=''
		return self
		
	def tostr(self):
		self.pull_deferred()
		return self.__str__()

		
# In[29]:


class StC(Struct): # Container
# nodep
    def __init__(self,talk):
        assert type(talk)==list
        Struct.__init__(self)
        self.talk=talk
        
    def __repr__(self):
        return 'StContainer'+repr_id(self)+'('+            repr(self.talk) +')'+repr_attrs(self)

    def __str__(self):
        return self.attrs.change( self.attrs.join(i[1] for i in self.talk) )


# In[30]:


show_verb_map={}

class StVerb(Struct):
# main maindep ip rp dp vp tp pp gde kogda skolko
	__slots__=[
		'word', # None или слово - индекс для отображения
		'oasp', # None или слово - с противоположной совершенностью
		
		'asp',	# 'sov'/'nesov' - аспект
		'_form',# 'neopr'/'povel'/'nast' - форма-наклонение-время
		'_rod', # 'm'/'g'/'s'
		'_chis',# 'ed'/'mn'
		'_pers' # 1/2/3 - лицо
	]
	def __init__(self,word,oasp=0,asp=None,form=None,chis=0,rod=0,pers=0):
		if type(word)==str:
			Struct.__init__(self)
			self.word=word
			assert oasp==None or type(oasp)==str ,                'oasp should be str or None'
			self.oasp=oasp
		else:
			Struct.__init__(self)
			self.word=None
			self.talk=word

			found=None
			for i in word:
				if i[0]=='main' or i[0]=='maindep':
					if found!=None:
						raise ValueError('we must have only one main or maindep')
					found =i#[1]
					if asp!=None or form!=None or chis!=0 or pers!=0:
						raise ValueError('main or maindep may conflits with asp/form/chis/pers')
					asp=get_property(asp=found)
					form=get_property(form=found)
					rod=get_property(rod=found)
					chis=get_property(chis=found)
					pers=get_property(pers=found)
		assert asp=='sov' or asp=='nesov' , \
				'wrong asp: '+repr(asp)
		assert form=='neopr' or form=='povel' or form=='nast' , \
				'wrong form: '+repr(form)
		assert form=='neopr' and chis==None or \
			form!='neopr' and (chis=='ed' or chis=='mn'), \
				'wrong chis: '+repr(chis)
		assert (form=='neopr' or form=='povel') and rod==None or \
			not(form=='neopr' or form=='povel') and (rod in {'m','g','s'}), \
				'wrong rod: '+repr(rod)
		assert (form=='neopr' or form=='povel') and pers==None or \
			not(form=='neopr' or form=='povel') and (pers in {1,2,3}), \
				'wrong pers: '+repr(pers)
		self.asp=asp
		self._form=form
		self._rod=rod
		self._chis=chis
		self._pers=pers

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
				
	def __repr__(self):
		return 'StVerb'+repr_id(self)+'('+(repr(self.talk) if self.word==None else repr(self.word)+','\
			+repr(self.oasp))+','+ 'asp='+repr(self.asp)+','+ 'form='+repr(self.form)+','+ 'chis='+repr(self.chis)+','+            'pers='+repr(self.pers)+')'+repr_attrs(self)

	def __str__(self):
		return self.attrs.change(
			self.attrs.join(i[1] for i in self.talk)
				if self.word==None else show_verb_map[self.word](self)
			)


# ### Склоняемые

# In[31]:


class StDeclinable(Struct):
    __slots__=['word','odush','rod','chis','_pad']
    
    @staticmethod
    def odush_checker(odush):
        if type(odush)!=bool : raise TypeError('odush must be bool, not '+repr(odush))
        return odush
        
    @staticmethod
    def rod_checker(rod):
        if rod!='m' and rod!='g' and rod!='s' : raise TypeError('rod must be m or g or s, not '+repr(rod))
        return rod

    @staticmethod
    def chis_checker(chis):
        if chis!='ed' and chis!='mn' : raise TypeError('chis must be ed or mn, not '+repr(chis))
        return chis

    @staticmethod
    def pad_checker(pad):
        if pad!='ip' and pad!='rp' and pad!='dp' and pad!='vp' and pad!='tp' and pad!='pp' : 
            raise TypeError('pad must be ip, rp, dp, vp, tp or pp, not '+repr(pad))
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
            #assert self.talk[0][1].attrs.pre==''
            
            found=None
            for i in word:
                if i[0]=='maindep':
                    if found!=None:
                        raise ValueError('we must have only one maindep')
                    found =i#[1]
                    if o!=None or r!=None or c!=None:
                        raise ValueError('maindep may conflits with o/r/c')
                    o=get_property(odush=found)
                    r=get_property(rod=found)
                    c=get_property(chis=found)
                    if p==None: 
                        p=get_property(pad=found)
        self.odush=self.odush_checker(o)
        self.rod  =self.  rod_checker(r)
        self.chis =self. chis_checker(c)
        self._pad =self.  pad_checker(p)
        
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
                
    def post_repr(self):
        return 'o='+repr(self.odush)+',r='+repr(self.rod)+            ',c='+repr(self.chis)+',p='+repr(self.pad)+')'+repr_attrs(self)
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
# dep, maindep, nodep, nomer, punct
    __slots__=['_chis','och']
    def __init__(self,word=None,och=0,o=None,r=None,c=None,p=None):
        if type(word)==list:
            if och!=0: raise ValueError('Noun-och must be in leaf')
        else:
            if type(och)!=str and och!=None: raise ValueError('och must be str')
            self.och=och
        StDeclinable.__init__(self,word,o,r,c,p)
    
    chis=property()
    @chis.getter
    def chis(self):
        return self._chis
    @chis.setter
    def chis(self,val):
        #print('set chis')#,repr(self))
        if not hasattr(self,'_chis'):
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

    pers=3 #for pronoun
    npad=property()
    @npad.getter
    def npad(self):
        return ''
    @npad.setter
    def npad(self,val):
        pass
        
    def __repr__(self):
        return 'StNoun'+repr_id(self)+'('+            (repr(self.talk) if self.word==None                  else repr(self.word)+','+repr(self.och))+','+            self.post_repr()
    
    show_map=show_noun_map


# In[33]:


# Местоимение личное
class StProNoun(StNoun):
    __slots__=['pers','npad']
    def __init__(self,word=None,och=0,pers=None,o=None,r=None,c=None,p=None,npad=''):
        assert type(word)==str
        StNoun.__init__(self,word,och,o,r,c,p)
        assert pers in {1,2,3}
        self.pers=pers
        assert npad in {'', 'n'} # его/него
        self.npad=npad


# In[34]:


show_num_map={}

# Числительное
class StNum(StDeclinable):
# maindep, quantity
    __slots__=['quantity']
    def __init__(self,word=None,quantity=None,o=None,r=None,c=None,p=None):
        if quantity!='1' and quantity!='2-4' and quantity!='>=5':
            raise TypeError('quantity must be "1", "2-4" or ">=5"')
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
        return 'StNum'+repr_id(self)+'('+            (repr(self.talk) if self.word==None                  else repr(self.word))+','+            repr(self.quantity)+','+            self.post_repr()
    
    show_map=show_num_map


# In[35]:


show_adj_map={}

# Прилагательное
class StAdj(StDeclinable):
#
    @staticmethod
    def pad_checker(pad):
        if pad!='ip' and pad!='rp' and pad!='dp' and pad!='vp' and pad!='tp' and                 pad!='pp' and pad!='sh' : 
            raise TypeError('pad must be ip, rp, dp, vp, tp, pp or sh')
        return pad# пока особого смысла в этом нет
    
    def __init__(self,word=None,o=None,r=None,c=None,p=None):
        StDeclinable.__init__(self,word,o,r,c,p)

    def __repr__(self):
        return 'StAdj'+repr_id(self)+'('+            (repr(self.talk) if self.word==None                  else repr(self.word))+','+            self.post_repr()
    
    show_map=show_adj_map
    
