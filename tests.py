import time
import sys

# In[3]:

N = None
TEST_ERRORS=[]

def test(real,expected):
	'''сравнивает real и expected, ошибки добавляет в TEST_ERRORS'''
	global N
	if real==expected:
		return True
	else:
		print('TestError')
		if type(real)==str or type(expected)==str:
			print(real)
		else:
			if len(real)!=len(expected):
				print(real)
			else:
				for i in range(len(real)):
					if real[i]!=expected[i]:
						print(i+1,')',real[i])
		TEST_ERRORS.append({'N':N,'type':'wrong result','expected':expected,
							'real':real})
		return False


# In[4]:

multiplier = 5
warning_catched = False

def ttest(f,*args):
	expected = args[-1]
	#del args[len(args)-1]
	args = args[:-1]
	ddt = len(repr(expected))
	global N
	try:
		start_time = time.time()
		test_OK = test(f(*args),expected)
		dt = time.time() - start_time
		global warning_catched
		if warning_catched:
			warning_catched = False
			print(expected)
			print('---')
		if test_OK:
			pass
			#print('OK')
		global multiplier
		if dt*1000>multiplier*ddt:
			average = dt
			LEN = 10
			for i in range(LEN):
				start_time = time.time()
				f(*args)
				average+= time.time() - start_time
			average/=(LEN+1)
			if print_timing : print('%d\t%d\t%d\t%f !'%(ddt,ddt*multiplier,average*1000,average*1000/ddt/multiplier))
			if average*1000>multiplier*ddt:
				print('over time ')
				#TEST_ERRORS.append
				print(
					{'N':N,'type':'over time','expected':expected,
					 'real time':int(1000*average),'expected time':ddt* multiplier})
		else:
			if print_timing : print('%d\t%d\t%d\t%f  '%(ddt,ddt*multiplier,dt     *1000,dt*    1000/ddt/multiplier))
	except BaseException as err:
		print('EXCEPTION CATCHED')
		TEST_ERRORS.append({'N':N,'type':'exception','expected':expected,
							'error':err})
		test_OK = True # не надо снова
		#print(err)
	if not test_OK and f==en2ru:
		scheme(*args)

def warning_hook(s):
	print('WARNING:',s)
	global warning_catched
	warning_catched = True

tmp_warning_fun = None

TestError = None
parse_system = None
en_dictionary = None
seq = None
W = None
SAttrs = None

tokenize = None

en2ru = None
en2ru_with_variants = None
decline = None
scheme = None
d_en2ru = None
pr_l_repr = None

p_noun = None
p_noun1 = None
r_noun_comma_noun = None
dict_pronoun_ip = None
dict_numeral = None
rv_noun_HAVE_noun = None

print_timing = None

def init(_parse_system, _en_dictionary,
	_en2ru, _with_variants, _decline, _scheme, _d_en2ru, _pr_l_repr, 
	_p_noun, _p_noun1, _r_noun_comma_noun, _rv_noun_HAVE_noun,
	_multiplier,_print_timing):
	global tmp_warning_fun
	global parse_system
	global en_dictionary
	global TestError
	global seq
	global W
	global SAttrs
	global tokenize

	global en2ru
	global en2ru_with_variants
	global decline
	global scheme
	global d_en2ru
	global pr_l_repr

	global p_noun
	global p_noun1
	global r_noun_comma_noun
	global dict_pronoun_ip
	global dict_numeral
	global rv_noun_HAVE_noun

	global multiplier
	global print_timing

	parse_system = _parse_system
	en_dictionary = _en_dictionary
	tmp_warning_fun = parse_system.warning_fun
	parse_system.warning_fun=warning_hook
	TestError = parse_system.TestError
	seq = parse_system.seq
	W = parse_system.W
	SAttrs = parse_system.SAttrs
	tokenize = parse_system.tokenize

	en2ru = _en2ru 
	en2ru_with_variants = lambda v,s : _with_variants(v,en2ru,s)
	decline = _decline
	scheme = _scheme
	d_en2ru = _d_en2ru
	pr_l_repr = _pr_l_repr

	p_noun = _p_noun
	p_noun1 = _p_noun1
	r_noun_comma_noun = _r_noun_comma_noun
	dict_pronoun_ip = en_dictionary.dict_pronoun_ip
	dict_numeral = en_dictionary.dict_numeral
	rv_noun_HAVE_noun = _rv_noun_HAVE_noun

	multiplier = _multiplier
	print_timing = _print_timing

