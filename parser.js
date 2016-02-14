// идея взята с https://habrahabr.ru/post/224081/

;var Parser = (function(Parser){
"use strict";
Parser = Parser || {};

//мы поняли то что прочитали, но это не то, что мы хотим
function ParseError(where,what,res){
	console.assert(typeof where == 'number','in ParseError where ('+where+') is not a number')
	this.err = 1
	this.what = what; // если what - массив, то where не имеет смысла
	this.where = where;
	this.res = res; // не обязательный
}
//мы не поняли, что прочитали
function FatalError(where,what){
	assert.isNumber(where,'in FatalError')
	this.err = 2
	this.what = what; // если what - массив, то where не имеет смысла
	this.where = where;
}

// is result
function isGood(r){
	return typeof r === 'object' ? !r.err : r!==undefined ;
}

// is result or ParseError
function notFatal(r){
	return typeof r === 'object' ? r.err===undefined || r.err<2 : r!==undefined ;
}

// основной конструктор
function Pattern(exec) {
	// если pos не передан, то строка должна соответствовать паттерну от начала и до конца
	// иначе ParseError(pos.x,'остались неразобранные символы',r)
    this.exec = function pattern_exec(str, pos/*.x*/){
		if(pos === undefined){
			pos = {x:0}//и далее передаем всегда по ссылке
			var r = exec(str,pos);
			if(!isGood(r))
				if(!r)
					return new FatalError(pos.x,'unknown error')
				else
					return r;
			else
				if(pos.x == str.length)		
					return r;
				else
					return new ParseError(pos.x,'unparsed chars are remained',r);
		}
		else return exec(str,pos);
	};
	// если результат - то transform, иначе - error_transform
	// можно преобразовать результат в ошибку и наоборот
    this.then = function pattern_then(transform/*(r,x)*/,error_transform/*(x,r)*/) {
		if(error_transform){
			console.assert(typeof error_transform === 'function')
			if(typeof tranform === 'function')
				return new Pattern(function pattern_then_reserr(str,pos/*.x*/){
					var x = pos.x;
					var r = exec(str, pos);
					return (!isGood(r)) ? 
						error_transform(x,r) : 
						transform(r,x);
				});
			else
				return new Pattern(function pattern_then_err(str,pos/*.x*/){
					var x = pos.x;
					var r = exec(str, pos);
					return (!isGood(r)) ? 
						error_transform(x,r) : 
						r;
				});
		}
		else if(typeof transform === 'function')
			return new Pattern(function pattern_then_res(str, pos/*.x*/) {
				var x = pos.x;
				var r = exec(str, pos);
				return (!isGood(r)) ? 
					r : 
					transform(r,x);
			});
	}
}
function Forward(){
	this.exec = function forwrd_exec(){		return this.pattern.exec.apply(this.pattern,arguments);	}
	this.then = function forward_then(){	return this.pattern.then.apply(this.pattern,arguments);	}
}


// если текст читается - возвращает его, иначе ничего
function txt(text) {
    return new Pattern(function txt_pattern(str, pos) {
        if (str.substr(pos.x, text.length) == text)	{
			pos.x += text.length;
			return text;
		}
    });
}

// если regexp читается (не забываем в начале ставить ^) 
//- возвращает массив разбора ([0] - вся строка, [1]... - соответствуют скобкам из regexp)
//, иначе ничего
function rgx(regexp) {
	console.assert(regexp instanceof RegExp, 'в rgx передан аргумент неправильного типа');
    return new Pattern(function rgx_pattern(str, pos) {
		var m;
        if (m = regexp.exec(str.slice(pos.x))){
			pos.x += m.index + m[0].length;
			return m
		}
    });
}

// ошибку или ничего преобразует в неошибку
// позицию восстанавливает, если ошибка
function opt(pattern) {
    return new Pattern(function opt_pattern(str, pos) {
		var x = pos.x;
        var r = pattern.exec(str, pos)
		if(!isGood(r))	{
			pos.x=x;	
			return {err:0};	//не ошибка	
		}
		return r;
    });
}

// читает последовательность, в случае неудачи позицию НЕ восстанавливает
function seq(isFatal/*(res//.a//,r//.res//,i,pos)*/, ...patterns) {
    return new Pattern(function seq_pattern(str, pos) {
        var res = {a:[]}; // a - array
        for (var i = 0; i < patterns.length; i++) {
            var r = { res : patterns[i].exec(str, pos) };
            if( isFatal(res,r,i,pos.x) )
				return r.res;
        }
        return res.a;
    });
}

// в случае ParseError у результата устанавливает .err=1 и .what = массиву ошибок ParseError
function need(...indexes){
	// резултат - после прочтения одного паттерна
	// ответ - результат всего seq
	if(indexes.length == 0)
		// + ВСЕ одиночные результаты добавляет в ответ как в массив
		return function need_all(res/*.a*/,r/*.res*/,i,pos){ // isFatal()
			if(!notFatal(r.res))
				return true;
			if(!isGood(r.res)){
				res.a.err = 1;
				if(res.a.what)
					res.a.what.push(r.res);
				else
					res.a.what = [r.res];
			}
			res.a.push(r.res);
			return false;
		}
	if(indexes.length == 1)
		// + единственный нужный результат становится ответом
		return function need_one(res/*.a*/,r/*.res*/,i,pos){ // isFatal()
			if(!notFatal(r.res))
				return true;
			if(!isGood(r.res)){
				res.a.err = 1;
				if(res.a.what)
					res.a.what.push(r.res);
				else
					res.a.what = [r.res];
			}
			if(i==indexes[0])	res.a = r.res;
			return false;
		}
	else
		// + добавляет результаты в заданные позиции ответа
		return function need_custom(res/*.a*/,r/*.res*/,i,pos){ // isFatal()
			if(!notFatal(r.res))
				return true;
			if(!isGood(r.res)){
				res.err = 1;
				if(res.what)
					res.what.push(r.res);
				else
					res.what = [r.res];
			}
			var k = indexes.indexOf(i);
			if(k!=-1)	res.a[k] = r.res;
			return false;
		}
}

// #todo сделать ограничения по количеству прочтений from & to

// читает последовательность паттернов, разделенных сепаратором
// ответ - массив результатов паттернов
// от паттерна не требует восстанавливать позицию в случае неудачи (делает это сам)
// если указан then - с его помощью обрабатываются пары seq(need(), separator, pattern)
function rep(pattern, options, separator, then) {
	var min = options && options.min || 0;
	var max = options && options.max || +Infinity;
	console.assert(0<=min && min<=max && 1<=max);
    var separated = !separator ? pattern :
		then ? seq(need(), separator, pattern).then(then) :
        seq(need(1), separator, pattern);

    return new Pattern(function rep_pattern(str, pos) {
        var res = [], x = pos.x, r = pattern.exec(str, pos);
		var i = 1;

		if(min>0 && !isGood(r)/* && isGoog(res)*/){
			res.err = 1;
			res.where = x;
			res.what = r.what;
		}
        while (i<min && notFatal(r)) {
			if(!isGood(r) && isGoog(res)){
				res.err = 1;
				res.where = x;
				res.what = r.what;
			}
            res.push(r);
            x = pos.x;
            r = separated.exec(str, pos/*.x*/);
			i++;
        }
		if(min>0 && !notFatal(r)){
			pos.x = x;
			return r;
		}
		if(!isGood(res) || i==1 && !isGood(r)){
			pos.x = x;
			return res;
		}
		
        while (i<max && isGood(r)) {
            res.push(r);
            x = pos.x;
            r = separated.exec(str, pos/*.x*/);
			i++;
        }
		if(isGood(r))
			res.push(r);
		else
			pos.x = x;
        return res;
    });
}


// то же что и rep, только допускает возможность ParseError
// в этом случае устанавливает .err = 1
function rep_more(pattern, separator) {
    var separated = !separator ? pattern :
        seq(need(1), separator, pattern);

    return new Pattern(function rep_more_pattern(str, pos/*.x*/) {
        var res = [], x = pos.x, r = pattern.exec(str, pos);
        while (notFatal(r)) {
            res.push(r);
			if(r.err) res.err = 1;
            x = pos.x;
            r = separated.exec(str, pos);
        }
		pos.x = x;
        return res;
    });
}

// перебирает паттерны с одной и той же позиции до достижения удачного результата
function any(isGood, ...patterns) {
    return new Pattern(function any_pattern(str, pos/*.x*/) {
		var errs = {a:{	err:2,//default fatal
						what:[]}}, 
			x = pos.x;
        for (var r, i = 0; i < patterns.length; i++){
			pos.x = x; // что бы у isGood была возможность выставить pos перед выходом из цикла
            r = patterns[i].exec(str, pos)
            if( isGood(errs,r,i,pos) )
				return r;
		}
		return errs.a;
    });
}
//сначала надо указывать попытки удачного прочтения, 
//а только потом попытки восстановления после ошибок

//неудачные результаты собирает в what как в массив
function collect(errs/*.a*/,r,i,pos/*.x*/){ // isGood
	if(r && (!r.err || r.err<=1) )
		return true;
	if(!r)
		return false;
	errs.a.what.push(r)//collect
	return false;
}

//ничего не собирает
function notCollect(errs/*.a*/,r,i,pos/*.x*/){//isGood
	return (r && (!r.err || r.err<=1) ); 
	/* далее идет неоптимизированный вариант предыдущей строчки
	if(r && r.err<=1 )
		return true;
	if(!r)
		return false;
	//not collect
	return false;
	*/
}

// #todo как понадобится - доделать
function exc(pattern, except) {
    return new Pattern(function exc_pattern(str, pos/*.x*/) {
        return !isGood(except.exec(str, pos)) && pattern.exec(str, pos);
    });
}

Parser.ParseError = ParseError;
Parser.FatalError = FatalError;
Parser.isGood = isGood;
Parser.notFatal = notFatal;
Parser.Pattern = Pattern;
Parser.Forward = Forward;
Parser.opt = opt;
Parser.txt = txt;
Parser.rgx = rgx;
Parser.seq = seq;
Parser.need = need;
Parser.rep = rep;
Parser.rep_more = rep_more;
Parser.any = any;
Parser.collect = collect;
Parser.notCollect = notCollect;
//Parser.exc = exc;

//alert('Parser загружен')
return Parser;
})()
