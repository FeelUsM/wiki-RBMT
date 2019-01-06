from parse_system import *

# ## Классы отображения

# ### Базовые

# In[27]:


def I(**args):
    if len(args)!=1:
        raise ValueError()
    p=[i for i in args.items()][0]
    if p[0] not in {'maindep','dep','nodep','punct','nomer','quantity',
                   'main','ip'}:
        raise ValueError()
    return p


# In[28]:


class Struct:
    __slots__=['attrs','talk']
    def __init__(self,attrs=None):
        if attrs==None:
            self.attrs=SAttrs()
        elif type(attrs)==list:
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


# In[29]:


class StC(Struct): # Container
# nodep
    def __init__(self,talk):
        assert type(talk)==list
        Struct.__init__(self,talk)
        self.talk=talk
        
    def __repr__(self):
        return 'StContainer<'+str(id(self))+'>('+            repr(self.talk) +')'#_'+repr(self.attrs)

    def __str__(self):
        return self.attrs.change( SAttrs.join(i[1] for i in self.talk) )
    


# In[30]:


show_verb_map={}

class StVerb(Struct):
# main maindep ip rp dp vp tp pp gde kogda skolko
    __slots__=['word','oasp','asp','_form','_rod','_chis','_pers']
    def __init__(self,word,oasp=0,asp=None,form=None,rod=0,chis=0,pers=0):
        if type(word)==str:
            Struct.__init__(self)
            self.word=word
            assert oasp==None or type(oasp)==str ,                'oasp should be str or None'
            self.oasp=oasp
        else:
            Struct.__init__(self,word)# для тегов
            self.word=None
            self.talk=word

            found=None
            for i in word:
                if i[0]=='main' or i[0]=='maindep':
                    if found!=None:
                        raise ValueError('we must have only one main or maindep')
                    found =i[1]
                    if asp!=None or form!=None or chis!=0 or pers!=0:
                        raise ValueError('main or maindep may conflits with asp/form/pers')
                    asp=found.asp
                    form=found.form
                    rod=found.rod
                    chis=found.chis
                    pers=found.pers
        assert asp=='sov' or asp=='nesov' , 'asp should be "sov" or "nesov"'
        assert form=='neopr' or form=='povel' or form=='nast' ,            'form should be "neopr" or "povel" or "nast"'
        assert form=='neopr' and chis==None or                 form!='neopr' and (chis=='ed' or chis=='mn'),            'wrong chis'
        assert (form=='neopr' or form=='povel') and rod==None or                 not(form=='neopr' or form=='povel') and (rod in {'m','g','s'}),            'wrong rod'
        assert (form=='neopr' or form=='povel') and pers==None or                 not(form=='neopr' or form=='povel') and (pers in {1,2,3}),            'wrong person'
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
                    i[1].form=val
                
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
                    i[1].rod=val
                
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
                    i[1].chis=val
                
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
                    i[1].pers=val
                
    def __repr__(self):
            #'<'+str(id(self))+'>'+\
        return 'StVerb'+            '('+(repr(self.talk) if self.word==None                  else repr(self.word)+','+repr(self.oasp))+','+            'asp='+repr(self.asp)+','+            'form='+repr(self.form)+','+            'chis='+repr(self.chis)+','+            'pers='+repr(self.pers)+')'

    def __str__(self):
        return self.attrs.change(
            SAttrs.join(i[1] for i in self.talk)
                if self.word==None else show_verb_map[self.word](self)
            )


# ### Склоняемые

# In[31]:


class StDeclinable(Struct):
    __slots__=['word','odush','rod','chis','_pad']
    
    @staticmethod
    def odush_checker(odush):
        if type(odush)!=bool : raise TypeError('odush must be bool')
        return odush
        
    @staticmethod
    def rod_checker(rod):
        if rod!='m' and rod!='g' and rod!='s' : raise TypeError('rod must be m or g or s')
        return rod

    @staticmethod
    def chis_checker(chis):
        if chis!='ed' and chis!='mn' : raise TypeError('chis must be ed or mn')
        return chis

    @staticmethod
    def pad_checker(pad):
        if pad!='ip' and pad!='rp' and pad!='dp' and pad!='vp' and pad!='tp' and pad!='pp' : 
            raise TypeError('pad must be ip, rp, dp, vp, tp or pp')
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
            Struct.__init__(self,word)# для тегов
            self.word=None
            self.talk=word
            assert self.talk[0][1].attrs.pre==''
            
            found=None
            for i in word:
                if i[0]=='maindep':
                    if found!=None:
                        raise ValueError('we must have only one maindep')
                    found =i[1]
                    if o!=None or r!=None or c!=None:
                        raise ValueError('maindep may conflits with o/r/c')
                    o=found.odush
                    r=found.rod
                    c=found.chis
                    if p==None: p=found.pad
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
                    i[1].pad=val
                
    def post_repr(self):
        return 'o='+repr(self.odush)+',r='+repr(self.rod)+            ',c='+repr(self.chis)+',p='+repr(self.pad)+')'#_'+repr(self.attrs)
    def __repr__(self):
        raise NotImplementedError('virtual function')

    show_map=None
    def __str__(self):
        return self.attrs.change(
            SAttrs.join(i[1] for i in self.talk)
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
                        i[1].chis=val

    pers=3
        
    def __repr__(self):
        return 'StNoun<'+str(id(self))+'>('+            (repr(self.talk) if self.word==None                  else repr(self.word)+','+repr(self.och))+','+            self.post_repr()
    
    show_map=show_noun_map


# In[33]:


# Местоимение личное
class StProNoun(StNoun):
    __slots__='pers'
    def __init__(self,word=None,och=0,pers=None,o=None,r=None,c=None,p=None):
        assert type(word)==str
        StNoun.__init__(self,word,och,o,r,c,p)
        assert pers in {1,2,3}
        self.pers=pers


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
                    i[1].pad=val
                if i[0]=='dep' or i[0]=='maindep' :
                    if self.quantity=='1':
                        i[1].pad=val
                    elif self.quantity=='2-4':
                        i[1].chis='mn'
                        if val=='ip':
                            i[1].chis='ed'
                            i[1].pad='rp'
                        elif val=='vp':
                            if i[1].odush :
                                i[1].pad='rp'
                            else:
                                i[1].chis='ed'
                                i[1].pad='rp'
                        else:
                            i[1].pad=val
                    elif self.quantity=='>=5':
                        if val=='ip' or val=='vp':
                            i[1].pad='rp'
                        else:
                            i[1].pad=val
                    else:
                        raise RuntimeError()

    def __repr__(self):
        return 'StNum<'+str(id(self))+'>('+            (repr(self.talk) if self.word==None                  else repr(self.word))+','+            repr(self.quantity)+','+            self.post_repr()
    
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
        return 'StAdj<'+str(id(self))+'>('+            (repr(self.talk) if self.word==None                  else repr(self.word))+','+            self.post_repr()
    
    show_map=show_adj_map
    