def finalize():
	global tmp_warning_fun
	parse_system.warning_fun = tmp_warning_fun


def test1():
	print('--- Lesson 1 ---')
	# In[9]:

	global N
	N=1


	# In[10]:


	ttest(en2ru,'cat','кот')#,60


	# In[11]:


	ttest(en2ru,'a cat','кот')#,90


	# In[12]:


	ttest(en2ru,'rat','крыса')#,60


	# In[13]:


	ttest(en2ru,'bat','летучая мышь')#,110


	# In[14]:


	ttest(en2ru,'a','некоторый')#,80


	# In[15]:


	ttest(en2ru,'lesson','урок')#,60


	# In[16]:


	ttest(en2ru,'_Cat and cat','_Кот и кот')#,120


	# In[17]:


	ttest(en2ru,'_a cat and cat','_кот и кот')#,150


	# In[18]:


	ttest(en2ru,'_a cat , cat','_кот, кот')#,150


	# In[19]:


	x=p_noun(tokenize('_a cat, cat'),0)[0][1]
	test(x.tostr(),'_кот, кот')


	# In[20]:


	s=tokenize('_a cat, cat')
	rezs=seq([ p_noun1, W(',')  , p_noun ],r_noun_comma_noun)(s,0)
	test(rezs[0][1].tostr(),'_кот, кот')


	# In[21]:


	test(p_noun(tokenize('cat,_cat,_a cat'),0)[1][1].tostr(),'кот,_кот,_кот')


	# In[22]:


	test(SAttrs().join(tokenize('cat,_cat,_a cat')),'cat,_cat,_a cat')


	# In[23]:


	ttest(en2ru,'rat, cat','крыса, кот')#,120

def test2():
	print('--- Lesson 2 ---')

	# In[24]:

	global N
	N=2


	# In[25]:


	ttest(en2ru,'cat AND_Rat','кот И_Крыса')#,125


	# In[26]:


	ttest(en2ru,'a pen and a hen','ручка и курица')#,170


	# In[27]:


	ttest(en2ru,'a bat and a cat','летучая мышь и кот')#,210


	# In[28]:


	ttest(en2ru,'a hen, a bat, a cat and a rat','курица, летучая мышь, кот и крыса')#,360

