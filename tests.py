import time

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

def ttest(f,arg,expected,ddt=5):
	ddt = len(repr(expected))
	global N
	try:
		start_time = time.time()
		test_OK = test(f(arg),expected)
		dt = time.time() - start_time
		if test_OK:
			pass
			#print('OK')
		global multiplier
		if dt*1000>multiplier*ddt:
			average = dt
			LEN = 10
			for i in range(LEN):
				start_time = time.time()
				f(arg)
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
		if isinstance(err,TestError):
			print('WARNING CATCHED')
			TEST_ERRORS.append({'N':N,'type':'warning','expected':expected,
								'warning':err})
			test_OK = False
		else:
			print('EXCEPTION CATCHED')
			TEST_ERRORS.append({'N':N,'type':'exception','expected':expected,
								'error':err})
			test_OK = True # не надо снова
		print(err)
	if not test_OK and f==en2ru:
		parse_system.warning_fun=warning_print
		try:
			scheme(arg)
		finally:
			parse_system.warning_fun=warning_hook

def warning_hook(s):
	raise TestError(s)
def warning_print(s):
	print(s)

TestError = None
parse_system = None
seq = None
W = None
SAttrs = None

tokenize = None

en2ru = None
decline = None
scheme = None
d_en2ru = None
pr_l_repr = None
p_noun = None
p_noun1 = None
r_noun_comma_noun = None

print_timing = None

def init(_parse_system, _TestError, _seq, _W, _SAttrs,
	_tokenize, 
	_en2ru, _decline, _scheme, _d_en2ru, _pr_l_repr, _p_noun, _p_noun1, _r_noun_comma_noun,
	_multiplier,_print_timing):
	global TestError
	global parse_system
	global seq
	global W
	global SAttrs

	global tokenize

	global en2ru
	global decline
	global scheme
	global d_en2ru
	global pr_l_repr
	global p_noun
	global p_noun1
	global r_noun_comma_noun

	global multiplier
	global print_timing

	TestError = _TestError
	parse_system = _parse_system
	seq = _seq
	W = _W
	SAttrs = _SAttrs

	tokenize = _tokenize

	en2ru = _en2ru 
	decline = _decline
	scheme = _scheme
	d_en2ru = _d_en2ru
	pr_l_repr = _pr_l_repr
	p_noun = _p_noun
	p_noun1 = _p_noun1
	r_noun_comma_noun = _r_noun_comma_noun

	multiplier = _multiplier
	print_timing = _print_timing


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


	test(p_noun(tokenize('cat,_cat,_a cat'),0)[0][1].tostr(),'кот,_кот,_кот')


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
	],8)#,20


	# In[42]:


	ttest(decline,'child, one child, children, two children, three children, five children',
	['ребёнок, один ребёнок, дети, два ребёнка, три ребёнка, пять детей',
	'нет ребёнка, одного ребёнка, детей, двух детей, трёх детей, пяти детей',
	'дать ребёнку, одному ребёнку, детям, двум детям, трём детям, пяти детям',
	'вижу ребёнка, одного ребёнка, детей, двух детей, трёх детей, пять детей',
	'творю ребёнком, одним ребёнком, детьми, двумя детьми, тремя детьми, пятью детьми',
	'думаю о ребёнке, одном ребёнке, детях, двух детях, трёх детях, пяти детях'])#,15

def test4():
	print('--- Lesson 4 (? видьте кота ?) ---')

	# In[43]:

	global N
	N=4


	# In[44]:


	ttest(en2ru,
	'''  A hat, a cup and a box.
	A bat, a hen and a fox.''',
	'''  Шляпа, чашка и ящик.
	Летучая мышь, курица и лиса.''',8)#,260


	# In[45]:


	ttest(en2ru,'I','я')#,60


	# In[46]:


	ttest(en2ru,'to see','видеть')#,20


	# In[47]:


	ttest(en2ru,'I see','я вижу')#,75


	# In[48]:


	ttest(en2ru,'see cat','видь кота')#,25


	# In[49]:


	ttest(en2ru,'''I see
	  a pig and a hen,
	  a dog and a gun,
	  a cat and a hat.''',
	'''Я вижу
	  свинью и курицу,
	  собаку и ружьё,
	  кота и шляпу.''',10)#,280


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


	ttest(en2ru,'have','имей')#,20


	# In[65]:


	ttest(en2ru,'I have a dog, but I have no cat.',
	      'У меня есть собака, но у меня нет кота.',10)#,45


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
	      'Скажи:" Семь, шесть, четыре, два, пять, три, один."',8)#,2200


	# In[86]:


	ttest(en2ru,'say: say seven','скажи: скажи семь',8)#,1200


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


	ttest(en2ru,'see','видь')


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


	ttest(en2ru,'have','имей')


	# In[99]:


	ttest(en2ru,'\nThis girl has three balls.','\nУ этой девочки есть три мяча.')

def test9():
	print('--- Lesson 9 ---')

	# In[100]:

	global N
	N=9


	# In[101]:


	ttest(en2ru,'She has ball','У Неё есть мяч')


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
	У того мальчика есть четыре ручки.''',17)


	# In[105]:


	ttest(en2ru,'''The girl has one dish.
	She has two spoons.
	The boy has three sticks.
	He has five stars.''',
	'''У девочки есть одно блюдо.
	У неё есть две ложки.
	У мальчика есть три палки.
	У него есть пять звёзд.''',17     )


	# In[106]:


	ttest(en2ru,'''This frog is on the log.
	That frog is in the lake.
	The snake is in the box.''',
	'''Эта ягушка на бревне.
	Та ягушка в озере.
	Змея в ящике.''',10     )


	# In[107]:


	ttest(en2ru,'''The spoon is in the cup.
	The squirrel is on the log.
	The doll is on the bed.''',
	 '''Ложка в чашке.
	Белка на бревне.
	Кукла на кровати.''',10    )


	# In[108]:


	ttest(en2ru,'''I like cakes.
	I have two cakes.
	He has two stars.
	She has three dolls.''',
	'''Я люблю торты.
	У меня есть два торта.
	У него есть две звезды.
	У неё есть три куклы.''',15     )


	# In[109]:


	ttest(en2ru,'''The doll is on the bed.
	The snake is in the lake.
	The hen is on the log.
	The bat is in the hat.''',
	 '''Кукла на кровати.
	Змея в озере.
	Курица на бревне.
	Летучая мышь в шляпе.''',15)


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
	У него есть шесть палок, но у него нет ружья.''',20     )


	# In[112]:


	ttest(en2ru,'''I like fish.
	One snake is in the lake.
	One frog is on the log.
	Jam is in the vase.''',
	'''Я люблю рыбу.
	Одна змея в озере.
	Одна ягушка на бревне.
	Джем в вазе.''',13     )

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
	Лови того кролика!''')

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
	Кот, кот, лови летучую мышь!
	Считай цыплят!
	Лови того мальчика!
	Покажи мне этого кролика!
	Считай от десяти до одного!
	У тебя есть кукла?
	Нет, у меня нет.
	Скажи десять слов!''')