def test3():
	print('--- Lesson 3 ---')

	# In[29]:

	global N
	N=3


	# In[30]:


	ttest(en2ru,'one','один')#,85


	# In[31]:


	ttest(en2ru,'a bat, a dog and a pig','летучая мышь, собака и свинья')#,290


	# In[32]:


	ttest(en2ru,'one dog','одна собака')#,90


	# In[33]:


	ttest(en2ru,'three dogs','три собаки')#,100


	# In[34]:


	ttest(decline,'rat and cat',
	['крыса и кот',
	 'нет крысы и кота',
	 'дать крысе и коту',
	 'вижу крысу и кота',
	 'творю крысой и котом',
	 'думаю о крысе и коте'])


	# In[35]:


	ttest(en2ru,'rat and cat','крыса и кот')#,120


	# In[36]:


	ttest(decline,'one bat and three cups',
	['одна летучая мышь и три чашки',
	'нет одной летучей мыши и трёх чашек',
	'дать одной летучей мыши и трём чашкам',
	'вижу одну летучую мышь и три чашки',
	'творю одной летучей мышью и тремя чашками',
	'думаю о одной летучей мыши и трёх чашках'])#,8


	# In[37]:


	ttest(en2ru,'one bat and three cups','одна летучая мышь и три чашки')#,205


	# In[38]:


	ttest(decline,'one, two, three, four, five',[
	    'один, два, три, четыре, пять',
	    'нет одного, двух, трёх, четырёх, пяти',
	    'дать одному, двум, трём, четырём, пяти',
	    'вижу один, два, три, четыре, пять',
	    'творю одним, двумя, тремя, четырьмя, пятью',
	    'думаю о одном, двух, трёх, четырёх, пяти',])#,15


	# In[39]:


	ttest(decline,'cat, one cat, cats, two cats, three cats, five cats',[
	    'кот, один кот, коты, два кота, три кота, пять котов',
	    'нет кота, одного кота, котов, двух котов, трёх котов, пяти котов',
	    'дать коту, одному коту, котам, двум котам, трём котам, пяти котам',
	    'вижу кота, одного кота, котов, двух котов, трёх котов, пять котов',
	    'творю котом, одним котом, котами, двумя котами, тремя котами, пятью котами',
	    'думаю о коте, одном коте, котах, двух котах, трёх котах, пяти котах',
	])#,15


	# In[40]:


	ttest(decline,'lesson, one lesson, lessons, two lessons, three lessons, five lessons',[
	    'урок, один урок, уроки, два урока, три урока, пять уроков',
	    'нет урока, одного урока, уроков, двух уроков, трёх уроков, пяти уроков',
	    'дать уроку, одному уроку, урокам, двум урокам, трём урокам, пяти урокам',
	    'вижу урок, один урок, уроки, два урока, три урока, пять уроков',
	    'творю уроком, одним уроком, уроками, двумя уроками, тремя уроками, пятью уроками',
	    'думаю о уроке, одном уроке, уроках, двух уроках, трёх уроках, пяти уроках',
	])#,20


	# In[41]:


	ttest(decline,'rat, one rat, rats, two rats, three rats, five rats',[
	    'крыса, одна крыса, крысы, две крысы, три крысы, пять крыс',
	    'нет крысы, одной крысы, крыс, двух крыс, трёх крыс, пяти крыс',
	    'дать крысе, одной крысе, крысам, двум крысам, трём крысам, пяти крысам',
	    'вижу крысу, одну крысу, крыс, двух крыс, трёх крыс, пять крыс',
	    'творю крысой, одной крысой, крысами, двумя крысами, тремя крысами, пятью крысами',
	    'думаю о крысе, одной крысе, крысах, двух крысах, трёх крысах, пяти крысах',
	])#,20


	# In[42]:


	ttest(decline,'child, one child, children, two children, three children, five children',
	['ребёнок, один ребёнок, дети, два ребёнка, три ребёнка, пять детей',
	'нет ребёнка, одного ребёнка, детей, двух детей, трёх детей, пяти детей',
	'дать ребёнку, одному ребёнку, детям, двум детям, трём детям, пяти детям',
	'вижу ребёнка, одного ребёнка, детей, двух детей, трёх детей, пять детей',
	'творю ребёнком, одним ребёнком, детьми, двумя детьми, тремя детьми, пятью детьми',
	'думаю о ребёнке, одном ребёнке, детях, двух детях, трёх детях, пяти детях'])#,15

def test4():
	print('--- Lesson 4 (? увидь кота ?) ---')

	# In[43]:

	global N
	N=4


	# In[44]:


	ttest(en2ru,
	'''  A hat, a cup and a box.
	A bat, a hen and a fox.''',
	'''  Шляпа, чашка и ящик.
	Летучая мышь, курица и лиса.''')#,260


	# In[45]:


	ttest(en2ru,'I','я')#,60


	# In[46]:


	ttest(en2ru,'to see','видеть')#,20


	# In[47]:


	ttest(en2ru,'I see','я вижу')#,75


	# In[48]:


	ttest(en2ru,'see cat','увидь кота')#,25


	# In[49]:


	ttest(en2ru,'''I see
	  a pig and a hen,
	  a dog and a gun,
	  a cat and a hat.''',
	'''Я вижу
	  свинью и курицу,
	  собаку и ружьё,
	  кота и шляпу.''')#,280


	# In[50]:


	ttest(en2ru,'I see one box, one hat and one cap',
	     'я вижу один ящик, одну шляпу и одну кепку')#,205


	# In[51]:


	ttest(en2ru,'I see jam and one cup',
	    'я вижу джем и одну чашку')#,140

def test5and6():
	print('--- Lessons 5, 6 ---')

	# In[52]:

	global N
	N=5


	# In[53]:


	ttest(en2ru,'A vase and a cup','Ваза и чашка')#,170


	# In[54]:


	ttest(en2ru,'A kitten and a rat.','Котёнок и крыса.')#,90


	# In[55]:


	ttest(en2ru,'A gun and a star.','Ружьё и звезда.')#,100


	# In[56]:


	ttest(en2ru,'two lamps','две лампы')#,80


	# In[57]:


	ttest(en2ru,'I see one dog and one cat.','Я вижу одну собаку и одного кота.')#,80


	# In[58]:


	ttest(en2ru,'a wolf and a squirrel, zebras, boys','волк и белка, зебры, мальчики')#,270


	# In[59]:


	ttest(decline,'six squirrels',['шесть белок',
	 'нет шести белок',
	 'дать шести белкам',
	 'вижу шесть белок',
	 'творю шестью белками',
	 'думаю о шести белках'])

def test7():
	print('--- Lesson 7 ---')

	# In[60]:

	global N
	N=7


	# In[61]:


	ttest(en2ru,'I have a cat.','У меня есть кот.')#,40


	# In[62]:


	ttest(en2ru,'I have no a cat.','У меня нет кота.')#,40


	# In[63]:


	ttest(en2ru,'I have no two guns.','У меня нет двух ружей.')#,40


	# In[64]:


	ttest(en2ru,'have','заимей')#,20


	# In[65]:


	ttest(en2ru,'I have a dog, but I have no cat.',
	      'У меня есть собака, но у меня нет кота.')#,45


	# In[66]:


	ttest(en2ru,'I have no lamp.','У меня нет лампы.')#,35


	# In[67]:


	ttest(en2ru,'copy-book','тетрадь')#,55


	# In[68]:


	ttest(en2ru,'give me','дай мне')#,20


	# In[69]:


	ttest(en2ru,'give me cat','дай мне кота')#,25


	# In[70]:


	ttest(en2ru,'to give me cat','давать мне кота')#,30


	# In[71]:


	ttest(en2ru,'I have a kitten, but I have no squirrel.'
	      ,'У меня есть котёнок, но у меня нет белки.')#,45


	# In[72]:


	ttest(en2ru,'Show me Lesson Four!','Покажи мне Урок Четыре!')#,15


	# In[73]:


	ttest(en2ru,'cat has cat','у кота есть кот')#,70


	# In[74]:


	ttest(en2ru,'cat has me','у кота есть я')#,60


	# In[75]:


	ttest(en2ru,'me','мне')#,10


	# In[76]:


	ttest(en2ru,'Good_morning','Доброе_утро')#,110


	# In[77]:


	ttest(en2ru,'good mornings','хорошие утра')#,130


	# In[78]:


	ttest(en2ru,'seven','семь')#,80

def test8():
	print('--- Lesson 8 (открывающие кавычки...) ---')

	# In[79]:

	global N
	N=8


	# In[80]:


	ttest(en2ru,'This boy has a ball.','У этого мальчика есть мяч.')#,60


	# In[81]:


	ttest(en2ru,'He has no a copy-book.','У него нет тетради.')#,40


	# In[82]:


	ttest(en2ru,'He has no him.','У него нет его.')#,30


	# In[83]:


	ttest(en2ru,'Say: Good morning!','Скажи: Доброе утро!')#,250


	# In[84]:


	ttest(en2ru,'Say information','Скажи информацию')#,220


	# In[85]:


	ttest(en2ru,'Say: "Seven, six, four, two, five, three, one."',
	      'Скажи:" Семь, шесть, четыре, два, пять, три, один."')#,2200


	# In[86]:


	ttest(en2ru,'say: say seven','скажи: скажи семь')#,1200


	# In[87]:


	ttest(en2ru,'I have cat too.','Я тоже имею кота.')#,20


	# In[88]:


	ttest(en2ru,'I have no star and he has no star.',
	      'У меня нет звезды и у него нет звезды.')#,40

def test8_1():
	print('--- Lesson 8.1 ---')

	# In[89]:

	global N
	N=8.1


	# In[90]:


	ttest(en2ru,'two balls','два мяча')


	# In[91]:


	ttest(en2ru,'boy sees','мальчик видит')


	# In[92]:


	ttest(en2ru,'see','увидь')


	# In[93]:


	ttest(en2ru,'boy says','мальчик говорит')


	# In[94]:


	ttest(en2ru,'say','скажи')


	# In[95]:


	ttest(en2ru,'boy gives','мальчик даёт')


	# In[96]:


	ttest(en2ru,'give','дай')


	# In[116]:


	ttest(en2ru,'boy has','у мальчика есть')


	# In[98]:


	ttest(en2ru,'have','заимей')


	# In[99]:


	ttest(en2ru,'\nThis girl has three balls.','\nУ этой девочки есть три мяча.')

def test9():
	print('--- Lesson 9 ---')

	# In[100]:

	global N
	N=9


	# In[101]:


	ttest(en2ru,'She has ball','у Неё есть мяч')


	# In[102]:


	ttest(en2ru,'the','определённый')


	# In[103]:


	ttest(en2ru,'''This girl has a fish.
	This fish is on the dish.''',
	'''У этой девочки есть рыба.
	Эта рыба на блюде.''')


	# In[104]:


	ttest(en2ru,'''This girl has three dolls.
	This boy has two balls.
	That girl has five books.
	That boy has four pens.''',
	'''У этой девочки есть три куклы.
	У этого мальчика есть два мяча.
	У той девочки есть пять книг.
	У того мальчика есть четыре ручки.''')


	# In[105]:


	ttest(en2ru,'''The girl has one dish.
	She has two spoons.
	The boy has three sticks.
	He has five stars.''',
	'''У девочки есть одно блюдо.
	У неё есть две ложки.
	У мальчика есть три палки.
	У него есть пять звёзд.''')


	# In[106]:


	ttest(en2ru,'''This frog is on the log.
	That frog is in the lake.
	The snake is in the box.''',
	'''Эта ягушка на бревне.
	Та ягушка в озере.
	Змея в ящике.''')


	# In[107]:


	ttest(en2ru,'''The spoon is in the cup.
	The squirrel is on the log.
	The doll is on the bed.''',
	 '''Ложка в чашке.
	Белка на бревне.
	Кукла на кровати.''')


	# In[108]:


	ttest(en2ru,'''I like cakes.
	I have two cakes.
	He has two stars.
	She has three dolls.''',
	'''Я люблю торты.
	У меня есть два торта.
	У него есть две звезды.
	У неё есть три куклы.''')


	# In[109]:


	ttest(en2ru,'''The doll is on the bed.
	The snake is in the lake.
	The hen is on the log.
	The bat is in the hat.''',
	 '''Кукла на кровати.
	Змея в озере.
	Курица на бревне.
	Летучая мышь в шляпе.''')


	# In[110]:


	ttest(en2ru,'''This girl has five
	kittens and two cats.''',
	'''У этой девочки есть пять
	котят и два кота.'''     )


	# In[111]:


	ttest(en2ru,'''She has three hens.
	I have four books and nine copy-books.
	This boy has eight stars.
	He has six sticks, but he has no gun.''',
	'''У неё есть три курицы.
	У меня есть четыре книги и девять тетрадей.
	У этого мальчика есть восемь звёзд.
	У него есть шесть палок, но у него нет ружья.''')


	# In[112]:


	ttest(en2ru,'''I like fish.
	One snake is in the lake.
	One frog is on the log.
	Jam is in the vase.''',
	'''Я люблю рыбу.
	Одна змея в озере.
	Одна ягушка на бревне.
	Джем в вазе.''')

def test10():
	print('--- Lesson 10 ---')
	global N
	N=10

	ttest(en2ru,'one girl','одна девочка')

	ttest(en2ru,'three chickens','три цыплёнка')

	ttest(en2ru,'I have no','у меня нет')

	ttest(en2ru,'Yes, she has.','Да, у неё есть.')

	ttest(en2ru,'one boy','один мальчик')

	ttest(en2ru,'''Count from one to ten! One, two, three,
	four, five, six, seven, eight, nine, ten.''',
	'''Считай от одного до десяти! Один, два, три,
	четыре, пять, шесть, семь, восемь, девять, десять.''')

	ttest(en2ru,'eight','восемь')

	ttest(en2ru,'''Count the rabbits!
	One, two.
	Count the chickens!
	One, two, three.
	This girl has three
	rabbits.
	She has five chickens.''',
	'''Считай кроликов!
	Один, два.
	Считай цыплят!
	Один, два, три.
	У этой девочки есть три
	кролика.
	У неё есть пять цыплят.''')

	ttest(en2ru,'''cat.
	____One,two.''',
	'''кот.
	____Один, два.''')

	ttest(en2ru,'two rabbits','два кролика')

	ttest(en2ru,'''Has this girl a kitten? Yes, she has.
	Has this girl a vase? Yes, she has.
	Has she a dog? Yes, she has.
	Has she a hat? Yes, she has.
	Has she a snake? No, she has not.
	Has she a frog? No, she has not.
	Has she a bat? No, she has not.''',
	'''У этой девочки есть котёнок? Да, у неё есть.
	У этой девочки есть ваза? Да, у неё есть.
	У неё есть собака? Да, у неё есть.
	У неё есть шляпа? Да, у неё есть.
	У неё есть змея? Нет, у неё нет.
	У неё есть ягушка? Нет, у неё нет.
	У неё есть летучая мышь? Нет, у неё нет.''')

	ttest(en2ru,'''That boy has two squirrels.
	He has one fox too.
	He has nine rabbits.
	He has four bats.''',
	'''У того мальчика есть две белки.
	Он тоже имеет одну лису.
	У него есть девять кроликов.
	У него есть четыре летучей мыши.''')

	ttest(en2ru,'''Has that boy a wolf?
	No, he has not.
	Has he a gun?
	No, he has not.
	Has he a pistol?
	No, he has not.
	Has he a stick?
	Yes, he has.
	Has he a ball?
	Yes, he has.''',
	'''У того мальчика есть волк?
	Нет, у него нет.
	У него есть ружьё?
	Нет, у него нет.
	У него есть пистолет?
	Нет, у него нет.
	У него есть палка?
	Да, у него есть.
	У него есть мяч?
	Да, у него есть.''')

	ttest(en2ru,'''You have one hen and eight chickens.
	You have nine rabbits too.''',
	'''У тебя есть одна курица и восемь цыплят.
	Ты тоже имеешь девять кроликов.''')

	ttest(en2ru,'you see me','ты видишь меня')

	ttest(en2ru,'''Have you a hat? Yes, I have.
	Have you a stick? No, I have not.
	Catch that rabbit!''',
	'''У тебя есть шляпа? Да, у меня есть.
	У тебя есть палка? Нет, у меня нет.
	Поймай того кролика!''')

	ttest(en2ru,'''Have you a ball?
	Yes, I have.
	Show me the ball!
	Cat, cat, catch a bat!
	Count the chickens!
	Catch that boy!
	Show me this rabbit!
	Count from ten to one!
	Have you a doll?
	No, I have not.
	Say ten words!''',
	'''У тебя есть мяч?
	Да, у меня есть.
	Покажи мне мяч!
	Кот, кот, поймай летучую мышь!
	Считай цыплят!
	Поймай того мальчика!
	Покажи мне этого кролика!
	Считай от десяти до одного!
	У тебя есть кукла?
	Нет, у меня нет.
	Скажи десять слов!''')

def test11():
	print('--- Lesson 11 ---')
	global N
	N=11

	ttest(en2ru,'How many balls have you?','Сколько у тебя мячей?')

	ttest(en2ru,'duck with duckling','утка с утёнком')

	ttest(en2ru,'''How many hens have you? I have eight
	hens.
	How many cows have you?''',
	'''Сколько у тебя куриц? У меня есть восемь
	куриц.
	Сколько у тебя коров?''')

	ttest(en2ru,'''We have one cow.
	How many dogs
	have you?
	I have two dogs.
	How many books
	has this boy?
	He has eleven.
	''',
	'''У нас есть одна корова.
	Сколько у тебя собак?
	У меня есть две собаки.
	Сколько у этого мальчика книг?
	У него есть одинадцать.''')

	ttest(en2ru,'''She has four.
	How many pens has she?
	She has ten pens.
	How many kittens have you?
	I have three kittens.
	''',
	'''У неё есть четыре.
	Сколько у неё ручек?
	У неё есть десять ручек.
	Сколько у тебя котят?
	У меня есть три котёнка.''')

	ttest(en2ru,'''I have a copy-book.
	You have a book.
	He has a ball.
	She has a doll.
	We have a cake.
	Have you many rabbits?
	We have many chickens.
	She has many hens.
	Count from ten to one!
	I see a girl with a doll.
	''',
	'''У меня есть тетрадь.
	У тебя есть книга.
	У него есть мяч.
	У неё есть кукла.
	У нас есть торт.
	У тебя есть много кроликов?
	У нас есть много цыплят.
	У неё есть много куриц.
	Считай от десяти до одного!
	Я вижу девочку с куклой.''')

	ttest(en2ru,'I see a girl with a doll.','Я вижу девочку с куклой.')

	ttest(en2ru,'cat with dog with rat','кот с собакой с крысой')

	ttest(en2ru,'It has four legs, a long tail and it give milk.',
		'У него есть четыре ноги, длинный хвост и оно даёт молоко.')

	ttest(en2ru,'it can give milk','оно может давать молоко')

	ttest(en2ru,'It has four legs, a long tail and it can give milk.',
		'У него есть четыре ноги, длинный хвост и оно может давать молоко.')

	ttest(en2ru_with_variants,[
		(dict_pronoun_ip['you'],"вы")
	],'''Have you a cat? Yes,
	we have.
	How many kittens has
	the cat?
	It has one kitten.
	How many ducks have
	you?
	We have two ducks and
	ten ducklings.''',
	'''У вас есть кот? Да,
	у нас есть.
	Сколько у
	кота котят?
	У него есть один котёнок.
	Сколько у
	вас уток?
	У нас есть две утки и
	десять утят.''')

	ttest(en2ru_with_variants,[
		(rv_noun_HAVE_noun,1) # не контекст
	],'''How many chickens has the hen?
	It has eleven.
	How many ducklings has the duck?
	It has eight.''',
	'''Сколько у курицы цыплят?
	У неё одинадцать.
	Сколько у утки утят?
	У неё восемь.''')

	ttest(en2ru_with_variants,[
		(rv_noun_HAVE_noun,1), # не контекст
		(dict_numeral['one'],"одна"),
		(dict_numeral['two'],"две")
	],'''How many kittens has the cat?
	It has three.
	How many dolls has the girl?
	She has two.
	How many sticks has the boy?
	He has five.
	How many hats have I?
	You have one.
	''',
	'''Сколько у кота котят?
	У него три.
	Сколько у девочки кукл?
	У неё две.
	Сколько у мальчика палок?
	У него пять.
	Сколько у меня шляп?
	У тебя одна.''')

def test12():
	print('--- Lesson 12 ---')
	global N
	N=12

	ttest(en2ru,'''They have a horse;
	it is black.
	They have a pig;
	it is big.
	They have a goat;
	it is white.
	They have a cow;
	the cow is red.
	They have no car.
	''',
	'''У них есть лошадь;
	она -- чёрная.
	У них есть свинья;
	она -- большая.
	У них есть коза;
	она -- белая.
	У них есть корова;
	корова -- красная.
	У них нет автомобиля.''')

	ttest(en2ru,'''We have four goats.
	We have a car; it is
	in the street.
	We have no ducks.
	''',
	'''У нас есть четыре козы.
	У нас есть автомобиль; он
	на улице.
	У нас нет уток.''')

	ttest(en2ru,'''You have a ribbon;
	it is in the box.''',
	'''У тебя есть лента;
	она в ящике.''')

	ttest(en2ru,'''You have a lemon;
	it is on the dish.
	You have no hens.
	''',
	'''У тебя есть лимон;
	он на блюде.
	У тебя нет куриц.''')

	ttest(en2ru,'He has one dog; it is black.',
	'У него есть одна собака; она -- чёрная.')

	ttest(en2ru,'''He has a hen; it has three chickens.
	He has a ball; it is big.
	''',
	'''У него есть курица; у него есть три цыплёнка.
	У него есть мяч; он -- большой.''')

	ttest(en2ru,'''She has a kitten; it is white.''',
	'У неё есть котёнок; он -- белый.')

	ttest(en2ru,'''This is a box; it is big.
	This is a rabbit; it is white.
	This is a girl; she is big.
	This is a boy; he is big too.
	''',
	'''Это ящик; он -- большой.
	Это кролик; он -- белый.
	Это девочка; она -- большая.
	Это мальчик; он тоже есть большой.''')

	ttest(en2ru,'''They have two kittens,
	three squirrels, eight
	ducklings and twelve
	chickens.
	''',
	'''У них есть два котёнка,
	три белки, восемь
	утят и двенадцать
	цыплят.''')

	ttest(en2ru,'This boy has a rabbit; it is in the box.',
	'У этого мальчика есть кролик; он в ящике.')

	ttest(en2ru,'That girl has a doll; it is big.',
	'У той девочки есть кукла; она -- большая.')

	ttest(en2ru,'She has a ribbon; the ribbon is red.',
	'У неё есть лента; лента -- красная.')

	ttest(en2ru,'The boy has a red star.',
	'У мальчика есть красная звезда.')

	ttest(en2ru,'We have twelve hens and eleven ducks.',
	'У нас есть двенадцать куриц и одинадцать уток.')

	ttest(en2ru,'He has a red horse.',
	'У него есть красная лошадь.')

	ttest(en2ru_with_variants,[
	    (dict_pronoun_ip['you'],"вы"),
	],'''How many lessons have you?
	We have five lessons.
	''',
	'''Сколько у вас уроков?
	У нас есть пять уроков.''')

	ttest(en2ru,'It has four legs, a short tail and it can give milk.',
	'У него есть четыре ноги, короткий хвост и оно может давать молоко.')

